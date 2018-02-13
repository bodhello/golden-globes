# -*- coding: utf-8 -*-
"""
Group members: 

David Wallach (daw647),
Bodhi Alarcon (bta566),
Junhao Li,
Weixin


This program uses the global variable YEAR to find the Wikipedia page of the associated
golden globes event. From the Wikipedia page, it scrapes the name of all the awards given as well 
as the host(s) of the event. 


Parser to find:

	1. Host(s) 
	2. Award Names
	3. Presenters
	4. Nominees
	5. Winners

	** Host(s) & Award Names are parsed from Wikipedia, all else is deduced from Twitter's tweets **
 

To Run:
	set the YEAR variable to the desired year in this file and then 
	>> python parser.py
"""

import os
import re
from operator import itemgetter
from collections import defaultdict 
import json
import requests
from bs4 import BeautifulSoup
import numpy as np


# GLOBAL DECLARATIONS

YEAR = 2018 			# the year the ceremony we want to find info abotu
FIRST = 1944 			# first ever golden globe
EXT = '../gg2018.json'	# path to twitter data from current file
suffixs = {				# dict used to convert year to word for url 

	1: "st",
	2: "nd",
	3: "rd",
}

regexs = {

	"name":  r'([A-Z][a-z]+(?=\s[A-Z])(?:\s[A-Z][a-z]+)+)'
}


nominee_words   = 'nom'
winner_words    = '(congr|win|won)'
presenter_words = '(pre|present)'
remove_words    = '(Best|Golden|Globe|Actor|Actress|Picture|Motion|Award|Year|Film|Animated|Feature)'



class Ceremony(object):
	"""
	Represents the whole ceremony
	"""
	def __init__(self, year):
		"""
		initalized year to be year and populates the awards list, name string, and
		host string using the scrape_names mehtod of the Ceremony class
		"""
		self.year = year
		self.awards = []
		self.hosts = []
		self.name = ''
		self.scrape_names()
		self.remove_words = self.build_remove_words()
		# print ("setting remove words to be {}".format(self.remove_words.encode('utf-8')))


	def __str__(self):
		"""
		string representation of a ceremony

		will build out later to inclue all the findings 
		"""
		return ("\nThe {} held during {}" .format(self.name, self.year))


	def scrape_names(self):
		"""
		Uses wikipeadia page of the golden globes ceremony associated with the YEAR global variable.
		Populates the ceremony object's awards, host and name attributes.  
		"""

		num_award = YEAR - FIRST + 1

		if (num_award % 10) in suffixs.keys():
			str_format = str(num_award) + suffixs[num_award % 10]
		else:
			str_format = str(num_award) + "th"

		# update ceremony object's name 
		self.name = str_format + " Golden Globe Awards"

		
		# make the web request and get the infromation from wiki page
		url = 'https://en.wikipedia.org/wiki/{}_Golden_Globe_Awards'.format(str_format)
		result = requests.get(url)
		c = result.content

		# store in BeautifulSoup object to parse HTML DOM
		soup = BeautifulSoup(c, "lxml")
		

		#
		#	Find Awards 
		#
		awards_div = soup.find("div", {"aria-labelledby" : "Golden_Globe_Awards"})

		awards = []
		tds = awards_div.find_all("td")
		for td in tds:
			lis = td.find_all("li")

			for li in lis:
				a = li.find("a")
				try:
					title = a["title"]
					award = Award(title)
					awards.append(award)
				except:
					continue


		awards_filtered = filter(lambda award: award.title.startswith("Golden Globe Award"), awards)	 # filter noise from awards list
		self.awards = awards_filtered 	# update ceremony object's award attribute


		#
		#	Find Host
		#
		hosts = []
		table = soup.find("table", {"class" : "infobox vevent"})
		trs = table.find_all("tr")
		for tr in trs:
			try:
				th = tr.find("th")
				if th.text == "Hosted by":
					a_tags = tr.find_all("a")
					for a in a_tags:
						hosts.append(a.text)
			except:
				continue

		# update ceremony object's host attribute
		self.hosts = hosts

	
	def build_remove_words(self):
		"""
		"""
		begin = '('
		end   = ')'
		keepers = ['the', 'for', '-', 'of', 'or', 'New']
		for award in self.awards:

			begin += '|'.join([word for word in award.title.split(' ') if word not in keepers])

		begin += end
		return begin


	def build_award_features(self):
		"""	
		Creats a list of most uncommon words found in each award based on all words present in all awards.
		Then sets each Award object in self.awards list to have the associated features list. 
		Used to find most important words in each award which is then used for matching tweets to associated awards.
		"""
		award_names = [award.title for award in self.awards]
		phrase_freqs = self.count_phrases(award_names, 1)


		# converts the phrase_freqs dictionary into a sorted list in ascending order
		# it creates each index as a tuple with the val[0] being the phrase
		# and val[1] being the frequency of that phrase
		phrase_freqs_sorted = sorted(phrase_freqs.items(), key=itemgetter(1), reverse=False)


		award_names = [award.title.split(' ') for award in self.awards]
		features_list = [[] for i in range(len(award_names))]
		min_len = np.zeros(len(award_names))
		feature_max = 5

		for val, freq in phrase_freqs_sorted:
			# check if we found a total of feature_max features
			if min(min_len) == feature_max: 
				break

			i = 0
			while i < len(award_names):
				# check if this value is in the award name
				if val.capitalize() in award_names[i]:
					if min_len[i] < feature_max:
						if val == 'Television':
							features_list[i].append('(Television)|(TV)')
						else:
							features_list[i].append(val)
						min_len[i] += 1
				i += 1


		for i, award in enumerate(self.awards):
			# print ("setting {} to have || features: {}".format(award.title.encode('utf-8'), features_list[i]))
			award.features_list = features_list[i]
	

	def remove_stop_words(self, words, stop_words):
		"""
		uses the stop_word string to remove all words represented in the stop_word string.
		the stop_word string is 1-x number of words concatenated together. 
		"""
		clean_words = []
		for word in words:
			if not re.search(word, stop_words, flags=re.I):
				clean_words.append(word)
		return clean_words
		

	def count_phrases(self, data, phrase_length, stop_words=None):
		"""
		Builds a frequency distrobution of all combinations of words of size phrase_length present in the
		given list, if one of the words present is in the stop_words then it will not be considered.
		"""
		phrase_freqs = defaultdict(lambda: 0)
		for i in range(len(data)):
			words = re.findall(r'[a-zA-Z]+', data[i])

			if stop_words != None:
				words = self.remove_stop_words(words, stop_words)

			for j in range(len(words) - phrase_length + 1):
				tmp_phrase = ''
				for k in range(phrase_length):
					tmp_phrase += words[j+k].lower()
					if k != phrase_length - 1:
						tmp_phrase += ' '

				phrase_freqs[tmp_phrase] += 1

		return phrase_freqs


	def clean_words(self, data, mode, min_word_len=3, word_dict=[]):
		"""
		if mode set to 1: filters out all words in each data instance with words less than min_word_len
		if mode set to not 1: filters out all words in each data instance if not present in word_dict
		returns a list of 'clean' data
		"""
		clean_data = []
		for inst in data:

			if mode == 1:
				words = filter(lambda w: len(w) >= min_word_len, inst.split(' '))
			else:
				words = filter(lambda w: w in word_dict, inst.split(' '))

			if len(words):
				clean_data.append(' '.join(words))

		return clean_data


	def keyword_search(self, keyword, data):
		"""
		"""
		matches = []
		for inst in data:
			if re.search(keyword, inst, flags=re.I):
				matches.append(inst)
		return matches


	def consolidate_freqs(self, freqs):
		"""

		"""
		top_5 = freqs[:5]
		rest  = freqs[5:]
		consolidated = {}

		for inst in top_5:
			total = inst[1]

			for sub_inst in rest:
				if self.similar(sub_inst[0], inst[0]):
					total += sub_inst[1]
			consolidated[inst] = total
		return consolidated


	def similar(self, phrase1, phrase2, threshold=0.8):
		"""
		"""
		total = 0
		p1_len = len(phrase1)
		p2_len = len(phrase2)
		ratio = 0.0
		if p1_len < p2_len:
			p2_split = phrase2.split(' ')
			for p in phrase1.split(' '):
				if p in p2_split:
					total += 1

			ratio = float(total / p1_len)

		else:
			p1_split = phrase1.split(' ')
			for p in phrase2.split(' '):
				if p in p1_split:
					total += 1

			ratio = float(total / p2_len) 

		return ratio >= threshold


	def parse_tweets(self, tweets):
		"""
		used to analyze the set of tweets and try to populate the winner, nominees, and presenter attributes of 
		each Award object in the Ceremony's awards attribute. 
		"""

		# print ("length of total tweets is {}".format(len(tweets)))
		tweets = list(set(self.clean_words(tweets, 1, 1)))
		# print ("length of clean tweets is {}".format(len(tweets)))


		# pl_ratio = []
		# iterate over all features for each index
		for award_idx in range(len(self.awards)):
			associated_tweets = tweets

			# if award_idx > 1: break

			# for feature_idx in range(len(self.awards[award_idx].features_list)):
			for feature_idx in range(2):
				features_list = self.awards[award_idx].features_list
				# feature = features_list[len(features_list) - feature_idx - 1]
				feature = features_list[feature_idx]
				associated_tweets = self.keyword_search(feature, associated_tweets)


				# print ('Found {} associated_tweets for award {}'.format(len(associated_tweets), self.awards[award_idx].title.encode('utf-8')))

				for tweet in associated_tweets:
					names = re.findall(regexs["name"], tweet)
					nominee = False
					winner = False
					presenter = False

					tweet_compact = ''.join(tweet.split(' '))
					if re.search(nominee_words, tweet_compact, flags=re.IGNORECASE):    nominee     = True
					if re.search(winner_words, tweet_compact, flags=re.IGNORECASE):     winner      = True
					if re.search(presenter_words, tweet_compact, flags=re.IGNORECASE):  presenter   = True
					

					for name in names:
						if winner:    self.awards[award_idx].winner[name] += 1
						if nominee:   self.awards[award_idx].nominees[name] += 1
						if presenter: self.awards[award_idx].presenters[name] += 1

			# winner = ''
			# pl_val = 0
			# for pl in range(2,6):
				# phrase_freqs = self.count_phrases(associated_tweets, pl)
				# s_phrase_freqs = sorted(phrase_freqs.items(), key=itemgetter(1), reverse=True)
				# print('freq distrobution for {}'.format(self.awards[award_idx].title.encode('utf-8')))
				# for val, freq in s_phrase_freqs[10:]:
				# 	print ('{} : {}'.format(val, freq))

				# if s_phrase_freqs:
				# 	curr_pl = s_phrase_freqs[0][1] / sum(phrase_freqs.values())
				# 	# print ('current pl is {}'.format(curr_pl))
				# 	pl_ratio.append(curr_pl)
				# 	if pl_val < curr_pl:
				# 			winner = s_phrase_freqs[0][0]
				# 			pl_val = curr_pl
			# if winner:
			# 	print ('Found winner: {} for award {}'.format(winner, self.awards[award_idx].title.encode('utf-8')))


		for award in self.awards:

			print ('For award: {}'.format(award.title.encode('utf-8')))

			winner = sorted(award.winner.items(), key=itemgetter(1), reverse=True)
			winner = filter(lambda w: not re.search(remove_words, w[0]), winner)
			winner = self.consolidate_freqs(winner)
			wns = [w[0] for w in winner]
			# print ('Winner is: {}'.format(winner[0][0]))
			print ('Winner is: {}'.format(wns))
			
			# nominees = sorted(award.nominees.items(), key=itemgetter(1), reverse=True)
			# nominees = filter(lambda w: not re.search(remove_words, w[0]), nominees)
			# ns = [n[0] for n in nominees[:5]]
			# print ('Nominees are: {}'.format(ns))

			# presenters = sorted(award.presenters.items(), key=itemgetter(1), reverse=True)
			# presenters = filter(lambda w: not re.search(remove_words, w[0]), presenters)
			# prs = [n[0] for n in presenters[:5]]
			# print ('Presenters are: {}'.format(prs))



class Award(object):
	"""
	Represents a single award
	"""
	def __init__(self, title):
		self.title = title
		self.presenters = defaultdict(lambda: 0)
		self.nominees = defaultdict(lambda: 0)
		self.winner = defaultdict(lambda: 0)
		self.features_list = []


def read_tweets():
	"""
	Reads in all the tweets into a list and returns the list. 
	Uses the global EXT variable to find the data file.
	"""
	cwd = os.getcwd() 
	path = cwd + '/' + EXT
	f = open(path)

	tweets_json = json.load(f)
	tweets = []
	for tweet in tweets_json:
		tweets.append(tweet['text'])
	return tweets



if __name__ == "__main__":
	ceremony = Ceremony(YEAR)
	ceremony.scrape_names()
	ceremony.build_award_features()
	tweets = read_tweets()
	ceremony.parse_tweets(tweets)
	print (ceremony)



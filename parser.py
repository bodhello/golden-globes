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
EXT = 'gg2018.json'		# path to twitter data from current file

suffixs = {				# dict used to convert year to word for url 

	1: "st",
	2: "nd",
	3: "rd",
}


class Ceremony(object):
	"""
	Represents the whole ceremony
	"""
	def __init__(self, year):
		self.year = year
		self.awards = []
		self.hosts = []
		self.name = ''
		self.scrape_names()



	def __str__(self):
		"""
		string representation of a ceremony

		will build out later to inclue all the findings 
		"""
		return ("\nThe {} held during {}" .format(ceremony.name, self.year))


	def scrape_names(self):
		"""
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


		# filter noise from awards list
		awards_filtered = filter(lambda award: award.title.startswith('Golden Globe Award'), awards)
		self.awards = awards_filtered 	# update ceremony object


		# for a in awards_filtered:
		# 	print (a.title)	

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

		# update ceremony object with host  
		self.hosts = hosts




	def build_award_features(self):
		"""	
		Creats a list of most uncommon words found in each award based on all words present in all awards.
		Then sets each Award object in self.awards list to have the associated features list. 
		Used to find most important words in each award which is then used for matching tweets to associated awards.
		"""

		phrase_freqs = self.count_phrases(phrase_length=1)


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
		

	def count_phrases(self, phrase_length, stop_words=None):
		"""
		Builds a frequency distrobution of all combinations of words of size phrase_length present in the
		given list, if one of the words present is in the stop_words then it will not be considered.
		"""
		phrase_freqs = defaultdict(lambda: 0)
		for i in range(len(self.awards)):
			words = re.findall(r'[a-zA-Z]+', self.awards[i].title)

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



	# def parse_tweets(tweets):
	# 	for award_idx in range(len(self.awards)):

	# 		for i in range(len(self.awards[award_idx].features_list)):



class Award(object):
	"""
	Represents a single award
	"""
	def __init__(self, title):
		self.title = title
		self.presenters = []
		self.nominees = []
		self.winner = None
		self.features_list = []
		self.confidence = 0




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
		tweets.append(tweet)
	return tweets

if __name__ == "__main__":
	ceremony = Ceremony(YEAR)
	ceremony.scrape_names()
	ceremony.build_award_features()
	# tweets = read_tweets()
	print (ceremony)


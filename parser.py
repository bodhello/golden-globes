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

	def __str__(self):
		return ("\nThe {} held during {}" .format(ceremony.name, self.year))


	def build_award_features(self):
		"""	
		"""

		phrase_freqs = self.count_phrases(phrase_length=1)


		# converts the phrase_freqs dictionary into a sorted list in ascending order
		# it creates each index as a tuple with the val[0] being the phrase
		# and val[1] being the frequency of that phrase
		phrase_freqs_sorted = sorted(phrase_freqs.items(), key=itemgetter(1), reverse = False)


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
				# check if this value is in the award nam
				if val.capitalize() in award_names[i]:
					if min_len[i] < feature_max:
						if val == 'Television':
							features_list[i].append('(Television)|(TV)')
						else:
							features_list[i].append(val)
						min_len[i] += 1
				i += 1





		# for i, award in enumerate(self.awards):
		# 	print ("setting {} to have || features: {}".format(award.title.encode('utf-8'), features_list[i]))
		# 	award.features_list = features_list[i]


	def count_phrases(self, phrase_length=2):
		"""
		"""
		phrase_freqs = defaultdict(lambda: 0)
		for i in range(len(self.awards)):
			words = re.findall(r'[a-zA-Z]+', self.awards[i].title)

			for j in range(len(words) - phrase_length + 1):
				tmp_phrase = ''
				for k in range(phrase_length):
					tmp_phrase += words[j+k].lower()
					if k != phrase_length - 1:
						tmp_phrase += ' '

				phrase_freqs[tmp_phrase] += 1

		return phrase_freqs


class Award(object):
	"""
	Represents a single award
	"""
	def __init__(self, title):
		self.title = title
		self.presenters = []
		self.nominees = []
		self.winner = None
		self.confidence = 0

def scrape_names(ceremony):
	"""
	"""

	num_award = YEAR - FIRST + 1

	if (num_award % 10) in suffixs.keys():
		str_format = str(num_award) + suffixs[num_award % 10]
	else:
		str_format = str(num_award) + "th"

	# update ceremony object's name 
	ceremony.name = str_format + " Golden Globe Awards"

	
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
	ceremony.awards = awards_filtered 	# update ceremony object


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
	ceremony.hosts = hosts


	return ceremony

def parse_tweets():
	"""
	uses ijson to parse the json representation of the tweets. Since there are so
	many tweets, ijson uses a generator allowing the program to not use all of its 
	memory on storing the tweets

	"""
	cwd = os.getcwd() 
	path = cwd + '/' + EXT
	f = open(path)


	tweets = json.load(f)

	# i = 0
	# for tweet in ijson.items(f, 'item'):
	# 	print (tweet)
	# 	i += 1
	# 	if i > 25: break


if __name__ == "__main__":
	ceremony = Ceremony(YEAR)
	ceremony = scrape_names(ceremony)
	ceremony.build_award_features()
	print (ceremony)
	# parse_tweets()
	# print_results(ceremony)


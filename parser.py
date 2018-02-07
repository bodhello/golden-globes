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
import ijson
import requests
from bs4 import BeautifulSoup


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
	def __init__(self, year):
		self.year = year
		self.awards = []
		self.hosts = []




class Award(object):
	def __init__(self, title):
		self.title = title
		self.presenters = []
		self.nominees = []
		self.winner = None
		self.confidence = 0



def scrape_names(ceremony):
	"""
	"""

	num_award = YEAR - FIRST

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

	i = 0
	for tweet in ijson.items(f, 'item'):
		print (tweet)
		i += 1
		if i > 25: break



def print_results(ceremony):
	"""
	prints the results of the programs findings in a nice and neat format
	"""
	print ("\nThe {} held during {}" ).format(ceremony.name, YEAR)
	if len(ceremony.hosts) > 1:
		# multiple hosts
		print ("Hosted by: {}").format(' and '.join(ceremony.hosts))
	else:
		# only one host
		print ("Hosted by: {}").format(ceremony.hosts[0])
	# for award in ceremony.awards:
	# 	print ("For award: {}").format(award.title)
	# 	print ("the presenters were: {}").format(" ".join(award.presenters))
	# 	print ("the nominees were: {}").format(" ".join(award.nominees))
	# 	print ("the winner was: {}").format(award.winner)


if __name__ == "__main__":
	ceremony = Ceremony(YEAR)
	ceremony = scrape_names(ceremony)
	# parse_tweets()
	print_results(ceremony)


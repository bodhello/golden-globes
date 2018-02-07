#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  6 11:16:13 2018

@author: weixinjiang
"""

from lxml import html
import requests
import re

def get_award_name(url='http://www.thetvaddict.com/2018/01/07/golden-globe-awards-golden-globes-2018-winners/?utm_source=dlvr.it&utm_medium=twitter'):
    page = requests.get(url)
    m = re.findall('>+best[^<]+<+',page.text,flags=re.I)
    award_name = []
    for i in range(len(m)):
        tmp = re.findall('[\w]+',m[i])
        award_name.append(tmp)
        
    return award_name

#page = requests.get('http://www.thetvaddict.com/2018/01/07/golden-globe-awards-golden-globes-2018-winners/?utm_source=dlvr.it&utm_medium=twitter')
#tree = html.fromstring(page.content)
#
###This will create a list of buyers:
##buyers = tree.xpath('//div[@title="buyer-name"]/text()')
###This will create a list of prices
##prices = tree.xpath('//span[@class="item-price"]/text()')
#
##regex = re.compile('>+best[^<]+<+',flags = re.I)
#m = re.findall('>+best[^<]+<+',page.text,flags=re.I)
#award_name = []
#for i in range(len(m)):
#    tmp = re.findall('[\w]+',m[i])
#    award_name.append(tmp)
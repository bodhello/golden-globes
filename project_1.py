#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  7 14:22:57 2018

@author: weixinjiang
"""

# =============================================================================
# import modules
# =============================================================================
from lxml import html
import requests
import json
import re
from operator import itemgetter
import numpy as np
import copy

# =============================================================================
# get award name from the website (online)
# =============================================================================
def get_award_name(url='http://www.thetvaddict.com/2018/01/07/golden-globe-awards-golden-globes-2018-winners/?utm_source=dlvr.it&utm_medium=twitter'):
    page = requests.get(url)
    m = re.findall('>+best[^<]+<+',page.text,flags=re.I)
    award_name = []
    for i in range(len(m)):
        tmp = re.findall('[\w]+',m[i])
        award_name.append(tmp)
    assert award_name    
    return award_name

# =============================================================================
# function defining: KeywordSearch
# =============================================================================
def KeywordSearch(keyword,dataset):
    new_dataset = []
    for data in dataset:
        if re.search(keyword,data,flags=re.I):
            new_dataset.append(data)
    assert new_dataset
    return new_dataset

def DeleteWord(word_list,word_dict):
    new_word_list = []
    for word in word_list:
        if not re.search(word,word_dict,flags = re.I):
            new_word_list.append(word)
    return new_word_list

def CountsPhrase(dataset,phrase_length=2,delete_mode=0,word_dict_delete=''):
    counts_phrase = dict()
    for i in range(len(dataset)):
        tmp_word_list = re.findall('[a-zA-Z]+',dataset[i])
        if delete_mode:
            tmp_word_list = DeleteWord(tmp_word_list,word_dict_delete)
        for j in range(len(tmp_word_list)-phrase_length+1):
            tmp_phrase=''
            for k in range(phrase_length):
                if k == phrase_length-1:
                    tmp_phrase += tmp_word_list[j+k].lower().capitalize()
                else:
                    tmp_phrase += tmp_word_list[j+k].lower().capitalize()
                    tmp_phrase += ' '
            if tmp_phrase in counts_phrase:
                counts_phrase[tmp_phrase] += 1
            else:
                counts_phrase[tmp_phrase] = 1
#    assert counts_phrase
    return counts_phrase
    
def CreateDict(counts_phrase,counts_threshold):
    sorted_counts_phrase = sorted(counts_phrase.items(),key=itemgetter(1),reverse=True)
    word_dict = []
    for phrase in sorted_counts_phrase:
        if phrase[1] < counts_threshold:
            break
        else:
            tmp_word_list = re.findall('[a-zA-Z]+',phrase[0])
            for word in tmp_word_list:
                if not word.lower() in word_dict:
                    word_dict.append(word.lower())
    #word_dict = list(set(word_dict))
    assert word_dict
    return word_dict

def CleanData(dataset,clean_mode=2,word_min_len=3,word_dict=[]):
    cleaned_dataset = []
    if clean_mode == 1:
        for data in dataset:
            tmp_str = ''
            tmp_word_list = re.findall('[a-zA-Z]+',data)
            for word in tmp_word_list:
                if not len(word) < word_min_len:
                    tmp_str += word.lower().capitalize()
                    tmp_str += ' '
            if tmp_str:
                cleaned_dataset.append(tmp_str)
    else:
        for data in dataset:
            tmp_word_list = re.findall('[a-zA-Z]+',data)
            tmp_str = ''
            for word in tmp_word_list:
                if word.lower() in word_dict:
                    tmp_str += word.lower().capitalize()
                    tmp_str += ' '
            if tmp_str:
                cleaned_dataset.append(tmp_str)
    assert cleaned_dataset
    return cleaned_dataset 
# =============================================================================
# loading data
# =============================================================================
dataset_tweets = json.load(open('gg2018.json'))
award_name = get_award_name()

# =============================================================================
# plain transform the original tweets
# =============================================================================
data_original = []
for i in range(len(dataset_tweets)):
    a = dataset_tweets[i]
    data_original.append(a['text'])
    
# =============================================================================
# translating award name into well-organized strings
# =============================================================================
award_name_v=[]
for i in range(len(award_name)):
    tmp_str=''
    for word in award_name[i]:
        tmp_str += word
        tmp_str += ' '
    award_name_v.append(tmp_str)

# =============================================================================
# Award Representation
# =============================================================================
counts_award_word = CountsPhrase(award_name_v,1,0,'')
sorted_counts_award_word = sorted(counts_award_word.items(), key=itemgetter(1), reverse = False)

award_feature_list = [([]) for i in range(len(award_name))]
min_len = np.zeros(len(award_name))
Feature_Max = 5
for value,freq in sorted_counts_award_word:
    if min(min_len) == Feature_Max:
        break
    i = 0
    while i<len(award_name):
        if value.capitalize() in award_name[i]:
            if min_len[i] < Feature_Max:
                if value == 'Television':
                    award_feature_list[i].append('(Television)|(TV)')
                else:
                    award_feature_list[i].append(value)
                min_len[i] += 1
        i += 1

uniqueness_check = []
for feature in award_feature_list:
    tmp = ''
    for i in range(len(feature)):
        tmp += feature[i]
    uniqueness_check.append(tmp)
    
if len(uniqueness_check) == len(list(set(uniqueness_check))):
    print('separable features')
else:
    print('enlarge the parameter FEATURE_MAX',len(list(set(uniqueness_check))))
    
# =============================================================================
# Get Names or Meaningful Phrases from the tweets
# =============================================================================

 
# =============================================================================
# Get Winner for each award
# =============================================================================
word_dict_delete = ''
for word in sorted_counts_award_word:
    word_dict_delete += word[0]
word_dict_delete += 'goldenglobeshttpsandwinnercongratulationsourwinnerwonwins'

data_original_c = list(set(CleanData(data_original,1,1,[])))

pl_ratio = []
for AWARD_INDEX in range(len(award_name)):
    data_award = data_original_c
    for i in range(len(award_feature_list[AWARD_INDEX])):
        tmp_feature_list = award_feature_list[AWARD_INDEX]
        feature = tmp_feature_list[len(tmp_feature_list)-1-i]
        data_award = KeywordSearch(feature,data_award)
# clean data
    data_award_c = data_award
    for i in range(0):
        counts_phrase = CountsPhrase(data_award_c,2,0,'')
        sorted_counts_phrase = sorted(counts_phrase.items(),key=itemgetter(1),reverse=True)
        counts_len = len(sorted_counts_phrase)
        counts_threshold = sorted_counts_phrase[np.int32(counts_len*0.5)][1]
        word_dict = CreateDict(counts_phrase,counts_threshold)
        data_award_c = CleanData(data_award_c,2,1,word_dict)

    pl_value = 0
    winner_name = ''
    for pl in range(2,6):
        counts_phrase = CountsPhrase(data_award_c,pl,1,word_dict_delete)
        sorted_counts_phrase = sorted(counts_phrase.items(),key=itemgetter(1),reverse=True)
        if sorted_counts_phrase:
            tmp = sorted_counts_phrase[0][1]/sum(counts_phrase.values())
            pl_ratio.append(tmp)
            if pl_value < tmp:
                winner_name = sorted_counts_phrase[0][0]
                pl_value = tmp
    if winner_name:
        print('****************************************************************',
              '\n AWARD NAME:',award_name_v[AWARD_INDEX],
              '\n WINNER:',winner_name,'\n')
    else:
        print('****************************************************************',
              '\n AWARD NAME:',award_name_v[AWARD_INDEX],
              '\n WINNER: MISSING!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!','\n')


# =============================================================================
# get nominees
# =============================================================================
#data_original_c = CleanData(data_original,1,3,[])
#keyword = 'nomin'
#data_nominee = KeywordSearch(keyword,data_original_c)
#data_nominee_c = data_nominee
#phrase_length = 2
#for i in range(20):
#    if (i+1)%8 == 0:
#        phrase_length += 1
#    counts_phrase = CountsPhrase(data_nominee_c,phrase_length)
##    sorted_counts_phrase = sorted(counts_phrase.items(),key=itemgetter(1),reverse=True)
#    word_dict = CreateDict(counts_phrase,100)
#    data_nominee_c = CleanData(data_nominee_c,2,1,word_dict)
    
# =============================================================================
# instance
# =============================================================================

#key_word = '(globe)|(gold)'
#data_goldenglobes = KeywordSearch(key_word,data_original)
#counts_award_word = CountsPhrase(award_name_v,1)
#data_goldenglobes_c = CleanData(data_goldenglobes,1,1,[])
    
    
#counts_phrase = CountsPhrase(data_goldenglobes,2)
#sorted_counts_phrase = sorted(counts_phrase.items(),key=itemgetter(1),reverse=False)
#word_dict = CreateDict(counts_phrase,counts_threshold=10)
#data_cleaned = CleanData(data_original,2,3,word_dict)




    

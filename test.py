#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 29 17:19:41 2018

@author: weixinjiang
"""
import os
os.system('cls')

import json
import re
from operator import itemgetter
import test_scaper
import numpy as np

# =============================================================================
# loading data and get award name
# =============================================================================
data = json.load(open('gg2018.json'))
award_name = test_scaper.get_award_name()

# =============================================================================
# count words frequency, dimention reduction
# =============================================================================
counts_award_word = dict()
for i in range(len(award_name)):
    tmp = award_name[i]
    for words in tmp:
        if words in counts_award_word:
            counts_award_word[words] += 1
        else:
            counts_award_word[words] = 1
sorted_counts_award_word = sorted(counts_award_word.items(), key=itemgetter(1), reverse = False)

# =============================================================================
# feature selection, automaticaly
# =============================================================================
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

# =============================================================================
# uniqueness
# =============================================================================
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
# plain transform the original tweets
# =============================================================================
data_original = []
for i in range(len(data)):
    a = data[i]
    data_original.append(a['text'])
    
# =============================================================================
# Selection, get tweets related to the topic of goldenglobes
# =============================================================================
key_word = re.compile('(golden)|(globe)',flags=re.I)
data_goldenglobes=[]
for i in range(len(data)):
    a = data[i]
    match_GoldenGlobes = key_word.search(a['text'])
    if match_GoldenGlobes:
        data_goldenglobes.append(a['text']) 
data_goldenglobes = list(set(data_goldenglobes))

      
# =============================================================================
# searching, for specific award
# =============================================================================
def Award_Search(award_feature,select_dataset):
    target_dataset = select_dataset
    for i in range(len(award_feature)):
        tmp = []
        for j in range(len(target_dataset)):
            if re.search(award_feature[len(award_feature)-1-i],target_dataset[j],flags=re.I):
                tmp.append(target_dataset[j])
        target_dataset = tmp
    return target_dataset


            
# =============================================================================
# calculating the frequency of all fix length phrase frequency
# =============================================================================
def DeleteAwardWord(word_list,counts_award_name):
    new_word_list=[]
    for word in word_list:
        if not word.lower().capitalize() in counts_award_name:
#            new_word_list.append(word)
            if not word.lower() in 'goldenglobes':
                new_word_list.append(word)
    return new_word_list

def CalPhraseCounts(data_award,phrase_length=1):
    counts_phrase = dict()
    for i in range(len(data_award)):
        tmp_word_list = re.findall('[a-zA-Z]{3,10}',data_award[i])
        tmp_word_list = DeleteAwardWord(tmp_word_list,counts_award_word)
        for j in range(len(tmp_word_list)-phrase_length+1):
            tmp_phrase=''
            for k in range(phrase_length):
                tmp_phrase += tmp_word_list[j+k].lower().capitalize()
            if tmp_phrase in counts_phrase:
                counts_phrase[tmp_phrase] += 1
            else:
                counts_phrase[tmp_phrase] = 1
    return counts_phrase

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
# output the winner for awards
# =============================================================================
for AWARD_INDEX in range(len(award_name)):
    data_award = Award_Search(award_feature_list[AWARD_INDEX],data_goldenglobes)
    counts_phrase = CalPhraseCounts(data_award,phrase_length=3)                
    sorted_counts_phrase = sorted(counts_phrase.items(), key=itemgetter(1), reverse = True)
    if sorted_counts_phrase:
        print('****************************************************************',
              '\n AWARD NAME:',award_name_v[AWARD_INDEX],
              '\n WINNER:',sorted_counts_phrase[0][0],'\n')
    else:
        print('****************************************************************',
              '\n AWARD NAME:',award_name_v[AWARD_INDEX],
              '\n WINNER: MISSING!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!','\n')

# =============================================================================
# Searching keyword
# =============================================================================
#def SearchKeyWord(key_word,dataset):
#    data_output = []
#    for tmp_tweets in dataset:
#        if re.search(key_word,tmp_tweets,flags=re.I):
#            data_output.append(tmp_tweets)
#    return data_output
            
# =============================================================================
# instance, for nomination
# =============================================================================
#select_feature = ['(nomin)+','(best)+']
#dataset_nominee = data_original
#for feature in select_feature:
#    dataset_nominee = SearchKeyWord(feature,dataset_nominee)
#counts_phrase = CalPhraseCounts(dataset_nominee,phrase_length=3)                
#sorted_counts_phrase = sorted(counts_phrase.items(), key=itemgetter(1), reverse = True)
        
# =============================================================================
# tweets cleaning
# =============================================================================
#def CleanSentence(dirty_data,reference_word):
    

# =============================================================================
# Selection, get tweets with the word best
# =============================================================================
#key_word = re.compile('[^\w]+best[^\w]+',flags=re.I)
#data_best=[]
#for i in range(len(data_goldenglobes)):
#    a = data_goldenglobes[i]
#    match_best = key_word.search(a)
#    if match_best:
#        data_best.append(a)
        
# =============================================================================
# Selection, get award 25
# =============================================================================
#key_words = re.compile('drama',flags = re.I)
#data_award_25 = []
#for i in range(len(data_best)):
#    tmp = data_best[i]
#    match_tmp = key_words.search(tmp)
#    if match_tmp:
#        data_award_25.append(tmp)

#key_word = re.compile('nominate',flags = re.I)
#data_award_25_nominate=[]
#for i in range(len(data_award_25)):
#    tmp = data_award_25[i]
#    match_tmp = key_word.search(tmp)
#    if match_tmp:
#        if not re.search('n.t[^\w]+',tmp,flags=re.I):
#            data_award_25_nominate.append(tmp)
#
#counts_award_25_nominate = dict()
#for i in range(len(data_award_25_nominate)):
#    tmp = re.findall('[\w]+',data_award_25_nominate[i])
#    for words in tmp:
#        if words.lower() in counts_award_25_nominate:
#            counts_award_25_nominate[words.lower()] += 1
#        else:
#            counts_award_25_nominate[words.lower()] = 1
#sorted_counts_award_25_nominate = sorted(counts_award_25_nominate.items(), key=itemgetter(1), reverse = True)
#        
#key_word = re.compile('(win[s]?)|(won)',flags = re.I)
#data_award_25_win=[]
#for i in range(len(data_award_25)):
#    tmp = data_award_25[i]
#    match_tmp = key_word.search(tmp)
#    if match_tmp:
#        data_award_25_win.append(tmp)







##counts = dict()
##for i in range(len(data_goldenglobes)):
###    m = re.split(' ', data_goldenglobes[i])
##    m = re.findall('[\w]+',data_goldenglobes[i])
##    for word in m:
##        if word.lower() in counts:
##            counts[word.lower()] += 1
##        else:
##            counts[word.lower()] = 1
##            
##sortedWords = sorted(counts.items(), key=itemgetter(1), reverse = True)
#
#counts_award = dict()
#key_word = re.compile('[^\w]+best[^\w]+',flags=re.I)
#data_best=[]
#for i in range(len(data_goldenglobes)):
#    a = data_goldenglobes[i]
#    match_best = key_word.search(a)
#    if match_best:
#        data_best.append(a)
#        split_words = re.findall('[\w]+',a)
#        best_posi = 0
#        award_posi = 0
#        if re.search('award',a,flags = re.I):
#            for posi,value in enumerate(split_words,1):
#                if value.lower() == 'best':
#                    best_posi = posi-1
#                elif value.lower() == 'award':
#                    award_posi = posi
#                    break
#
#        if award_posi-1-best_posi>1 and best_posi and award_posi-1-best_posi<15:
#            award_name = ''
#            for i in range(best_posi,award_posi):
#                award_name += split_words[i].lower().capitalize()
#            if award_name in counts_nominate:
#                counts_award[award_name] += 1
#            else:
#                counts_award[award_name] = 1
#
#sorted_counts_award = sorted(counts_award.items(), key=itemgetter(1), reverse = True)
#
#
#
#
#key_word = re.compile('nominate[d]*',flags=re.I)
#data_nominate=[]
#for i in range(len(data_best)):
#    a = data_best[i]
#    match_nominate = key_word.search(a)
#    if match_nominate:
#        data_nominate.append(a)
##        split_words = re.findall('[\w]+',a)
##        best_posi = 0
##        award_posi = 0
##        if re.search('award',a,flags = re.I):
##            for posi,value in enumerate(split_words,1):
##                if value.lower() == 'best':
##                    best_posi = posi-1
##                elif value.lower() == 'award':
##                    award_posi = posi
##                    break
##        else:
##            for posi,value in enumerate(split_words,1):
##                if value.lower() == 'best':
##                    best_posi = posi-1
##                    break
#                
##        if award_posi>best_posi and best_posi:
##            award_name = ''
##            for i in range(best_posi,award_posi):
##                award_name += split_words[i].lower()
##            if award_name in counts_nominate:
##                counts_nominate[award_name] += 1
##            else:
##                counts_nominate[award_name] = 1
##        else:
##            for i in range(best_posi,min(best_posi+3,len(split_words)-1)):
##                if split_words[i].lower() in counts_nominate:
##                    counts_nominate[split_words[i].lower()] += 1
##                else:
##                    counts_nominate[split_words[i].lower()] = 1
#                    
##sorted_counts_nominate = sorted(counts_nominate.items(), key=itemgetter(1), reverse = True)
#
#
#        
#key_word = re.compile('(win[s]?)|(won)',flags=re.I)
#counts_win_award = dict()
#data_win =[]
#for i in range(len(data_best)):
#    a = data_best[i]
#    match_win = key_word.search(a)
#    if match_win:
#        data_win.append(a)
#        split_words = re.findall('[\w]+',a)
#        best_posi = 0
#        award_posi = 0
#        if re.search('award',a,flags = re.I):
#            for posi,value in enumerate(split_words,1):
#                if value.lower() == 'best':
#                    best_posi = posi-1
#                elif value.lower() == 'award':
#                    award_posi = posi
#                    break
#
#        if award_posi-1-best_posi>1 and best_posi and award_posi-1-best_posi<15:
#            award_name = ''
#            for i in range(best_posi,award_posi):
#                award_name += split_words[i].lower().capitalize()
#            if award_name in counts_nominate:
#                counts_win_award[award_name] += 1
#            else:
#                counts_win_award[award_name] = 1
#
#sorted_counts_win_award = sorted(counts_win_award.items(), key=itemgetter(1), reverse = True)
#        
#
##counts = dict()
###key_word = re.compile('[A-Z][a-z]+')
##for i in range(len(data_best)):
##    m = re.findall('[A-Z][a-z]+',data_best[i])
##    for word in m:
##        if word in counts:
##            counts[word] += 1
##        else:
##            counts[word] = 1
##sortedWords = sorted(counts.items(), key=itemgetter(1), reverse = True)   
#   
#
##key_word = re.compile('award',flags=re.I)
##data_award=[]
##for i in range(len(data_goldenglobes)):
##    a = data_goldenglobes[i]
##    match_award = key_word.search(a)
##    if match_award:
##        data_award.append(a)
##        
##key_word = re.compile('w[io]+n[s]*',flags=re.I)
##data_award_win =[]
##for i in range(len(data_award)):
##    a = data_award[i]
##    match_award_win = key_word.search(a)
##    if match_award_win:
##        data_award_win.append(a)
##
##key_word = re.compile('best',flags=re.I)
##data_award_best =[]
##for i in range(len(data_award)):
##    a = data_award[i]
##    match_award_best = key_word.search(a)
##    if match_award_best:
##        data_award_best.append(a)
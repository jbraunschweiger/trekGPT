# -*- coding: utf-8 -*-
"""
Created on Thu May  6 11:01:01 2021

@author: Dr. Birko-Katarina Ruzicka
"""

#%% run program and save results


from bs4 import BeautifulSoup
import requests
import re
from collections import defaultdict
from time import sleep

def get_dialogue(series):
    
    if series not in ['StarTrek', 'Animated', 'NextGen', 'DS9', 'Voyager',
                      'Enterprise', 'Discovery', 'Picard']:
        print('Series name must be one of the following:')
        print("'StarTrek', 'Animated', 'NextGen', 'DS9' 'Voyager', \
              'Enterprise', 'Discovery', 'Picard'")
    else:
        print('Loading data for ' + series + '... ')
    
    # get the urls of all episodes in a series:
    if series == 'Voyager':
        series_url = 'http://chakoteya.net/Voyager/episode_listing.htm'
    elif series == 'Animated':
        series_url = 'http://chakoteya.net/StarTrek/episodes.htm'
    elif series == 'Discovery':
        series_url = 'http://chakoteya.net/STDisco17/episodes.html'
    elif series == 'Picard':
        series_url = 'http://chakoteya.net/StarTrekPIC/episodes.html'
    else:
        series_url = f'http://chakoteya.net/{series}/episodes.htm'
    html = requests.get(series_url).text
    soup = BeautifulSoup(html, 'html.parser')
    
    if series == 'Animated':
        url_root = 'http://chakoteya.net/StarTrek/'
        links, url_ends = [], []
        episode_count = 0
        for link in soup.find_all('a'):
            links.append(link.get('href'))
        for link in links:
            if str(link)[:3] == 'TAS':
                url_ends.append(link)
                episode_count += 1
    elif series == 'Discovery':
        url_root = 'http://chakoteya.net/STDisco17/'
        links, url_ends, s2ep, s3ep = [], [], [], []
        episode_count = 0
        for link in soup.find_all('a'):
            links.append(link.get('href'))
        for i in range(201, 215):
            s2ep = str(i) + '.html'
            links.append(s2ep)
        for i in range(301, 314):
            s3ep = str(i) + '.html'
            links.append(s3ep)
        for link in links:
            if str(link)[0].isdigit() and len(str(link)) < 12:
                url_ends.append(link)
                episode_count += 1
    elif series == 'Picard':
        url_root = 'http://chakoteya.net/StarTrekPIC/'
        links, url_ends, s1ep = [], [], []
        episode_count = 0
        for link in soup.find_all('a'):
            links.append(link.get('href'))
        for i in range(101, 111):
            s1ep = str(i) + '.html'
            links.append(s1ep)
        for link in links:
            if str(link)[0].isdigit():
                url_ends.append(link)
                episode_count += 1
    else:
        url_root = f'http://chakoteya.net/{series}/'
        links, url_ends = [], []
        episode_count = 0
        for link in soup.find_all('a'):
            links.append(link.get('href'))
        for link in links:
            if str(link)[0].isdigit() and len(str(link)) < 12:
                url_ends.append(link)
                episode_count += 1
    url_full = []
    for p, _ in enumerate(url_ends):
        url_full.append(url_root + url_ends[p])

    # get the html soup for each episode in series:
    for i in range(0, episode_count):
        # create episode names:
        if series == 'StarTrek':
            episode = 'tos_' + str(i).zfill(3)
        elif series == 'Animated':
            episode = 'tas_' + str(i).zfill(3)
        elif series == 'NextGen':
            episode = 'tng_' + str(i).zfill(3)
        elif series == 'DS9':
            episode = 'ds9_' + str(i).zfill(3)
        elif series == 'Voyager':
            episode = 'voy_' + str(i).zfill(3)
        elif series == 'Enterprise':
            episode = 'ent_' + str(i).zfill(3)
        elif series == 'Discovery':
            episode = 'dis_' + str(i).zfill(3)
        elif series == 'Picard':
            episode = 'pic_' + str(i).zfill(3)
        
        ep_html = requests.get(url_full[i]).text
        sleep(1)  # prevent server refusal
        soup_ep = BeautifulSoup(ep_html, 'html.parser')
        
        # clean up the html soup for each episode:
        
        # convert soup to text:
        ep_text = [text for text in soup_ep.stripped_strings]
        ep_title_sections = ep_text[0].split(' - ', 1)
        ep_title = ep_title_sections[len(ep_title_sections)-1]
        ep_text = ep_text[4:]  # skip header
            
        # remove entries that begin with forbidden string:
        for forbidden in ['(', '[', '<', 'CBS', '.', '\r']:
            ep_text = [i for i in ep_text if not i.startswith(forbidden)]
        
        # remove superfluous linebreaks:
        ep_text2 = []
        for j, _ in enumerate(ep_text):
            ep_text2.append(ep_text[j].replace('\n', ' '))
        
        # remove lines that do not begin with 3 consecutive capitals,
        # or begin with a ':', or only contain capitals
        ep_text3 = []
        for j, _ in enumerate(ep_text2):
            if len(ep_text2[j]) > 3 and ep_text2[j][1:3].isupper() \
               and ep_text2[j][0] != ':' and not ep_text2[j].isupper():
                ep_text3.append(ep_text2[j])

        # fix instances where char and line are not divided by colon:
        ep_text4 = ep_text3.copy()
        # replace every instance of 'char [OC] line' with 'char: line'
        for j, entry in enumerate(ep_text4):
            ep_text4[j] = re.sub(' \[OC] ', ': ', entry)
        # replace every instance of 'char line' with 'char: line'
        for j, entry in enumerate(ep_text4):
            if ':' not in entry:
                # replace first empty space with ': '
                ep_text4[j] = re.sub(' ', ': ', entry, 1)
        for j, entry in enumerate(ep_text4):
            ep_text4[j] = re.sub('::', ':', entry)

        # restructure context comments:
        ep_text5 = ep_text4.copy()
        comment_pattern = ' [\(\[].*?[\)\]]'  # catches everything between () or []
        for j, entry in enumerate(ep_text5):
            # replace [comment text... ] and (comment text...) with COMMENT: comment text
            if entry.startswith('[') or entry.startswith('('):
                ep_text5[j] = 'COMMENT: ' + entry
        
        ep_text = ep_text5.copy()

        # transform text into dictionary of form (char: line):
        ep_dialogue = defaultdict(list)
        
        
        with open('input.txt', 'a') as file:
            file.write('# ' + ep_title + '\n\n')
            for j, entry in enumerate(ep_text):
                match1 = re.search('.*:', entry)
                cast_member = match1.group()[:-1]
                while cast_member[-1] == ' ' or cast_member[-1] == '\r':
                    cast_member = cast_member[:-1]
                
                match2 = re.search(':.*', entry)
                text_line = match2.group()[2:].strip()

                if cast_member == 'COMMENT':
                    file.write('[' + text_line + ']\n\n')
                else:
                    file.write('@' + cast_member + '\n' + text_line + '\n\n')
        
    print(f'{series} complete.')
#clear file 
with open('input.txt', 'w') as file:
    file.write('')

get_dialogue('StarTrek')
# TAS = get_dialogue('Animated')
get_dialogue('NextGen')
get_dialogue('DS9')
get_dialogue('Voyager')
get_dialogue('Enterprise')
# DIS = get_dialogue('Discovery')
# PIC = get_dialogue('Picard')
    
pass
# %%

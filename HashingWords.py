#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun  4 20:09:33 2020

@author: rohith
"""

import sqlite3
from bs4 import BeautifulSoup
import enchant
from bs4.element import Comment

def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True

def text_from_html(body):
    soup = BeautifulSoup(body, 'html.parser')
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)  
    return u" ".join(t.strip() for t in visible_texts)

d = enchant.Dict("en_US")

conn = sqlite3.connect("SearchEngineDB.sqlite")
cur = conn.cursor()

cur.execute(''' CREATE TABLE IF NOT EXISTS Keywords(
keyword TEXT,
pid INTEGER,
count INTEGER,
CONSTRAINT pk1 PRIMARY KEY(keyword,pid),
CONSTRAINT fk1 FOREIGN KEY(pid) REFERENCES Pages(pid)
);
            ''')

cur.execute("SELECT * FROM Stopwords")
rows = cur.fetchall()
stopWords  = []
for row in rows:
    stopWords.append(row[0])

cur.execute("SELECT pid,html FROM Pages WHERE html is NOT NULL AND error is NULL AND pid NOT in(SELECT DISTINCT(pid) FROM Keywords) ORDER BY pid")
rows = cur.fetchall()

for row in rows:
    pid = row[0]
    cur.execute("DELETE FROM Keywords WHERE pid=?",(pid,))
    conn.commit()
    html = row[1]
    soup = BeautifulSoup(html,'html.parser')
    #text = soup.get_text()
    text = text_from_html(html)
    lines = text.split("\n")
    
    keyWords = dict()
    
    count=0
    #handle = open("fun.txt","a")
    for line in lines:
        if line.strip()!="":
            lst = line.split()
            for w in lst:
                if w.isalpha():
                    word = w.strip().lower()
                    if word not in stopWords:
                        if d.check(word):#check whether it is an english word or not
                            print(word)
                            cur.execute("INSERT OR IGNORE INTO Keywords(keyword,pid) VALUES(?,?)",(word,pid))
                            keyWords[word] = keyWords.get(word,0) + 1
                            #handle.write(word)
                            #handle.write("\n")
                            count = count+1
            for key,value in keyWords.items():
                cur.execute("UPDATE Keywords SET count=? WHERE keyword=? AND pid=?",(value,key,pid))
    #handle.close()
    conn.commit()
    print("Total words in page:",pid,"=",count)
#cur.execute("ALTER TABLE Pages SET html=NULL")
#conn.commit()
conn.close()
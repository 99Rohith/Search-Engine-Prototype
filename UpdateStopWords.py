#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun  4 22:40:08 2020

@author: rohith
"""

import sqlite3

conn = sqlite3.connect("SearchEngineDB.sqlite")
cur = conn.cursor()

cur.execute(''' CREATE TABLE IF NOT EXISTS Stopwords(
        uselessword TEXT UNIQUE
        );
''')

handle = open("StopWordsList.txt")

count = 0

for line in handle:
    print(count,sep = " ")
    spl = line.split()
    for word in spl:
        if word is not None:
            print(word)
            cur.execute(''' INSERT OR IGNORE INTO Stopwords(uselessword) VALUES(?)''',(word,))
            count = count+1
            
conn.commit()
handle.close()
conn.close()
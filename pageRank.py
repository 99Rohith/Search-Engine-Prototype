#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  2 18:47:09 2020

@author: rohith
"""

import sqlite3

alpha = 0.85 #dampning factor

conn = sqlite3.connect("SearchEngineDB.sqlite")
cur = conn.cursor()


cur.execute("SELECT * FROM Links")
rows = cur.fetchall()
links_from = []
links_to = []
for row in rows:
    #links_from[i]->links2[i]
    links_from.append(row[0])
    links_to.append(row[1])

cur.execute("SELECT pid FROM Pages")
rows = cur.fetchall()
pids = []
for row in rows:
    pids.append(row[0])

N = len(pids)

cur.execute("SELECT DISTINCT(from_id) FROM Links")
rows = cur.fetchall()
from_ids = []
for row in rows:
    from_ids.append(row[0])

cur.execute("SELECT DISTINCT(to_id) FROM Links")
rows = cur.fetchall()
to_ids = []
for row in rows:
    to_ids.append(row[0])        

old_ranks = dict()
new_ranks = dict()

for pid in pids:
    old_ranks[pid] = 0
    if pid in from_ids:
        new_ranks[pid] = 1/(links_from.count(pid))
    else:
        new_ranks[pid] = 1/N

Iter = int(input("Enter Number of Iterations"))

while Iter>0:
    old_pg_sum = 0
    for pid in pids:
        old_ranks[pid]=new_ranks[pid]
        old_pg_sum += old_ranks[pid]
        new_ranks[pid] = 0
    
    for i in range(len(links_from)):
        new_ranks[links_to[i]] += old_ranks[links_from[i]]/links_from.count(links_from[i])
    
    # There is a 85% chance that the user will land on a page by clicking a link from another page
	# There is a 15% chance that the user knows about the page already(from bookmarks etc)ie.,
	# The user doen't come from any other page
    new_pg_sum = 0
    for pid in pids:
        new_ranks[pid] = (alpha*(new_ranks[pid])) + ((1-alpha)/N)
        new_pg_sum += new_ranks[pid]
    
    evap = (old_pg_sum - new_pg_sum)/N
    
    avgSqDiff = 0
    new_pg_sum = 0
    for pid in pids:
        new_ranks[pid] += evap
        new_pg_sum += new_ranks[pid]
        diff = old_ranks[pid] - new_ranks[pid]
        avgSqDiff += (diff*diff)
    
    avgSqDiff = avgSqDiff/N
    print(avgSqDiff)
    
    Iter = Iter-1

cur.execute("UPDATE Pages SET curRank = newRank")
conn.commit()

for pid in pids:
    cur.execute("UPDATE Pages SET newRank=? WHERE pid=?",(new_ranks[pid],pid))

conn.commit()
conn.close()
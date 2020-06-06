#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  1 18:17:18 2020

@author: rohith
"""

import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup
import ssl
import sqlite3

#Below 3 lines are required to open https sites
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

conn = sqlite3.connect("SearchEngineDB.sqlite")
cur = conn.cursor()

cur.executescript('''
CREATE TABLE IF NOT EXISTS Pages(
pid INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
url TEXT UNIQUE,
html TEXT UNIQUE,
error INTEGER,
curRank REAL,
newRank REAL);

CREATE TABLE IF NOT EXISTS Links(
from_id INTEGER,
to_id INTEGER,
CONSTRAINT pk PRIMARY KEY(from_id,to_id)
);

CREATE TABLE IF NOT EXISTS websites(
url TEXT UNIQUE
);
''')
conn.commit()

def fetchIDandURL(cur):
    cur.execute(''' SELECT pid,url FROM Pages WHERE html is NULL AND error is NULL ORDER BY RANDOM() LIMIT 1 ;''')
    row = cur.fetchone()
    if row is None:
        print("No pages to crawl..Terminating program")
        return None
    else:
        return row

def InsertIntoWebsites(url):
    ipos = url.find('/')#Process the url and take only upto /
    url = url[:ipos]
    cur.execute(''' INSERT OR IGNORE INTO  websites VALUES(?)''',(url,))
    conn.commit()

row = ()
url = None
userurl = False

opt = input("Do you want to enter a new url?(Y/y) for yes:")
if opt=='y' or opt =='Y':
    url = input("Enter url:")
    #check for constraints
    if len(url)<1:
        print("No url entrered....")
        opt = 'n'
    #Trim the url
    else:
        if url.endswith('/'):
            url = url[:-1]
        cur.execute(''' INSERT OR IGNORE INTO Pages(url,html,error,curRank) VALUES
                        (?,NULL,NULL,?) ''',(url,1.0))
        conn.commit()
        cur.execute(''' SELECT pid,url FROM Pages WHERE url=?; ''',(url,))
        row = cur.fetchone()
        userurl = True
        
if opt!='y' and opt!='Y':
    #check whether Pages table have any urls to Crawl
    row = fetchIDandURL(cur)#defined above
        
if row is not None:
    print("Selected url:",row[1])
    inp = input("How many webpages do u want to crawl:")
    if len(inp)==0: many=0
    else: many = int(inp)
    while many>0:
        if userurl == False:
            row = fetchIDandURL(cur)
        if row is not None:
            userurl = False
            pid = int(row[0])
            url = str(row[1])
            OpenFlag = False
            try:
                handle = urllib.request.urlopen(url, context = ctx)
                OpenFlag = True
            except:
                print("Couldn't open connection to:",url)
                cur.execute('DELETE FROM Pages WHERE url=?', ( url, ) )
                conn.commit()
            if OpenFlag:
                InsertIntoWebsites(url)
                page_type = handle.info().get_content_type()
                error_code = handle.getcode()
                print("url=",url, " content_type=", page_type," Error_code=",error_code)
                if page_type == "text/html" and error_code==200:
                    html = handle.read()
                    cur.execute('UPDATE OR IGNORE Pages SET html=? WHERE url=?', (memoryview(html), url ) )
                    cur.execute('DELETE FROM LINKS WHERE from_id=?', (pid,) )
                    conn.commit()
                    soup = BeautifulSoup(html, 'html.parser')
                    tags = soup('a')
                    countPerPage=51
                    for tag in tags:
                        countPerPage = countPerPage-1;
                        href = tag.get('href',None)
                        up = urllib.parse.urlparse(href)
                        #Now we check whether it is a complete url or whether it depends on parent page
                        if len(up.scheme)==0:#scheme is nothing but 'http or https'
                            href = urllib.parse.urljoin(url,href)#It is not a complete url so join the parent url to it
                        ipos = href.find('#')#Now check whether it is a link to top of the page
                        if ( ipos > 1 ) : href = href[:ipos]
                        if ( href.endswith('.png') or href.endswith('.jpg') or href.endswith('.gif') ) : continue
                        if ( href.endswith('/') ) : href = href[:-1]
                        print(href)
                        cur.execute(''' INSERT OR IGNORE INTO Pages(url,html,error,curRank) VALUES(?,NULL,NULL,1.0)''',(href,))
                        conn.commit()
                        cur.execute(''' SELECT pid FROM Pages WHERE url=? ''',(href,))
                        row = cur.fetchone()
                        from_id = pid
                        to_id = int(row[0])
                        if from_id !=to_id:
                            cur.execute(''' INSERT OR IGNORE INTO Links(from_id,to_id) VALUES(?,?) ''',(from_id,to_id))
                            conn.commit()
                        if countPerPage==0:
                            break
                elif page_type!="text/html" and error_code==200:
                    cur.execute('DELETE FROM Pages WHERE url=?', ( url, ) )
                    conn.commit()
                elif error_code!=200:
                    cur.execute("UPDATE Pages SET error=? WHERE url=?",(error_code,url))
                    conn.commit()
        many = many-1
conn.close()
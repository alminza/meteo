# -*- coding: utf-8 -*-
"""
Created on Tue Oct 27 12:47:57 2020

@author: Malcor
"""



import sqlite3

def temperature (file):
    reading = open(file,'r')
    final = []
    for line in reading:
        L = line.split()
        final.append(L)
    return final
    

final=temperature("/Users/Malcor/Documents/meteo stat.txt")
      
    
conn = sqlite3.connect('BDDlite.db')
c = conn.cursor()
"""""c.execute('''CREATE TABLE info_meteolite
             (Date text, Time text)''')"""
  
tab = []
for i, item in enumerate(final):
    if i > 2:
        tab.append((item[0],item[1]))

"""for i in tab:
    print (tab)"""
    
for row in tab:
    c.execute('INSERT INTO info_meteolite VALUES (?,?)', row)
    conn.commit()

c.execute("SELECT * FROM info_meteolite")

print(c.fetchall())
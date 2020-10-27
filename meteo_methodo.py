# -*- coding: utf-8 -*-
"""
Created on Mon Oct 26 09:17:47 2020

@author: Malcor
"""

import sqlite3
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


engine = create_engine('sqlite:///BDDlite.db', echo=True)


    
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()
class User(Base):
    __tablename__ = 'info_meteolite'
    Date = Column(Integer, primary_key=True)
    Time = Column(String)


# Querying
k= []
for instance in session.query(User).order_by('Date'):
   k.append(instance)

  
print(k)



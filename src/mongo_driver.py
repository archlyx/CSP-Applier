#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
MongoDriver - The Class handle MongoDB operations:
1) insert: directly insert dictionary to collection

2) update: given the assumption that record with the hashURL already in, the function take a new record with same
hashURL and replace the old one

3) query: return the record (dictionary) with specific urlHash

4) hasURL: See if record with specific urlHash is in the database
"""

from pymongo import MongoClient

class MongoDriver:

    def __init__(self):

        # connect to local host
        client = MongoClient('localhost', 27017)

        # data base name CSP
        self.db = client.CSP

        # collection name template.py
        self.collection = self.db.template

    def insert(self, doc):
        if not self.has_url(doc["URLHash"]):
            self.collection.insert(doc)

    def update(self, doc):
        url_hash = doc["URLHash"]
        if not self.has_url(url_hash):
            return

        self.collection.remove({"URLHash": url_hash})
        self.insert(doc)

    def query(self, url_hash):
        return self.collection.find_one({"URLHash": url_hash})

    def has_url(self, url_hash):
        return self.collection.find_one({"URLHash": url_hash}) is None

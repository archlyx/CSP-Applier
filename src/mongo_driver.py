#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from pymongo import MongoClient

class MongoDriver:
    """
    The wrapper for handling the operations of the database. The name of the database
    is 'CSP', and the collection name is 'template'.
    """

    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.db = client.CSP
        self.collection = self.db.template

    def insert(self, doc):
        """
        Directly insert dictionary to the collection

        :param doc: a dictionary to insert
        :return: None
        """
        if not self.has_key(doc["key"]):
            self.collection.insert(doc)

    def update(self, doc):
        """
        Given the assumption that record with the key already in,
        the function take a new record with same key and replace the old one

        :param doc: The new dictionary to replace the old one
        :return: None
        """
        key = doc["key"]
        if not self.has_key(key):
            return

        self.collection.remove({"key": key})
        self.insert(doc)

    def query(self, key):
        """
        Return the record (dictionary) with specific urlHash

        :param key: The key string
        :return: A dictionary
        """
        return self.collection.find_one({"key": key})

    def has_key(self, key):
        """
        See if record with specific key is in the database

        :param key: The key string
        :return: Boolean
        """
        return self.collection.find_one({"key": key}) is None

from pymongo import MongoClient

'''
## The Class handle MongodDB operations:
1) insert: directly insert dictionary to collection

2) update: given the assumption that record with the hashURL already in, the function take a new record with same
hashURL and replace the old one

3) query: return the record (dictonary) with specific urlHash

4) hasURL: See if record with specific urlHash is in the database
'''

class MongoDriver:
  def __init__(self):
    
    ##connect to local host
    client = MongoClient('localhost', 27017)

    ##data base name CSP
    self.db = client.CSP
    
    ##collection name template
    self.collection = self.db.template

  def insert(self, doc):
    if not self.hasURL(doc["URLHash"]):
      self.collection.insert(doc)

  def update(self, doc):
    urlHash = doc["URLHash"]
    if not self.hasURL(urlHash):
      return

    self.collection.remove({"URLHash":urlHash})
    self.insert(doc)
    
  def query(self, urlHash):
    return self.collection.find_one({"URLHash":urlHash})

  def hasURL(self, urlHash):
    return self.collection.find_one({"URLHash":urlHash}) != None

def main():
  driver = MongoDriver()

if __name__ == '__main__':
    main()

    

from pymongo import MongoClient

def mongoConnection():
    client = MongoClient("mongodb://127.0.0.1:27017")
    return client.nlp_research;

def getTrainedDataSet():
    db = mongoConnection()
    return db.trained_data_sets.find()

def getCategories():
    db = mongoConnection()
    return db.categories.find()
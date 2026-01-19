import random
from pymongo import MongoClient
from faker import Faker

#CONFIG 
fake = Faker(['pl_PL']) 
client = MongoClient("MongoDBurl")
db = client["databaseName"]



def seed_smth(arg="piszemy sparametryzowane"): 
    pass 



if __name__=="__main__": 
    seed_smth()
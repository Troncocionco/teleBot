from bs4 import BeautifulSoup
import requests
from pprint import pprint
from pymongo import MongoClient, ASCENDING
from datetime import date
import json
import os

with open(os.getenv('BOT_CONF_FILE')) as f:
  conf_File = json.load(f)

mongo_user = conf_File['Users']['Giacomo']['Mongo']['user']
mongo_password = conf_File['Users']['Giacomo']['Mongo']['password']

client = MongoClient(f"mongodb+srv://{mongo_user}:{mongo_password}@sandbox.zkkx5fv.mongodb.net")
db = client["comicsReleases"]
collection = db["ita_releases"]

#collection.update_many({}, {"$set": {"week": "5"}})

#collection.delete_many({})

today = str(date.today())
week = str(int(date.today().strftime("%U")))

url='https://www.comicsbox.it'

response = requests.get(url)
soup = BeautifulSoup(response.text, 'html5lib')

table = soup.find("div", {'id': 'carousel-ITA'})
childrens = table.findChildren("a", recursive=False)

results = []

for i in childrens:
    href = 'https://www.comicsbox.it/' + i.attrs.get("href")
    data_src ='https://www.comicsbox.it/cover' + str(i.attrs.get("href")).replace("albo", "") + ".jpg"
    
    title = i.findChildren("img")[0].attrs.get("title")
    
    results.append({"href": href, "data_src": data_src, "title": title , "date": today, "week": week})


collection.insert_many(results)
collection.create_index([("title", ASCENDING)], unique=True)


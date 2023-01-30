from bs4 import BeautifulSoup
import requests
from pprint import pprint
from pymongo import MongoClient, ASCENDING
from datetime import date
import json

with open(os.getenv('BOT_CONF_FILE')) as f:
  conf_File = json.load(f)

mongo_user = conf_File['Users']['Giacomo']['Mongo']['user']
mongo_password = conf_File['Users']['Giacomo']['Mongo']['password']

#client = MongoClient("mongodb://localhost:27017/")
client = MongoClient(f"mongodb+srv://{mongo.user}:{mongo.password}@sandbox.zkkx5fv.mongodb.net")
db = client["comicsReleases"]
collection = db["ita_releases"]

#collection.delete_many({})

today = str(date.today())

url='https://www.comicsbox.it'

response = requests.get(url)
soup = BeautifulSoup(response.text, 'html5lib')

table = soup.find("div", {'id': 'carousel-ITA'})
childrens = table.findChildren("a", recursive=False)

results = []

for i in childrens:
    href = 'https://www.comicsbox.it' + i.attrs.get("href")

    img = i.findChildren("img")
    title = img[0].attrs.get("title")
    data_src ='https://www.comicsbox.it' + img[0].attrs.get("data-src")
    
    results.append({"href": href, "data_src": data_src, "title": title , "date": today})


collection.insert_many(results)
collection.create_index([("title", ASCENDING)], unique=True)


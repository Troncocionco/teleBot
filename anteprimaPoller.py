from bs4 import BeautifulSoup
import requests
from pprint import pprint
from pymongo import MongoClient, ASCENDING, DESCENDING
from datetime import date
import json
import os
import logging

# Logic (daily)
# 1. Import file per configurazione
# 2. Connessione al db
# 3. Fetch last docs available on db
# 4. If date on document match current month --> Stop
# 5. If date on document dont match current month --> attempt fetching new one from panini.it
# 6. Stop


#Import configuration file
with open(os.getenv('BOT_CONF_FILE')) as f:
  conf_File = json.load(f)

#Connect to MongoDB Collection
mongo_user = conf_File['Users']['Giacomo']['Mongo']['user']
mongo_password = conf_File['Users']['Giacomo']['Mongo']['password']

client = MongoClient(f"mongodb+srv://{mongo_user}:{mongo_password}@sandbox.zkkx5fv.mongodb.net")
db = client["anteprimePanini"]
collection = db["archivio"]

#Define local path for storage resources
res_path = conf_File['HOME']+"res/"
print(f"Res path is : {res_path}")

#Instanciate logger
log_file = conf_File['preview_log'] 

# Configure the logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create a file handler
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.DEBUG)

# Create a formatter and add it to the file handler
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
file_handler.setFormatter(formatter)

# Add the file handler to the logger
logger.addHandler(file_handler)


def previewPolling():

    current_year = str(date.today().year)
    current_month = str(date.today().year)

    query = {"year": current_year}

    #Pick-up lastet, current year from db
    try:
        #Fetch all documents from current year
        logger.info(f"Attempting to fetch Anteprima year: {current_year}...")
        document = list(collection.find(query).sort("number", DESCENDING))[0]
    except:
        #On first month of the year, fetch latest from year before
        logger.warning("Year requested({current_year}) still not available! Fallback to previous year releases.")
        query = {"year": str(int(current_year) - 1), "month": "12"}
        document = list(collection.find(query).sort("number", DESCENDING))[0]

    numbAnteprima = document['number']
    #print(f"Number fetched from Mongo returns type {numbAnteprima}")

    if document['month'] == "1":
    #if document['month'] == str(date.today().month):
        #Stop. You have the latest Anteprima
        logger.info("Latest Anteprima already within the collection! Stop.")
    else:
        numbAnteprima = numbAnteprima + 1
        #Attempt fetching new Anteprima
        logger.info(f"Attempt fetching new Anteprima #{numbAnteprima}...")
        try:
            url = f"https://www.panini.it/media/flowpaper/A{numbAnteprima}/docs/A{numbAnteprima}.pdf"
            r = requests.get(url)
            pprint(r.headers)
            if(r.headers["Content-Type"] == "application/pdf"):
                logger.info("Success! Attempting insertion of a new record in Mongo...")
                collection.insert_one({"url": url, "year": current_year, "month": current_month, "number": numbAnteprima})
                logger.info("Insertion completed successfully! Stop.")
                with open(f"{res_path}A{numbAnteprima}.pdf", "wb") as file:
                    file.write(r.content)
                logger.info("Persisted file locally!")
            else:
                raise ContentDecodingError
        except:
            logger.warning("New Anteprima still not available! Stop.")

previewPolling()

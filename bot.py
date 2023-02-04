#!/usr/bin/python3
import os
import json
import schedule
from pprint import pprint
from bs4 import BeautifulSoup
import re
import time
import telegram
import datetime
import requests
from telegram.ext import Updater, CommandHandler, InlineQueryHandler, MessageHandler, Filters
from pymongo import MongoClient, DESCENDING
import logging



#Need an environment variable
with open(os.getenv('BOT_CONF_FILE')) as f:
  conf_File = json.load(f)

path = conf_File['HOME']

updater = Updater(token=conf_File['TOKEN'], use_context=True)
dispatcher = updater.dispatcher

mongo_user = conf_File['Users']['Giacomo']['Mongo']['user']
mongo_password = conf_File['Users']['Giacomo']['Mongo']['password']

client = MongoClient(f"mongodb+srv://{mongo_user}:{mongo_password}@sandbox.zkkx5fv.mongodb.net")

log_file = conf_File['bot_log'] 

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


############
# Handlers #
############

def start(update, context):
    """Send a message when the command /start is issued."""
    logger.info(f"/start command issued: {update.message}" )

    name = update.message.from_user.first_name

    context.bot.sendMessage(chat_id, f"Ciao {name}!" )

def myip(update, context):
    """ Replace with addresses of few services when the command /ip is issued"""
    message = update.message
    chat_id = message.chat_id

    if str(chat_id) in conf_File['AllowedUser']:
        ip_request = requests.get("http://checkip.amazonaws.com")
        URL = ip_request.content.decode("UTF-8")[:-1]
        context.bot.sendMessage(chat_id, "IP_telebot: "+URL)
        context.bot.sendMessage(chat_id, "Server Fumetti: "+ conf_File['Domain']['domain1']['domain-1-name'] )
        context.bot.sendMessage(chat_id, "Server Backup Fumetti: "+ conf_File['Domain']['domain2']['domain-2-name'] + ":" + conf_File['Domain']['domain2']['domain-2-port'] )
    else:
        logger.warning(f"Unauthorized /ip command issued! {update.message.from_user.id} - {update.message.from_user.name}" )

# def inline_query(update, context):
#     """Handle the inline query."""
#     query = update.inline_query.query
#     # handle the inline query here
#     pass

def anteprima(update, context):

    logger.info(f"/anteprima command issued! Passed arguments {context.args} ")

    db = client["anteprimePanini"]
    collection = db["archivio"]  
    try:
        if context.args != []:
            query = {"number": int(context.args[0])}
            document = list(collection.find(query))[0]
            pprint(document)
        else:
            document = list(collection.find().sort("number", DESCENDING))[0]
            pprint(document)

        context.bot.send_document(
            chat_id=update.effective_chat.id, 
            document="https://www.panini.it/media/flowpaper/A373/docs/A373.pdf", 
            caption=f"Anteprima #{document['number']} "
        )

    except Exception as e:
        print(e.message)
        context.bot.send_message(chat_id=update.effective_chat.id, text="Release not available!")
    

def uscite(update, context, cursor_week=0, max_rec=10):
    """Send a message when the command /uscite is issued."""
    try:
        if (context.args[0]):
            cursor_week = context.args[0]
        if (context.args[1]):
            max_rec = int(context.args[1])
        logger.info(f"/uscite called with arguments: {update.message} - args_1:'{context.args[0]}' args_2:'{context.args[1]}'")
    except:
        logger.info(f"/uscite called without arguments: {update.message}")

    db = client["comicsReleases"]
    collection = db["ita_releases"]

    # Get today's date
    current_week = int(datetime.datetime.today().strftime("%U"))
    target_week = str(current_week - int(cursor_week))

    # Query for documents with a "date" field equal to today's date
    query = {"week": target_week}
    documents = list(collection.find(query).sort("_id", DESCENDING))
    print("Scaricato # " + str(len(documents)) + " documenti")

    if (len(documents) < max_rec):
        max_rec = len(documents)
    else:
        for i in range(max_rec):
            photo = documents[i]['data_src']
            caption = documents[i]['title'] + '\n' + documents[i]['href']
            print(photo, caption)
            context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo, caption=caption)
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"Hello {update.message.from_user.first_name}! Ecco le ultime {max_rec} uscite italiane aggiornate alla week #{target_week}")


def channel_message(update, context):
    """Handle messages from a channel."""
    pprint(update.channel_post.text)
    text_msg = update.channel_post.text
    
    #cid = "@rss_torrg" #Channel Torrent Galaxy RSS Feed
    cid = conf_File['Users']['Giacomo']['ChannelID'] #Channel Torrent Galaxy RSS Feed

    countFiltri = len(conf_File['Users']['Giacomo']['Filters'])

    for i in conf_File['Users']['Giacomo']['Filters']:

        pattern = str(conf_File['Users']['Giacomo']['Filters'][i]['pattern'])
        filterMsg = str(conf_File['Users']['Giacomo']['Filters'][i]['messaggio'])
        result = re.search(pattern, text_msg)

        if result:
            if (pattern == 'XXX -' or pattern == 'XXX-'):
                logger.info("Msg from channel matched del-regex! Deleting message... ")
                context.bot.delete_message(chat_id=update.channel_post.chat_id, message_id=update.channel_post.message_id)
            else:
                logger.info("Msg from channel matched regex! Forwarding message... ")
                context.bot.forward_message(chat_id=conf_File['Users']['Giacomo']['Pers_ChatID'], from_chat_id=update.channel_post.chat_id, message_id=update.channel_post.message_id)

##############################################################################            

# Error Handler         
def error_callback(bot, update, error):
    try:
        raise error
    except TelegramError as te:
        print(f'TelegramError: {te}')
    except Exception as e:
        print(f'Error: {e}')

############

# Remider Spotify
def reminderSpotify():
    pprint("Current jobs schedule ", schedule.get_jobs())
    chat_ref = conf_File['Users']['Giacomo']['ChannelID']

    people = ["Virgilio", "Tom", "Luca", "Valerio", "Gianluca", "Giacomo"]


    current_month = datetime.datetime.now().month
    if datetime.datetime.now().day == 15:

        person_to_pay = people[(current_month % len(people))-1 ]
        tag = conf_File['Users'][person_to_pay]["tag"]

        updater.bot.sendMessage(chat_ref, "📌Questo mese tocca pagare a @" + person_to_pay)


############

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

anteprima_handler = CommandHandler('anteprima', anteprima)
dispatcher.add_handler(anteprima_handler)

uscite_handler = CommandHandler('uscite', uscite)
dispatcher.add_handler(uscite_handler)

myip_handler = CommandHandler('ip', myip)
dispatcher.add_handler(myip_handler)

# inline_query_handler = InlineQueryHandler(inline_query)
# dispatcher.add_handler(inline_query_handler)

#cid = "@rss_torrg" #Channel Torrent Galaxy RSS Feed
cid = conf_File['Users']['Giacomo']['ChannelID'] #Channel Torrent Galaxy RSS Feed

channel_message_handler = MessageHandler(Filters.chat(int(cid)), channel_message)
dispatcher.add_handler(channel_message_handler)

updater.dispatcher.add_error_handler(error_callback)

updater.start_polling()

schedule.every(1).day.at("10:00").do(reminderSpotify)

while 1:
    schedule.run_pending()
    time.sleep(5)
    

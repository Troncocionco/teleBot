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
from pymongo import MongoClient



#Need an environment variable
with open(os.getenv('BOT_CONF_FILE')) as f:
  conf_File = json.load(f)

path = conf_File['HOME']

updater = Updater(token=conf_File['TOKEN'], use_context=True)
dispatcher = updater.dispatcher

mongo_user = conf_File['Users']['Giacomo']['Mongo']['user']
mongo_password = conf_File['Users']['Giacomo']['Mongo']['password']

############
# Handlers #
############

def start(update, context):
    """Send a message when the command /start is issued."""
    name = update.message.from_user.first_name
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"Hello {name}! How can I help you today?")


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

# def inline_query(update, context):
#     """Handle the inline query."""
#     query = update.inline_query.query
#     # handle the inline query here
#     pass

def uscite(update, context):
    """Send a message when the command /uscite is issued."""
    name = update.message.from_user.first_name
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"Hello {name}! Ecco le uscite italiane aggiornate ad oggi")
    # Add call to function to pull the latest release from db


    client = MongoClient(f"mongodb+srv://{mongo_user}:{mongo_password}@sandbox.zkkx5fv.mongodb.net")
    db = client["comicsReleases"]
    collection = db["ita_releases"]

    # Get today's date
    today = str(datetime.datetime.now().date())

    # Query for documents with a "date" field equal to today's date
    query = {"date": today}
    documents = list(collection.find(query))

    for i in range(10):
        photo = documents[i]['data_src']
        caption = documents[i]['title'] + '\n' + documents[i]['href']
        print(photo, caption)
        context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo, caption=caption)
    
    #pprint(documents) 


def channel_message(update, context):
    """Handle messages from a channel."""
    pprint(type(update.channel_post.text))
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
                print("Match del-regex! Deleting message... ")
                context.bot.delete_message(chat_id=update.channel_post.chat_id, message_id=update.channel_post.message_id)
            else:
                print("Match regex! Forwarding message... ")
                #bot.sendMessage(chat_ref, filterMsg)
                context.bot.forward_message(chat_id=conf_File['Users']['Giacomo']['Pers_ChatID'], from_chat_id=update.channel_post.chat_id, message_id=update.channel_post.message_id)

#########################################################
#                Features                               #
#########################################################
"""
def ubooquity(update, context):

    chat_id=update.effective_chat.id

    if str(chat_id) in conFile['AllowedUser']:
        if not context.args:
            output = subprocess.check_output(['bash','/home/pi/Ubooquity/run-ubooquity.sh', 'status'])
            context.bot.send_message(chat_id=update.effective_chat.id, text=output.decode('utf-8'))
        else:
            output = subprocess.check_output(['bash','/home/pi/Ubooquity/run-ubooquity.sh', context.args[0]])
            context.bot.send_message(chat_id=update.effective_chat.id, text=output.decode('utf-8'))

def download(update, context):
    pprint(type(context.args[0]))
    pprint(context.args[0])
    chat_id=update.effective_chat.id

    if str(chat_id) in conFile['AllowedUser']:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Attenzione non scaricare file superiore a 200Mb!")
        fileName = str(context.args[0]).split("/")[-1]
        fileName = "/data_500GB/Fumetti/USA/"+ fileName + ".cbr"
        r = requests.get(str(context.args[0]), allow_redirects=True)

        open(fileName, 'wb').write(r.content)



        subprocess.run(["bash", "download.sh", context.args[0]])
        output = subprocess.check_output(["ls","-t","/data_500GB/Fumetti/USA"])
        output = str(output).replace("\\n",' #')
        pprint(output)
        context.bot.send_message(chat_id=update.effective_chat.id, text=output) 
        
"""
##############################################################################    
                
                
def error_callback(bot, update, error):
    try:
        raise error
    except TelegramError as te:
        print(f'TelegramError: {te}')
    except Exception as e:
        print(f'Error: {e}')


############


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
    

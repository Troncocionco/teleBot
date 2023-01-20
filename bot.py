#!/usr/bin/python3

from cmath import log
import time
import schedule
import random
import datetime
import telepot
import requests
import os
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from pprint import pprint
import logging
import re
import json

"""
- `/ip` - 
- `/anteprima` - 
- `/testUp` - 
"""

#Need an environment variable
with open(os.getenv('BOT_CONF_FILE')) as f:
  conf_File = json.load(f)

path = conf_File['HOME']


#my_logger.debug('this is debug')
#my_logger.critical('this is critical')

def on_chat_message(msg):

    logging.basicConfig(filename=conf_File['Log_directory'], filemode='a',format='[%(asctime)s] - %(name)s - %(levelname)s - %(message)s')

    logging.info(msg)
    content_type, chat_type, chat_id = telepot.glance(msg)
    reg_Anteprima = "/anteprima\s([0-9]*)"
    command = msg['text']

    chat_ref = conf_File['Users']['Admin']['Chat_ID_Reference']
    
    try:
        user = msg['from']['username']
        bot.sendMessage(chat_id, 'Ciaone ' + str(user))
    except:
        logging.info("Non e' una chat privata!")
        #channelFiltering(msg, chat_ref)
        
    option = {
        "channel"
    }

    if chat_type == "channel":
        channelFiltering(msg, chat_ref)
    elif command == '/roll':
        bot.sendMessage(chat_id, random.randint(1,6))
    elif command == '/time':
        bot.sendMessage(chat_id, str(datetime.datetime.now()))
    elif command == '/ip':
        if str(chat_id) in conf_File['AllowedUser']:
            ip_request = requests.get("http://checkip.amazonaws.com")
            URL = ip_request.content.decode("UTF-8")[:-1]
            bot.sendMessage(chat_id, "IP_telebot: "+URL)
            bot.sendMessage(chat_id, "Server Fumetti: "+ conf_File['Domain']['domain1']['domain-1-name'] )
            bot.sendMessage(chat_id, "Server Backup Fumetti: "+ conf_File['Domain']['domain2']['domain-2-name'] + ":" + conf_File['Domain']['domain2']['domain-2-port'] )

    elif "/anteprima" in command:
        try:
            numbAnteprima = re.match(reg_Anteprima, command).group(1)
	    
            #Va cambiato sendDocument, non e' piu una risorsa locale
            url = "https://www.panini.it/media/flowpaper/A"+numbAnteprima+"/docs/A"+numbAnteprima+".pdf"
            bot.sendMessage(chat_id, url, disable_web_page_preview = False)
        except:
            last_prev = os.listdir(conf_File['HOME'] + "res/")
            last_prev = sorted(last_prev)
            bot.sendMessage(chat_id, str(datetime.date.today()) + " - Last downloaded: " + last_prev[-1])
            #bot.sendMessage(chat_id, "Nota: Febbraio 2021 --> #354")

def channelFiltering(msg, chat_ref):
    #cid = "@rss_torrg" #Channel Torrent Galaxy RSS Feed
    cid = "-1001159149797L" #Channel Torrent Galaxy RSS Feed
    msg_id = msg['message_id']

    countFiltri = len(conf_File['Users']['Admin']['Filters'])
    #print(countFiltri)

    text_msg = msg['text']
    
    for i in conf_File['Users']['Admin']['Filters']:
        #print(conf_File['Users']['Admin']['Filters'][i])
        pattern = str(conf_File['Users']['Admin']['Filters'][i]['pattern'])
        filterMsg = str(conf_File['Users']['Admin']['Filters'][i]['messaggio'])
        result = re.search(pattern, text_msg)

        if result:
            if (pattern == 'XXX -' or pattern == 'XXX-'):
                pprint("Questo dovrei cancellarlo")
                bot.deleteMessage((cid, msg_id))
            else:
                pprint("Questo dovrei lasciarlo passare")
                bot.sendMessage(chat_ref, filterMsg)
                logging.info(filterMsg)
                bot.forwardMessage(chat_ref, cid, msg_id)   

    
bot = telepot.Bot(conf_File['TOKEN'])

#MessageLoop(bot, on_chat_message).run_as_thread()
bot.message_loop({'chat': on_chat_message})

print('I am listening ...')

def previewPolling(t):
    
    ref = 366
    today = datetime.date.today()
    ref_day = datetime.date(2022,2,15)

    numbAnteprima = str((today-ref_day).days//30 + ref)


    url = "https://www.panini.it/media/flowpaper/A"+numbAnteprima+"/docs/A"+numbAnteprima+".pdf"
    
    print("Attempting to retrive Antemprima #"+numbAnteprima+"...")
    r = requests.get(url, allow_redirects=True)
    fileExist = not os.path.exists(path +'/res/'+ numbAnteprima +".pdf")
    print(fileExist)

    if((r.headers["Content-Type"] == "application/pdf") & fileExist):
        open(path+'/res/A' + numbAnteprima+'.pdf', 'wb').write(r.content)
        print("Done!")
    else:
        print("Failed!")
        logging.info("File Anteprima #" + numbAnteprima + " still not available!")
    return

schedule.every().day.at("16:15").do(previewPolling,'Attempting to retrive new Anteprima...')

while 1:
    schedule.run_pending()
    time.sleep(10)

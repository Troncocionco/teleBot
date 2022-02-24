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
- `/roll` - reply with a random integer between 1 and 6, like rolling a dice.
- `/time` - reply with the current time, like a clock.
- `/ip` - 
- `/anteprima` - 
- `/testUp` - 

"""
with open('/home/pi/giacominoBot/conf.json') as f:
  conf_File = json.load(f)

path = conf_File['HOME']


#my_logger.debug('this is debug')
#my_logger.critical('this is critical')

def on_chat_message(msg):

    logging.basicConfig(filename=conf_File['Log_directory'], filemode='a',format='[%(asctime)s] - %(name)s - %(levelname)s - %(message)s')

    pprint(msg)
    logging.info(msg)
    content_type, chat_type, chat_id = telepot.glance(msg)
    reg_Anteprima = "/anteprima\s([0-9]*)"
    command = msg['text']

    chat_ref = conf_File['Users']['Admin']['Chat_ID_Reference']
    
    try:
        user = msg['from']['username']
        bot.sendMessage(chat_id, 'Ciaone ' + str(user))
    except:
        print("Non e' una chat privata!")
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
            URL = str(ip_request.content)
            URL = URL[:-1]
            bot.sendMessage(chat_id, "IP_RaspberryPi_Zero: "+URL)
            bot.sendMessage(chat_id, "Server Fumetti: comicsauthority.zapto.org:2202")
            bot.sendMessage(chat_id, "Server Backup Fumetti: comicsauthority2.zapto.org:2202")
    elif command == "/up":
        bashCommand = "ping -c 3 192.168.1.38"
        resp = os.system(bashCommand)
        if resp == 0:
            bot.sendMessage(chat_id, "Server Up!")
        else:
            bot.sendMessage(chat_id, "Server Down or Unreachable!")
    elif "/anteprima" in command:
        numbAnteprima = re.match(reg_Anteprima, command).group(1)
        #Va cambiato sendDocument, non e' piu una risorsa locale
        url = "https://www.panini.it/media/flowpaper/A"+numbAnteprima+"/docs/A"+numbAnteprima+".pdf"
        bot.sendMessage(chat_id, "Nota: Febbraio 2021 --> #354")
        bot.sendMessage(chat_id, url, disable_web_page_preview = False)

def channelFiltering(msg, chat_ref):
    cid = "@rss_torrg" #Channel Torrent Galaxy RSS Feed
    msg_id = msg['message_id']

    countFiltri = len(conf_File['Users']['Admin']['Filters'])
    #print(countFiltri)

    text_msg = msg['text']

    for i in conf_File['Users']['Admin']['Filters']:
        #print(conf_File['Users']['Admin']['Filters'][i])
        pattern = str(conf_File['Users']['Admin']['Filters'][i]['pattern'])
        filterMsg = str(conf_File['Users']['Admin']['Filters'][i]['messaggio'])
        result = re.match(pattern, text_msg)
  
        if result:
            if (pattern == 'XXX -' or pattern == 'XXX-'):
                bot.deleteMessage((cid, msg_id))
                break
            else:
                bot.sendMessage(chat_ref, filterMsg)
                logging.info(filterMsg)
                bot.forwardMessage(chat_ref, cid, msg_id)
        

    #print ("CID: "+cid+"\nMSID: "+str(msg_id))

"""     pattern1 = 'XXX\-'
    pattern2 = 'TV-Episodes.*\n.*\nDexter.S09'
    pattern3 = '.*?Miami Heat.*\n\nvia.*'
    pattern4 = 'TV-Episodes.*\n.*\nStar.Wars.The.Bad.Batch.S'
    pattern5 = 'TV-Ep.*\n.*\nLoki'

    result1 = re.match(pattern1, text_msg)
    result2 = re. match(pattern2, text_msg)
    result3 = re.match(pattern3,text_msg)
    result4 = re.match(pattern4, text_msg)
    result5 = re.match(pattern5, text_msg)

    if result1:
        print("Pornazzo! Censura!")
        logging.info("Pornazzo! Censura!")
        bot.deleteMessage((cid, msg_id))
    elif result2:
        bot.sendMessage(chat_ref, "***Nuova Puntata #Dexter!***")
        logging.info("***Nuova Puntata #Dexter!***")
        bot.forwardMessage(chat_ref, cid, msg_id)
    elif result3:
        bot.sendMessage(chat_ref, "***Hanno giocato gli #Heat!***")
        logging.info("***Hanno giocato gli Heat!***")
        bot.forwardMessage(chat_ref, cid, msg_id)
    elif result4:
        bot.sendMessage(chat_ref, "***Nuova Puntata Star Wars #BadBatch!***")
        logging.info("***Nuova Puntata BadBatch!***")
        bot.forwardMessage(chat_ref, cid, msg_id)
    elif result5:
        bot.sendMessage(chat_ref, "***Nuova Puntata #Loki!***")
        logging.info("***Nuova Puntata MARVEL Loki!***")
        bot.forwardMessage(chat_ref, cid, msg_id)        
    else:
        print("OK.") """
    

def on_callback_query(msg):

    pprint(msg)

    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
    
    if query_data == 'Request-Lista Spesa':
        print("Callback Query(Q_ID, From, Q_Data): ", query_id, from_id, query_data)
        f = open('resource/listaSpesa.txt', 'r')
        file_lista=f.read()
        bot.answerCallbackQuery(query_id,text=file_lista, show_alert='True')
    
    
    bot.answerCallbackQuery(query_id,text="YEAH")

bot = telepot.Bot(conf_File['TOKEN'])

#MessageLoop(bot, on_chat_message).run_as_thread()
bot.message_loop({'chat': on_chat_message,
  'callback_query': on_callback_query})

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



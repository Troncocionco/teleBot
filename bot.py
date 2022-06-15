# coding=utf-8
from ast import get_docstring
import atexit
import os
from uuid import uuid4
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import InlineQueryResultArticle, ParseMode, InputTextMessageContent, Update
from telegram.error import Unauthorized, BadRequest, TimedOut, NetworkError, ChatMigrated, TelegramError
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, InlineQueryHandler
from telegram.utils.helpers import escape_markdown
from pprint import pprint
import logging
import requests
import json
import subprocess
from bs4 import BeautifulSoup
from pprint import pprint

with open('conf.json') as f:
  conFile = json.load(f)

updater = Updater(conFile['TOKEN'], use_context=True) #use_Context: al bot vengono passati anche i CallBackContext
dispatcher = updater.dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)



def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

def send_message(update, context, message):
    pprint(update)
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)

def ip(update, context):
    chat_id=update.effective_chat.id

    if str(chat_id) in conFile['AllowedUser']:
        ip_request = requests.get("http://checkip.amazonaws.com")
        URL = ip_request.content.decode('utf-8')[:-1]
        context.bot.send_message(chat_id=update.effective_chat.id, text="IP_Pubblico: "+URL)
        context.bot.send_message(chat_id=update.effective_chat.id, text="Server Fumetti: "+URL+":2202")

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
    #pprint(type(context.args[0]))
    #pprint(context.args[0]) 
    chat_id=update.effective_chat.id

    if str(chat_id) in conFile['AllowedUser']:
        subprocess.run(["bash", "download.sh", context.args[0]])
        output = subprocess.check_output(["ls","-t","/data_500GB/Fumetti/USA"])
        output = str(output).replace("\\n",' #')
        pprint(output)
        context.bot.send_message(chat_id=update.effective_chat.id, text=output)


def cbQuery(update, context) -> None:
    """Handle the inline query."""
  
    query = update.inline_query.query

    if query == "":
        return
    pprint(str(query))
    url='https://www.comicsbox.it/search.php'
    params ={'stringa': str(query),'criterio': 'ita', 'submit':''}

    response=requests.post(url, data=params)
    soup = BeautifulSoup(response.text, 'html5lib')
    
    table = soup.find_all("span", class_="title")

    results = []

    for i in enumerate(table[:30]):

        id = i[0]
        link = i[1].find("a")['href']
        link = "https://comicsbox.it/"+ link
        thumb = link.replace("serie","cover") + "_001.jpg"

        value = i[1].text

        item = InlineQueryResultArticle(
            id=str(i[0]),
            title= str(value),
            input_message_content= InputTextMessageContent(link),
            description=str(value))

        results.append(item)

    update.inline_query.answer(results)

dispatcher.add_handler(InlineQueryHandler(cbQuery))

#Handler per download remotizzato
download_handler = CommandHandler('down',download)
dispatcher.add_handler(download_handler)

#Handler per messaggi_comando
start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

#Handler per Serverino Ubooquity
ubooquity_handler = CommandHandler('ubo', ubooquity)
dispatcher.add_handler(ubooquity_handler)

#Handler per messaggi_comando con argomenti
ip_handler = CommandHandler('ip', ip)
dispatcher.add_handler(ip_handler)



updater.start_polling()

# -*- coding: utf-8 -*-
import sys
import json
import base64
import requests
import string
from imp import reload

reload(sys)

import skypebot

from flask import Flask, request
import Tensorflow_chat_bot_response as bt


app = Flask(__name__)

client_id = 'f6a6d0ee-1856-4c36-a545-a427aef5a001'  #Microsoft ID
client_secret = 'MS3JDeGrSLmeHaHpqTtgvsS' #Microsoft mot de passe

bot = skypebot.SkypeBot(client_id,client_secret)



@app.route('/', methods=['POST'])
def webhook():
  if request.method == 'POST':
    try:
        data = json.loads(request.data)
        service = data['serviceUrl']
        user_id=data['from']['name']
        if data['type'] =='message':

            sender = data['conversation']['id']
            print (sender)
            print (data['from']['name'])
            text = data['text']
            res=bt.response(text,user_id)
            process_messages(sender,res,service)

        else:
            pass
    except Exception as e:
      print (traceback.format_exc()) # si il y a un erreur

  return 'Ok'


#envoyer le message vers Skype
def process_messages(sender,text,service):
  bot.send_message(service,sender,text)




if __name__ == '__main__':
    app.run()

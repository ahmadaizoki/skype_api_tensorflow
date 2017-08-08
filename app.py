# -*- coding: utf-8 -*-
import sys
import traceback
import json
import base64
import requests
import string
from imp import reload

reload(sys)

import skypebot

from flask import Flask, request
import Tensorflow_chat_bot_response as bt
import config as conf


app = Flask(__name__)

##################################################
#skype bot

client_id = conf.id_Micosoft  #Microsoft ID
client_secret = conf.password_Microsoft #Microsoft mot de passe

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

#########################################################################
#facebook bot

from pymessager.message import Messager
client=Messager(conf.fb_access_token)

@app.route('/webhook', methods=["GET"])
def fb_webhook():
    verification_code = conf.fb_verifing_token
    verify_token = request.args.get('hub.verify_token')
    if verification_code == verify_token:
        return request.args.get('hub.challenge')


@app.route('/webhook', methods=['POST'])
def fb_receive_message():
    message_entries = json.loads(request.data.decode('utf8'))['entry']
    for entry in message_entries:
        for message in entry['messaging']:
            if message.get('message'):
                user_id="{sender[id]}".format(**message)
                text="{message[text]}".format(**message)
                res=bt.response(text,user_id)
                if res=="De rien":
                    client.send_image(user_id,conf.deRien)
                elif (res=="ok"):
                    Template=[]
                    client.send_generic(user_id, Template.Generic([
                        Template.GenericElement("rift",
                          subtitle="Next-generation virtual reality",
                          item_url="https://www.oculus.com/en-us/rift/",
                          image_url=CONFIG['SERVER_URL'] + "/assets/rift.png",
                          buttons=[
                              Template.ButtonWeb("Open Web URL", "https://www.oculus.com/en-us/rift/"),
                              Template.ButtonPostBack("tigger Postback", "DEVELOPED_DEFINED_PAYLOAD"),
                              Template.ButtonPhoneNumber("Call Phone Number", "+16505551234")
                          ]),
                        Template.GenericElement("touch",
                          subtitle="Your Hands, Now in VR",
                          item_url="https://www.oculus.com/en-us/touch/",
                          image_url=CONFIG['SERVER_URL'] + "/assets/touch.png",
                          buttons=[
                              Template.ButtonWeb("Open Web URL", "https://www.oculus.com/en-us/rift/"),
                              Template.ButtonPostBack("tigger Postback", "DEVELOPED_DEFINED_PAYLOAD"),
                              Template.ButtonPhoneNumber("Call Phone Number", "+16505551234")
                          ])
                    ]))
                else:
                    client.send_text(user_id,res)
    return "Ok"

########################################################################
if __name__ == '__main__':
    app.run()

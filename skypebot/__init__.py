# -*- coding: utf-8 -*-

import threading

import sys
import requests
import time
from datetime import *
from time import *

from skypebot import skype_api



class SkypeBot:

    def __init__(self, client_id,client_secret):


        def token_func():
            global token
            payload = "grant_type=client_credentials&client_id="+client_id+"&client_secret="+client_secret+"&scope=https%3A%2F%2Fgraph.microsoft.com%2F.default"
            response = requests.post("https://login.microsoftonline.com/common/oauth2/v2.0/token?client_id="+client_id+"&client_secret="+client_secret+"&grant_type=client_credentials&scope=https%3A%2F%2Fgraph.microsoft.com%2F.default",data=payload,headers={"Content-Type":"application/x-www-form-urlencoded"})
            data = response.json()
            token = data["access_token"]


        def runit():
            while True:
                token_func()
                sleep(3000)

        self.t = threading.Thread(target=runit)
        self.t.daemon = True
        self.t.start()

    def send_message(self,service,sender, text):

        return skype_api.send_message(token,service,sender, text)

# -*- coding: utf-8 -*-
import requests
import json
import traceback
import sys

import time
from datetime import *
from time import *
import base64

from imp import reload
from sys import version_info
import string

reload(sys)

#il faut le texte qu'il soit UTF-8 et composé de 320 alphabets

def send_message(token,service,sender,text):
    try:
        payload = {
                    "type": "message",
                    "text": text
                    }
        r = requests.post(service+'/v3/conversations/'+sender+'/activities/',headers={"Authorization": "Bearer "+token,"Content-Type":"application/json"},json=payload)

        print (r)

    except Exception as e:
        print (e)
        pass

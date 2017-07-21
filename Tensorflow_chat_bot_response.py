# les packages necessaires pour NLP
import nltk
from nltk.stem.lancaster import LancasterStemmer
stemmer = LancasterStemmer()

# les packages necessaires por Tensorflow
import numpy as np
import tflearn
import tensorflow as tf
import random

############################################

#connexion a la base
import os
import psycopg2

#essayer de cinnecter
try:
    conn=psycopg2.connect("postgres://xpmqhxcaiquvwy:7b300499f98a11666ffc1d3a14f2bba8d17859bed31e3f9f37451e2c57ba00ec@ec2-79-125-125-97.eu-west-1.compute.amazonaws.com:5432/db63uu5csa2t5l")
except:
    print ("echec de connexion")

cur=conn.cursor()
############################################

# faire appeler  la data structure
import pickle
data = pickle.load( open( "training_data", "rb" ) )
words = data['words']
classes = data['classes']
train_x = data['train_x']
train_y = data['train_y']

# appler le fichier json
import json
with open('intents.json') as json_data:
    intents = json.load(json_data)

############################################

# construire le reseau de neuron
net = tflearn.input_data(shape=[None, len(train_x[0])])
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, len(train_y[0]), activation='softmax')
net = tflearn.regression(net)

# Definir la module et telecharger tensorboard
model = tflearn.DNN(net, tensorboard_dir='tflearn_logs')

#############################################

def clean_up_sentence(sentence):
    # pattern tokenizer
    sentence_words = nltk.word_tokenize(sentence)
    # reserve chaque mot
    sentence_words = [stemmer.stem(word.lower()) for word in sentence_words]
    print (sentence_words)
    return sentence_words

# construire une matrice de 0 et 1 pour les mots dans la phrase
def bow(sentence, words, show_details=False):
    # pattern tokenizer
    sentence_words = clean_up_sentence(sentence)
    # sac de mots
    bag = [0]*len(words)
    for s in sentence_words:
        for i,w in enumerate(words):
            if w == s:
                bag[i] = 1
                if show_details:
                    print ("found in bag: %s" % w)

    return(np.array(bag))

############################################################

print (classes)

#################################################################

# appeler ma module
model.load('./model.tflearn')

############################################################

def selectPool():
    res=[]
    cur=conn.cursor()
    try:
        cur.execute("SELECT * FROM pool")
        rows=cur.fetchall()
        lenrow=len(rows)
    except:
        print ("erreur connexion")
    for i in range (lenrow):
        res=res+[rows[i][1]]
    return res

#############################################################

def selectBreakfast():
    res=[]
    cur=conn.cursor()
    try:
        cur.execute("SELECT * FROM breakfast")
        rows=cur.fetchall()
        lenrow=len(rows)
    except:
        print ("erreur connexion")
    for i in range (lenrow):
        res=res+[rows[i][1]]
    return res

##############################################################

def selectFitness():
    res=[]
    cur=conn.cursor()
    try:
        cur.execute("SELECT * FROM fitness")
        rows=cur.fetchall()
        lenrow=len(rows)
    except:
        print ("erreur connexion")
    for i in range (lenrow):
        res=res+[rows[i][1]]
    return res

#################################################################

def selectRestaurant():
    res=[]
    cur=conn.cursor()
    try:
        cur.execute("SELECT * FROM restaurant")
        rows=cur.fetchall()
        lenrow=len(rows)
    except:
        print ("erreur connexion")
    for i in range (lenrow):
        res=res+[rows[i][1]]
    return res

##################################################################

def inPool(sentence):
    sent=nltk.word_tokenize(sentence)
    res=selectPool()
    for i in sent:
        if i in res:
            return True
            break
    return False

###################################################################

def inBreakfast(sentence):
    sent=nltk.word_tokenize(sentence)
    res=selectBreakfast()
    for i in sent:
        if i in res:
            return True
            break
    return False

####################################################################

def inRestaurant(sentence):
    sent=nltk.word_tokenize(sentence)
    res=selectRestaurant()
    for i in sent:
        if i in res:
            return True
            break
    return False

#####################################################################

def inFitness(sentence):
    sent=nltk.word_tokenize(sentence)
    res=selectFitness()
    for i in sent:
        if i in res:
            return True
            break
    return False

######################################################################

# la data structure pour la contexte d'utilisateur
context = {}

ERROR_THRESHOLD = 0.25
def classify(sentence):
    # generer la probability de la module
    results = model.predict([bow(sentence, words)])[0]
    # filter la probability
    results = [[i,r] for i,r in enumerate(results) if r>ERROR_THRESHOLD]
    # trier a partir de la probability
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append((classes[r[0]], r[1]))
    # return l'intention et la probability
    print (return_list)
    return return_list

def response(sentence, userID='123', show_details=False):
    results = classify(sentence)
    # si on a classifie ,trouve moi l'intention
    if results:
        # loop as long as there are matches to process
        while results:
            for i in intents['intents']:
                # trouver l'intention
                if i['tag'] == results[0][0]:
                    # si il y a une contexte
                    if 'context_set' in i:
                        if show_details: print ('context:', i['context_set'])
                        context[userID] = i['context_set']

                    # si il y a pas de contexte
                    if not 'context_filter' in i or \
                        (userID in context and 'context_filter' in i and i['context_filter'] == context[userID]):
                        if show_details: print ('tag:', i['tag'])
                        # choisit une reponse de l'intention
                        if i['tag']=='horaires':
                            if inPool(sentence):
                                return ('les horaire de pool')
                                break
                            elif inBreakfast(sentence):
                                return ('les horaire de breakfast')
                                break
                            elif inRestaurant(sentence):
                                return ('les horaires de restaurant')
                                break
                            elif inFitness(sentence):
                                return ('les horaires de fitness')
                                break
                            else:
                                return random.choice(i['responses'])
                        else:
                            return random.choice(i['responses'])

            results.pop(0)

##############################################################################

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
import config

#essayer de cinnecter
try:
    conn=psycopg2.connect(config.db_url)
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
with open(config.data_set) as json_data:
    intents = json.load(json_data)

with open(config.data) as horaires_data:
    horaires=json.load(horaires_data)
############################################

# construire le reseau de neuron
net = tflearn.input_data(shape=[None, len(train_x[0])])
net = tflearn.fully_connected(net, 14)
net = tflearn.fully_connected(net, 14)
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

def selectHoraire(mots):
    res=[]
    rows=[]
    try:
        cur.execute("""SELECT parametre FROM horaires WHERE mot=%(mots)s""",{"mots":mots})
        rows=cur.fetchall()
    except:
        print ("erreur connexion")
    if rows!=[]:
        return rows[0][0]
    else:
        return

################################################################

def inHoraire(sentence):
    sent=nltk.word_tokenize(sentence)
    for i in sent:
        res=selectHoraire(i)
        if res:
            return res
            break

#################################################################

#Ajouter dans la base
def addMotToHoraire(sentence,user_id):
    sent=nltk.word_tokenize(sentence)
    j=0
    for i in sent:
        j+=1
        if (i=='le'or i=='la' or i=='les' or i=='au' or i=='l'):
            if (sent[j]!="horaires" and sent[j]!="hotel" and sent[j]!="salle"):
                try:
                    cur.execute("""INSERT INTO horaires (mot,flag,id_user) VALUES (%(mot)s,0,%(user_id)s)""",{"mot":sent[j],"user_id":user_id})
                    conn.commit()
                    print ("Done!")
                except:
                    print ("erreur connexion")
                    print (sent[j])
                    return True
                break
    return False

def addToQuestion(sentence,flag,user_id,intent,prop):
    try:
        cur.execute("""INSERT INTO question (question,traiter,id_user,intent,prop) VALUES (%(sentence)s,%(flag)i,%(user_id)s,%(intent)s,%(prop)s)""",{"sentence":sentence,"flag":flag,"user_id":user_id,"intent":intent,"prop":prop})
        conn.commit()
    except:
        print ("erreur connexion")

def lastHoraires(user_id):
    rows=[]
    try:
        cur.execute("""SELECT mot FROM horaires WHERE id_user=%(user_id)s""",{"user_id":user_id})
        rows=cur.fetchall()
    except:
        print ("erreur connexion")
    j=len(rows)
    return rows[j-1][0]

def updateHoraires(parametre,user_id):
    mot=lastHoraires(user_id)
    try:
        cur.execute("""UPDATE horaires SET parametre=%(parametre)s WHERE (mot=%(mot)s AND id_user=%(user_id)s)""",{"parametre":parametre,"mot":mot,"user_id":user_id})
        conn.commit()
    except:
        print ("erreur connexion")
    return True

def lastQuestion(user_id):
    rows=[]
    try:
        cur.execute("""SELECT question FROM question WHERE id_user=%(id_user)s""",{"id_user":id_user})
        rows=cur.fetchall()
    except:
        print ("erreur connexion")
    j=len(rows)
    return rows[j-1][0]

def updateQuestion(flag,user_id):
    question=lastQuestion(user_id)
    try:
        cur.execute("""UPDATE question SET flag=%(flag)i WHERE (question=%(question)s AND id_user=%(user_id)s)""",{"flag":flag,"question":question,"user_id":user_id})
        conn.commit()
    except:
        print ("erreur connexion")
    return True

#################################################################

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


def response(sentence,user_id, userID='123', show_details=False):
    results = classify(sentence)
    sentence=sentence.lower()
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
                        if i['tag']=='horaires':
                            hor=inHoraire(sentence)
                            if hor=='pool':
                                addToQuestion(sentence,2,user_id,i['tag'],str(results))
                                return (config.message_data_null)
                                #return (horaires["horaires"][0]["pool"])
                                break
                            elif hor=='breakfast':
                                addToQuestion(sentence,2,user_id,i['tag'],str(results))
                                return ("Du "+config.breakfasts_date_from+" au "+config.breakfasts_date_to+" a partir de: "+config.breakfasts_period_from+" jusqu'a: "+config.breakfasts_period_to)
                                break
                            elif hor=='restaurant':
                                addToQuestion(sentence,2,user_id,i['tag'],str(results))
                                return (config.message_data_null)
                                #return (horaires["horaires"][0]["restaurant"])
                                break
                            elif hor=='fitness':
                                addToQuestion(sentence,2,user_id,i['tag'],str(results))
                                return ("Du "+config.fitness_date_from+" au "+config.fitness_date_to+" a partir de: "+config.fitness_period_from+" jusqu'a: "+config.fitness_period_to)
                                break
                            else:
                                if (addMotToHoraire(sentence,user_id)):
                                    print ("add to horaires")
                                else:
                                    addToQuestion(sentence,0,user_id,i['tag'],str(results))
                                    print ("add to question")
                                return random.choice(i['responses'])

                    # si il y a pas de contexte
                    if not 'context_filter' in i or \
                        (userID in context and 'context_filter' in i and i['context_filter'] == context[userID]):
                            if show_details: print ('tag:', i['tag'])
                            # choisit une reponse de l'intention
                            if i['tag']=='q_horaires':
                                if sentence=='pool':
                                    if (updateHoraires('pool',user_id)):
                                        return (config.message_data_null)
                                        #return (horaires["horaires"][0]["pool"])
                                    else:
                                        return (config.message_data_null)
                                        #return (horaires["horaires"][0]["pool"])
                                    break
                                elif sentence=='breakfast':
                                    if (updateHoraires('breakfast',user_id)):
                                        return ("Du "+config.breakfasts_date_from+" au "+config.breakfasts_date_to+" a partir de: "+config.breakfasts_period_from+" jusqu'a: "+config.breakfasts_period_to)
                                    else:
                                        return ("Du "+config.breakfasts_date_from+" au "+config.breakfasts_date_to+" a partir de: "+config.breakfasts_period_from+" jusqu'a: "+config.breakfasts_period_to)
                                    break
                                elif sentence=='restaurant':
                                    if (updateHoraires('restaurant',user_id)):
                                        return (config.message_data_null)
                                        #return (horaires["horaires"][0]["restaurant"])
                                    else:
                                        return (config.message_data_null)
                                        #return (horaires["horaires"][0]["restaurant"])
                                    break
                                elif sentence=='fitness':
                                    if (updateHoraires('fitness',user_id)):
                                        return ("Du "+config.fitness_date_from+" au "+config.fitness_date_to+" a partir de: "+config.fitness_period_from+" jusqu'a: "+config.fitness_period_to)
                                    else:
                                        return ("Du "+config.fitness_date_from+" au "+config.fitness_date_to+" a partir de: "+config.fitness_period_from+" jusqu'a: "+config.fitness_period_to)
                                    break
                                elif sentence=='autre horaire':
                                    updateQuestion(1,user_id)
                                    return (config.message_data_null)
                                else:
                                    return random.choice(i['responses'])
                            else:
                                addToQuestion(sentence,user_id,i['tag'],str(results))
                                return random.choice(i['responses'])
                    else:
                        return config.message_noIntent

            results.pop(0)

##############################################################################

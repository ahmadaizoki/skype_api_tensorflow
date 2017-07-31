# les packages necessaires pour NLP
import nltk
from nltk.stem.lancaster import LancasterStemmer
stemmer = LancasterStemmer()

# les packages necessaires por Tensorflow
import numpy as np
import tflearn
import tensorflow as tf
import random

#################################################

# appler le fichier json
import json
with open('intents.json') as json_data:
    intents = json.load(json_data)

################################################

words = []
classes = []
documents = []
ignore_words = ['?']
# loop sur chaque phrase
for intent in intents['intents']:
    for pattern in intent['patterns']:
        # tokenizer chaque mot dans la phrase
        w = nltk.word_tokenize(pattern)
        # ajouter dansliste
        words.extend(w)
        # ajouter dans documentation en corpus
        documents.append((w, intent['tag']))
        # ajouter dans la liste de classes
        if intent['tag'] not in classes:
            classes.append(intent['tag'])

# reserve chaque mot et enleve les doubles
words = [stemmer.stem(w.lower()) for w in words if w not in ignore_words]
words = sorted(list(set(words)))

# supprimer les doubles
classes = sorted(list(set(classes)))

print (len(documents), "documents")
print (len(classes), "classes", classes)
print (len(words), "unique stemmed words", words)

#################################################

# construire notre data pour entrainer le bot
training = []
output = []
# vide vector pour la resultat
output_empty = [0] * len(classes)

# l'ensemble pour entrainer et le sac de mots pur chasque phrase
for doc in documents:
    # initializer le sac ce mots
    bag = []
    # lister les mots tokenize pour les patterns
    pattern_words = doc[0]
    # reserve chaque mot
    pattern_words = [stemmer.stem(word.lower()) for word in pattern_words]
    # creer le sac de mots
    for w in words:
        bag.append(1) if w in pattern_words else bag.append(0)

    # la sorti est  '0' pour cahque tag et  '1' pour l'actuel tag
    output_row = list(output_empty)
    output_row[classes.index(doc[1])] = 1

    training.append([bag, output_row])

# construire le np.array
random.shuffle(training)
training = np.array(training)

# creer les lists pour l'entrainer et le tester
train_x = list(training[:,0])
train_y = list(training[:,1])

##################################################

# reinitialiser la data ghraph
tf.reset_default_graph()
# construire les reseaux de neurons
net = tflearn.input_data(shape=[None, len(train_x[0])])
net = tflearn.fully_connected(net, 12)
net = tflearn.fully_connected(net, 12)
net = tflearn.fully_connected(net, len(train_y[0]), activation='softmax')
net = tflearn.regression(net)

# Definer la module et telecharger tensorboard
model = tflearn.DNN(net, tensorboard_dir='tflearn_logs')
# commencer a entrainer(en utilisant l'algo gradient descent)
model.fit(train_x, train_y, n_epoch=1000, batch_size=8, show_metric=True)
model.save('model.tflearn')

####################################################

def clean_up_sentence(sentence):
    # pattern tokenizer
    sentence_words = nltk.word_tokenize(sentence)
    # reserve chaque mot
    sentence_words = [stemmer.stem(word.lower()) for word in sentence_words]
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
                    print ("trouve dans la sac: %s" % w)

    return(np.array(bag))

######################################################

p = bow("Quel heure la piscine?", words)
print (p)
print (classes)

######################################################

print(model.predict([p]))

######################################################

# sauvgarder les data en structure
import pickle
pickle.dump( {'words':words, 'classes':classes, 'train_x':train_x, 'train_y':train_y}, open( "training_data", "wb" ) )

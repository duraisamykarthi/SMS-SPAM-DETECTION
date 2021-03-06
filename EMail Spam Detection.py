# -*- coding: utf-8 -*-
"""
Created on Thu Jan  3 08:37:45 2019

@author: KARTHI
"""

import sys
import nltk
import sklearn
import pandas
import numpy

print('Python: {}'.format(sys.version))
print('NLTK: {}'.format(nltk.__version__))
print('Scikit-learn: {}'.format(sklearn.__version__))
print('Pandas: {}'.format(pandas.__version__))
print('numpy: {}'.format(numpy.__version__))

# 1.Load the dataset

import pandas as pd
import numpy as np

# Load the dataset of sms messages
df = pd.read_table('SMSSpamCollection', header = None, encoding = 'utf-8')

# print useful information about the dataset
print(df.info()) 
print(df.head())

# Check class distribution
classes = df[0]
print(classes.value_counts())

# 2.Preprocess the data

# Convert the labels to binary values , 0 = ham, 1 = spam
from sklearn.preprocessing import LabelEncoder

encoder = LabelEncoder()
Y = encoder.fit_transform(classes)

print(classes[:10])
print(Y[:10])

# Store the SMS message data

text_messages = df[1]
print(text_messages[:10])

# Use regular expressions to replace email addresses, urls, phone numbers, other numbers, symbols

# Replace email addresses with 'emailaddr'
processed = text_messages.str.replace(r'^.+@[^\.].*\.[a-z]{2,}$', 'emailaddr')

# Replace urls with 'webaddress'
processed = processed.str.replace(r'^http\://[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,3}(/\S*)?$', 'webaddress')

# Replace money symblos with 'moneysymb'
processed = processed.str.replace(r'£|\$', 'moneysymb')

# Replace 10 digit phone numbers with 'phonenumber'
processed = processed.str.replace(r'^\(?[\d]{3}\)?[\s-]?[\d]]{3}[\s-]?[\d]{4}$','phonenumber')

# Replace normal numbers with 'numbr'
processed = processed.str.replace(r'\d+(\.\d+)?','numbr')

# Replace punctuation
processed = processed.str.replace(r'[^\w\d\s]',' ')

# Replace whitespace between terms with a single space
processed = processed.str.replace(r'\s+', ' ')

# Remove Leading and Trailing whitespaces
processed = processed.str.replace(r'^\s+|\s+?$', '')

# Change words to lower case - Hello, HEllo, hello are all same word!
processed = processed.str.lower()
print(processed)

# remove stop words from text messages
from nltk.corpus import stopwords
stop_words = set(stopwords.words('english'))
processed = processed.apply(lambda x: ' '.join(term for term in x.split() if term not in stop_words))

# Remove word stems using a porter stemmer
ps = nltk.PorterStemmer()
processed = processed.apply(lambda x: ' '.join(ps.stem(term) for term in x.split()))

print(processed)

from nltk.tokenize import word_tokenize

# Creating a bag-of-words
all_words = []

for message in processed:
    words = word_tokenize(message)
    for w in words:
        all_words.append(w)
        
all_words = nltk.FreqDist(all_words) # For find most common words

# Print the total number of words and the 15 most common words
print('Number of words: {}'.format(len(all_words)))
print('Most common words: {}'.format(all_words.most_common(15)))

# Use the 1500 most common words as features
word_features = list(all_words.keys())[:1500]

# define a find_features function
def find_features(message):
    words = word_tokenize(message)
    features = {}
    for word in word_features:
        features[word] = (word in words)
        
    return features

# Lets see an example
features = find_features(processed[0])
for key, value in features.items():
    if value == True:
        print(key)
        
print(processed[0])

print(features)

# find features for all messages
messages = list(zip(processed, Y)) # y-binary class label for spam or not spam

# define a seed for reproducibility
seed = 1
np.random.seed = seed
np.random.shuffle(messages)

# Call find_features function for each SMS messages
featuresets = [(find_features(text), label) for (text, label) in messages]
 
# split training and testing datasets using sklearn
from sklearn import model_selection

training, testing = model_selection.train_test_split(featuresets, test_size = 0.25, random_state = seed)

print('Training: {}'.format(len(training)))
print('Testing: {}'.format(len(testing)))

# Deploying sklearn classifiers
# 4.Scikit-Learn Classifiers with NLTK
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression,SGDClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix

# Define models to train
names = ['K Nearest Neighbors', 'Decision Tree', 'Random Forest', 'Logistic Regression', 'SGD Classifier', 'Naive Bayes', 'SVM Linear']

classifiers = [
        KNeighborsClassifier(),
        DecisionTreeClassifier(),
        RandomForestClassifier(),
        LogisticRegression(),
        SGDClassifier(max_iter = 100),
        MultinomialNB(),
        SVC(kernel = 'linear')
        ]

models = list(zip(names, classifiers))
print(models)

# wrap models in NLTK
from nltk.classify.scikitlearn import SklearnClassifier

for name, model in models:
    nltk_model = SklearnClassifier(model)
    nltk_model.train(training)
    accuracy = nltk.classify.accuracy(nltk_model, testing)*100
    print('{} Accuracy: {}'.format(name,accuracy))
    
# ensemble method - Voting classifier
from sklearn.ensemble import VotingClassifier

# Define models to train
names = ['K Nearest Neighbors', 'Decision Tree', 'Random Forest', 'Logistic Regression', 'SGD Classifier', 'Naive Bayes', 'SVM Linear']

classifiers = [
        KNeighborsClassifier(),
        DecisionTreeClassifier(),
        RandomForestClassifier(),
        LogisticRegression(),
        SGDClassifier(max_iter = 100),
        MultinomialNB(),
        SVC(kernel = 'linear')
        ]

models = list(zip(names, classifiers))

nltk_ensemble = SklearnClassifier(VotingClassifier(estimators = models, voting = 'hard', n_jobs = -1))
nltk_ensemble.train(training)
accuracy = nltk.classify.accuracy(nltk_ensemble, testing)*100
print('Ensemble Method Accuracy: {}'.format(accuracy))

# Make class label prediction for testing set
txt_features, labels = list(zip(*testing))
prediction = nltk_ensemble.classify_many(txt_features)

# Print a confusion matrix and a classification report
print(classification_report(labels, prediction))

pd.DataFrame(
        confusion_matrix(labels, prediction),
        index = [['actual','actual'],['ham', 'spam']],
        columns = [['predicted','predicted'],['ham','spam']])
        

















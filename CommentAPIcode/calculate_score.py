#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'simranjitsingh'

# This code calculate all the scores i.e Articles Relevance Score , Conversational Relevance Scores ,
# Readability Score and Personal Experience Score
# Subroutines used : CleanAndTokenize,TextStatistics

from nltk.probability import FreqDist
from nltk.corpus import stopwords
import nltk.tag, nltk.util, nltk.stem
import re
import math
from decimal import *
import mysql.connector
import sys
import json
import string
from ConfigParser import SafeConfigParser
from nltk.tokenize import WhitespaceTokenizer
from CleanTokenize import CleanAndTokenize
from TextStatistics import TextStatistics

stopword_list = stopwords.words('english')
porter = nltk.PorterStemmer()
word_features = []
vocab_freq = {}
nDocuments = 0

# JSON containing Frequency of each word
json_data = open("apidata/vocab_freq.json")

vocab_freq = json.load(json_data)

count_read = open("apidata/count.txt", "r")

# Total Number of comments collected
nDocuments = int(count_read.read())

# List of Personal Words from LIWC dictionary
with open("apidata/personal.txt") as f:
    personal_words = f.read().splitlines()

parser = SafeConfigParser()
parser.read('apidata/database.ini')

user = parser.get('credentials', 'user')
password = parser.get('credentials', 'password')
host = parser.get('credentials', 'host')
database = parser.get('credentials', 'database')

def NormalizeVector(vector):
    length = ComputeVectorLength(vector)
    for (k,v) in vector.items():
        if length > 0:
            vector[k] = v / length
    return vector

def ComputeVectorLength(vector):
    length = 0;
    for d in vector.values():
        length += d * d
    length = math.sqrt(length)
    return length

 # Assuming that both vectors are normalized
def ComputeCosineSimilarity(v1, v2):
	dotproduct = 0
	for (key1,val1) in v1.items():
		if key1 in v2:
			dotproduct += val1 * v2[key1]
	return dotproduct;

def escape_string(string):
    res = string
    res = res.replace('\\','\\\\')
    res = res.replace('\n','\\n')
    res = res.replace('\r','\\r')
    res = res.replace('\047','\134\047') # single quotes
    res = res.replace('\042','\134\042') # double quotes
    res = res.replace('\032','\134\032') # for Win32
    return res

def error_name():
    exc_type, exc_obj, exc_tb = sys.exc_info()
    msg = str(exc_type)
    error = re.split(r'[.]',msg)
    error = re.findall(r'\w+',error[1])
    error_msg = str(error[0])
    return error_msg

def ComputeCommentArticleRelevance(comment_text,ID,operation):

    cnx = mysql.connector.connect(user=user, password=password, host=host, database=database)
    cursor = cnx.cursor()

    if operation == 'add':
        articleID = ID
        cursor.execute("select full_text from articles where articleID = '" + str(articleID) + "'")
        article_data = cursor.fetchall()
    elif operation == 'update':
        commentID = ID
        cursor.execute("select articleID from comments where commentID ='"+ str(commentID) +"' ")
        fetch_data = cursor.fetchall()
        if len(fetch_data) > 0:
            articleID = fetch_data[0][0]
        else:
            ArticleRelevance = 0.0
            return ArticleRelevance
        cursor.execute("select full_text from articles where articleID = '" + str(articleID) + "'")
        article_data = cursor.fetchall()
    else:
        ArticleRelevance = 0.0
        return ArticleRelevance
    cnx.close

    if len(article_data) < 1:
        ArticleRelevance = 0.0
        return ArticleRelevance
    for data in article_data:
        article_text = data[0]

    comment_text = escape_string(comment_text.strip())

    # clean and tokenize the comment text and article text, also exclude the stopwords
    token_list = CleanAndTokenize(comment_text)
    token_list = [word for word in token_list if word not in stopword_list]
    comment_stemmed_tokens = [porter.stem(token) for token in token_list]
    comment_stemmed_tokens_fd  = FreqDist(comment_stemmed_tokens)
    token_list = CleanAndTokenize(article_text)
    token_list = [word for word in token_list if word not in stopword_list]
    article_stemmed_tokens = [porter.stem(token) for token in token_list]
    article_stemmed_tokens_fd  = FreqDist(article_stemmed_tokens)

    # now create the feature vectors for article and comment
    article_features = {}
    comment_features = {}

    # Calculate weight for each word in the comment with tf-idf
    for w in vocab_freq:
            df = vocab_freq[w]
            log_fraction = (nDocuments / df)
            if log_fraction < 1:
                log_fraction = Decimal(nDocuments) / Decimal(df)
            if w in article_stemmed_tokens:
                 article_features[w] = article_stemmed_tokens_fd[w] * math.log(log_fraction)
            else:
                 article_features[w] = 0.0
            if w in comment_stemmed_tokens:
                 comment_features[w] = comment_stemmed_tokens_fd[w] * math.log(log_fraction)
            else:
                 comment_features[w] = 0.0

    # normalize vectors
    article_features = NormalizeVector(article_features)
    comment_features = NormalizeVector(comment_features)
    comment_article_similarity = ComputeCosineSimilarity (article_features, comment_features)
    return comment_article_similarity


def ComputeCommentConversationalRelevance(comment_text,ID,operation):

    cnx = mysql.connector.connect(user=user, password=password, host=host, database=database)
    cursor = cnx.cursor()

    if operation == 'add':
        articleID = ID
        cursor.execute("select commentBody from comments where articleID = '" + str(articleID) + "' ")
        comment_data = cursor.fetchall()
    elif operation == 'update':
        commentID = ID
        cursor.execute("select articleID from comments where commentID ='"+ str(commentID) +"' ")
        fetch_data = cursor.fetchall()
        if len(fetch_data) > 0:
            articleID = fetch_data[0][0]
        else:
            ConversationalRelevance = 0.0
            return ConversationalRelevance
        cursor.execute("select commentBody from comments "
                       "where articleID = '"+ str(articleID) +"' and commentID < '"+ str(commentID) +"' ")
        comment_data = cursor.fetchall()
    else:
        ConversationalRelevance = 0.0
        return ConversationalRelevance
    cnx.close
    if len(comment_data) < 10:
        ConversationalRelevance = 0.0
        return ConversationalRelevance

    centroid_comment_stemmed_tokens = []
    centroid_comment_features = {}

    # clean and tokenize the all the comments text and also exclude the stopwords
    comment_list = list(zip(*comment_data)[0])
    for comment in comment_list:
                token_list = CleanAndTokenize(comment)
                token_list = [word for word in token_list if word not in stopword_list]
                # Update and compute the centroid
                centroid_comment_stemmed_tokens.extend([porter.stem(token) for token in token_list])
    centroid_comment_stemmed_tokens_fd = FreqDist(centroid_comment_stemmed_tokens)

    # Calculate weight for each word in all the comments with tf-idf
    for w in vocab_freq:
                log_fraction = (nDocuments / vocab_freq[w])
                if log_fraction < 1:
                    log_fraction = Decimal(nDocuments) / Decimal(vocab_freq[w])
                if w in centroid_comment_stemmed_tokens:
                    centroid_comment_features[w] = centroid_comment_stemmed_tokens_fd[w] * math.log(log_fraction)
                else:
                    centroid_comment_features[w] = 0.0

    # normalize vector
    centroid_comment_features = NormalizeVector(centroid_comment_features)

    # Now compute distance to  comment
    comment_stemmed_tokens = []
    comment_features = {}
    comment_text = escape_string(comment_text.strip())
    token_list = CleanAndTokenize(comment_text)
    token_list = [word for word in token_list if word not in stopword_list]
    comment_stemmed_tokens.extend([porter.stem(token) for token in token_list])
    comment_stemmed_tokens_fd  = FreqDist(comment_stemmed_tokens)
    # Calculate weight for each word in the comment with tf-idf
    for w in vocab_freq:
                log_fraction = (nDocuments / vocab_freq[w])
                if log_fraction < 1:
                    log_fraction = Decimal(nDocuments) / Decimal(vocab_freq[w])
                if w in comment_stemmed_tokens:
                    comment_features[w] = comment_stemmed_tokens_fd[w] * math.log(log_fraction)
                else:
                    comment_features[w] = 0.0
    comment_features = NormalizeVector(comment_features)
    comment_originality = ComputeCosineSimilarity (centroid_comment_features, comment_features)
    return comment_originality

def calcPersonalXPScores(comment_text):

    tokenizer = WhitespaceTokenizer()
    personal_xp_score = 0
    text = comment_text.lower()

    #filter out punctuations
    punctuations = string.punctuation # includes following characters: !"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~
    excluded_punctuations = ["$", "%", "'"]
    for p in punctuations:
        if p not in excluded_punctuations:
            text = text.replace(p, " ")

    # tokenize it
    text_tokens = tokenizer.tokenize(text)

    # if the tokens are in the personal_words List then increment score
    for tok in text_tokens:
        tok_stem = porter.stem(tok)
        if tok_stem in personal_words:
            personal_xp_score = personal_xp_score + 1

    # normalize by number of tokens
    personal_xp_score = float(personal_xp_score) / float(len(text_tokens))

    return personal_xp_score

def calcReadability(comment_text):

    textstat = TextStatistics("")
    text = comment_text.lower()

    #filter out punctuations
    punctuations = string.punctuation # includes following characters: !"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~
    excluded_punctuations = ["$", "%", "'"]
    for p in punctuations:
        if p not in excluded_punctuations:
            text = text.replace(p, " ")

    readability_score = textstat.smog_index(text=text)
    return readability_score

def updateComment(comment_text,commentID):
    operation = "update"
    ArticleRelevance = ComputeCommentArticleRelevance(comment_text,commentID,operation)
    ConversationalRelevance = ComputeCommentConversationalRelevance(comment_text,commentID,operation)
    PersonalXP = calcPersonalXPScores(comment_text)
    Readability = calcReadability(comment_text)
    return (ArticleRelevance,ConversationalRelevance,PersonalXP,Readability)

def addComment(comment_text,articleID):
    operation = "add"
    ArticleRelevance = ComputeCommentArticleRelevance(comment_text,articleID,operation)
    ConversationalRelevance = ComputeCommentConversationalRelevance(comment_text,articleID,operation)
    PersonalXP = calcPersonalXPScores(comment_text)
    Readability = calcReadability(comment_text)
    return (ArticleRelevance,ConversationalRelevance,PersonalXP,Readability)



__author__ = 'ssachar'

from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, jsonify
import time
from bs4 import BeautifulSoup
import calculate_score
import mysql.connector
import json
from mysql.connector.errors import Error
import re
import sys

app = Flask(__name__)
app.debug = True

cnx = mysql.connector.connect(user='your user ID', password='Your Password',
                               host='hostname like 127.0.0.1',
                               database='Name of the database')

cursor = cnx.cursor()

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

@app.route('/commentIQ/v1/addArticle_Cname', methods=['GET', 'POST'])
def addArticle_Cname():
    if request.method == 'POST':
        try:
            current_time = time.strftime("%Y-%m-%d %I:%M:%S")
            data = request.data
            dataDict = json.loads(data)
            article_text = escape_string(dataDict['article_text'].strip())
            insert_query = "INSERT INTO cname_articles (pubDate, full_text)" \
                                        " VALUES('%s', '%s')" % \
                                        (current_time, article_text)
            cursor.execute(insert_query)
            Cname_articleID = cursor.lastrowid
            rowsaffected = cursor.rowcount
            if rowsaffected == 1:
                status = "Insert Successful"
            else:
                status = "Insert failed"
        except:
            Cname_articleID = None
            status = error_name()
    else:
        Cname_articleID = None
        status = "Operation failed - use Post method"

    return jsonify(Cname_articleID = Cname_articleID,status = status)

@app.route('/commentIQ/v1/updateArticle_Cname', methods=['GET', 'POST'])
def updateArticle_Cname():
    if request.method == 'POST':
        try:
            data = request.data
            dataDict = json.loads(data)
            articleID = dataDict['articleID']
            article_text = escape_string(dataDict['article_text'].strip())
            update = "update cname_comments set full_text = '"+ article_text +"', " \
                     " where articleID = '"+ str(articleID) +"' "
            cursor.execute(update)
            rowsaffected = cursor.rowcount
            if rowsaffected == 1:
                status = "Update Successful"
            else:
                status = "No update performed"
        except:
            status = error_name()

@app.route('/commentIQ/v1/addComment_Cname', methods=['GET', 'POST'])
def addComment_Cname():
    if request.method == 'POST':
        try:
            data = request.data
            dataDict = json.loads(data)
            articleID = dataDict['articleID']
            commentBody = escape_string(dataDict['commentBody'].strip())
            current_time = time.strftime("%Y-%m-%d %I:%M:%S")
            cursor.execute("select count(*) from cname_articles where articleID = '"+ str(articleID) +"' ")
            count = cursor.fetchall()[0][0]
            if count < 1 :
                return jsonify(ArticleRelevance = 0.0, ConversationalRelevance = 0.0 , PersonalXP = 0.0 , \
                               Readability = 0.0, Cname_CommentID = None ,status = "Operation failed")
            else:
                ArticleRelevance, ConversationalRelevance, PersonalXP, Readability = \
                calculate_score.addComment(commentBody,articleID)
                insert_query = "INSERT INTO cname_comments (commentBody, approveDate, articleID,ArticleRelevance," \
                               "ConversationalRelevance, PersonalXP, Readability) " \
                               "VALUES ('%s','%s','%s','%s','%s','%s','%s')" % \
                               (commentBody,current_time,articleID,str(ArticleRelevance),str(ConversationalRelevance) \
                               ,str(PersonalXP),str(Readability))
                cursor.execute(insert_query)
                Cname_CommentID = cursor.lastrowid
    #           cnx.commit()
                rowsaffected = cursor.rowcount
                if rowsaffected == 1:
                    status = "Insert Successful"
                else:
                    status = "Insert failed"
        except:
            ArticleRelevance = 0.0
            ConversationalRelevance = 0.0
            PersonalXP = 0.0
            Readability = 0.0
            status = error_name()
            Cname_CommentID = None
    else:
        ArticleRelevance = 0.0
        ConversationalRelevance = 0.0
        PersonalXP = 0.0
        Readability = 0.0
        Cname_CommentID = None
        status = "Operation failed - use Post method"

    return jsonify(ArticleRelevance = ArticleRelevance, ConversationalRelevance = ConversationalRelevance, \
                   PersonalXP = PersonalXP, Readability = Readability, Cname_CommentID = Cname_CommentID,status=status)

@app.route('/commentIQ/v1/updateComment_Cname', methods=['GET', 'POST'])
def updateComment_Cname():
    if request.method == 'POST':
        try:
            data = request.data
            dataDict = json.loads(data)
            commentID = dataDict['commentID']
            commentBody = escape_string(dataDict['commentBody'].strip())

            ArticleRelevance, ConversationalRelevance, PersonalXP, Readability  = \
            calculate_score.updateComment(commentBody,commentID)

            update = "update cname_comments set ArticleRelevance = '"+ str(ArticleRelevance) +"', " \
                     "ConversationalRelevance = '"+ str(ConversationalRelevance) +"' , " \
                     "PersonalXP = '"+ str(PersonalXP) +"', Readability = '"+ str(Readability) +"'," \
                     "CommentBody = '" + commentBody + "' where commentID = '"+ str(commentID) +"' "
            cursor.execute(update)
            rowsaffected = cursor.rowcount
            if rowsaffected == 1:
                status = "Update Successful"
            else:
                status = "No update performed"
        except:
            ArticleRelevance = 0.0
            ConversationalRelevance = 0.0
            PersonalXP = 0.0
            Readability = 0.0
            status = error_name()
    else:
        ArticleRelevance = 0.0
        ConversationalRelevance = 0.0
        PersonalXP = 0.0
        Readability = 0.0
        status = "Operation failed - use Post method"

    return jsonify(ArticleRelevance = ArticleRelevance, ConversationalRelevance = ConversationalRelevance, \
                   PersonalXP = PersonalXP, Readability = Readability, status = status)

@app.route('/commentIQ/v1/deleteComment_Cname/<commentID>',methods=['GET'])
def deleteComment_Cname(commentID):
    try:
        if isinstance(commentID, int):
            commentID = str(commentID)
        commentID = commentID.replace("'", '')
        commentID = commentID.replace('"', '')
        delete = "delete from cname_comments where commentID = '"+ commentID +"'"
        cursor.execute(delete)
        rowsaffected = cursor.rowcount
        if rowsaffected == 1:
            status = "success"
        else:
            status = "operation failed"
    except:
        status = error_name()
    return jsonify(status = status)

@app.route('/commentIQ/v1/getArticleRelevance_Cname/<commentID>',methods=['GET'])
def getArticleRelevance_Cname(commentID):
    try:
        if isinstance(commentID, int):
            commentID = str(commentID)
        commentID = commentID.replace("'", '')
        commentID = commentID.replace('"', '')
        cursor.execute("select ArticleRelevance from cname_comments where commentID = '" + commentID + "' ")
        scores = cursor.fetchall()
        rowsaffected = cursor.rowcount
        if rowsaffected == 1:
            status = "success"
            ArticleRelevance = scores[0][0]
        else:
            status = "operation failed"
            ArticleRelevance = 0.0
    except:
        ArticleRelevance = 0.0
        status = error_name()
    return jsonify(ArticleRelevance = ArticleRelevance, status = status)

@app.route('/commentIQ/v1/getConversationalRelevance_Cname/<commentID>',methods=['GET'])
def getConversationalRelevance_Cname(commentID):
    try:
        if isinstance(commentID, int):
            commentID = str(commentID)
        commentID = commentID.replace("'", '')
        commentID = commentID.replace('"', '')
        cursor.execute("select ConversationalRelevance from cname_comments where commentID = '" + commentID + "' ")
        scores = cursor.fetchall()
        rowsaffected = cursor.rowcount
        if rowsaffected == 1:
            status = "success"
            ConversationalRelevance = scores[0][0]
        else:
            status = "operation failed"
            ConversationalRelevance = 0.0
    except:
        status = error_name()
        ConversationalRelevance = 0.0
    return jsonify(ConversationalRelevance = ConversationalRelevance, status = status)

@app.route('/commentIQ/v1/getPersonalXP_Cname/<commentID>',methods=['GET'])
def getPersonalXP_Cname(commentID):
    try:
        if isinstance(commentID, int):
            commentID = str(commentID)
        commentID = commentID.replace("'", '')
        commentID = commentID.replace('"', '')
        cursor.execute("select PersonalXP from cname_comments where commentID = '" + commentID + "' ")
        scores = cursor.fetchall()
        rowsaffected = cursor.rowcount
        if rowsaffected == 1:
            status = "success"
            PersonalXP = scores[0][0]
        else:
            status = "operation failed"
            PersonalXP = 0.0
    except:
        PersonalXP = 0.0
        status = error_name()
    return jsonify(PersonalXP = PersonalXP, status = status)

@app.route('/commentIQ/v1/getReadability_Cname/<commentID>',methods=['GET'])
def getReadability_Cname(commentID):
    try:
        if isinstance(commentID, int):
            commentID = str(commentID)
        commentID = commentID.replace("'", '')
        commentID = commentID.replace('"', '')
        cursor.execute("select Readability from cname_comments where commentID = '" + commentID + "' ")
        scores = cursor.fetchall()
        rowsaffected = cursor.rowcount
        if rowsaffected == 1:
            status = "success"
            Readability = scores[0][0]
        else:
            status = "operation failed"
            Readability = 0.0
    except:
        Readability = 0.0
        status = error_name()
    return jsonify(Readability = Readability, status = status)


@app.route('/commentIQ/v1/getScores_Cname/<commentID>',methods=['GET'])
def getScores_Cname(commentID):
    try:
        if isinstance(commentID, int):
            commentID = str(commentID)
        commentID = commentID.replace("'", '')
        commentID = commentID.replace('"', '')
        cursor.execute("select ArticleRelevance,ConversationalRelevance,PersonalXP,Readability from cname_comments " \
                       "where commentID = '" + commentID + "' ")
        scores = cursor.fetchall()
        rowsaffected = cursor.rowcount
        if rowsaffected == 1:
            status = "success"
            ArticleRelevance = scores[0][0]
            ConversationalRelevance = scores[0][1]
            PersonalXP = scores[0][2]
            Readability = scores[0][3]
        else:
            status = "operation failed"
            ArticleRelevance = 0.0
            ConversationalRelevance = 0.0
            PersonalXP = 0.0
            Readability = 0.0
    except:
        status = error_name()
        ArticleRelevance = 0.0
        ConversationalRelevance = 0.0
        PersonalXP = 0.0
        Readability = 0.0
    return jsonify(ArticleRelevance = ArticleRelevance, ConversationalRelevance = ConversationalRelevance, \
                   PersonalXP = PersonalXP, Readability = Readability, status = status)


if __name__ == '__main__':
    app.run()


__author__ = 'ssachar'

from flask import Flask, request, jsonify
import time
import mysql.connector
import json
from mysql.connector.errors import Error
from calculate_score import error_name, escape_string, addComment, updateComment
from ConfigParser import SafeConfigParser

app = Flask(__name__)
app.debug = True

# Get the config file for database
parser = SafeConfigParser()
# Edit the config file to fill in your credentials
parser.read('apidata/database.ini')

# Fetch the credentials from config file
user = parser.get('credentials', 'user')
password = parser.get('credentials', 'password')
host = parser.get('credentials', 'host')
database = parser.get('credentials', 'database')

cnx = mysql.connector.connect(user=user, password=password, host=host, database=database)
cursor = cnx.cursor()

#Add the article Text and return the ArticleID
@app.route('/commentIQ/v1/addArticle', methods=['GET', 'POST'])
def addArticle():
    if request.method == 'POST':
        try:
            current_time = time.strftime("%Y-%m-%d %I:%M:%S")
            data = request.data
            dataDict = json.loads(data)
            article_text = escape_string(dataDict['article_text'].strip())
            insert_query = "INSERT INTO articles (pubDate, full_text)" \
                                        " VALUES('%s', '%s')" % \
                                        (current_time, article_text)
            cursor.execute(insert_query)
            articleID = cursor.lastrowid
            rowsaffected = cursor.rowcount
            if rowsaffected == 1:
                status = "Insert Successful"
            else:
                status = "Insert failed"
        except:
            articleID = None
            status = error_name()
    else:
        articleID = None
        status = "Operation failed - use Post method"

    return jsonify(articleID = articleID,status = status)

#Update the article Text
@app.route('/commentIQ/v1/updateArticle', methods=['GET', 'POST'])
def updateArticle():
    if request.method == 'POST':
        try:
            data = request.data
            dataDict = json.loads(data)
            articleID = dataDict['articleID']
            article_text = escape_string(dataDict['article_text'].strip())
            update = "update articles set full_text = '"+ article_text +"' " \
                     " where articleID = '"+ str(articleID) +"' "
            cursor.execute(update)
            rowsaffected = cursor.rowcount
            if rowsaffected == 1:
                status = "Update Successful"
            else:
                status = "No update performed"
        except:
            status = error_name()
    return jsonify(status = status)

# Add the comment Text and return all the scores
@app.route('/commentIQ/v1/addComment', methods=['GET', 'POST'])
def AddComment():
    if request.method == 'POST':
        try:
            data = request.data
            dataDict = json.loads(data)
            articleID = dataDict['articleID']
            commentBody = escape_string(dataDict['commentBody'].strip())
            current_time = time.strftime("%Y-%m-%d %I:%M:%S")
            cursor.execute("select count(*) from articles where articleID = '"+ str(articleID) +"' ")
            count = cursor.fetchall()[0][0]
            if count < 1 :
                return jsonify(ArticleRelevance = 0.0, ConversationalRelevance = 0.0 , PersonalXP = 0.0 , \
                               Readability = 0.0, CommentID = None ,status = "Operation failed")
            else:
                # Call addComment() function of subroutine - calculate_score to calculate all the scores
                ArticleRelevance, ConversationalRelevance, PersonalXP, Readability = \
                addComment(commentBody,articleID)
                insert_query = "INSERT INTO comments (commentBody, approveDate, articleID,ArticleRelevance," \
                               "ConversationalRelevance, PersonalXP, Readability) " \
                               "VALUES ('%s','%s','%s','%s','%s','%s','%s')" % \
                               (commentBody,current_time,articleID,str(ArticleRelevance),str(ConversationalRelevance) \
                               ,str(PersonalXP),str(Readability))
                cursor.execute(insert_query)
                CommentID = cursor.lastrowid
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
            CommentID = None
    else:
        ArticleRelevance = 0.0
        ConversationalRelevance = 0.0
        PersonalXP = 0.0
        Readability = 0.0
        CommentID = None
        status = "Operation failed - use Post method"

    return jsonify(ArticleRelevance = ArticleRelevance, ConversationalRelevance = ConversationalRelevance, \
                   PersonalXP = PersonalXP, Readability = Readability, CommentID = CommentID,status=status)

#Update the comment Text and return the updated scores
@app.route('/commentIQ/v1/updateComment', methods=['GET', 'POST'])
def UpdateComments():
    if request.method == 'POST':
        try:
            data = request.data
            dataDict = json.loads(data)
            commentID = dataDict['commentID']
            commentBody = escape_string(dataDict['commentBody'].strip())

            # Call updateComment() function of subroutine - calculate_score to re-calculate all the scores
            ArticleRelevance, ConversationalRelevance, PersonalXP, Readability  = \
            updateComment(commentBody,commentID)

            update = "update comments set ArticleRelevance = '"+ str(ArticleRelevance) +"', " \
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

#Delete the comment from the database
@app.route('/commentIQ/v1/deleteComment/<commentID>',methods=['GET'])
def deleteComment(commentID):
    try:
        if isinstance(commentID, int):
            commentID = str(commentID)
        commentID = commentID.replace("'", '')
        commentID = commentID.replace('"', '')
        delete = "delete from comments where commentID = '"+ commentID +"'"
        cursor.execute(delete)
        rowsaffected = cursor.rowcount
        if rowsaffected == 1:
            status = "success"
        else:
            status = "operation failed"
    except:
        status = error_name()
    return jsonify(status = status)

# Return the Score of ArticleRelevance for the comment
@app.route('/commentIQ/v1/getArticleRelevance/<commentID>',methods=['GET'])
def getArticleRelevance(commentID):
    try:
        if isinstance(commentID, int):
            commentID = str(commentID)
        commentID = commentID.replace("'", '')
        commentID = commentID.replace('"', '')
        cursor.execute("select ArticleRelevance from comments where commentID = '" + commentID + "' ")
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

# Return the Score of ConversationalRelevance for the comment
@app.route('/commentIQ/v1/getConversationalRelevance/<commentID>',methods=['GET'])
def getConversationalRelevance(commentID):
    try:
        if isinstance(commentID, int):
            commentID = str(commentID)
        commentID = commentID.replace("'", '')
        commentID = commentID.replace('"', '')
        cursor.execute("select ConversationalRelevance from comments where commentID = '" + commentID + "' ")
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

# Return the Score of Personal Experience for the comment
@app.route('/commentIQ/v1/getPersonalXP/<commentID>',methods=['GET'])
def getPersonalXP(commentID):
    try:
        if isinstance(commentID, int):
            commentID = str(commentID)
        commentID = commentID.replace("'", '')
        commentID = commentID.replace('"', '')
        cursor.execute("select PersonalXP from comments where commentID = '" + commentID + "' ")
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

# Return the Score of Readability for the comment
@app.route('/commentIQ/v1/getReadability/<commentID>',methods=['GET'])
def getReadability(commentID):
    try:
        if isinstance(commentID, int):
            commentID = str(commentID)
        commentID = commentID.replace("'", '')
        commentID = commentID.replace('"', '')
        cursor.execute("select Readability from comments where commentID = '" + commentID + "' ")
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

# Return all the scores for the comment
@app.route('/commentIQ/v1/getScores/<commentID>',methods=['GET'])
def getScores(commentID):
    try:
        if isinstance(commentID, int):
            commentID = str(commentID)
        commentID = commentID.replace("'", '')
        commentID = commentID.replace('"', '')
        cursor.execute("select ArticleRelevance,ConversationalRelevance,PersonalXP,Readability from comments " \
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


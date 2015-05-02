__author__ = 'ssachar'

# This is python-flask api code to send scores as response for the desired operations
# The response keys and values depends upon the end points requested
# subroutine used - calculate_score.py

from flask import Flask, request, jsonify, make_response
import time
import datetime
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


#Add the article Text and return the ArticleID
@app.route('/commentIQ/v1/addArticle', methods=['GET', 'POST', 'DELETE'])
def addArticle():
    if request.method == 'POST':
        try:
            current_time = time.strftime("%Y-%m-%d %I:%M:%S")
            data = request.data
            dataDict = json.loads(data)
            article_text = escape_string(dataDict['article_text'].strip())

            cnx = mysql.connector.connect(user=user, password=password, host=host, database=database)
            cursor = cnx.cursor()

            insert_query = "INSERT INTO articles (pubDate, full_text)" \
                                        " VALUES('%s', '%s')" % \
                                        (current_time, article_text)
            cursor.execute(insert_query)
            articleID = cursor.lastrowid
            rowsaffected = cursor.rowcount
            cnx.commit()
            cnx.close

            if rowsaffected == 1:
                status = "Add Successful"
            else:
                status = "Add failed"
        except:
            articleID = None
            status = error_name()
    else:
        articleID = None
        status = "Operation failed - use HTTP POST method"

    return jsonify(articleID = articleID,status = status)

#Update the article Text
@app.route('/commentIQ/v1/updateArticle', methods=['GET', 'POST', 'DELETE'])
def updateArticle():
    if request.method == 'POST':
        try:
            data = request.data
            dataDict = json.loads(data)
            articleID = dataDict['articleID']
            article_text = escape_string(dataDict['article_text'].strip())

            cnx = mysql.connector.connect(user=user, password=password, host=host, database=database)
            cursor = cnx.cursor()

            update = "update articles set full_text = '"+ article_text +"' " \
                     " where articleID = '"+ str(articleID) +"' "
            cursor.execute(update)
            rowsaffected = cursor.rowcount
            cnx.commit()
            cnx.close

            if rowsaffected == 1:
                status = "Update Successful"
            else:
                status = "Update failed"
        except:
            status = error_name()
    else:
        status = "Operation failed - use HTTP POST method"
    return jsonify(status = status)

# Add the comment Text and return all the scores
@app.route('/commentIQ/v1/addComment', methods=['GET', 'POST', 'DELETE'])
def AddComment():
    if request.method == 'POST':
        try:
            data = request.data
            dataDict = json.loads(data)
            articleID = dataDict['articleID']
            commentBody = escape_string(dataDict['commentBody'].strip())
            current_time = time.strftime("%Y-%m-%d %H:%M:%S")

            if 'commentDate' in dataDict:
                commentDate = dataDict['commentDate']
                try:
                    datetime.datetime.strptime(commentDate, '%Y-%m-%d %H:%M:%S')
                except:
                    err_msg =  "Incorrect date format, Correct format should be YYYY-MM-DD H:M:S"
                    return jsonify(ArticleRelevance = 0.0, ConversationalRelevance = 0.0 , PersonalXP = 0.0 , \
                               Readability = 0.0, Length = 0.0,commentID = None ,status = err_msg)
            else:
                commentDate = ""

            if 'recommendationCount' in dataDict:
                recommendationCount = int(dataDict['recommendationCount'])
            else:
                recommendationCount = 0

            if 'username' in dataDict:
                username = dataDict['username']
            else:
                username = ""

            if 'location' in dataDict:
                location = dataDict['location']
            else:
                location = ""

            cnx = mysql.connector.connect(user=user, password=password, host=host, database=database)
            cursor = cnx.cursor()

            cursor.execute("select count(*) from articles where articleID = '"+ str(articleID) +"' ")
            count = cursor.fetchall()[0][0]
            if count < 1 :
                return jsonify(ArticleRelevance = 0.0, ConversationalRelevance = 0.0 , PersonalXP = 0.0 , \
                               Readability = 0.0, Length = 0.0,commentID = None ,status = "Operation failed")
            else:
                # Call addComment() function of subroutine - calculate_score to calculate all the scores
                ArticleRelevance, ConversationalRelevance, PersonalXP, Readability, Length = \
                addComment(commentBody,articleID)
                insert_query = "INSERT INTO comments (commentBody, creationDate, articleID," \
                               "commentDate,recommendationCount,username,location," \
                               "ArticleRelevance,ConversationalRelevance, PersonalXP, Readability, CommentLength)" \
                               "VALUES ('%s','%s','%s','%s','%d','%s','%s','%s','%s','%s','%s','%s')" % \
                               (commentBody,current_time,articleID,commentDate,recommendationCount,username,location, \
                                str(ArticleRelevance),str(ConversationalRelevance),str(PersonalXP),str(Readability),str(Length))
                cursor.execute(insert_query)
                CommentID = cursor.lastrowid
                cnx.commit()
                rowsaffected = cursor.rowcount
                cnx.close
                if rowsaffected == 1:
                    status = "Add Successful"
                else:
                    status = "Add failed"

        except:
            ArticleRelevance = 0.0
            ConversationalRelevance = 0.0
            PersonalXP = 0.0
            Readability = 0.0
            Length = 0.0
            status = error_name()
            CommentID = None
    else:
        ArticleRelevance = 0.0
        ConversationalRelevance = 0.0
        PersonalXP = 0.0
        Readability = 0.0
        Length = 0.0
        CommentID = None
        status = "Add operation failed - use HTTP POST method"

    return jsonify(ArticleRelevance = ArticleRelevance, ConversationalRelevance = ConversationalRelevance, \
                   PersonalXP = PersonalXP, Readability = Readability, Length = Length,  \
                   commentID = CommentID,status=status)

#Update the comment Text and return the updated scores
@app.route('/commentIQ/v1/updateComment', methods=['GET', 'POST', 'DELETE'])
def UpdateComments():
    if request.method == 'POST':
        try:
            data = request.data
            dataDict = json.loads(data)
            commentID = dataDict['commentID']

            cnx = mysql.connector.connect(user=user, password=password, host=host, database=database)
            cursor = cnx.cursor()

            cursor.execute("select commentDate,recommendationCount,username,location from comments where commentID = '"+ str(commentID) +"'")

            for row in cursor:
                commentDate = row[0]
                recommendationCount = row[1]
                username = row[2]
                location = row[3]

            commentBody = escape_string(dataDict['commentBody'].strip())

            if 'commentDate' in dataDict:
                commentDate = dataDict['commentDate']
                try:
                    datetime.datetime.strptime(commentDate, '%Y-%m-%d %H:%M:%S')
                except:
                    err_msg =  "Incorrect date format, Correct format should be YYYY-MM-DD H:M:S"
                    return jsonify(ArticleRelevance = 0.0, ConversationalRelevance = 0.0 , PersonalXP = 0.0 , \
                               Readability = 0.0, Length = 0.0 ,status = err_msg)

            if 'recommendationCount' in dataDict:
                recommendationCount = dataDict['recommendationCount']

            if 'username' in dataDict:
                username = dataDict['username']

            if 'location' in dataDict:
                location = dataDict['location']

            # Call updateComment() function of subroutine - calculate_score to re-calculate all the scores
            ArticleRelevance, ConversationalRelevance, PersonalXP, Readability, Length  = \
            updateComment(commentBody,commentID)

            update = "update comments set ArticleRelevance = '"+ str(ArticleRelevance) +"', " \
                     "ConversationalRelevance = '"+ str(ConversationalRelevance) +"' , " \
                     "PersonalXP = '"+ str(PersonalXP) +"', Readability = '"+ str(Readability) +"'," \
                     "CommentLength = '"+ str(Length) +"', CommentBody = '" + commentBody + "' ," \
                     "commentDate = '"+ str(commentDate) +"', recommendationCount = '" + str(recommendationCount) + "', " \
                     "username = '"+ str(username) +"', location = '" + str(location) + "' " \
                     " where commentID = '"+ str(commentID) +"' "
            cursor.execute(update)
            rowsaffected = cursor.rowcount
            cnx.commit()
            cnx.close

            if rowsaffected == 1:
                status = "Update Successful"
            else:
                status = "No update performed"
        except:
            ArticleRelevance = 0.0
            ConversationalRelevance = 0.0
            PersonalXP = 0.0
            Readability = 0.0
            Length = 0.0
            status = error_name()
    else:
        ArticleRelevance = 0.0
        ConversationalRelevance = 0.0
        PersonalXP = 0.0
        Readability = 0.0
        Length = 0.0
        status = "Update Operation failed - use HTTP POST method"

    return jsonify(ArticleRelevance = ArticleRelevance, ConversationalRelevance = ConversationalRelevance, \
                   PersonalXP = PersonalXP, Readability = Readability, Length = Length, status = status)

#Delete the comment from the database
@app.route('/commentIQ/v1/deleteComment/<commentID>',methods=['GET', 'POST', 'DELETE'])
def deleteComment(commentID):
    if request.method == 'DELETE':
        try:
            if isinstance(commentID, int):
                commentID = str(commentID)
            commentID = commentID.replace("'", '')
            commentID = commentID.replace('"', '')

            cnx = mysql.connector.connect(user=user, password=password, host=host, database=database)
            cursor = cnx.cursor()

            delete = "delete from comments where commentID = '"+ commentID +"'"
            cursor.execute(delete)
            rowsaffected = cursor.rowcount

            cnx.commit()
            cnx.close

            if rowsaffected == 1:
                status = "Delete successful"
            else:
                status = "Delete failed"
        except:
            status = error_name()
    else:
        status = "Operation failed - Use HTTP DELETE method"
    return jsonify(status = status)

# Return the Score of ArticleRelevance for the comment
@app.route('/commentIQ/v1/getArticleRelevance/<commentID>',methods=['GET', 'POST', 'DELETE'])
def getArticleRelevance(commentID):
    if request.method == 'GET':
        try:
            if isinstance(commentID, int):
                commentID = str(commentID)
            commentID = commentID.replace("'", '')
            commentID = commentID.replace('"', '')

            cnx = mysql.connector.connect(user=user, password=password, host=host, database=database)
            cursor = cnx.cursor()

            cursor.execute("select ArticleRelevance from comments where commentID = '" + commentID + "' ")
            scores = cursor.fetchall()
            rowsaffected = cursor.rowcount

            cnx.close

            if rowsaffected == 1:
                status = "success"
                ArticleRelevance = scores[0][0]
            else:
                status = "operation failed"
                ArticleRelevance = 0.0
        except:
            ArticleRelevance = 0.0
            status = error_name()
    else:
        ArticleRelevance = 0.0
        status = "Operation failed - Use HTTP GET method"
    return jsonify(ArticleRelevance = ArticleRelevance, status = status)

# Return the Score of ConversationalRelevance for the comment
@app.route('/commentIQ/v1/getConversationalRelevance/<commentID>',methods=['GET', 'POST', 'DELETE'])
def getConversationalRelevance(commentID):
    if request.method == 'GET':
        try:
            if isinstance(commentID, int):
                commentID = str(commentID)
            commentID = commentID.replace("'", '')
            commentID = commentID.replace('"', '')

            cnx = mysql.connector.connect(user=user, password=password, host=host, database=database)
            cursor = cnx.cursor()

            cursor.execute("select ConversationalRelevance from comments where commentID = '" + commentID + "' ")
            scores = cursor.fetchall()
            rowsaffected = cursor.rowcount

            cnx.close

            if rowsaffected == 1:
                status = "success"
                ConversationalRelevance = scores[0][0]
            else:
                status = "operation failed"
                ConversationalRelevance = 0.0
        except:
            status = error_name()
            ConversationalRelevance = 0.0
    else:
        ConversationalRelevance = 0.0
        status = "Operation failed - Use HTTP GET method"
    return jsonify(ConversationalRelevance = ConversationalRelevance, status = status)

# Return the Score of Personal Experience for the comment
@app.route('/commentIQ/v1/getPersonalXP/<commentID>',methods=['GET', 'POST', 'DELETE'])
def getPersonalXP(commentID):
    if request.method == 'GET':
        try:
            if isinstance(commentID, int):
                commentID = str(commentID)
            commentID = commentID.replace("'", '')
            commentID = commentID.replace('"', '')

            cnx = mysql.connector.connect(user=user, password=password, host=host, database=database)
            cursor = cnx.cursor()

            cursor.execute("select PersonalXP from comments where commentID = '" + commentID + "' ")
            scores = cursor.fetchall()
            rowsaffected = cursor.rowcount

            cnx.close

            if rowsaffected == 1:
                status = "success"
                PersonalXP = scores[0][0]
            else:
                status = "operation failed"
                PersonalXP = 0.0
        except:
            PersonalXP = 0.0
            status = error_name()
    else:
        PersonalXP = 0.0
        status = "Operation failed - Use HTTP GET method"
    return jsonify(PersonalXP = PersonalXP, status = status)

# Return the Score of Readability for the comment
@app.route('/commentIQ/v1/getReadability/<commentID>',methods=['GET', 'POST', 'DELETE'])
def getReadability(commentID):
    if request.method == 'GET':
        try:
            if isinstance(commentID, int):
                commentID = str(commentID)
            commentID = commentID.replace("'", '')
            commentID = commentID.replace('"', '')

            cnx = mysql.connector.connect(user=user, password=password, host=host, database=database)
            cursor = cnx.cursor()

            cursor.execute("select Readability from comments where commentID = '" + commentID + "' ")
            scores = cursor.fetchall()
            rowsaffected = cursor.rowcount

            cnx.close

            if rowsaffected == 1:
                status = "success"
                Readability = scores[0][0]
            else:
                status = "operation failed"
                Readability = 0.0
        except:
            Readability = 0.0
            status = error_name()
    else:
        Readability = 0.0
        status = "Operation failed - Use HTTP GET method"
    return jsonify(Readability = Readability, status = status)

# Return the Score of Length for the comment
@app.route('/commentIQ/v1/getLength/<commentID>',methods=['GET', 'POST', 'DELETE'])
def getLength(commentID):
    if request.method == 'GET':
        try:
            if isinstance(commentID, int):
                commentID = str(commentID)
            commentID = commentID.replace("'", '')
            commentID = commentID.replace('"', '')

            cnx = mysql.connector.connect(user=user, password=password, host=host, database=database)
            cursor = cnx.cursor()

            cursor.execute("select CommentLength from comments where commentID = '" + commentID + "' ")
            scores = cursor.fetchall()
            rowsaffected = cursor.rowcount

            cnx.close

            if rowsaffected == 1:
                status = "success"
                Length = scores[0][0]
            else:
                status = "operation failed"
                Length = 0.0
        except:
            Length = 0.0
            status = error_name()
    else:
        Length = 0.0
        status = "Operation failed - Use HTTP GET method"
    return jsonify(Length = Length, status = status)


# Return all the scores for the comment
@app.route('/commentIQ/v1/getScores/<commentID>',methods=['GET', 'POST', 'DELETE'])
def getScores(commentID):
    if request.method == 'GET':
        try:
            if isinstance(commentID, int):
                commentID = str(commentID)
            commentID = commentID.replace("'", '')
            commentID = commentID.replace('"', '')

            cnx = mysql.connector.connect(user=user, password=password, host=host, database=database)
            cursor = cnx.cursor()

            cursor.execute("select ArticleRelevance,ConversationalRelevance,PersonalXP,Readability, CommentLength " \
                           "from comments where commentID = '" + commentID + "' ")
            scores = cursor.fetchall()
            rowsaffected = cursor.rowcount

            cnx.close

            if rowsaffected == 1:
                status = "success"
                ArticleRelevance = scores[0][0]
                ConversationalRelevance = scores[0][1]
                PersonalXP = scores[0][2]
                Readability = scores[0][3]
                Length = scores[0][4]
            else:
                status = "operation failed"
                ArticleRelevance = 0.0
                ConversationalRelevance = 0.0
                PersonalXP = 0.0
                Readability = 0.0
                Length = 0.0
        except:
            status = error_name()
            ArticleRelevance = 0.0
            ConversationalRelevance = 0.0
            PersonalXP = 0.0
            Readability = 0.0
            Length = 0.0
    else:
        ArticleRelevance = 0.0
        ConversationalRelevance = 0.0
        PersonalXP = 0.0
        Readability = 0.0
        Length = 0.0
        status = "Operation failed - Use HTTP GET method"
    return jsonify(ArticleRelevance = ArticleRelevance, ConversationalRelevance = ConversationalRelevance, \
                   PersonalXP = PersonalXP, Readability = Readability, Length = Length, status = status)

@app.route('/commentIQ/v1/getVocabulary',methods=['GET', 'POST', 'DELETE'])
def getVocab():
    vocab_json_data = open("apidata/vocab_freq.json")
    vocab_freq = json.load(vocab_json_data)
    response = make_response(jsonify(vocab_freq))
    response.headers["Content-Disposition"] = "attachment; filename=vocab_freq.json"
    return response

if __name__ == '__main__':
    app.run()


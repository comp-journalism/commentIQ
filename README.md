CommentIQ API
=========
Comment IQ API is a RESTful API used to evaluate the comment score on a news article and return the scores based on 4 criterias i.e Article Relevance, Conversational Relevance, Personal Experience and readability.      
(Get API code and get it running on your machine. Follow the instructions <a href="https://github.com/comp-journalism/commentIQ/tree/master/CommentAPIcode" target="_blank">here</a> )

####Article Relevance 
It is a criteria to calculate the comment score based on artcile similarity. Article Relevance score is calculated by taking cosine similarity or dot product of the respective normalized feature vectors for a comment and article to which it is attached.

####Conversational Relevance
Conversational Relevance measures how similar a comment is to other comments on the same article.Only those articles with 10 or more comments were considered in order to ensure that there was enough of a discussion to produce robust feature vectors. To measure conversational relevance, for each article’s comments a centroid feature vector was created representing the text of all of the comments on the article that were posted before a given comment. This represents the terms used across the thread up to that point in time. Then, for each comment in the thread its cosine similarity to this centroid representation was calculated in order to measure the comment’s conversational relevance.

#### Personal Experience
It is a criteria to calculate the comment score based on comments which express personal experiences and use words in LIWC categories “I”, “We”, “Family”, and “Friends” which would reflect personal (1st and 3rd person pronouns) and close relational (i.e. family and friends) experiences.

#### Readability
The Readability score specifies specifically criteria related to the style, clarity, adherence to standard grammar, and degree to which a comment is well-articulated.The Readability score is the SMOG index or reading grade level of the text.

(Get API code and get it running on your machine. Follow the instructions <a href="https://github.com/comp-journalism/commentIQ/tree/master/CommentAPIcode" target="_blank">here</a> )

###How to use CommentIQ API
There are 10 Different Request points and each Request point have specific function, parameters and responses.


1. [Add Article](#1)
2. [Update Article](#2)
3. [Add Comment](#3)
4. [Update Comment](#4)
5. [Delete Comment](#5)
6. [Get Article Relevance Score](#6)
7. [Get Conversational Relevance Score](#7)
8. [Get Personal Experience Score](#8)
9. [Get Readability Score](#9)
10. [Get All Scores](#10)

                                 
|Name    |  Values and Notes          |
|:----------|:-------------|
| Base URL |  http://ec2-54-173-77-171.compute-1.amazonaws.com/commentIQ/v1 |
| HTTP methods |  POST/GET |
| Response format |  JSON (.json) |

###  <a name="1"></a>1. Add Article
#### 
For new articles, article text needs to be send via HTTP POST method and a auto generated ArticleID will be send in response. This Article ID needs to be kept note of in order to update the article or adding comment to the article in future.             
<b>Note: </b> Article ID is crucial in order to get the comment score

| Name   | Values and Notes           |
|:----------|:-------------|
| URL |  http://ec2-54-173-77-171.compute-1.amazonaws.com/commentIQ/v1/addArticle |
| HTTP method |  POST |
| Response format |  JSON (.json) |    

###  Parameters

| Name   | Values and Notes           |
|:----------|:-------------|
| article_text | Should be sent as key name In JSON format |

### Response

| Name   | Values and Notes           |
|:----------|:-------------|
| ArticleID | Auto-generated ArticleID |
| status | Success/Failure |


###  Example
##### Python Code
```sh
your_article_text = "Your Article Text"
url = "http://ec2-54-173-77-171.compute-1.amazonaws.com/commentIQ/v1/addArticle"
params = {'article_text' : your_article_text }
param_json = json.dumps(params)
response = requests.post(url, param_json)
response_articleID = response.json()['articleID']
status = response.json()['status']
```
##### RESPONSE JSON
```sh
{
    "ArticleID": "172"
    "status": "Insert Successful"
}        
```


### 2. <a name="2"></a>Update Article
#### 
To update articles - updated article text and ArticleID needs to be send via HTTP POST method.                
<b>Note: </b> It is important to update the API database with updated article text in order to calculate correct Article Relevance Score for a comment.

| Name   | Values and Notes           |
|:----------|:-------------|
| URL |  http://ec2-54-173-77-171.compute-1.amazonaws.com/commentIQ/v1/updateArticle |
| HTTP method |  POST |
| Response format |  JSON (.json) |    

###  Parameters

| Name   | Values and Notes           |
|:----------|:-------------|
| article_text | Should be sent as key name In JSON format |
| articleID | Should be sent as key name In JSON format |

### Response

| Name   | Values and Notes           |
|:----------|:-------------|
| status | Success/Failure |


###  Example
##### Python Code
```sh
your_article_text = "Updated Article Text"
url = "http://ec2-54-173-77-171.compute-1.amazonaws.com/commentIQ/v1/updateArticle"
params = {'article_text' : your_article_text, 'articleID' : articleID }
param_json = json.dumps(params)
response = requests.post(url, param_json)
status = response.json()['status']
```
##### RESPONSE JSON
```sh
{
    "status": "Update Successful"
}        
```

### 3. <a name="3"></a>Add Comment
#### 
For new comments - Comment Text and Article ID needs to be send via HTTP POST method. All the scores will be calculated and send via Response. An auto-generated commentID will also be send in response.                                                  

<b>Note: </b> This Comment ID needs to be kept note of in order to update or delete the Comment in future.


| Name   | Values and Notes           |
|:----------|:-------------|
| URL |  http://ec2-54-173-77-171.compute-1.amazonaws.com/commentIQ/v1/addComment |
| HTTP method |  POST |
| Response format |  JSON (.json) |    

###  Parameters

| Name   | Values and Notes           |
|:----------|:-------------|
| commentBody | Should be sent as key name In JSON format |
| articleID | Should be sent as key name In JSON format |

### Response

| Name   | Values and Notes           |
|:----------|:-------------|
| ArticleRelevance | Comment Article Relevance Score |
| ConversationalRelevance | Comment Conversational Relevance Score |
| PersonalXP | Comment Personal Experience Score |
| Readability | Comment Readability Score |
| CommentID | AutoGenerated Comment ID |
| status | Success/Failure |

###  Example
##### Python Code
```sh
your_comment_text = "Your Comment Text"
articleID = 78
url = "http://ec2-54-173-77-171.compute-1.amazonaws.com/commentIQ/v1/addComment"
params = {'commentBody' : your_comment_text, 'articleID' : articleID }
param_json = json.dumps(params)
response = requests.post(url, param_json)
AR = response.json()['ArticleRelevance']
CR = response.json()['ConversationalRelevance']
personal_exp = response.json()['PersonalXP']
readability = response.json()['Readability']
commentID = response.json()['CommentID']
status = response.json()['status']
```
##### RESPONSE JSON
```sh
{
    "ArticleRelevance": "0.06496080742983745"
    "ConversationalRelevance": "0.4046152704799379"
    "Readability": "0.0727272727273"
    "PersonalXP": "17.2"
    "status": "Insert Successful"
    "CommentID": "1714"
}        
```


### 4. <a name="4"></a>Update Comment
#### 
To update comment - Comment Text and Comment ID needs to be send via HTTP POST method. All the scores will be calculated and send via Response.           
<b>Note: </b> It is important to update the API database with updated comment text in order to update correct Scores for a comment.


| Name   | Values and Notes           |
|:----------|:-------------|
| URL |  http://ec2-54-173-77-171.compute-1.amazonaws.com/commentIQ/v1/updateComment |
| HTTP method |  POST |
| Response format |  JSON (.json) |    

###  Parameters

| Name   | Values and Notes           |
|:----------|:-------------|
| commentBody | Should be sent as key name In JSON format |
| commentID | Should be sent as key name In JSON format |

### Response

| Name   | Values and Notes           |
|:----------|:-------------|
| ArticleRelevance | Comment Article Relevance Score |
| ConversationalRelevance | Comment Conversational Relevance Score |
| PersonalXP | Comment Personal Experience Score |
| Readability | Comment Readability Score |
| status | Success/Failure |

###  Example
##### Python Code
```sh
updated_comment_text = "Your Update Comment Text"
commentID = 172
url = "http://ec2-54-173-77-171.compute-1.amazonaws.com/commentIQ/v1/updateComment"
params = {'commentBody' : update_comment_text, 'commentID' : commentID }
param_json = json.dumps(params)
response = requests.post(url, param_json)
AR = response.json()['ArticleRelevance']
CR = response.json()['ConversationalRelevance']
personal_exp = response.json()['PersonalXP']
readability = response.json()['Readability']
status = response.json()['status']
```
##### RESPONSE JSON
```sh
{
    "ArticleRelevance": "0.06496080742983745"
    "ConversationalRelevance": "0.4046152704799379"
    "Readability": "0.0727272727273"
    "PersonalXP": "17.2"
    "Status": "Update Successful"
}        
```

### 5. <a name="5"></a>Delete Comment
#### 
To delete a comment - Comment ID needs to be send via HTTP GET method.           
<b>Note: </b> Since Conversational Relevance depends upon all the previous comments, database needs to be updated with any deleted comment.


| Name   | Values and Notes           |
|:----------|:-------------|
| URL |  http://ec2-54-173-77-171.compute-1.amazonaws.com//commentIQ/v1/deleteComment/<b>commentID</b> |
| HTTP method |  GET |
| Response format |  JSON (.json) |    

###  Parameters

| Name   | Values and Notes           |
|:----------|:-------------|
| commentID | Should be sent as part of URL |


### Response

| Name   | Values and Notes           |
|:----------|:-------------|
| status | Success/Failure |


###  Example
##### Python Code
```sh
commentID = 172
url = "http://ec2-54-173-77-171.compute-1.amazonaws.com/commentIQ/v1/deleteComment/'"+ str(commentID) +"'"
response = requests.get(url)
print response.json()
```
##### RESPONSE JSON
```sh
{
    "status": "success"
}        
```

### 6. <a name="6"></a>Get Article Relevance Score
#### 
To get Article Relevance Score of a comment - Comment ID needs to be send via HTTP GET method. The Article Relevance score will be fetched and send via Response.


| Name   | Values and Notes           |
|:----------|:-------------|
| URL |  http://ec2-54-173-77-171.compute-1.amazonaws.com//commentIQ/v1/getArticleRelevance/<b>commentID</b> |
| HTTP method |  GET |
| Response format |  JSON (.json) |    

###  Parameters

| Name   | Values and Notes           |
|:----------|:-------------|
| commentID | Should be sent as part of URL |


### Response

| Name   | Values and Notes           |
|:----------|:-------------|
| ArticleRelevance | Comment Article Relevance Score |
| status | Success/Failure |

###  Example
##### Python Code
```sh
commentID = 172
url = "http://ec2-54-173-77-171.compute-1.amazonaws.com/commentIQ/v1/getArticleRelevance/'"+ str(commentID) +"'"
response = requests.get(url)
print response.json()
```
##### RESPONSE JSON
```sh
{
    "ArticleRelevance": "0.06496080742983745"
    "status": "success"
}        
```
### 7. <a name="7"></a>Get Conversational Relevance Score
#### 
To get Conversational Relevance Score of a comment - Comment ID needs to be send via HTTP GET method. The Conversational Relevance score will be fetched and send via Response.


| Name   | Values and Notes           |
|:----------|:-------------|
| URL |  http://ec2-54-173-77-171.compute-1.amazonaws.com//commentIQ/v1/getConversationalRelevance/<b>commentID</b> |
| HTTP method |  GET |
| Response format |  JSON (.json) |    

###  Parameters

| Name   | Values and Notes           |
|:----------|:-------------|
| commentID | Should be sent as part of URL |


### Response

| Name   | Values and Notes           |
|:----------|:-------------|
| ConversationalRelevance | Comment Conversational Relevance Score |
| status | Success/Failure |

###  Example
##### Python Code
```sh
commentID = 172
url = "http://ec2-54-173-77-171.compute-1.amazonaws.com/commentIQ/v1/getConversationalRelevance/'"+ str(commentID) +"'"
response = requests.get(url)
print response.json()
```
##### RESPONSE JSON
```sh
{
    "ConversationalRelevance": "0.40461527048"
    "status": "success"
}        
```

### 8. <a name="8"></a>Get Personal Experience Score
#### 
To get Personal Experience Score of a comment - Comment ID needs to be send via HTTP GET method. The Personal Experience score will be fetched and send via Response.


| Name   | Values and Notes           |
|:----------|:-------------|
| URL |  http://ec2-54-173-77-171.compute-1.amazonaws.com//commentIQ/v1/getPersonalXP/<b>commentID</b> |
| HTTP method |  GET |
| Response format |  JSON (.json) |    

###  Parameters

| Name   | Values and Notes           |
|:----------|:-------------|
| commentID | Should be sent as part of URL |


### Response

| Name   | Values and Notes           |
|:----------|:-------------|
| PersonalXP | Comment Personal Experience Score |
| status | Success/Failure |

###  Example
##### Python Code
```sh
commentID = 172
url = "http://ec2-54-173-77-171.compute-1.amazonaws.com/commentIQ/v1/getPersonalXP/'"+ str(commentID) +"'"
response = requests.get(url)
print response.json()
```
##### RESPONSE JSON
```sh
{
    "PersonalXP": "0.0727272727273"
    "status": "success"
}        
```


### 9. <a name="9"></a>Get Readability Score
#### 
To get Readability Score of a comment - Comment ID needs to be send via HTTP GET method. The Readability score will be fetched and send via Response.


| Name   | Values and Notes           |
|:----------|:-------------|
| URL |  http://ec2-54-173-77-171.compute-1.amazonaws.com//commentIQ/v1/getReadability/<b>commentID</b> |
| HTTP method |  GET |
| Response format |  JSON (.json) |    

###  Parameters

| Name   | Values and Notes           |
|:----------|:-------------|
| commentID | Should be sent as part of URL |


### Response

| Name   | Values and Notes           |
|:----------|:-------------|
| Readability | Comment Readability Score |
| status | Success/Failure |

###  Example
##### Python Code
```sh
commentID = 172
url = "http://ec2-54-173-77-171.compute-1.amazonaws.com/commentIQ/v1/getReadability/'"+ str(commentID) +"'"
response = requests.get(url)
print response.json()
```
##### RESPONSE JSON
```sh
{
    "Readability": "17.2"
    "status": "success"
}        
```

### 10. <a name="10"></a>Get All Scores
#### 
To get All Scores of a comment - Comment ID needs to be send via HTTP GET method. All the scores will be fetched and send via Response.


| Name   | Values and Notes           |
|:----------|:-------------|
| URL |  http://ec2-54-173-77-171.compute-1.amazonaws.com//commentIQ/v1/getScores/<b>commentID</b> |
| HTTP method |  GET |
| Response format |  JSON (.json) |    

###  Parameters

| Name   | Values and Notes           |
|:----------|:-------------|
| commentID | Should be sent as part of URL |


### Response

| Name   | Values and Notes           |
|:----------|:-------------|
| ArticleRelevance | Comment Article Relevance Score |
| ConversationalRelevance | Comment Conversational Relevance Score |
| PersonalXP | Comment Personal Experience Score |
| Readability | Comment Readability Score |
| status | Success/Failure |

###  Example
##### Python Code
```sh
commentID = 172
url = "http://ec2-54-173-77-171.compute-1.amazonaws.com/commentIQ/v1/getScores/'"+ str(commentID) +"'"
response = requests.get(url)
print response.json()
```
##### RESPONSE JSON
```sh
{
    "ArticleRelevance": "0.06496080742983745"
    "ConversationalRelevance": "0.4046152704799379"
    "Readability": "0.0727272727273"
    "PersonalXP": "17.2"
    "Status": "success"
}        
```

(Get API code and get it running on your machine. Follow the instructions <a href="https://github.com/comp-journalism/commentIQ/tree/master/CommentAPIcode" target="_blank">here</a> )
CommentIQ API
=========
The Comment IQ API is a RESTful API used to evaluate comments on news articles and return scores based on four criteria shown to correlate with higher quality comments: Article Relevance, Conversational Relevance, Personal Experience, and Readability. 
These four criteria are explained briefly below, and in more detail in two research papers (including their validation as measures of higher quality comments):
* N. Diakopoulos. The Editor’s Eye: Curation and Comment Relevance on the New York Times. Proc. Conference on Computer Supported Cooperative Work (CSCW). 2015. [<a href="http://www.nickdiakopoulos.com/wp-content/uploads/2011/07/the_editors_eye_final.pdf">PDF</a>]
* N. Diakopoulos. Picking the NYT Picks: Editorial Criteria and Automation in the Curation of Online News Comments. #ISOJ Journal. 2015. 

To install the API code and run it locally on your own server follow the instructions <a href="https://github.com/comp-journalism/commentIQ/tree/master/CommentAPIcode" target="_blank">here</a>

####Article Relevance 
This criterion calculates the comment score based on article similarity. The Article Relevance score is calculated by taking the cosine similarity or dot product of the respective normalized feature vectors for a comment and article to which it is attached.

####Conversational Relevance
Conversational Relevance measures how similar a comment is to other comments on the same article. To measure conversational relevance, for each article’s comments a centroid feature vector is created representing the text of all of the comments on the article that were posted before a given comment. This represents the terms used across the thread up to that point in time. Then, for the next comment in the thread its cosine similarity to this centroid representation is calculated in order to measure the comment’s conversational relevance.

#### Personal Experience
The Personal Experience score is a measure of expressions of personal experiences calculated by counting the rate of use of words in <a href="http://www.liwc.net/">Linguistic Inquiry and Word Count</a> (LIWC) categories “I”, “We”, “Family”, and “Friends” which would reflect personal (1st and 3rd person pronouns) and close relational (i.e. family and friends) experiences. 

#### Readability
The Readability score is calculated as the <a href="http://www.readabilityformulas.com/smog-readability-formula.php">SMOG</a> index or reading grade level of the text. 

#### Brevity
The Brevity score is computed as the number of words in a comment.

###How to use the CommentIQ API
There are 10 Different endpoints currently availabe, with their specific function, parameters and responses as described below. The basic gist of it is that you pass the API content (articles, and then comments associated with those articles) and the API will pass back the relevant scores. In order to provide a faster response time, content is cached on the CommentIQ server, which means that if your content changes (e.g. if an article is updated, or a comment is updated or deleted) you need to use the corresponding API endpoints so that the CommentIQ cache is synced and returning accurate scores.


1. [Add Article](#1)
2. [Update Article](#2)
3. [Add Comment](#3)
4. [Update Comment](#4)
5. [Delete Comment](#5)
6. [Get Article Relevance Score](#6)
7. [Get Conversational Relevance Score](#7)
8. [Get Personal Experience Score](#8)
9. [Get Readability Score](#9)
10. [Get Brevity Score](#10)
11. [Get All Scores](#11)

                                 
|Name    |  Values and Notes          |
|:----------|:-------------|
| Base URL |  http://ec2-54-173-77-171.compute-1.amazonaws.com/commentIQ/v1 |
| HTTP methods |  POST/GET |
| Response format |  JSON (.json) |

###  <a name="1"></a>1. Add Article
#### 
For new articles, article text needs to be sent via an HTTP POST method and an auto generated ArticleID will be sent in response. This Article ID needs to be kept track of in order to update the article or to add comments to the article in the future.             
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
imoport requests
import json

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
    "status": "Add Successful"
}        
```


### 2. <a name="2"></a>Update Article
#### 
To update articles - updated article text and ArticleID needs to be send via HTTP POST method.                
<b>Note: </b> It is important to update the API database with updated article text if it changes in order to calculate correct Article Relevance Score for a comment.

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
imoport requests
import json

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
For new comments - Comment Text and Article ID need to be sent via an HTTP POST method. All the scores will be calculated and sent via Response. An auto-generated commentID will also be sent in response.                                                  

<b>Note: </b> This Comment ID needs to be kept track of in order to update or delete the comment in the future.


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
| Brevity | Comment Brevity Score |
| CommentID | AutoGenerated Comment ID |
| status | Success/Failure |

###  Example
##### Python Code
```sh
imoport requests
import json

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
brevity = response.json()['Brevity']
commentID = response.json()['CommentID']
status = response.json()['status']
```
##### RESPONSE JSON
```sh
{
    "ArticleRelevance": "0.06496080742983745"
    "ConversationalRelevance": "0.4046152704799379"
    "PersonalXP": "0.0727272727273"
    "Readability": "17.2"
    "Brevity": "55"
    "status": "Add Successful"
    "CommentID": "1714"
}        
```


### 4. <a name="4"></a>Update Comment
#### 
To update comment - Comment Text and Comment ID nees to be sent via an HTTP POST method. All the scores will be calculated and sent via Response.           
<b>Note: </b> It is important to update the API with comment text that has changed in order to calculate the correct scores for a comment.


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
| Brevity | Comment Brevity Score |
| status | Success/Failure |

###  Example
##### Python Code
```sh
imoport requests
import json

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
brevity = response.json()['Brevity']
status = response.json()['status']
```
##### RESPONSE JSON
```sh
{
    "ArticleRelevance": "0.06496080742983745"
    "ConversationalRelevance": "0.4046152704799379"
    "PersonalXP": "0.0727272727273"
    "Readability": "17.2"
    "Brevity": "55"
    "Status": "Update Successful"
}        
```

### 5. <a name="5"></a>Delete Comment
#### 
To delete a comment - Comment ID needs to be sent via an HTTP DELETE method.           
<b>Note: </b> Since Conversational Relevance depends upon all the previous comments, the database needs to be updated with any deleted comment(s).


| Name   | Values and Notes           |
|:----------|:-------------|
| URL |  http://ec2-54-173-77-171.compute-1.amazonaws.com//commentIQ/v1/deleteComment/<b>commentID</b> |
| HTTP method |  DELETE |
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
imoport requests
import json

commentID = 172
url = "http://ec2-54-173-77-171.compute-1.amazonaws.com/commentIQ/v1/deleteComment/'"+ str(commentID) +"'"
response = requests.delete(url)
print response.json()
```
##### RESPONSE JSON
```sh
{
    "status": "Delete successful"
}        
```

### 6. <a name="6"></a>Get Article Relevance Score
#### 
To get the Article Relevance Score of a comment - the Comment ID needs to be sent via an HTTP GET method. The Article Relevance score will be fetched and sent via Response.


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
imoport requests
import json

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
To get the Conversational Relevance Score of a comment - the Comment ID needs to be sent via HTTP GET method. The Conversational Relevance score will be fetched and sent via Response.


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
imoport requests
import json

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
To get the Personal Experience Score of a comment - the Comment ID needs to be sent via HTTP GET method. The Personal Experience score will be fetched and sent via Response.


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
imoport requests
import json

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
To get the Readability Score of a comment - Comment ID needs to be sent via an HTTP GET method. The Readability score will be fetched and sent via Response.


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
imoport requests
import json

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


### 10. <a name="10"></a>Get Brevity Score
#### 
To get the Brevity Score of a comment - Comment ID needs to be sent via an HTTP GET method. The Brevity score will be fetched and sent via Response.


| Name   | Values and Notes           |
|:----------|:-------------|
| URL |  http://ec2-54-173-77-171.compute-1.amazonaws.com//commentIQ/v1/getBrevity/<b>commentID</b> |
| HTTP method |  GET |
| Response format |  JSON (.json) |    

###  Parameters

| Name   | Values and Notes           |
|:----------|:-------------|
| commentID | Should be sent as part of URL |


### Response

| Name   | Values and Notes           |
|:----------|:-------------|
| Brevity | Comment Brevity Score |
| status | Success/Failure |

###  Example
##### Python Code
```sh
imoport requests
import json

commentID = 172
url = "http://ec2-54-173-77-171.compute-1.amazonaws.com/commentIQ/v1/getBrevity/'"+ str(commentID) +"'"
response = requests.get(url)
print response.json()
```
##### RESPONSE JSON
```sh
{
    "Brevity": "55"
    "status": "success"
}        
```

### 11. <a name="11"></a>Get All Scores
#### 
To get All Scores of a comment - the Comment ID needs to be sent via HTTP GET method. All the scores will be fetched and sent via Response.


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
| Brevity | Comment Brevity Score |
| status | Success/Failure |

###  Example
##### Python Code
```sh
imoport requests
import json

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
    "PersonalXP": "0.0727272727273"
    "Readability": "17.2"
    "Brevity": "55"
    "Status": "success"
}        
```

To install the API code and run it locally on your own server follow the instructions <a href="https://github.com/comp-journalism/commentIQ/tree/master/CommentAPIcode" target="_blank">here</a>

CommentIQ API Code
========
Get the code up and running on your machine in 5 steps:                                            

1. Installing the required packages
2. Setup your database and table structure
3. Create a vocabulary (optional)
4. Run the CommentIQ API code


### 1. Install the required packages

Please install the following softwares/packages before proceeding to step2

* <a href="https://www.python.org/download/releases/2.7/" target="_blank">Python 2.7</a>
* <a href="https://pypi.python.org/pypi/Flask" target="_blank">Flask</a>
* <a href="http://www.nltk.org/install.html" target="_blank">NLTK</a>
* <a href="http://johnlaudun.org/20130126-nltk-stopwords/" target="_blank">NLTK corpus</a> for 'stop words'
* <a href="http://dev.mysql.com/downloads/mysql/" target="_blank">MySQL</a>
* <a href="https://dev.mysql.com/downloads/connector/python/" target="_blank">MySQL Python connector</a>
* <a href="http://www.crummy.com/software/BeautifulSoup/#Download" target="_blank">BeautifulSoup (bs4)</a>
* <a href="http://docs.python-requests.org/en/latest/user/install/" target="_blank">Requests</a> (optional, if following example code below) 


### 2. Setup your database and table structure

The structures for all database tables are present in a self contained SQL file, TableStructures.sql, in the 'apidata' folder. 

First create a MySQL database, and then import the table structures in Tablestructures.sql. You'll need to do this in order to advance to step 3 and 4. In order to create a database and import tables follow the <a href="http://www.cyberciti.biz/faq/import-mysql-dumpfile-sql-datafile-into-my-database/" target="_blank">instructions</a> to import a MySQL Database.

Then, edit the database.ini file in the 'apidata' folder and fill in your credentials for your MySQL database connection
```sh
[credentials]
user=john
password=nash
host=127.0.0.1
database=comment_iq
```

### 3. Create a vocabulary (optional)
In order to run the API code we need to create a vocabulary of unigrams which is used in calculating scores. This vocabulary is used to define a feature vector to describe each comment and article. It is advisable to get a fair amount of data like 3 months worth of comments in order to get more accurate results. You might also consider updating your vocabulary periodically so that new words that are introduced in the news can be accounted for. 

For convenience, and to get started with the API quickly, a vocabulary file is provide when you check out the project. It's called vocab_freq.json and is within the 'apidata' folder. You can also download that file <a href="http://api.comment-iq.com/commentIQ/v1/getVocabulary" target="_blank">here</a>. However, for the best results we recommend that you create your own vocabulary. 

NYT API access is necessary to download comment data that is processed to produce a vocabulary. To request NYT API keys see <a href="http://developer.nytimes.com/docs/reference/keys" target="_blank">here</a>

To create the vocabulary using the NYT API, you need to edit a config file in the 'apidata' folder with your credentials to access that API:
keys_config.ini
```sh
[API-KEYS]
KEY1=
KEY2=
```
Edit the keys_config.ini file and fill in your NYT API key(s). 
```sh
[API-KEYS]
KEY1=cksdh4934dkhf:0:2091
KEY2=cksdh4934dkhf:0:2092
```

####
Python script to perform this operation : NytApiCall_ComputeVocab.py
####Steps to Run NytApiCall_ComputeVocab.py :


Each NYT API keys have a limit of 5000 calls per day. So please make sure the key limit does not exceed more than 5000. Exceeding the key limit will lead to "Developer over rate" and you will not be able to fetch more comments via the same API key. Click <a href="http://developer.nytimes.com/docs/faq#9a" target="_blank">here</a> for more information. 

The Code perform 4 operations:

1. User Input: The user specifies a starting date, ending date, offset value of their choice, which specifis the range of data to collect.
2. Collect Comments:                    
    * This function will collect all the comments data from the New York Times as per the mentioned dates. 
    * The comments data will be stored in the vocab_comments table. 
    * The offset value is 25 which means each call will fetch 25 comments. 
    * The user can also decrease the key_limit value if desired to run a small cycle.
    * Maintains a dictionary of 3 months worth of latest comments data (comments data of more than 3 month will be deleted).
3. Compute Vocabulary: Gets the frequency distribution of each word across all comments in the vocab_comments table and stores in a JSON for later reference (vocab_freq.json).
4. Get Document Count: Counts the number of comments in the vocab_comments table and stores in a JSON (document_count.json) which will be later used to calculate feature vectors.

###4. Run the CommentIQ API code
The python-flask code, CommentIQ_API.py, uses the subroutine, calculate_score.py, and its functions to perform the calculations of all of the criteria. Look for inline comments in order to understand the complete code.

run the code
```sh 
>>> python commentIQ_API.py 
```
This will start the flask server and you can start using the CommentIQ API.

<b>Note: </b>For the local machine the base url will change according to your host name. For example most local machines will have local server running on 127.0.0.1:5000.  In this case the base url will be : http://127.0.0.1:5000/commentIQ/v1
#####
###  Examples
##### Add Article (Python Code)
```sh
imoport requests
import json

your_article_text = "Your Article Text"
url = "http://127.0.0.1:5000/commentIQ/v1/addArticle"
params = {'article_text' : your_article_text }
param_json = json.dumps(params)
response = requests.post(url, param_json)
response_articleID = response.json()['articleID']
status = response.json()['status']
```
##### RESPONSE JSON
```sh
{
    "ArticleID": "78"
    "status": "Add Successful"
}        
```
##### Add Comment (Python Code)
```sh
import requests
import json

your_comment_text = "Your Comment Text"
articleID = 78
url = "http://127.0.0.1:5000/commentIQ/v1/addComment"
params = {'commentBody' : your_comment_text, 'articleID' : articleID }
param_json = json.dumps(params)
response = requests.post(url, param_json)
AR = response.json()['ArticleRelevance']
CR = response.json()['ConversationalRelevance']
personal_exp = response.json()['PersonalXP']
readability = response.json()['Readability']
Length = response.json()['Length']
commentID = response.json()['commentID']
status = response.json()['status']
```
##### RESPONSE JSON
```sh
{
    "ArticleRelevance": "0.06496080742983745"
    "ConversationalRelevance": "0.4046152704799379"
    "Readability": "0.0727272727273"
    "PersonalXP": "17.2"
    "Length": "55"
    "status": "Add Successful"
    "commentID": "1714"
}        
```

In order to understand how the CommentIQ API works refer <a href="https://github.com/comp-journalism/commentIQ" target="_blank">this</a> link




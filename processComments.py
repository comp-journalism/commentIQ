from nltk.probability import FreqDist
from nltk.corpus import stopwords
from nltk.tokenize import SpaceTokenizer, WhitespaceTokenizer
import nltk.tag, nltk.util, nltk.stem
from HTMLParser import HTMLParser
import htmlentitydefs
import re # regular expressions
import string, math
from bs4 import BeautifulSoup
import csv
from datetime import date
from datetime import datetime
from datetime import timedelta
import calendar


stopword_list = stopwords.words('english')
porter = nltk.PorterStemmer()
doc_frequency = {}
word_features = []
vocab_freq = {}


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

 # Assumes that both vectors are normalized
def ComputeCosineSimilarity(v1, v2):
	dotproduct = 0
	for (key1,val1) in v1.items():
		if key1 in v2:
			dotproduct += val1 * v2[key1]
	return dotproduct;  


def CleanAndTokenize(text):
	
	# Strip URLs and replace with token "URLURLURL"
	r = re.compile(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")
	text = re.sub(r, " URLURLURL", text)

	# Strip html tags
	soup = BeautifulSoup(text)
	for tag in soup.findAll(True):
		tag.replaceWithChildren()
		text = soup.get_text()

	# Normalize everything to lower case
	text = text.lower()
	
	# Strip line breaks and endings \r \n
	r = re.compile(r"[\r\n]+")
	text = re.sub(r, "", text)

	table = {
		ord(u'\u2018') : u"'",
		ord(u'\u2019') : u"'",
		ord(u'\u201C') : u'"',
		ord(u'\u201d') : u'"',
		ord(u'\u2026') : u'',
		ord(u'\u2014') : u'', # get rid of em dashes
	}
	text = text.translate(table)

	# Normalize contractions
	# e.g. can't => can not, it's => it is, he'll => he will
	text = text.replace("can't", "can not")
	text = text.replace("couldn't", "could not")
	text = text.replace("don't", "do not")
	text = text.replace("didn't", "did not")
	text = text.replace("doesn't", "does not")
	text = text.replace("shouldn't", "should not")
	text = text.replace("haven't", "have not")
	text = text.replace("aren't", "are not")
	text = text.replace("weren't", "were not")
	text = text.replace("wouldn't", "would not")
	text = text.replace("hasn't", "has not")
	text = text.replace("hadn't", "had not")
	text = text.replace("won't", "will not")
	text = text.replace("wasn't", "was not")
	text = text.replace("can't", "can not")
	text = text.replace("isn't", "is not")
	text = text.replace("ain't", "is not")    
	text = text.replace("it's", "it is")
	
	text = text.replace("i'm", "i am")
	text = text.replace("i'm", "i am")
	text = text.replace("i've", "i have")
	text = text.replace("i'll", "i will")
	text = text.replace("i'd", "i would")
 
	text = text.replace("we've", "we have")
	text = text.replace("we'll", "we will")
	text = text.replace("we'd", "we would")
	text = text.replace("we're", "we are")
	
	text = text.replace("you've", "you have")
	text = text.replace("you'll", "you will")
	text = text.replace("you'd", "you would")
	text = text.replace("you're", "you are")
	
	text = text.replace("he'll", "he will")
	text = text.replace("he'd", "he would")
	text = text.replace("he's", "he has")
	
	text = text.replace("she'll", "she will")
	text = text.replace("she'd", "she would")
	text = text.replace("she's", "she has")
	
	text = text.replace("they've", "they have")
	text = text.replace("they'll", "they will")
	text = text.replace("they'd", "they would")
	text = text.replace("they're", "they are")
	
	text = text.replace("that'll", "that will")
	text = text.replace("that's", "that is")
	text = text.replace("there's", "there is")

	
	# Strip punctuation (except for a few)
	punctuations = string.punctuation # includes following characters: !"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~
	excluded_punctuations = ["$", "%"]
	for p in punctuations:
		if p not in excluded_punctuations:
			text = text.replace(p, " ")

	# Condense double spaces
	text = text.replace("  ", " ")

	# Tokenize the text 
	# NOTE: Using a simple tokenizer based on spaces ... 
	# Could also try a more sophisticated tokenizer if abbreviations / contractions should be conserved
	tokenizer = WhitespaceTokenizer()
	text_tokens = tokenizer.tokenize(text)
	
	return text_tokens



# Computes the vocabulary to be used for vector operations
def ComputeVocabulary():
	# Get the data
	csvFile = open("data/comments_study.csv", 'Ur')
	csvReader = csv.reader(csvFile, delimiter=',', quotechar='"')
	comments  = {}
	for row in csvReader:
		# don't read 1st line
		if csvReader.line_num > 1:			
			comments[row[0]] = row

	# Compute Vocabulary and output it for later
	tokens = []
	n = 0
	nDocuments = len(comments)
	for c in comments:
		n = n + 1
		if n % 100 == 0 :
			print n
		ct = CleanAndTokenize(comments[c][2].decode("utf8"))
		ct = [w for w in ct if w not in stopword_list]
		stemmed_tokens = [porter.stem(t) for t in ct]
		tokens.extend(stemmed_tokens)
		for t in stemmed_tokens:
			if t not in doc_frequency:
				doc_frequency[t] = 1
			else:
				doc_frequency[t] = doc_frequency[t]+1

	#print tokens
	fd = FreqDist(tokens)

	# find cutoff
	unigram_cutoff = 0
	for (i, (key, val)) in enumerate(fd.items()):
		#print str(i) + " " + str(key) + " " + str(fd[key])
		if fd[key] < 10:
			unigram_cutoff = i - 1
			break
	print "unigram cutoff: " + str(unigram_cutoff)
	word_features.extend(fd.keys()[:unigram_cutoff])

	fileWriter = csv.writer(open("data/vocab.csv", "w+"),delimiter=",")
	for w in word_features:
		row = [w.encode("utf8"), doc_frequency[w]]
		fileWriter.writerow(row)



def ComputeCommentArticleRelevance():
	# Read in the vocabulary and the document frequencies 
	csvFile = open("data/vocab.csv", 'Ur')
	csvReader = csv.reader(csvFile, delimiter=',', quotechar='"')
	# Vocab freq stores the vocab as keys and the doc frequency as values
	for row in csvReader:
		if csvReader.line_num > 1:			
			vocab_freq[row[0]] = int(row[1])

	# commentID,commentTitle,commentBody,approveDate,recommendationCount,display_name,location,commentQuestion,commentSequence,status,articleURL,editorsSelection,in_study
	csvFile = open("data/comments_study.csv", 'Ur')
	csvReader = csv.reader(csvFile, delimiter=',', quotechar='"')
	comments  = {}
	for row in csvReader:
		if csvReader.line_num > 1:			
			comments[row[0]] = row

	# The number of documents is the number of comments
	nDocuments = len(comments)

	# articleID,pubDate,headline,articleURL,fullText,materialType,snippet
	csvFile = open("data/articles.csv", 'Ur')
	csvReader = csv.reader(csvFile, delimiter=',', quotechar='"')
	articles  = {}
	for row in csvReader:
		if csvReader.line_num > 1:
			# key on the article URL			
			articles[row[3]] = row

	# output file will have have a final row that is the comment-article relevance
	fileWriter = csv.writer(open("data/comment_study_article_relevance.csv", "w+"),delimiter=",")
	# for each article and the comments on each
	for (j, (commentID, comment)) in enumerate(comments.items()):
		print "comment: " + str(j)
		ct = CleanAndTokenize(comment[2].decode("utf8"))
		ct = [w for w in ct if w not in stopword_list]
		comment_stemmed_tokens = [porter.stem(t) for t in ct]
		comment_stemmed_tokens_fd  = FreqDist(comment_stemmed_tokens)

		# Get the article full text
		ct = CleanAndTokenize(articles[comment[10]][4].decode("utf8"))
		ct = [w for w in ct if w not in stopword_list]
		article_stemmed_tokens = [porter.stem(t) for t in ct]
		article_stemmed_tokens_fd  = FreqDist(article_stemmed_tokens)
		
		# now create the feature vectors for article and comment (this is redudant for the article on every iteration)
		article_features = {}
		comment_features = {}
		for w in vocab_freq:
			df = vocab_freq[w]
			article_features[w] = article_stemmed_tokens_fd[w] * math.log(nDocuments / df)
			comment_features[w] = comment_stemmed_tokens_fd[w] * math.log(nDocuments / df)
		# normalize vectors
		article_features = NormalizeVector(article_features)
		comment_features = NormalizeVector(comment_features)
		comment_article_similarity = ComputeCosineSimilarity (article_features, comment_features)

		# Extend the row with the similarity value and write it out
		comment[2] = ""
		comment.append(comment_article_similarity)
		fileWriter.writerow(comment)


def ComputeCommentConversationalRelevance():
	# Read in the vocabulary and the document frequencies 
	csvFile = open("data/vocab.csv", 'Ur')
	csvReader = csv.reader(csvFile, delimiter=',', quotechar='"')
	# Vocab freq stores the vocab as keys and the doc frequency as values
	for row in csvReader:
		if csvReader.line_num > 1:			
			vocab_freq[row[0]] = int(row[1])

	# Get articles with only more than 10 commnts on them
	articles = {}
	# commentID,commentTitle,commentBody,approveDate,recommendationCount,display_name,location,commentQuestion,commentSequence,status,articleURL,editorsSelection,in_study
	csvFile = open("data/comments_study.csv", 'Ur')
	csvReader = csv.reader(csvFile, delimiter=',', quotechar='"')
	nDocuments = 0
	for row in csvReader:
		if csvReader.line_num > 1:	
			nDocuments = nDocuments + 1
			article_url = row[10]
			# convert to unix time
			row[3] = datetime.strptime(row[3], "%Y-%m-%d %H:%M:%S")
			row[3] = calendar.timegm(row[3].utctimetuple())
			if article_url not in articles:
				articles[article_url] = []
				articles[article_url].append(row)
			else:
				articles[article_url].append(row)


	fileWriter = csv.writer(open("data/comment_study_comment_conversational_relevance.csv", "w+"),delimiter=",")
	nc = 0
	for a in articles:
		print a
		comments = articles[a]
		if len(comments) >= 10:
			# sort by time 
			comments.sort(key=lambda x: x[3])

			# get the centroid of first 10 comments (then we incrementally update it)
			centroid_comment_stemmed_tokens = []
			#print articles[a]
			for comment in comments[0:10]:
				ct = CleanAndTokenize(comment[2].decode("utf8"))
				ct = [w for w in ct if w not in stopword_list]
				centroid_comment_stemmed_tokens.extend([porter.stem(t) for t in ct])
				#print len(comment_stemmed_tokens)
			#comment_stemmed_tokens_fd  = FreqDist(comment_stemmed_tokens)
			
			# Now just look at 11 though N comments (there must be at least 10 before it to compute the centroid)
			for comment in comments[10:]:
				ct = CleanAndTokenize(comment[2].decode("utf8"))
				ct = [w for w in ct if w not in stopword_list]

				# Update and compute the centroid
				centroid_comment_stemmed_tokens.extend([porter.stem(t) for t in ct])	
				centroid_comment_stemmed_tokens_fd = FreqDist(centroid_comment_stemmed_tokens)
				centroid_comment_features = {}
				for w in vocab_freq:
					centroid_comment_features[w] = centroid_comment_stemmed_tokens_fd[w] * math.log(nDocuments / vocab_freq[w])					
				centroid_comment_features = NormalizeVector(centroid_comment_features)

				# Now compute dist to  comment				
				comment_stemmed_tokens = []
				comment_stemmed_tokens.extend([porter.stem(t) for t in ct])	
				comment_stemmed_tokens_fd  = FreqDist(comment_stemmed_tokens)

				comment_features = {}			
				for w in vocab_freq:
					comment_features[w] = comment_stemmed_tokens_fd[w] * math.log(nDocuments / vocab_freq[w])
				comment_features = NormalizeVector(comment_features)
				comment_originality = ComputeCosineSimilarity (centroid_comment_features, comment_features)

				# Extend the row with the similarity value and write it out
				comment[2] = ""
				comment.append(comment_originality)
				fileWriter.writerow(comment)

#ComputeVocabulary()

# Compute similarities requires that the vocab file already by computed
#ComputeCommentArticleRelevance()
ComputeCommentConversationalRelevance()

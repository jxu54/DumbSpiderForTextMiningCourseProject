# Jinli Xu
# This is all codes for text mining final project

##############################   scrapying   ##########################################
from bs4 import BeautifulSoup
import time
from random import choice
from urllib.request import time
import requests

# my full user agent information in request header
user_agent = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36'

# collect links for each review post
links = []
for i in range(1, 200):
	req = requests.get('http://pitchfork.com/reviews/albums/?page=%i' %i, headers={'User-Agent': user_agent})
	soup = BeautifulSoup(req.text, 'html.parser')
	time.sleep(choice([0.5,0.7,0.85,1,1.3]))
	print("Item No." + "%i" %i + ", " + "%i" %time.time())
	# put links being collected in a list (proper format)
	for link in soup.find_all('a', class_="album-link"):
		links.append(''.join(['http://pitchfork.com',link.get('href')]))
# write links into a txt file
with open("C:/Users/emano_000/Desktop/links.txt", "w") as l:
	for link in links:
		l.write(link + "\n")
# read links from the file
links = []
with open("C:/Users/emano_000/Desktop/links.txt") as l:
	for link in l.read().strip().split("\n"):
		links.append(link)


# initialize lists for different information
titles = []
artists = []
scores = []
genres = []
abstracts = []
texts = []
start = 0 # if the loop is interupted in the middle, we can set where to start and continue with the scraping
# scraping process
for i in range(start, len(links)):
	req = requests.get(links[i], headers={'user-agent': user_agent})
	soup = BeautifulSoup(req.text, 'html.parser')
	# extract key info
	title = soup.find_all('h1', class_="review-title")[0].get_text()
	artist = soup.find_all('h2', class_="artists")[0].get_text()
	score = soup.find_all('span', class_="score")[0].string # makes scores not a simple string type
	genre = soup.find_all('ul', class_= "genre-list before")[0].get_text()
	abstract = soup.find_all('div', class_="abstract")[0].get_text()
	contents = soup.find_all('div', class_="contents dropcap")[0].get_text()
	# put info into lists
	titles.append(title)
	artists.append(artist)
	scores.append(str(score))
	genres.append(u'%s' %genre)
	abstracts.append(u'%s' %abstract)
	texts.append(u'%s' %contents)
	time.sleep(choice([0.5,0.7,0.85,1,1.3])) # set a random sleep time to avoid being blocked
	print("%i" %i + " - " + title + " finished, " + "%i" %time.time())

#########################   Clean & Pre-Processing  ###################################

# delete foreign charactors such as 印象III : なんとなく、パブロ in texts
import re
texts[53] = re.sub('印象III : なんとなく、パブロ', 'TITLE', texts[53])
titles[53] = re.sub('印象III : なんとなく、パブロ', 'TITLE', titles[53])
texts[53] = re.sub('有名税', 'YouMingShui', texts[53])
texts[53] = re.sub('ゆらゆらボックス', 'WAVES', texts[53])
artists[633] = re.sub('Mgła', 'Mgla', artists[633])
titles[865] = 'Yeah thats the full title 14 Year Old High School PC-Fascist Hype Lords'
titles[971] = 'O Delta'
titles[1997] = 'Ruuckverzauberung 9  Musik Fur Kulturinstitutionen'
titles[2287] = 'TANHA'
artists[2287] = 'LeeAru-2'
titles[2328] = 'KpaN Krai'

# translate function is the fastest!
# tag words in quotes
def tag_words_in_quotes(text):
	import re
	import string
	matches = re.findall(r'\"(.+?)\"', text) # get all sub strings in quotes
	if not matches:
		return(text)
	else:
		translator = str.maketrans({key: None for key in string.punctuation})
		for match in matches:
			match_org = match.translate(translator)
			words = []
			words = match_org.split(' ') # split the sentences into individual words
			# tag each word in the list of words
			i = 0
			for i in range(0, len(words)):
				word = words[i]
				words.pop(i)
				words.insert(i, word + "_Q")
			match_new = " ".join(words) # join tagged words into complete sentences
			text = re.sub(match_org, match_new, text)
			return(text)
# remove escape charactors and all puctuactions (except underscore and dash) in texts
def remove_escape_chars(text):
	import re
	import string
	text = text.encode('ascii', 'replace')
	text = str(text) # cure the Type after encode
	text = text.replace("\n", " ")
	text = text.replace("?", " ")
	punc = string.punctuation.replace("_","")
	punc = punc.replace("-","")
	# punc = punc.replace("'","") # keep ' will cause problems when using weka
	translator = str.maketrans({key: None for key in punc})
	text = text.translate(translator)
	return(text)

# replace ":" and "\'" in titles so that we can use them as file names
import string
punc = string.punctuation.replace("-","")
translator = str.maketrans({key: None for key in punc}) # clean up titles
titles_new = []
for title in titles:
	title = title.replace('\'', '')
	title = title.replace(':', '-')
	title = title.translate(translator)
	title = remove_escape_chars(title)
	titles_new.append(title)

artists_new = []
abstracts_new = []
texts_new = []

for artist in artists:
	artist = remove_escape_chars(artist)
	artists_new.append(artist)

for abstract in abstracts:
	abstract = tag_words_in_quotes(abstract)
	abstract = remove_escape_chars(abstract)
	abstract = abstract[1:] # delete string header b
	abstracts_new.append(abstract)

for text in texts:
	text = tag_words_in_quotes(text)
	text = remove_escape_chars(text)
	text = text[1:] # delete string header b
	texts_new.append(text)

# normalized scores
scores_new = []
for score in scores:
	score = round(float(score))
	scores_new.append(score)

score_level = []
for score in scores_new:
	if (score <= 6):
		level = "Good"
	elif (score == 7):
		level = "Great"
	else:
		level = "MustHave"
	score_level.append(level)

# now the data we have:
# titles_new, artists, scores, scores_new, genres, abstracts_new, texts_new

###########################   topic modeling   ########################################

# output to multiple txt files for Mallet
for i in range(0,2400):
	with open('reviews\%i-%s.txt' %(i+1, titles_new[i]), 'w') as f:
		f.write(texts_new[i])

###########################   classification   ########################################

# output scrapying results to a csv file, don't forget to set a seperator
import csv
output = zip(titles_new, artists_new, scores, scores_new, score_level, genres, abstracts_new, texts_new)
with open('metadata_reviews.csv','w') as f:
	writer = csv.writer(f, delimiter=',', lineterminator='\n')
	writer.writerow('title, artist, score, rounded_score, score_level, genres, abstract, text'.split(', '))
	for row in output: writer.writerow(row)

# read from csv file
import pandas
data = pandas.read_csv('metadata_reviews.csv', header = 0, encoding = 'latin1')
texts = data.text.tolist()


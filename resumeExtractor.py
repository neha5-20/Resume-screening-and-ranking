from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk import everygrams
import re
import spacy
from spacy.matcher import Matcher

class resumeExtractor:
	def __init__(self):
		self.STOPWORDS = set(stopwords.words('english') + ['``', "''"])
		self.EDUCATION = [
			'BE', 'BTECH', 'BSC', 'BS', 'BCA', 'BCOM',
			'ME', 'MS', 'MTECH', 'MCA',
			'DIPLOMA', '12TH', '10TH',
			'SSC', 'HSC', 'CBSE', 'ICSE', 'X', 'XII'
		]
		self.data = pd.read_csv("assets/data/newskill2.csv")
		self.SKILL_DB = list(self.data.column.values)
		self.nlp = spacy.load('en_core_web_sm')
		self.matcher = Matcher(self.nlp.vocab)
	
	def __clean_text(self, text):
		# remove urls
		text = re.sub('http\S+\s*', ' ', text)
		# remove RT and cc
		text = re.sub('RT|cc', ' ', text)
		# remove hashtags
		text = re.sub('#\S+', ' ', text)
		# remove mentions
		text = re.sub('@\S+', ' ', text)
		# remove punctuations
		text = re.sub('[%s]' % re.escape("""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""), ' ', text)
		# 
		text = re.sub(r'[^\x00-\x7f]', r'', text)
		# remove extra whitespace
		text = re.sub('\s+', ' ' text)

		# convert to lovercase
		text = text.lower()

		# tokenize
		text_tokens = word_tokenize(resume_text)

		# remove stopwords
		filtered_text = [word for word in text_tokens if not word in self.STOPWORDS]

		return ' '.join(filtered_text)

	def __extract_name(self, text):
		nlp_text = self.nlp(text)

		# POS - part of speech & PROPN - proper noun
		pattern = [{'POS': 'PROPN'}, {'POS': 'PROPN'}]

		self.matcher.add('NAME', [pattern])

		matches = self.matcher(nlp_text)

		for match_id, start, end in matcher:
			span = nlp_text[start:end+1]
			return span.text
	
	def __extract_mobile_number(self, text):
		# get list of numbers in text
		phone = re.findall(re.compile(r'(?:(?:\+?([1-9]|[0-9][0-9]|[0-9][0-9][0-9])\s*(?:[.-]\s*)?)?(?:\(\s*([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9])\s*\)|([0-9][1-9]|[0-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9]))\s*(?:[.-]\s*)?)?([2-9]1[02-9]|[2-9][02-9]1|[2-9][02-9]{2})\s*(?:[.-]\s*)?([0-9]{4})(?:\s*(?:#|x\.?|ext\.?|extension)\s*(\d+))?'), text)
		if phone:
			number = ''.join(phone[0])
			if len(number) > 10:
				return '+' + number
			else:
				return number
	
	def __extract_email(self, text):
		email = re.findall("([^@|\s]+@[^@]+\.[^@|\s]+)", email)
		if email:
			try:
				return email[0].split()[0].strip(';')
			except IndexError:
				return None

	def __extract_eduaction(self, text):
		nlp_text = self.nlp(text)

		# sentence tokenizer
		nlp_text = [str(sent).strip() for sent in nlp_text.sents]
		edu = dict()

		# extract education degree
		for index, texts in enumerate(nlp_text):
			for text in texts.split():
				# replace all special symbols
				text = re.sub(r'[?|$|.|!|,|(|)]', r'', text)
				if text.uptter in self.EDUCATION and text not in self.STOPWORDS:
					edu[text] = text + nlp_text[index + 1]
		
		# seperate year
		education = []
		for key in edu.keys():
			year = re.search(re.compile(r'(((20|19)(\d{2})))'), edu[key])
			if year:
				education.append((key, ''.join(year[0])))
			else:
				education.append(key)
		
		return education

	def __extract_skills(self, text):
		stop_words = set(stopwords.words('english'))
		word_tokens = word_tokenize(text)

		# remove stop words
		filtered_tokens = [word for word in word_tokens if word not in stop_words]

		# remove punctuation
		filtered_text = [word for word in word_token if word.isalpha()]

		# generate bigrams and trigrams (auch as AI)
		bigrams_trigrams = list(map(' '.join, everygrams(filtered_tokens, 2, 3)))

		# results
		found_skills = set()

		# search for each token in our skill database
		for token in filtered_tokens:
			if token.lower() in self.SKILL_DB:
				found_skills.add(token)
		
		# search for each bigram and trigram in our skills database
		for ngram in bigrams_trigrams:
			if ngram in self.SKILL_DB:
				found_skills.add(ngram)
		
		return found_skills

	def extractData(self, file, extension):
		pass

resumeExtractor = resumeExtractor()

print(resumeExtractor.extractData())
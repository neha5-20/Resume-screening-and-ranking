from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
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
		pass

	def __extract_skills(self, text):
		pass

	def extractData(self, file, extension):
		pass

resumeExtractor = resumeExtractor()

print(resumeExtractor.extractData())
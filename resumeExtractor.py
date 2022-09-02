import nltk
nltk.download('stopwords') # run only once and then comment
from nltk.corpus import stopwords
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
		pass

	def __extract_name(self, text):
		pass
	
	def __extract_mobile_number(self, text):
		pass
	
	def __extract_email(self, text):
		pass

	def __extract_eduaction(self, text):
		pass

	def __extract_skills(self, text):
		pass

	def extractData(self, file, extension):
		pass

resumeExtractor = resumeExtractor()

print(resumeExtractor.extractData())
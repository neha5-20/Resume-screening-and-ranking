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

		#tokenize
		text_tokens = word_tokenize(resume_text)

		# remove stopwords
		filtered_text = [word for word in text_tokens if not word in self.STOPWORDS]

		return ' '.join(filtered_text)

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
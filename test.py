from resumeExtractor import resumeExtractor
from resumeCategorizer import resumeCategorizer
from jdExtractor import jdExtractor
from jdResumeComparision import jdResumeComparision

if __name__ == "__main__":
	
	resumeExtractor = resumeExtractor()
	data = resumeExtractor.extractData('assets/resume/vaibhav resume.pdf', 'pdf')
	resumeData = data[5]
	
	print("\n---------------------------- Resume Screening ----------------------------")
	print(data)
	print("---------------------------- Resume Screening ----------------------------\n")

	jdExtractor = jdExtractor()
	jobDescData = jdExtractor.extractData('assets/job_desc/python job desc.pdf', 'pdf')
	
	print("\n----------------------------- Job Decription -----------------------------")
	print(jobDescData)
	print("----------------------------- Job Decription -----------------------------\n")

	jdResumeComparision = jdResumeComparision()
	score = jdResumeComparision.match(jobDescData, resumeData)

	print("\n--------------------------- JD Resume Scoring ----------------------------")
	print("Match Percentage : " + str(score) + "%")
	print("--------------------------- JD Resume Scoring ----------------------------\n")
	
	resumeScreen = resumeCategorizer()
	categories = resumeScreen.screenResume(resumeData)
	
	print("\n---------------------------- Job Categorizer -----------------------------")
	print(categories)
	print("---------------------------- Job Categorizer -----------------------------\n")
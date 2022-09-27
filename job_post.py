from lib2to3.pytree import Node
from flask import Blueprint, render_template, request, redirect, session, jsonify
from database import mongo
from werkzeug.utils import secure_filename
from jdExtractor import jdExtractor
from jdResumeComparision import jdResumeComparision
from bson.objectid import ObjectId
from datetime import datetime
import pickle
import os

job_post = Blueprint('job_post', __name__, static_folder='static', template_folder='templates')

JD_FOLDER = 'static/job_descriptions'

# --------------------------- Database Collections --------------------------- #
JOBS = mongo.db.JOBS
Applied_EMP = mongo.db.Applied_EMP
resumeFetchedData = mongo.db.resumeFetchedData
# --------------------------- Database Collections --------------------------- #

# ----------------------------- ML pickel import ----------------------------- #
jdExtractorObj = pickle.load(open('jdExtractor.pkl', 'rb'))
jdResumeComparisionObj = pickle.load(open('jdResumeComparision.pkl', 'rb'))
# ----------------------------- ML pickel import ----------------------------- #

def getExtension(filename):
	return filename.rsplit('.',1)[1].lower()

def allowedExtension(filename):
	permittedExtension = ['docx', 'pdf']
	return '.' in filename and getExtension(filename) in permittedExtension

@job_post.route('/post_job')
def post_job():
	fetched_jobs = JOBS.find(
		{},
		{
			'_id': 1,
			'job_profile': 1,
			'company_name': 1,
			'created_at': 1,
			'jd_filename': 1,
			'last_date': 1,
			'salary': 1
		}
	).sort([('created_at', -1)])

	if fetched_jobs == None:
		render_template('job_post.html', errorMsg="Problem in Jobs Fetch")
	else:
		jobs = {}
		count = 0
		for job in fetched_jobs:
			jobs[count] = {
				'job_id': job['_id'],
				'job_profile': job['job_profile'],
				'company_name': job['company_name'],
				'created_at': job['created_at'],
				'jd_filename': job['jd_filename'],
				'last_date': job['last_date'],
				'salary': job['salary']
			}

			return render_template('job_post.html', len=len(jobs), data=jobs)

@job_post.route('/add_job')
def add_job():
	try:
		file = request.files['jd']
		
		job_profile = str(request.form.get('job_profile'))
		company_name = str(request.form.get('company_name'))
		last_date = str(request.form.get('last_date'))
		salary = str(request.form.get('salary'))
		
		filename = secure_filename(file.filename)
		file.save(os.path.join(JD_FOLDER, filename))
		
		fetchedData = jdExtractorObj.extractData(JD_FOLDER + '/' + filename, getExtension(file.filename))

		result = JOBS.insert_one({
			'job_id': ObjectId(),
			'job_profile': job_profile,
			'company_name': company_name,
			'created_at': datetime.now(),
			'jd_filename': filename,
			'last_date': last_date,
			'salary': salary
		})

		if result == None:
			return render_template('job_post.html', errorMsg='Job Add Error Occured')
		else:
			return redirect('/HR/post_job')
	except:
		print('Job Creation Exception occured')

@job_post.route('/show_job')
def show_job():
	fetched_jobs = JOBS.find(
		{},
		{
			'_id': 1,
			'job_profile': 1,
			'company_name': 1,
			'created_at': 1,
			'jd_filename': 1,
			'last_date': 1,
			'salary': 1
		}
	).sort([('created_at', -1)])

	if fetched_jobs == None:
		return render_template('all_jobs.html', errorMsg='Problem in jobs fetched')
	else:
		jobs = {}
		count = 0

		for job in fetched_jobs:
			jobs[count] = {
				'job_id': job['_id'],
				'job_profile': job['job_profile'],
				'company_name': job['company_name'],
				'created_at': job['created_at'],
				'jd_filename': job['jd_filename'],
				'last_date': job['last_date'],
				'salary': job['salary']
			}
		
		return render_template('all_jobs.html', len=len(jobs), data=jobs)

@job_post.route('/apply_job', methods=['POST'])
def apply_job():
	job_id = request.form['job_id']
	jd_data = JOBS.find_one(
		{'_id': ObjectId(job_id)},
		{'job_description': 1}
	)
	emp_data = resumeFetchedData.find_one(
		{'user_id': ObjectId(session['user_id'])},
		{'resume_data': 1}
	)
	match_percentage = jdResumeComparisionObj.match(str(jd_data['job_description']), str(emp_data['resume_data']))

	result = Applied_EMP.insert_one({
		'job_id': ObjectId(job_id),
		'user_id': ObjectId(session['user_id']),
		'user_name': session['user_name'],
		'matching_percentage': match_percentage
	})

	if result == None:
		return jsonify({'status_code':400, 'message': 'problem in applying'})
	else:
		return jsonify({'status_code':200, 'message': 'applied successfully'})

@job_post.route('/view_applied_candidates', methods=['POST', 'GET'])
def view_applied_candidates():
	job_id = request.form['job_id']

	data = Applied_EMP.find(
		{'job_id': ObjectId(job_id)},
		{
			'user_name': 1,
			'matching_percentage': 1,
		}
	).sort([('matching_percentage', -1)])

	if data == None:
		return jsonify({'status_code':400, 'message': 'problem in fetching data'})
	else:
		result = {}
		count = 0
		result[1] = 200
		for applicant in data:
			result[count+2] = {
				'name': applicant['user_name'],
				'match': applicant['matching_percentage']
			}
			count += 1
		result[0] = count

		return result
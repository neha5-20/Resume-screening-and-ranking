from flask import Flask, render_template, request, session, redirect, abort, jsonify
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
from google.oauth2 import id_token
from werkzeug.utils import secure_filename
from bson.objectid import ObjectId
from resumeExtractor import resumeExtractor
from resumeCategorizer import resumeCategorizer
from database import mongo
import os
import pickle
import pathlib
import requests
import google.auth.transport.requests

app = Flask(__name__)

# ------------------------- Google OAuth Configuration start ----------------------------- #

# it is necessary to set a password when dealing with OAuth 2.0
app.secret_key = "ragnosva"

# this is to set our environment to https because OAuth 2.0 only supports https environments
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1" 

# enter your client id you got from Google console
# GOOGLE_CLIENT_ID = "497569231971-gqeg9t65skhghcd1kob8k4igp11ds3l1.apps.googleusercontent.com"
GOOGLE_CLIENT_ID = "497569231971-l4eoroqomrupkkvpogcfl7te54j3tbp8.apps.googleusercontent.com"

# set the path to where the .json file you got Google console is
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, 'client_secret.json')

# Flow is OAuth 2.0 a class that stores all the information on how we want to authorize our users
flow = Flow.from_client_secrets_file(
	client_secrets_file=client_secrets_file,
	# here we are specifing what do we get after the authorization
	scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
	# and the redirect URI is the point where the user will end up after the authorization
	redirect_uri="http://127.0.0.1:5000/callback"
)

# -------------------------- Google OAuth Configuration end ---------------------------- #


# ------------------------- MongoDB Atlas Configuration start --------------------------- #
resumeFetchedData = mongo.db.resumeFetchedData
Ranked_resume = mongo.db.Ranked_resume
IRS_USERS = mongo.db.IRS_USERS
JOBS = mongo.db.JOBS
# -------------------------- MongoDB Atlas Configuration end ---------------------------- #

# -------------------------- ML pickel import start ---------------------------- #
extractorObj = pickle.load(open('resumeExtractor.pkl', 'rb'))
categorizerObj = pickle.load(open('resumeCategorizer.pkl', 'rb'))
# --------------------------- ML pickel import end ----------------------------- #

app.config['UPLOAD_FOLDER'] = 'static/resumes/'

@app.route('/')
def home():
	return render_template("index.html")

@app.route('/emp')
def emp():
	if 'user_id' in session and 'user_name' in session:
		return render_template('EmployeeDashboard.html')
	else:
		# return render_template('index.html', errorMsg='Login First')
		return redirect('/')

@app.route('/login')
def login():
	authorization_url, state = flow.authorization_url()
	session['state'] = state
	return redirect(authorization_url)

@app.route('/callback')
def callback():
	flow.fetch_token(authorization_response=request.url)

	if not session['state'] == request.args['state']:
		abort(500) # state does not match!

	credentials = flow.credentials
	request_session = requests.session()
	cached_session = cachecontrol.CacheControl(request_session)
	token_request = google.auth.transport.requests.Request(session=cached_session)

	id_info = id_token.verify_oauth2_token(
		id_token=credentials._id_token,
		request=token_request,
		audience=GOOGLE_CLIENT_ID
	)

	result = None
	result = IRS_USERS.find_one({'email':id_info.get('email')}, {'_id': 1})
	if result == None:
		session['user_id'] = str(IRS_USERS.insert_one({
			'name': id_info.get('name'),
			'email': id_info.get('email'),
			'google_id': id_info.get('sub')
		}).inserted_id)
		session['user_name'] = str(id_info.get('name'))
	else:
		session['user_id'] = str(result['_id'])
		session['user_name'] = str(id_info.get('name'))

	return redirect('/emp')

@app.route('/logout')
def logout():
	session.pop('user_id', None)
	session.pop('user_name', None)
	return redirect('/')

def getExtension(filename):
	return filename.rsplit('.',1)[1].lower()

def allowedExtension(filename):
	permittedExtension = ['docx', 'pdf']
	return '.' in filename and getExtension(filename) in permittedExtension

@app.route('/uploadResume', methods=['POST'])
def uploadResume():
	if 'user_id' in session and 'user_name' in session:
		try:
			file = request.files['resume']
			filename = secure_filename(file.filename)
			if file and allowedExtension(file.filename):
				temp = resumeFetchedData.find_one(
					{'user_id': ObjectId(session['user_id'])}, 
					{'resume_title': 1}
				)
				if temp == None:
					pass
				else:
					resumeFetchedData.delete_one(
						{'user_id': ObjectId(session['user_id'])},
					)
					Ranked_resume.delete_one(
						{'user_id': ObjectId(session['user_id'])}, 
					)
					os.remove(os.path.join(app.config['UPLOAD_FOLDER'], temp['resume_title']))
				file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
				fetchedData = extractorObj.extractData(app.config['UPLOAD_FOLDER'] + filename, getExtension(filename))
				skillsPercentage = categorizerObj.screenResume(fetchedData[5])

				result = resumeFetchedData.insert_one({
					'user_id': ObjectId(session['user_id']),
					'name': fetchedData[0],
					'mobile_number': fetchedData[1],
					'email': fetchedData[2],
					'education': fetchedData[3],
					'skills': list(fetchedData[4]),
					'appear': 0,
					'resume_title': filename,
					'resume_data': fetchedData[5]
				})

				if result == None:
					return render_template('EmployeeDashboard.html', errorMsg='Problem in Resume Data Storage')
				else:
					result = Ranked_resume.insert_one({
						'user_id': ObjectId(session['user_id']),
						'top_skills': dict(skillsPercentage)
					})

					if result == None:
						return render_template('EmployeeDashboard.html', errorMsg='Problem in skills data storage')
					else:
						return render_template('EmployeeDashboard.html', successMsg='Resume Screening successful')
			else:
				return render_template('EmployeeDashboard.html', errorMsg='Document type not allowed')
		except:
			print('Resume Upload Failed')
	else:
		return render_template('index.html', errorMsg='Login First')

@app.route('/HR')
def HR():
	return render_template('CompanyDashboard.html')

@app.route('/viewDetails', methods=['POST', 'GET'])
def viewDetails():
	employee_id = request.form['employee_id']
	result = resumeFetchedData.find({ 'user_id' : ObjectId(employee_id) })
	data = result[0]
	result = {
		'name': data['name'],
		'email': data['email'],
		'mobile_number': data['mobile_number'],
		'skills': data['skills'],
		'education': data['education']
	}

	return jsonify(result)

@app.route('/empSearch', methods=['POST'])
def empSearch():
	category = str(request.form.get('category'))
	
	topEmployees = Ranked_resume.find(
		{'top_skills.' + category: {'$ne': None}},
		{'top_skills.' + category: 1, 'user_id': 1}
	).sort([('top_skills.' + category, -1)])

	if topEmployees == None:
		return render_template('CompanyDashboard.html', errorMsg='Problem in category fetch')
	else:
		selectedResume = {}
		count = 0
		
		for emp in topEmployees:
			data = IRS_USERS.find_one(
				{'_id': ObjectId(emp['user_id'])},
				{'_id': 1, 'name': 1, 'email': 1}
			)
			selectedResume[count] = {
				'_id': data['_id'],
				'name': data['name'],
				'email': data['email']
			}
			count += 1

		return render_template('CompanyDashboard.html', len=len(selectedResume), data=selectedResume)

if __name__ == "__main__":
	app.run(debug=True)
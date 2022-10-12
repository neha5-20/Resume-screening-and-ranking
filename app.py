from flask import Flask, render_template, request, session, redirect, abort
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
from google.oauth2 import id_token
from bson.objectid import ObjectId
from database import mongo
from applicant import applicant
from employer import employer
import os
import pathlib
import requests
import google.auth.transport.requests
import bcrypt

import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.register_blueprint(applicant, url_prefix='/applicant')
app.register_blueprint(employer, url_prefix='/employer')

# ------------------------- Google OAuth Configuration start ----------------------------- #

# it is necessary to set a password when dealing with OAuth 2.0
app.secret_key = "ragnosva"

# this is to set our environment to https because OAuth 2.0 only supports https environments
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1" 

# enter your client id you got from Google console
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')

# set the path to where the .json file you got Google console is
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, 'client_secret.json')

# Flow is OAuth 2.0 a class that stores all the information on how we want to authorize our users
flow = Flow.from_client_secrets_file(
	client_secrets_file = client_secrets_file,
	# here we are specifing what do we get after the authorization
	scopes = [
		"https://www.googleapis.com/auth/userinfo.profile", 
		"https://www.googleapis.com/auth/userinfo.email", 
		"openid"
	],
	# and the redirect URI is the point where the user will end up after the authorization
	redirect_uri = "http://127.0.0.1:5000/callback"
)

# -------------------------- Google OAuth Configuration end ---------------------------- #


# -------------------------------- MongoDB Collections --------------------------------- #
Users = mongo.db.Users
# -------------------------------- MongoDB Collections --------------------------------- #

def profileHome():
	if session['profile'] == 'applicant':
		return '/applicant'
	elif session['profile'] == 'employer':
		return '/employer'
	return '/profile'

@app.route('/')
def home():
	return render_template("index.html")

@app.route('/email-signup', methods=['POST', 'GET'])
def emailSignUp():
	if 'user_id' in session and 'user_name' in session:
		return redirect(profileHome())
	else:
		if request.method == 'POST':
			message = ''
	
			user = request.form.get('name')
			email = request.form.get('email')

			password1 = request.form.get('password1')
			password2 = request.form.get('password2')

			user_found = Users.find_one({'name': user})
			email_found = Users.find_one({'email': email})

			if user_found:
				message = 'There already is a user by that name'
				return render_template('index.html', errorMsg=message)
			
			if email_found:
				message = 'There already is a user by that email'
				return render_template('index.html', errorMsg=message)

			if password1 != password2:
				message = 'Passwords shoud match!'
				return render_template('index.html', errorMsg=message)

			else:
				hashed = bcrypt.hashpw(password1.encode('utf-8'), bcrypt.gensalt())
				user_input = {
					'name': user,
					'email': email,
					'password': hashed,
					'profile': None
				}

				session['user_id'] = str(Users.insert_one(user_input).inserted_id)
				session['user_name'] = str(user_input['name'])

			return redirect('/profile')

		else:
			return render_template('signup.html')

@app.route('/email-login')
def emailLogin():
	if 'user_id' in session and 'user_name' in session:
		return redirect(profileHome())
	else:
		return render_template('login.html')

@app.route('/login', methods=['POST'])
def login2():

	message = 'Please login to  your account'

	email = request.form.get('email')
	password = request.form.get('password')

	user_found = Users.find_one({ 'email': email })

	if user_found == None:
		message = 'email not found'
		return render_template('login.html', errorMsg=message)

	else:
		if hasattr(user_found, 'google_id'):
			message = 'This email id was used to login using Google Account'
			return render_template('login.html', errorMsg=message)

		password_check = user_found['password']

		if bcrypt.checkpw(password.encode('utf-8'), password_check):
			session['user_id'] = str(user_found['_id'])
			session['user_name'] = str(user_found['name'])
			session['profile'] = str(user_found['profile'])
			return redirect(profileHome())
		else:
			message = 'Wrong Password'
			return render_template('login.html', errorMsg=message)
	
@app.route('/google-login')
def login():
	if 'user_id' in session and 'user_name' in session:
		return redirect(profileHome())
	else:
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
	result = Users.find_one({'email':id_info.get('email')}, {'_id': 1, 'name': 1, 'profile': 1})
	
	if result == None:
		session['user_id'] = str(Users.insert_one({
			'name': id_info.get('name'),
			'email': id_info.get('email'),
			'google_id': id_info.get('sub'),
			'profile': None
		}).inserted_id)
		session['user_name'] = str(id_info.get('name'))
	else:
		session['user_id'] = str(result['_id'])
		session['user_name'] = str(result['name'])
		session['profile'] = str(result['profile'])

		return redirect(profileHome())

	return redirect('/profile')

@app.route('/profile', methods=['POST', 'GET'])
def profile():
	if request.method == 'POST':
		choice = request.args.get('profile')

		session['profile'] = choice
		Users.find_one_and_update(
			{'_id': ObjectId(session['user_id'])},
			{ '$set': { 'profile': choice } }
		)
		return redirect(profileHome())
	return render_template("profile.html")

@app.route('/logout')
def logout():
	session.pop('user_id', None)
	session.pop('user_name', None)
	session.pop('profile', None)
	return redirect('/')



if __name__ == "__main__":
	app.run(debug=True)
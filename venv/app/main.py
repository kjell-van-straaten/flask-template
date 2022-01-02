from collections import namedtuple
from flask import Flask, render_template, request,g, redirect, session, Response, url_for
from app.functions import *
from app.classes import *
from bson import ObjectId
import datetime

app= Flask(__name__)
app.secret_key = 'courgette'

#establish connection to db
db1 = connect_db()

accounts = db1.Account

@app.before_request
def before_request():
  g.user = None
  if 'user_id' in session:
    #current_user = accounts.find_one({"_id": ObjectId(session['user_id'])})
    user = User(current_user['_id'],current_user['name'],current_user['password'], current_user['role'], current_user['team'])
    g.user = user

@app.route('/')
def index():
  return render_template('landingpage.html')

@app.route('/navbar')
def navbar():
  if g.user:
    current_user = g.user
      
  else:
    current_user = False

  return render_template('navbar.html', current_user=current_user)

@app.route('/logout')
def logout():
  session.pop('user_id', None)
  return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
   
    session.pop('user_id', None)

    username = request.form['username']
    password = request.form['password']

    #find instance associated to given name, if no instance is found NONE is returned
    login_user = accounts.find_one({"name": username})
    
    #if we have a user, and the decrypted passwords match then save new user id and redirect to tournaments page;
    if login_user and (login_user["password"] == hash(password)):
      user = User(login_user['_id'],login_user['name'],login_user['password'], login_user['role'], login_user['team'])
      session['user_id'] = str(user.id)
      return redirect("/")

    #else, redirect to login page again
    else:
      return render_template('login.html', failed = True)

  else: 
    return render_template('login.html')

#page for creating account, POST account into database, w/ encrypted password
@app.route('/signup', methods=['POST', 'GET'])
def signup():
  if request.method == 'POST':
    username = request.form['username']
    password = request.form['password']
    email = request.form['email']
    team = request.form['team']

    if accounts.find_one({"name": username}):
      return render_template('signup.html', failed = True) 

    else:
      create_record(accounts, [username, email, hash(password), 'none', team])
      return redirect('/login')

  return render_template('signup.html')



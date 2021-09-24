from flask import Flask, render_template, request,g, redirect, session, Response, url_for
#from app.functions import *
from functions import *

app= Flask(__name__)
app.secret_key = 'courgette'

class User:
  def __init__(self, id, username, password):
    self.id = id
    self.username = username
    self.password = password

  def __repr__(self):
    return f'<User: {self.username}>'

users = []
users.append(User(id=1, username='admin', password='123'))

@app.before_request
def before_request():
  g.user = None
  if 'user_id' in session:
    user = [x for x in users if x.id == session['user_id']][0]
    g.user = user

@app.route('/')
#landing page; should have functionality on finding a tournament to bet on, or logging in for creating/overviewing owned tournaments.
def index():
  if not g.user:
    return redirect('/login')
  return "<h1>Faka ambre</h1>"

@app.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
    print("in post")
    session.pop('user_id', None)

    username = request.form['username']
    password = request.form['password']

    print(username)

    user = [x for x in users if x.username == username][0]
    if user and user.password == password:
      session['user_id'] = user.id
      return redirect("/")

    return redirect('/login')

  else: 
    return render_template('login.html')

#@app.route('/login')
#login page; add functionality to go to sign-up page, add functionality to check login, and save current logged in account (hard?)
#def login():
#  return render_template('login.html')

#TODO1: build page for creating account, POST account into database, w/ encrypted password
@app.route('/signup', METHODS=['POST', 'GET'])
def signup():
  if request.method == 'POST':
    username = request.form['username']
    password = request.form['password']
    email = request.form['email']

    if check_existence(username):
      return "account already exists"

    else:
      create_record(accounts, [username, fernet.encrypt(password.encode()), email])

  return render_template('signup.html')

#TODO2: build landing page post-login, overviewing tournaments, allowing to create tournament.
#@app.route('/tournaments')

#TODO3: build tournament overview (i.e. analytics dashboard, settings, leaderboards) for selected tournament in TODO2, based on logged in account (Hard!)
#@app.route('/tournaments/{tournament_name}')

#TODO4: build betting page for selected tournament, pulls active (in the next 7 days) matches, 
#and optionality to fill in scores which can be posted (only if owner of tournament!)
#@app.route('/bet/{tournament_name}')

#establish connection to db
db = connect_db()

#establish encryption
#fernet = encryption()

#fernet.encrypt(password.encode())
#fernet.decrypt(encPassword).decode()

accounts = db.Account
bets = db.Bet
matches = db.Match
tournaments = db.Tournaments



#create_record(accounts, ['BitchBoy2','No', '789'])


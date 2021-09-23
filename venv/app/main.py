from flask import Flask, render_template
from app.functions import *

app= Flask(__name__)

@app.route('/')
#landing page; should have functionality on finding a tournament to bet on, or logging in for creating/overviewing owned tournaments.
def index():
  return "<h1>Faka ambre</h1>"

@app.route('/login')
#login page; add functionality to go to sign-in page, add functionality to check login, and save current logged in account (hard?)
def login():
  return render_template('login.html')

#TODO1: build page for creating account, POST account into database, w/ encrypted password
#@app.route('/sign_up')

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
fernet = encryption()

#fernet.encrypt(password.encode())
#fernet.decrypt(encPassword).decode()

accounts = db.Account
bets = db.Bet
matches = db.Match
tournaments = db.Tournaments



create_record(accounts, ['BitchBoy2','No', '789'])


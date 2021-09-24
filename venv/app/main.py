from flask import Flask, render_template, request,g, redirect, session, Response, url_for
from app.functions import *
from app.classes import *
from bson import ObjectId

app= Flask(__name__)
app.secret_key = 'courgette'

#establish connection to db
db = connect_db()

accounts = db.Account
bets = db.Bet
matches = db.Match
tournaments = db.Tournament

#establish encryption
fernet = encryption()

@app.before_request
def before_request():
  g.user = None
  if 'user_id' in session:
    current_user = accounts.find_one({"_id": ObjectId(session['user_id'])})
    user = User(current_user['_id'],current_user['name'],current_user['password'])
    g.user = user

@app.route('/', methods=['GET', 'POST'])
#landing page; should have functionality on finding a tournament to bet on, or logging in for creating/overviewing owned tournaments.
def index():
    if request.method == 'POST':
      tournament_name = request.form['search-term']
      tournament = tournaments.find_one({"name": tournament_name})
      if tournament:
        return redirect(url_for('bet_tournament', name=tournament_name))
      else:
        return render_template('home.html', failed=True)

    else:
      return render_template('home.html')

@app.route('/navbar')
def navbar():
  if g.user:
    current_user = g.user.username
  else:
    current_user = False
  return render_template('navbar.html', current_user=current_user)

@app.route('/logout')
def logout():
  print(session['user_id'] + 'logged out')
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
    if login_user and (fernet.decrypt(login_user["password"]).decode() == password):
      user = User(login_user['_id'],login_user['name'],login_user['password'])
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

    if accounts.find_one({"name": username}):
      return render_template('signup.html') #add argument that acc already exists

    else:
      create_record(accounts, [username, email, fernet.encrypt(password.encode())])
      return redirect('/login')

  return render_template('signup.html')

#TODO2: build landing page post-login, overviewing tournaments
@app.route('/tournaments')
def tournament_page():
  if not g.user:
    return redirect('/login')
  return render_template('tournaments.html')

#TODO2.5: create tournament page
@app.route('/create_tournament')
def create_tournaments():
  if not g.user:
    return redirect('/login')
  return render_template('createTournament.html')

#TODO3: build tournament overview (i.e. analytics dashboard, settings, leaderboards) for selected tournament in TODO2, based on logged in account (Hard!)
@app.route('/tournaments/{tournament_name}')
def tournament_overview():
  if not g.user:
    return redirect('/login')
  return render_template('tournamentOverview.html', tournament_name = "clicked tournament")

#TODO4: build betting page for selected tournament, pulls active (in the next 7 days) matches, 
#and optionality to fill in scores which can be posted (only if owner of tournament!)
@app.route('/bet/<name>')
def bet_tournament(name):
  return render_template('betTournament.html', name = name)

#fernet.encrypt(password.encode())


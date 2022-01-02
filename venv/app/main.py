from collections import namedtuple
from flask import Flask, render_template, request,g, redirect, session, Response, url_for
from app.functions import *
from app.classes import *
from bson import ObjectId
import datetime

app= Flask(__name__)
app.secret_key = 'courgette'

#establish connection to db
db1, db2 = connect_db()

accounts = db1.Account
bets = db1.Bet
matches = db1.Match
tournaments = db1.Tournament
euros = db2.Euros
fines = db2.Fines

#establish encryption
fernet = encryption()

@app.before_request
def before_request():
  g.user = None
  if 'user_id' in session:
    current_user = accounts.find_one({"_id": ObjectId(session['user_id'])})
    user = User(current_user['_id'],current_user['name'],current_user['password'], current_user['role'], current_user['team'])
    g.user = user

@app.route('/')
def index():
  return render_template('landingpage.html')

@app.route('/boetepot/config', methods=['GET', 'POST'])
def boetepot_config():
  if not g.user:
    return redirect('/login')
  
  elif 'boetepotmeester' not in g.user.roles:
    return redirect('/')

  if request.method == 'POST':
    if 'new_euro' in request.form:
      euro = request.form['name']
      description = request.form['description']
      team = g.user.team

      if euros.find_one({"name": euro}):
        team_euros = list(euros.find({"team": g.user.team}))
        return render_template('boetepotconfig.html', euros = team_euros, failed = True) 

      else:
        create_record(euros, [euro, description, team])
        team_euros = list(euros.find({"team": g.user.team}))
        return render_template('boetepotconfig.html', euros = team_euros, success = True)

    else:
      euro = [v for k,v in request.form.to_dict().items() if 'edit euro' in k][0]
      description = request.form['edit description {}'.format(euro)]
      euros.update_one({"name" : euro}, {"$set": {"description": description}})

  team_euros = list(euros.find({"team": g.user.team}))
  return render_template('boetepotconfig.html', euros = team_euros)

@app.route('/boetepot/input', methods=['GET', 'POST'])
def boetepot_input():
  team_euros = list(
    euros.find({
      "team": g.user.team
    }))
  
  active_euros = [i['name'] for i in team_euros]

  users = ["Ilja", "Gijs", "Hodor", "Koen", "Youri", "Barbie", "Niels", "Kjell", "Bram", "Sander", "Ali", "Zdravko", "Evgeni"]

  if not g.user:
    return redirect('/login')
  
  elif 'boetepotmeester' not in g.user.roles:
    return redirect('/')

  if request.method == 'POST':
    if 'new_fine' in request.form:
      name = request.form['name']
      euro = request.form['euro']
      amount = request.form['amount']
      week = datetime.date.today().isocalendar().week
      team = g.user.team

      create_record(fines, [int(amount), euro, name, team, int(week)])
      team_fines = list(fines.find({"team": g.user.team}))
      return render_template('boetepotinput.html', fines = team_fines, success = True, euros = active_euros, users = users)

    else:
      fine = [v for k,v in request.form.to_dict().items() if 'edit fine' in k][0]

      fines.delete_one({"_id": ObjectId(fine)})

  team_fines = list(fines.find({"team": g.user.team}))
  return render_template('boetepotinput.html', fines = team_fines, euros = active_euros, users = users)

@app.route('/boetepot', methods=['GET', 'POST'])
def boetepot():
  if not g.user:
    return redirect('/login')
  
  if 'boetepotlezer' not in g.user.roles:
    return redirect('/')

  team_euros = list(
    euros.find({
      "team": g.user.team
    }))

  team_fines = list(fines.aggregate(
        [
          {"$match":
            {
              'team': g.user.team
            }
          },
          {
            "$group":
              {
                "_id": "$name",
                "euros": {"$sum": "$amount" }
              }
          }
        ]
      ))
  team_fines = sorted(team_fines, key=lambda d: d['euros'], reverse=True) 

  total_amount = list(fines.aggregate(
        [
          {"$match":
            {
              'team': g.user.team
            }
          },
          {
            "$group":
              {
                "_id": 1,
                "euro": {"$sum": "$amount" }
              }
          }
        ]
      ))[0]['euro']

  euro_fines = list(fines.aggregate(
        [
          {"$match":
            {
              'team': g.user.team
            }
          },
          {
            "$group":
              {
                "_id": "$euro",
                "euro": {"$sum": "$amount" }
              }
          }
        ]
      ))
  euro_fines = sorted(euro_fines, key=lambda d: d['euro'], reverse=True) 

  week_fines = list(fines.aggregate(
        [
          {"$match":
            {
              'team': g.user.team
            }
          },
          {
            "$group":
              {
                "_id": "$week",
                "euro": {"$sum": "$amount" }
              }
          }
        ]
      ))
  week_fines = sorted(week_fines, key=lambda d: d['euro'], reverse=True) 

  return render_template('boetepot.html', current_user = g.user, euros=team_euros, fines=team_fines, total_amount = total_amount, euro_fines = euro_fines, week_fines = week_fines)

@app.route('/totolanding', methods=['GET', 'POST'])
#landing page; should have functionality on finding a tournament to bet on, or logging in for creating/overviewing owned tournaments.
def toto():
  all_tournaments = list(tournaments.find({}))
  return render_template('totolanding.html', tournaments = all_tournaments)
  # if request.method == 'POST':
  #   tournament_name = request.form['search-term']
  #   tournament = tournaments.find_one({"name": tournament_name})
  #   if tournament:
  #     return redirect(url_for('bet_tournament', name=tournament_name))
  #   else:
  #     return render_template('home.html', failed=True)
  # else:
  #   return render_template('home.html', tournaments = all_tournaments)

@app.route('/navbar')
def navbar():
  toto, boetepotmeester, boetepotlezer = False, False, False
  if g.user:
    current_user = g.user

    if 'toto' in g.user.roles:
      toto = True
    if 'boetepotmeester' in g.user.roles:
      boetepotmeester = True
    if 'boetepotlezer' in g.user.roles:
      boetepotlezer = True
      
  else:
    current_user = False

  return render_template('navbar.html', current_user=current_user, toto=toto, boetepotmeester=boetepotmeester, boetepotlezer=boetepotlezer)

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
    if login_user and (fernet.decrypt(login_user["password"]).decode() == password):
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
      create_record(accounts, [username, email, fernet.encrypt(password.encode()), 'none', team])
      return redirect('/login')

  return render_template('signup.html')

#landing page for tournaments, add statistics per tournament
@app.route('/tournaments', methods=['POST', 'GET'])
def tournament_page():
  if not g.user:
    return redirect('/login')

  else:
    user_tournaments = list(tournaments.find({"owner": g.user.username}))

    if request.method == 'POST':
      tournament_name = request.form['tournamentname']

      if not tournaments.find_one({"name": tournament_name}):
        create_record(tournaments, [tournament_name, g.user.username])
        return render_template('tournaments.html', user_tournaments=user_tournaments, success = True)

      else:
        return render_template('tournaments.html', user_tournaments=user_tournaments, failed = True)

    return render_template('tournaments.html', user_tournaments=user_tournaments)

#TODO3: build tournament overview (i.e. analytics dashboard, settings, leaderboards) for selected tournament, allow modifying results of matches
#TODO5: add possibility of deleting matches
@app.route('/tournaments/<tournament_name>', methods=['GET', 'POST'])
def tournament_overview(tournament_name):
  scores = []
  #check if login
  if not g.user:
    return redirect('/login')

  #check ownership of tournament
  elif not g.user.username == tournaments.find_one({"name": tournament_name})['owner']:  
     return redirect("/")
  
  else:
    tournament_matches2 = find_tournament_matches(matches, tournament_name)

    outcomes = bets.aggregate(
        [
          {
            "$group":
              {
                "_id": "$name",
                "team": { "$first": "$team" },
                "score": {"$sum": "$outcome" },
                "perfect": { "$sum": "$perfect"},
                "predictions": {"$sum": 1}
              }
          }
        ]
      )

    for outcome in outcomes:
      scores.append(outcome)
          
    if request.method == 'POST':
      if 'new_match' in request.form:
        party_1 = request.form['party 1']
        party_2 = request.form['party 2']
        date = datetime.datetime.strptime(request.form['date'], '%Y-%m-%d')
        match_name = party_1 + ' - ' + party_2
        if not matches.find_one({"name": match_name}):
          create_record(matches, [match_name, date, g.user.username, party_1, party_2, tournament_name, 'n.a.', 'n.a.', 'n.a.'])
          tournament_matches2 = find_tournament_matches(matches, tournament_name)
          return render_template('matchesOverview.html', name = tournament_name, matches = tournament_matches2, success=True, scores = scores)

        else:
          return render_template('matchesOverview.html', name = tournament_name, matches = tournament_matches2, failed=True, scores = scores)
      
        
      else:
        match = [v for k,v in request.form.to_dict().items() if 'edit match' in k][0]
        party_1 = request.form['edit party 1 {}'.format(match)]
        party_2 = request.form['edit party 2 {}'.format(match)]

        if party_2 > party_1:
          winner = match.split('-')[1][1:]
        else:
          winner = match.split('-')[0][:-1]

        matches.update_one({"name" : match}, {"$set": {"result_1": party_1, "result_2": party_2, "winner": winner}})

        update_predictions(tournament_name, match, matches, bets)

        tournament_matches2 = find_tournament_matches(matches, tournament_name)

        return render_template('matchesOverview.html', name = tournament_name, matches = tournament_matches2, scores = False)

    else: 
      return render_template('matchesOverview.html', name = tournament_name, matches = tournament_matches2, scores = scores)

@app.route('/toto/<name>', methods=['GET', 'POST'])
def bet_tournament(name):
  active_matches = list(
    matches.find({
      "tournament": name, 
      "date": {"$gte": datetime.datetime.today(), "$lte": datetime.datetime.today() + datetime.timedelta(days=5)}
    }))

  active_matches2 = []

  for tourny_match in active_matches:
      tourny_match['date'] = tourny_match['date'].date()
      active_matches2.append(tourny_match)

  if request.method == 'POST':
    better_name = request.form['name']
    email = request.form['e-mail']
    
    if better_name == '' or email == '':
      return render_template('toto.html', name = name, matches=active_matches2, failed=True)
      
    else:
      input = request.form.to_dict()
      unique_matches = [k[12:] for k,v in input.items() if 'bet party 1' in k]

      for match in unique_matches:
        match_object = matches.find_one({"tournament": name, "name": match})

        party_1 = [v for k,v in input.items() if (match in k and 'party 1' in k)][0]
        party_2 = [v for k,v in input.items() if (match in k and 'party 2' in k)][0]

        if party_2 > party_1:
          winner = match.split('-')[1][1:]
        else:
          winner = match.split('-')[0][:-1]

        create_record(bets, [name, match, winner, party_1, party_2, better_name, email, '0', '0', match_object['date']])

      return render_template('toto.html', name = name, matches=active_matches2, success=True)


  return render_template('toto.html', name = name, matches=active_matches2)


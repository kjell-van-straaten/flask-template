from flask import Flask, render_template
from app.functions import *

app= Flask(__name__)
@app.route('/')
def index():
  return "<h1>Faka ambre</h1>"


@app.route('/login')
def login():
  return render_template('login.html')


db = connect_db()

accounts = db.Account
bets = db.Bet
matches = db.Match
tournaments = db.Tournaments

create_record(accounts, ['BitchBoy2','No', '789'])


from app.functions import create_record
from flask import Flask

from functions import *

app= Flask(__name__)
@app.route('/')
def index():
  return "<h1>Faka ambre</h1>"

db = connect_db()

accounts = db.Account
bets = db.Bet
matches = db.Match
tournaments = db.Tournaments

create_record(accounts, ['BitchBoy2','No', '789'])


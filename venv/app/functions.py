from pymongo import MongoClient
from cryptography.fernet import Fernet
import ssl


def connect_db():
    test_str = "7yPxFfQLlq1ssIIm"
    access_line = "mongodb+srv://admin:{}@cluster0.mdtqp.mongodb.net/myFirstDatabase?retryWrites=true&w=majority".format(test_str)
    client = MongoClient(access_line, ssl_cert_reqs=ssl.CERT_NONE)
    db1 = client.get_database("TournamentApp")
    db2 = client.get_database("Boetepot")
    return db1, db2

def encryption():
    key = b's81T7YjKtDgGwZs5etFstUsFE6ndduFkdct-OT-k7Rg='
    fernet = Fernet(key)
    return fernet

def create_record(table, attributes: list):
    keys = table.find_one().keys()
    
    new_entry= dict()

    index = 0

    for key in keys:
        if key != '_id':
            new_entry[key]=attributes[index]
            index += 1

    result = table.insert_one(new_entry)
    return result
    
def update_predictions(tournament_name, match_name: str, matches_table, bets_table):
    match = matches_table.find_one({"name": match_name, "tournament": tournament_name})
    winner = match['winner']
    result = match['result_1'] + '-' + match['result_2']

    bets = list(bets_table.find({"tournament": tournament_name, "match": match_name}))

    for bet in bets:
        if winner == bet['prediction']:
            outcome = 1
            if result == (bet['party 1'] + '-' + bet['party 2']):
                perfect = 1
            else:
                perfect = 0
        else:
            outcome, perfect = 0, 0

        bets_table.update_one({"_id" : bet['_id']}, {"$set": {"outcome": outcome, "perfect": perfect}})

def find_tournament_matches(matches_table, tournament_name):

    tournament_matches = list(matches_table.find({"tournament": tournament_name}))

    tournament_matches2 = []

    for tourny_match in tournament_matches:
      tourny_match['date'] = tourny_match['date'].date()
      tournament_matches2.append(tourny_match)
    
    return tournament_matches2
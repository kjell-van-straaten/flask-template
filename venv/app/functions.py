from pymongo import MongoClient
from cryptography.fernet import Fernet
import ssl


def connect_db():
    test_str = "7yPxFfQLlq1ssIIm"
    access_line = "mongodb+srv://admin:{}@cluster0.mdtqp.mongodb.net/myFirstDatabase?retryWrites=true&w=majority".format(test_str)
    client = MongoClient(access_line, ssl_cert_reqs=ssl.CERT_NONE)
    db = client.get_database("TournamentApp")
    return db

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
    
    
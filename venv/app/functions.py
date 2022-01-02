from pymongo import MongoClient
import ssl


def connect_db():
    test_str = "7yPxFfQLlq1ssIIm"
    access_line = "mongodb+srv://admin:{}@cluster0.mdtqp.mongodb.net/myFirstDatabase?retryWrites=true&w=majority".format(test_str)
    client = MongoClient(access_line, ssl_cert_reqs=ssl.CERT_NONE)
    db1 = client.get_database("CollectionName")
    return db1

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

import json

from google.cloud import pubsub_v1
from pymongo import MongoClient
from time import sleep

# env
PATH_KEY = 'projectunigap-9c392d765774.json'
PROJECT_ID = 'projectunigap'
TOPIC_NAME = 'glamira-streaming'

# Connect to Mongo
# mg_client = MongoClient('mongodb://glamira:admin@127.0.0.1:27017/?authMechanism=DEFAULT&authSource=glamira')
# mg_db = mg_client['glamira']
# mg_collection = mg_db['summary']

mg_client = MongoClient('mongodb://localhost:27017')
mg_db = mg_client['glamira']
mg_collection = mg_db['glamira_raw']

lastTimeStamp = None

LIMIT=100

# Connect to Pub/Sub
publisher = pubsub_v1.PublisherClient.from_service_account_json(PATH_KEY)

try:
    fileReadLastTimeStamp = open("LastTimeStamp","r")
    lastTimeStamp = fileReadLastTimeStamp.read()
except:
    lastTimeStamp = None

if lastTimeStamp:
    documents = mg_collection.find({"time_stamp": {"$gt": int(lastTimeStamp)}}).limit(LIMIT).sort("time_stamp", 1)
else:
    documents = mg_collection.find().limit(LIMIT).sort("time_stamp", 1)

results = list(documents.clone())

# Query and puslish data
while(len(results) > 0):
    print("=================================")
    if lastTimeStamp is not None:
        print("Start send Pub/Sub from Timestamp: " + str(lastTimeStamp))
    else:
        print("Start send Pub/Sub from Timestamp from Beginning")

    for doc in results:
        lastTimeStamp = doc['time_stamp']
        doc.pop("_id")
        if 'option' in doc and 'category id' in doc['option']:
            doc['option']['category_id'] = doc['option'].pop('category id')

        data = (json.dumps(doc)).encode("utf-8")
        print("lastTimeStamp: " + str(lastTimeStamp) + " sent")

        topic_path = publisher.topic_path(PROJECT_ID, TOPIC_NAME)
        future = publisher.publish(topic_path, data)
        print(f"{future.result()}")

    try:
        fWriteLastTimeStamp = open("LastTimeStamp", "w")
        fWriteLastTimeStamp.write(str(lastTimeStamp))
        fWriteLastTimeStamp.close()
    except:
        lastTimeStamp = None

    sleep(60)   

    if lastTimeStamp:
        documents = mg_collection.find({"time_stamp": {"$gt": int(lastTimeStamp)}}).limit(LIMIT).sort("time_stamp", 1)
    else:
        documents = mg_collection.find().limit(LIMIT).sort("time_stamp", 1)

    results = list(documents.clone())

print('Done!')
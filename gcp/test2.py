# Python program to read
# json file
import requests
import json

# Opening JSON file
f = open('example_array.json')

# returns JSON object as 
# a dictionary
data = json.load(f)

# Iterating through the json
# list
for i in data:
    r = requests.post(url="https://us-central1-projectunigap.cloudfunctions.net/glamira-streaming-publisher-function", json=i)
    print(i, r.text)

# Closing file
f.close()
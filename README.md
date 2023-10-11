# Overview
- Developer: Phong Nguyen.
- Target release: 7 July, 2023.
- Epic: Architecture pipeline Glamira
- Coach: Huy Do.

# Overall requirement 
## Input
- Simulate Streaming (event data immediately) and Batching data (analytics by week) flow
- Component (GCS, BigQuery, CloudFunction, Spark Dataproc, Pub/Sub, ...)
## Output
- DA and DS: thinking insight (Session, Conference rate, click to rate, Decision..) or recommendation

# Setup local by using backup file and upload raw data to Google Cloud Storage

1. Prepare the evironment variables
```
MONGO_USERNAME=glamira
MONGO_PASS=admin
MONGO_DATABASE=glamira
MONGO_TABLE=summary

BACKUP_TIME=$(date '+%Y-%m-%d')
```

2. Restore Glamira dump folder
```
mongorestore -d $MONGO_DATABASE --uri="mongodb://$MONGO_USERNAME:$MONGO_PASS@localhost:27017" ./glamira
```

3. Export to json file
```
mongoexport -u=$MONGO_USERNAME -p=$MONGO_PASS --authenticationDatabase=admin -d $MONGO_DATABASE -c $MONGO_TABLE --type=json --out summary-$BACKUP_TIME.json
```

4. Remove fields not use
```
jq 'del(._id)' -c summary-$BACKUP_TIME.json > summary-$BACKUP_TIME-converted.json
```

5. Copy file to GPS Bucket
```
gsutil cp summary-$BACKUP_TIME-converted.json gs://${BUCKET}
```

# Reference
- https://cloud.google.com/compute/docs/general-purpose-machines
- https://cloud.google.com/dataproc/docs/guides/create-cluster
- https://cloud.google.com/dataproc/docs/guides/submit-job
- https://cloud.google.com/functions/docs/tutorials/pubsub
- https://cloud.google.com/pubsub/docs/publisher#publish-messages-to-a-topic
- https://bilgedemirkaya.medium.com/how-to-do-apache-beam-transform-with-mongodb-in-python-59e206a3802d
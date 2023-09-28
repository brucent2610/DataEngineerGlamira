# CloudFunction Pub/Sub Streaming Data

1. Prepare the evironment variables
```
PROJECT_ID=`gcloud config get-value project`
SERVICE_ACCOUNT=$(gsutil kms serviceaccount)
REGION=us-central1
PUBSUB_TOPICS=glamira-streaming
FUNCTION_GLAMIRA_STREAMING_PUBLISHER_NAME=glamira-streaming-publisher-function
FUNCTION_GLAMIRA_STREAMING_SUBSCRIBER_NAME=glamira-streaming-subscriber-function
DATAPROC_CLUSTER_NAME=glamira-dataproc
DATAPROC_BUCKET=glamira-dataproc-script
DATAPROC_BUCKET_URI=gs://${DATAPROC_BUCKET}/pyspark/glamira.py

2. Create Pub/Sub Streaming data
```
gcloud pubsub topics create $PUBSUB_TOPICS
```

3. Add permission
```
gcloud projects add-iam-policy-binding $PROJECT_ID --member serviceAccount:$SERVICE_ACCOUNT --role roles/pubsub.publisher
```

4. Create cloud function for Publisher
```
gcloud functions deploy ${FUNCTION_GLAMIRA_STREAMING_PUBLISHER_NAME} \
--gen2 \
--runtime=python311 \
--region=${REGION} \
--source=. \
--entry-point=index \
--max-instances=10 \
--trigger-http \
--set-env-vars PROJECT_ID=$PROJECT_ID,PUBSUB_TOPICS=$PUBSUB_TOPICS

gcloud functions delete ${FUNCTION_GLAMIRA_STREAMING_NAME} --region=$REGION
```

5. Test Cloud Function Publisher
```
curl -X POST https://$REGION-$PROJECT_ID.cloudfunctions.net/$FUNCTION_GLAMIRA_STREAMING_PUBLISHER_NAME -H "Content-Type:application/json" -d '{"message":"Hello World"}'
```

6. View Logs Publisher
```
gcloud beta functions logs read $FUNCTION_GLAMIRA_STREAMING_PUBLISHER_NAME --gen2 --limit=100 --region=$REGION
```

7. Create cloud function for Subscriber
```
gcloud functions deploy ${FUNCTION_GLAMIRA_STREAMING_SUBSCRIBER_NAME} \
--gen2 \
--runtime=python311 \
--region=${REGION} \
--source=. \
--entry-point=subscribe \
--max-instances=10 \
--trigger-topic=$PUBSUB_TOPICS \
--set-env-vars PROJECT_ID=$PROJECT_ID,REGION=$REGION,CLUSTER_NAME=$DATAPROC_CLUSTER_NAME,PYTHON_FILE_URI=$DATAPROC_BUCKET_URI

gcloud functions delete ${FUNCTION_GLAMIRA_STREAMING_SUBSCRIBER_NAME} --region=$REGION
```

8. View Logs Publisher
```
gcloud beta functions logs read $FUNCTION_GLAMIRA_STREAMING_SUBSCRIBER_NAME --gen2 --limit=100 --region=$REGION
```

9. Create Dataproc Cluster
```
gcloud dataproc clusters create $DATAPROC_CLUSTER_NAME \
--region=$REGION \
--master-machine-type=n2-standard-2 \
--master-boot-disk-size=30GB \
--master-boot-disk-type=pd-standard
```

10. Create Dataproc Bucket script
```
gsutil mb -c standard -l ${REGION} gs://${DATAPROC_BUCKET}
```

11. Sync Python script to Bucket
```
gsutil -m -o "GSUtil:parallel_thread_count=4" rsync -d -r . gs://${DATAPROC_BUCKET}/pyspark
```
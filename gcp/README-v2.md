# CloudFunction Pub/Sub Streaming Data

1. Prepare the evironment variables
```
PROJECT_ID=`gcloud config get-value project`
SERVICE_ACCOUNT=$(gsutil kms serviceaccount)
REGION=us-central1
PUBSUB_TOPICS=glamira-streaming
FUNCTION_GLAMIRA_STREAMING_PUBLISHER_NAME=glamira-streaming-publisher-function

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
curl -X POST https://$REGION-$PROJECT_ID.cloudfunctions.net/$FUNCTION_GLAMIRA_STREAMING_PUBLISHER_NAME -H "Content-Type:application/json" -d @example.json
```

6. View Logs Publisher
```
gcloud beta functions logs read $FUNCTION_GLAMIRA_STREAMING_PUBLISHER_NAME --gen2 --limit=100 --region=$REGION
```
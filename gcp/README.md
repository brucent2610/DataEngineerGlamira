# CloudFunction Pub/Sub Streaming Data

1. Prepare the evironment variables
```
PROJECT_ID=`gcloud config get-value project`
SERVICE_ACCOUNT=$(gsutil kms serviceaccount)
REGION=us-central1
PUBSUB_TOPICS=glamira-streaming
FUNCTION_GLAMIRA_STREAMING_NAME=glamira-streaming-function

2. Create Pub/Sub Streaming data
```
gcloud pubsub topics create $PUBSUB_TOPICS
gcloud pubsub subscriptions create --topic $PUBSUB_TOPICS $PUBSUB_TOPICS-sub
```

3. Add permission
```
gcloud projects add-iam-policy-binding $PROJECT_ID --member serviceAccount:$SERVICE_ACCOUNT --role roles/pubsub.publisher
```

4. Create cloud function
```
gcloud functions deploy ${FUNCTION_GLAMIRA_STREAMING_NAME} \
--gen2 \
--runtime=python37 \
--region=${REGION} \
--source=. \
--entry-point=index \
--max-instances=10 \
--set-env-vars GOOGLE_CLOUD_PROJECT=$PROJECT_ID
```
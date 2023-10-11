# CloudFunction Pub/Sub Streaming Data

1. Prepare the evironment variables
```
PROJECT_ID=`gcloud config get-value project`
SERVICE_ACCOUNT=$(gsutil kms serviceaccount)
REGION=us-central1
PUBSUB_TOPICS=glamira-streaming
FUNCTION_GLAMIRA_STREAMING_PUBLISHER_NAME=glamira-streaming-publisher-function

DATAFLOW_BUCKET=glamira-dataflow-bucket
DATAFLOW_RUNNER=DataflowRunner
DATAFLOW_GCS_OUTPUT=$PROJECT_ID-cloud-data-lake
DATAFLOW_WINDOW_DURATION=60
DATAFLOW_ALLOWED_LATENESS=1
DATAFLOW_DEADLETTER_BUCKET=$PROJECT_ID-cloud-data-lake

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

7. Install Apache Beam package
```
python3 -m pip install apache-beam[gcp]
```

8. Create bucket for store pipeline information
```
gsutil mb -c standard -l ${REGION} gs://$DATAFLOW_BUCKET
```

9. Run pipeline
```
python3 glamira_streaming_pipeline.py \
--project=${PROJECT_ID} \
--region=${REGION} \
--staging_location=gs://${DATAFLOW_BUCKET}/staging \
--temp_location=gs://${DATAFLOW_BUCKET}/temp \
--runner=${DATAFLOW_RUNNER} \
--topic=projects/${PROJECT_ID}/topics/${PUBSUB_TOPICS} \
--window_duration=${DATAFLOW_WINDOW_DURATION} \
--allowed_lateness=${DATAFLOW_ALLOWED_LATENESS} \
--dead_letter_bucket=gs://${DATAFLOW_DEADLETTER_BUCKET}/glamira/error \
--output_bucket=gs://${DATAFLOW_GCS_OUTPUT}/glamira/output
```
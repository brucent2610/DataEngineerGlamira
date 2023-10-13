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
DATAFLOW_TEMPLATE_IMAGE="gcr.io/$PROJECT_ID/dataflow/glamira_pipeline:latest"
DATAFLOW_TEMPLATE_PATH="gs://${DATAFLOW_BUCKET}/templates/glamira_pipeline.json"
DATAFLOW_JOB_NAME="glamira-streaming-event-pipeline"

VM_NAME=glamira-mongodb

FIREWALL_RULE_NAME=rule-allow-tcp-27017-dataflow

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
--output_bucket=gs://${DATAFLOW_GCS_OUTPUT}/glamira/output \
--output_mongo_uri=mongodb://glamira:glamira@10.128.0.15:27017/glamira
```

10. Create VM for MongoDB
```
gcloud compute instances create $VM_NAME \
  --machine-type=e2-micro \
  --zone ${ZONE} \
  --image-project=ubuntu-os-cloud \
  --image-family=ubuntu-2204-lts \
  --boot-disk-size=20G
  --scopes=storage-rw
```

11. Add firewall
```
gcloud compute firewall-rules create $FIREWALL_RULE_NAME \
    --network "default" \
    --action allow \
    --direction "ingress" \
    --target-tags dataflow \
    --source-tags dataflow \
    --priority 0 \
    --rules tcp:27017
gcloud compute instances add-tags $VM_NAME --tags dataflow
gcloud compute firewall-rules list
```

12. Build Custom Fex Template
```
gcloud config set builds/use_kaniko True
gcloud builds submit --tag $DATAFLOW_TEMPLATE_IMAGE .
gcloud beta dataflow flex-template build $DATAFLOW_TEMPLATE_PATH \
  --image "$DATAFLOW_TEMPLATE_IMAGE" \
  --sdk-language "PYTHON" \
  --metadata-file "metadata.json"
```

13. Run Dataflow Job by Template
```
gcloud beta dataflow flex-template run ${DATAFLOW_JOB_NAME}-$(date +%Y%m%H%M$S) \
  --region=$REGION \
  --template-file-gcs-location ${DATAFLOW_TEMPLATE_PATH} \
  --parameters "project=${PROJECT_ID},region=${REGION},staging_location=gs://${DATAFLOW_BUCKET}/staging,temp_location=gs://${DATAFLOW_BUCKET}/temp,topic=projects/${PROJECT_ID}/topics/${PUBSUB_TOPICS},window_duration=${DATAFLOW_WINDOW_DURATION},allowed_lateness=${DATAFLOW_ALLOWED_LATENESS},dead_letter_bucket=gs://${DATAFLOW_DEADLETTER_BUCKET}/glamira/error,output_bucket=gs://${DATAFLOW_GCS_OUTPUT}/glamira/output,output_mongo_uri=mongodb://glamira:glamira@10.128.0.15:27017/glamira"
```

14. Run Dataflow Job by Template
```
python3 glamira_streaming_pipeline.py \
--project=${PROJECT_ID} \
--region=${REGION} \
--sdk_container_image=$DATAFLOW_TEMPLATE_IMAGE \
--staging_location=gs://${DATAFLOW_BUCKET}/staging \
--temp_location=gs://${DATAFLOW_BUCKET}/temp \
--runner=${DATAFLOW_RUNNER} \
--topic=projects/${PROJECT_ID}/topics/${PUBSUB_TOPICS} \
--window_duration=${DATAFLOW_WINDOW_DURATION} \
--allowed_lateness=${DATAFLOW_ALLOWED_LATENESS} \
--dead_letter_bucket=gs://${DATAFLOW_DEADLETTER_BUCKET}/glamira/error \
--output_bucket=gs://${DATAFLOW_GCS_OUTPUT}/glamira/output \
--output_mongo_uri=mongodb://glamira:glamira@10.128.0.15:27017/glamira
--sdk_location=container
```
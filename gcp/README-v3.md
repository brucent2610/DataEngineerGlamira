# CloudFunction Pub/Sub Streaming Data UnigapProject

1. Prepare the evironment variables
```
PROJECT_ID=`gcloud config get-value project`
SERVICE_ACCOUNT=$(gsutil kms serviceaccount)
REGION=us-central1
ZONE=us-central1-a
PUBSUB_TOPICS=glamira-streaming
FUNCTION_GLAMIRA_STREAMING_PUBLISHER_NAME=glamira-streaming-publisher-function

DATAFLOW_BUCKET=glamira-dataflow-bucket
DATAFLOW_RUNNER=DataflowRunner
DATAFLOW_GCS_OUTPUT=glamira-gcs
DATAFLOW_WINDOW_DURATION=1800
DATAFLOW_ALLOWED_LATENESS=1
DATAFLOW_DEADLETTER_BUCKET=glamira-gcs-deadletter
DATAFLOW_TEMPLATE_IMAGE="gcr.io/$PROJECT_ID/dataflow/glamira_pipeline:dev-v1"
DATAFLOW_TEMPLATE_PATH="gs://${DATAFLOW_BUCKET}/templates/glamira_pipeline.json"
DATAFLOW_JOB_NAME="glamira-streaming-event-pipeline"

VM_NAME=vm-mongo
VM_IP=10.128.0.18
VM_MONGO_USER=glamira
VM_MONGO_PASSWORD=QNscg2hBKCuCHVsX6t9J
VM_MONGO_URI=mongodb://${VM_MONGO_USER}:${VM_MONGO_PASSWORD}@${VM_IP}:27017/glamira?authSource=admin
VM_MONGO_URI=mongodb+srv://${VM_MONGO_USER}:${VM_MONGO_PASSWORD}@${VM_IP}/glamira

FIREWALL_RULE_NAME=rule-allow-tcp-27017-dataflow

#Dev configuration
VM_IP=glamira.jp9f18n.mongodb.net
DATAFLOW_RUNNER=DirectRunner

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
--allow-unauthenticated \
--set-env-vars PROJECT_ID=$PROJECT_ID,PUBSUB_TOPICS=$PUBSUB_TOPICS

gcloud functions delete ${FUNCTION_GLAMIRA_STREAMING_NAME} --region=$REGION

gcloud functions add-iam-policy-binding ${FUNCTION_GLAMIRA_STREAMING_NAME} --member="allUsers" --role="roles/cloudfunctions.invoker" --region=$REGION

gcloud functions add-invoker-policy-binding ${FUNCTION_GLAMIRA_STREAMING_NAME} --region=$REGION --member="allUsers"
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
gsutil mb -c standard -l ${REGION} gs://$DATAFLOW_GCS_OUTPUT
gsutil mb -c standard -l ${REGION} gs://$DATAFLOW_DEADLETTER_BUCKET
```

9. Run pipeline
```
python3 glamira_streaming_pipeline.py \
--project=${PROJECT_ID} \
--region=${REGION} \
--staging_location=gs://${DATAFLOW_BUCKET}/staging \
--temp_location=gs://${DATAFLOW_BUCKET}/temp \
--runner=${DATAFLOW_RUNNER} \
--requirements_file=requirements.txt \
--topic=projects/${PROJECT_ID}/topics/${PUBSUB_TOPICS} \
--window_duration=${DATAFLOW_WINDOW_DURATION} \
--allowed_lateness=${DATAFLOW_ALLOWED_LATENESS} \
--dead_letter_bucket=gs://${DATAFLOW_DEADLETTER_BUCKET}/glamira_streaming_data \
--output_bucket=gs://${DATAFLOW_GCS_OUTPUT}/glamira_streaming_data \
--output_mongo_uri=${VM_MONGO_URI}
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
gcloud dataflow flex-template build $DATAFLOW_TEMPLATE_PATH \
  --image "$DATAFLOW_TEMPLATE_IMAGE" \
  --sdk-language "PYTHON" \
  --metadata-file "metadata.json"
```

13. Run Dataflow Job by Template
```
gcloud dataflow flex-template run ${DATAFLOW_JOB_NAME}-$(date +%Y%m%H%M$S) \
  --region=$REGION \
  --template-file-gcs-location ${DATAFLOW_TEMPLATE_PATH} \
  --parameters "project=${PROJECT_ID},region=${REGION},staging_location=gs://${DATAFLOW_BUCKET}/staging,temp_location=gs://${DATAFLOW_BUCKET}/temp,topic=projects/${PROJECT_ID}/topics/${PUBSUB_TOPICS},window_duration=${DATAFLOW_WINDOW_DURATION},allowed_lateness=${DATAFLOW_ALLOWED_LATENESS},dead_letter_bucket=gs://${DATAFLOW_DEADLETTER_BUCKET}/glamira_streaming_data,output_bucket=gs://${DATAFLOW_GCS_OUTPUT}/glamira_streaming_data,output_mongo_uri=${VM_MONGO_URI}
```
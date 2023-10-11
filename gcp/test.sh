#!/bin/bash
PROJECT_ID=`gcloud config get-value project`
REGION=us-central1
FUNCTION_GLAMIRA_STREAMING_PUBLISHER_NAME=glamira-streaming-publisher-function

for ((i=1; i<=20; i=i+1))
do 
    curl -X POST https://$REGION-$PROJECT_ID.cloudfunctions.net/$FUNCTION_GLAMIRA_STREAMING_PUBLISHER_NAME -H "Content-Type:application/json" -d @example.json
done

for ((i=1; i<=2; i=i+1))
do 
    curl -X POST https://$REGION-$PROJECT_ID.cloudfunctions.net/$FUNCTION_GLAMIRA_STREAMING_PUBLISHER_NAME -H "Content-Type:application/json" -d @example_fail.json
done
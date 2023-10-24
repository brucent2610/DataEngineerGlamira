#!/bin/bash
PROJECT_ID=projectunigap
REGION=us-central1
FUNCTION_GLAMIRA_STREAMING_PUBLISHER_NAME=glamira-streaming-publisher-function

for ((i=1366; i<=1000000; i=i+1))
do 
    echo "Success Event No: $i\n"
    curl -X POST https://$REGION-$PROJECT_ID.cloudfunctions.net/$FUNCTION_GLAMIRA_STREAMING_PUBLISHER_NAME -H "Content-Type:application/json" -d @example.json
    echo "\n"
done

for ((i=1; i<=100; i=i+1))
do 
    echo "Failed Event No: $i\n"
    curl -X POST https://$REGION-$PROJECT_ID.cloudfunctions.net/$FUNCTION_GLAMIRA_STREAMING_PUBLISHER_NAME -H "Content-Type:application/json" -d @example_fail.json
    echo "\n"
done

for ((i=1; i<=10; i=i+1))
do 
    echo "Failed JSON format Event No: $i\n"
    curl -X POST https://$REGION-$PROJECT_ID.cloudfunctions.net/$FUNCTION_GLAMIRA_STREAMING_PUBLISHER_NAME -H "Content-Type:application/json" -d @example_fail_not_json.json
    echo "\n"
done
import os
import base64

from cloudevents.http import CloudEvent
import functions_framework

from google.cloud import dataproc_v1 as dataproc
from google.cloud import storage

project_id = os.getenv('PROJECT_ID')
region = os.getenv('REGION')
cluster_name = os.getenv('CLUSTER_NAME')

def submit_job():
    # Create the job client.
    job_client = dataproc.JobControllerClient(
        client_options={"api_endpoint": f"{region}-dataproc.googleapis.com:443"}
    )

    # Create the job config. 'main_jar_file_uri' can also be a
    # Google Cloud Storage URL.
    job = {
        "placement": {"cluster_name": cluster_name},
        "spark_job": {
            "main_class": "org.apache.spark.examples.SparkPi",
            "python_file_uris": ["file:///usr/lib/spark/examples/jars/spark-examples.jar"],
            "args": ["1000"],
        },
    }

    operation = job_client.submit_job_as_operation(
        request={"project_id": project_id, "region": region, "job": job}
    )
    response = operation.result()

    # Dataproc job output gets saved to the Google Cloud Storage bucket
    # allocated to the job. Use a regex to obtain the bucket and blob info.
    matches = re.match("gs://(.*?)/(.*)", response.driver_output_resource_uri)

    output = (
        storage.Client()
        .get_bucket(matches.group(1))
        .blob(f"{matches.group(2)}.000000000")
        .download_as_bytes()
        .decode("utf-8")
    )

    print(f"Job finished successfully: {output}")

# [END dataproc_submit_job]

# Triggered from a message on a Cloud Pub/Sub topic.
@functions_framework.cloud_event
def subscribe(cloud_event: CloudEvent) -> None:
    # Print out the data from Pub/Sub, to prove that it worked
    print(
        "Hello, " + base64.b64decode(cloud_event.data["message"]["data"]).decode() + "!"
    )

# [END functions_cloudevent_pubsub]
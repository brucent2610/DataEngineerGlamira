import os
from google.cloud import pubsub_v1

# TODO(developer)
project_id = os.getenv('PROJECT_ID')
topic_id = os.getenv('PUBSUB_TOPICS')

publisher = pubsub_v1.PublisherClient()
# The `topic_path` method creates a fully qualified identifier
# in the form `projects/{project_id}/topics/{topic_id}`
topic_path = publisher.topic_path(project_id, topic_id)

def index(request):
    try:
        message = request.get_json().get('message')
        resPubSub = publisher.publish(topic_path, message.encode("utf-8"))
        print(resPubSub.result())
        return f"OK"
    except Exception as error:
        print("An exception occurred:", error) 
        return f"Not OK"
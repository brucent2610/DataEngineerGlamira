import os
from google.cloud import pubsub_v1

# TODO(developer)
# project_id = "your-project-id"
# topic_id = "your-topic-id"

publisher = pubsub_v1.PublisherClient()
# The `topic_path` method creates a fully qualified identifier
# in the form `projects/{project_id}/topics/{topic_id}`
topic_path = publisher.topic_path(project_id, topic_id)

def index(request):
    try:
        testAttribute = request.get_json().get('test')
        resPubSub = publisher.publish(topic_path, testAttribute)
        print(resPubSub.result())
        return f"OK"
    except:
        return f"Not OK"
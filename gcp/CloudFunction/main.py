import os
from google.cloud import pubsub_v1

def index(request):
    try:
        testAttribute = request.get_json().get('test')
        topic_name = 'projects/data-engineer-393307/topics/glamira-streaming'.format(
            project_id=os.getenv('GOOGLE_CLOUD_PROJECT'),
            topic='pubsub-publisher',
        )
        publisher.publish(topic_name, b'', testAttribute=testAttribute)
        return f"OK"
    except:
        return f"Not OK"
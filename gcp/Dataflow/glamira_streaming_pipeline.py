import json
import typing
import logging
import apache_beam as beam
from apache_beam.transforms.trigger import AccumulationMode, AfterCount, AfterWatermark
from apache_beam.transforms.combiners import CountCombineFn
import argparse

# {
#     "time_stamp": 1591266092,
#     "ip": "37.170.17.183",
#     "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1 Mobile/15E148 Safari/604.1",
#     "resolution": "375x667",
#     "user_id_db": "502567",
#     "device_id": "beb2cacb-20af-4f05-9c03-c98e54a1b71a",
#     "api_version": "1.0",
#     "store_id": "12",
#     "local_time": "2020-06-04 12:21:27",
#     "show_recommendation": "false",
#     "current_url": "https://www.glamira.fr/glamira-pendant-viktor.html?alloy=yellow-375",
#     "referrer_url": "https://www.glamira.fr/men-s-necklaces/",
#     "email_address": "pereira.vivien@yahoo.fr",
#     "recommendation": false,
#     "utm_source": false,
#     "utm_medium": false,
#     "collection": "view_product_detail",
#     "product_id": "110474",
#     "option": [
#         {
#             "option_label": "alloy",
#             "option_id": "332084",
#             "value_label": "",
#             "value_id": "3279318"
#         },
#         {
#             "option_label": "diamond",
#             "option_id": "",
#             "value_label": "",
#             "value_id": ""
#         }
#     ]
# }

class Event(typing.NamedTuple):
    time_stamp: int
    ip: str
    user_agent: str
    resolution: str
    user_id_db: str
    device_id: str
    api_version: str
    store_id: str
    local_time: str
    current_url: str
    referrer_url: str
    email_address: str
    recommendation: bool
    utm_source: boll
    collection: str
    product_id: str


beam.coders.registry.register_coder(Event, beam.coders.RowCoder)

class JsonToEvent(beam.DoFn):

    def process(self, line):
        row = json.loads(line)
        yield Event(**row)

class ConvertCountToDict(beam.DoFn):

    def process(self, element, window=beam.DoFn.WindowParam):
        window_start = window.start.to_utc_datetime().strftime("%Y-%m-%dT%H:%M:%S")
        output = {"event" : element, "timestamp_window": window_start}
        yield output

class EventTransform(beam.PTransform):

    def expand(self, pcoll):
        
        output = (pcoll | "ParseJson" >> beam.ParDo(JsonToEvent()))

        return output

def run():

    parser = argparse.ArgumentParser(description='Load from Json from Pub/Sub into Google Cloud Storage and MongoDB')

    parser.add_argument('--topic', required=True, help='Topic Pub/Sub')

    opts = parser.parse_args()

    topic = opts['topic']

    p = beam.Pipeline()

    (p 
        | "ReadFromPubSub" >> beam.io.ReadFromPubSub(topic=topic) 
        | "Transform" >> EventTransform()
        | "ConvertToDict" >> beam.ParDo(ConvertCountToDict())
    )

if __name__ == '__main__':
    run()
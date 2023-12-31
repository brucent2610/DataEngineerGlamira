import os

import json
import logging
import time
import argparse
import IP2Location
import apache_beam as beam

from datetime import datetime
from apache_beam.io import fileio
from apache_beam.io import mongodbio
from apache_beam.options.pipeline_options import GoogleCloudOptions
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.options.pipeline_options import StandardOptions
from apache_beam.transforms.trigger import AfterWatermark, AfterCount, AfterProcessingTime
from apache_beam.transforms.trigger import AccumulationMode
from apache_beam.transforms.combiners import CountCombineFn
from apache_beam.runners import DataflowRunner, DirectRunner

from google.cloud import storage
from typing import NamedTuple, List
from pymongo import MongoClient

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

class Option(NamedTuple):
    option_label: str
    option_id: str
    value_label: str
    value_id: str

class EventLog(NamedTuple):
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
    show_recommendation: str
    recommendation: bool
    utm_source: bool
    utm_medium: bool
    collection: str
    product_id: str
    option: List[Option]

beam.coders.registry.register_coder(EventLog, beam.coders.RowCoder)

class ConvertToEventLogFn(beam.DoFn):

    schema = {}

    def setup(self):
        try:
            # Download file schema db location in gcs
            storage_client = storage.Client()
            bucket = storage_client.get_bucket("glamira-gcs")
            blob = bucket.blob("schema/default.json")
            schema = blob.download_as_string(client=None)

            self.schema = json.loads(schema)
        except:
            raise ValueError("Failed to start ConvertToEventLogFn Bundle.")

    def process(self, element):
        try:
            row = json.loads(element.decode('utf-8'))
            for key in (self.schema).keys():
                if key not in row: 
                    row[key] = self.schema[key]
            yield beam.pvalue.TaggedOutput('parsed_row', row)
        except:
            if(element is None):
                yield beam.pvalue.TaggedOutput('unparsed_row', "")
            else:
                yield beam.pvalue.TaggedOutput('unparsed_row', element.decode('utf-8'))


class GetTimestampFn(beam.DoFn):
    def process(self, element, window=beam.DoFn.WindowParam):
        # window_start = window.start.to_utc_datetime().strftime("%Y-%m-%dT%H:%M:%S")
        # output = {'data': element, 'timestamp': window_start}
        # row = element._asdict()
        # yield json.dumps(row)
        yield json.dumps(element)

class UpdateMongoDB(beam.DoFn):

    def __init__(self, output_mongo_uri):
        self.output_mongo_uri = output_mongo_uri

    def connectMongoDB(self):
        try:
            self.mongodbClient = MongoClient(self.output_mongo_uri)
        except:
            raise ValueError("Failed to Connect Mongo UpdateMongoDB Bundle.")

    def setup(self):
        try:
            self.connectMongoDB()
        except ValueError:
            print("Setup UpdateMongoDB failed"):

    def process(self, element, window=beam.DoFn.WindowParam):
        database = self.mongodbClient['glamira']
        collection = database['events']
        print(element["activities"])
        collection.update_one({
            'device_id': element["device_id"]
        }, {
            '$set': {
                "activities": element["activities"]
            }
        })

    def teardown(self):
        if(self.mongodbClient is not None): 
            self.mongodbClient.close()

class TransformBeforeToMongoDBFn(beam.DoFn):

    def __init__(self, output_mongo_uri):
        self.databaseIps = None
        self.output_mongo_uri = output_mongo_uri

    def getDatabaseLocationFile(self):
        try:
            # Download file db location in gcs
            storage_client = storage.Client()
            bucket = storage_client.get_bucket("glamira-gcs")
            blob = bucket.blob("location/IP-COUNTRY.BIN")
            blob.download_to_filename("IP-COUNTRY.BIN")

            if(os.path.isfile("IP-COUNTRY.BIN")):
                # Initialize a IP2Location
                self.databaseIps = IP2Location.IP2Location("IP-COUNTRY.BIN")
            else:
                raise ValueError("File IP-COUNTRY.BIN download not exists TransformBeforeToMongoDBFn Bundle.")    
            
        except:
            raise ValueError("File IP-COUNTRY.BIN failed to download IP-COUNTRY.BIN TransformBeforeToMongoDBFn Bundle.")

    def connectMongoDB(self):
        try:
            self.mongodbClient = MongoClient(self.output_mongo_uri)
        except:
            raise ValueError("Failed to Connect Mongo TransformBeforeToMongoDBFn Bundle.")

    def setup(self):
        try:
            self.getDatabaseLocationFile()
            self.connectMongoDB()
        except ValueError:
            print("Setup TransformBeforeToMongoDBFn failed"):


    def process(self, element, window=beam.DoFn.WindowParam):
        # row = element._asdict()
        row = element
        if(row['device_id'] is None): 
            yield beam.pvalue.TaggedOutput('no_device_id_event', row)
        if(row['ip'] is not None):
            rec = self.databaseIps.get_all(row['ip'])
            row['country'] = rec.country_long
            # row['country'] = "Vietnam"
        database = self.mongodbClient['glamira']
        collection = database['events']
        device = collection.find_one({
            'device_id': row["device_id"]
        })
        if(device):
            row.pop("device_id")
            activities = device["activities"]
            activities.append(row)
            activities.sort(key=lambda x:x['time_stamp'], reverse=True)
            device["activities"] = activities[:5]
            yield beam.pvalue.TaggedOutput('update_device_id_event', device)
        else:
            event = {
                "device_id": row["device_id"]
            }
            row.pop("device_id")
            activities = [row]
            event["activities"] = activities
            yield beam.pvalue.TaggedOutput('create_device_id_event', event)

    def teardown(self):
        if(self.mongodbClient is not None): 
            self.mongodbClient.close()

def run():

    parser = argparse.ArgumentParser(description='Load from Json from Pub/Sub into Google Cloud Storage and MongoDB')

    parser.add_argument('--project', required=True, help='Project')
    parser.add_argument('--region', required=True, help='Region')
    parser.add_argument('--topic', required=True, help='Topic Pub/Sub')
    parser.add_argument('--staging_location', required=True, help='Staging Location')
    parser.add_argument('--temp_location', required=True, help='Temp Location')

    parser.add_argument('--window_duration', required=True, help='Window duration in seconds')
    parser.add_argument('--allowed_lateness', required=True, help='Allowed lateness')
    parser.add_argument('--output_bucket', required=True, help='GCS Output')
    parser.add_argument('--dead_letter_bucket', required=True, help='GCS Dead Letter Bucket')
    parser.add_argument('--runner', required=True, help='Specify Apache Beam Runner')
    parser.add_argument('--output_mongo_uri', required=True, help='URI MongoDB')

    opts, pipeline_opts = parser.parse_known_args()

    pipeline_opts.append("--max_num_workers=2")
    pipeline_opts.append("--save_main_session")
    pipeline_opts.append("--streaming")
    pipeline_opts.append("--allow_unsafe_triggers")
    pipeline_opts.append("--sdk_location=container")

    # Setting up the Beam pipeline options
    options = PipelineOptions(pipeline_opts)
    options.view_as(GoogleCloudOptions).project = opts.project
    options.view_as(GoogleCloudOptions).region = opts.region
    options.view_as(GoogleCloudOptions).job_name = '{0}{1}'.format('glamira-streaming-event-pipeline-',time.time_ns())
    options.view_as(StandardOptions).runner = opts.runner

    topic = opts.topic
    output_path = opts.output_bucket
    output_error_path = opts.dead_letter_bucket

    output_mongo_uri = opts.output_mongo_uri

    window_duration = opts.window_duration
    allowed_lateness = opts.allowed_lateness

    p = beam.Pipeline(options=options)

    rows = (p 
        | 'ReadFromPubSub' >> beam.io.ReadFromPubSub(topic)
        | 'ParseJson' >> beam.ParDo(ConvertToEventLogFn()).with_outputs('parsed_row', 'unparsed_row')
    )

    (rows.unparsed_row
        | 'BatchOver10s' >> beam.WindowInto(beam.window.FixedWindows(120), trigger=AfterProcessingTime(120), accumulation_mode=AccumulationMode.DISCARDING)
        | 'WriteUnparsedToGCS' >> fileio.WriteToFiles(output_error_path, shards=1, max_writers_per_bundle=0)
    )

    window_transforms = (rows.parsed_row
        | "WindowByMinute" >> beam.WindowInto(beam.window.FixedWindows(int(window_duration)), trigger=AfterWatermark(late=AfterCount(1)), allowed_lateness=int(allowed_lateness), accumulation_mode=AccumulationMode.ACCUMULATING)
        # | "CountPerMinute" >> beam.CombineGlobally(CountCombineFn()).without_defaults()
        # | "AddWindowTimestamp" >> beam.ParDo(GetTimestampFn())
    )

    (window_transforms 
        | "TransformBeforeToGCS" >> beam.ParDo(GetTimestampFn())
        | 'WriteparsedToGCS' >> fileio.WriteToFiles(output_path, shards=1, max_writers_per_bundle=0)
    )

    mongo_transformed = (window_transforms 
        | "TransformBeforeToMongoDB" >> beam.ParDo(TransformBeforeToMongoDBFn(output_mongo_uri)).with_outputs('no_device_id_event', 'update_device_id_event', 'create_device_id_event')
    )

    (mongo_transformed.no_device_id_event
        | 'WriteNoDeviceIdToGCS' >> fileio.WriteToFiles(output_error_path, shards=1, max_writers_per_bundle=0)
    )

    (mongo_transformed.update_device_id_event
        | "UpsertparsedToMongoDB" >> beam.ParDo(UpdateMongoDB(output_mongo_uri))
    )

    (mongo_transformed.create_device_id_event
        | 'WriteparsedToMongoDB' >> mongodbio.WriteToMongoDB(uri=output_mongo_uri, db='glamira', coll='events')
    )

    logging.getLogger().setLevel(logging.INFO)
    logging.info("Building pipeline ...")

    p.run().wait_until_finish()

if __name__ == '__main__':
    run()
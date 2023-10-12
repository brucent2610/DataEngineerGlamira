import logging
import json
import unittest
import sys

import apache_beam as beam

from glamira_streaming_pipeline import *
from apache_beam.testing.test_pipeline import TestPipeline
from apache_beam.testing.util import BeamAssertException
from apache_beam.testing.util import assert_that, equal_to_per_window, equal_to, is_empty
from apache_beam.testing.test_stream import TestStream
from apache_beam.transforms.window import TimestampedValue, IntervalWindow
from apache_beam.options.pipeline_options import PipelineOptions, StandardOptions

class ConvertToEventLogFnTest(unittest.TestCase):

    def test_convert_to_event_log(self):
        with TestPipeline() as p:
            request_data = {
                "time_stamp":1591266092,
                "ip":"37.170.17.183",
                "user_agent":"Mozilla/5.0 (iPhone; CPU iPhone OS 13_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1 Mobile/15E148 Safari/604.1",
                "resolution":"375x667",
                "user_id_db":"502567",
                "device_id":"beb2cacb-20af-4f05-9c03-c98e54a1b71a",
                "api_version":"1.0",
                "store_id":"12",
                "local_time":"2020-06-04 12:21:27",
                "show_recommendation":"false",
                "current_url":"https://www.glamira.fr/glamira-pendant-viktor.html?alloy=yellow-375",
                "referrer_url":"https://www.glamira.fr/men-s-necklaces/",
                "email_address":"pereira.vivien@yahoo.fr",
                "recommendation":False,
                "utm_source":False,
                "utm_medium":False,
                "collection":"view_product_detail",
                "product_id":"110474"
            }
            message = json.dumps(request_data)
            message = message.encode("utf-8")
            input_lines = p | beam.Create([message])
            output = (input_lines | beam.ParDo(ConvertToEventLogFn()).with_outputs('parsed_row', 'unparsed_row').with_output_types(EventLog))
            self.assertTrue(output.parsed_row is not None)
            assert_that(
                output.parsed_row,
                equal_to([
                    EventLog(
                        1591266092, 
                        "37.170.17.183", 
                        "Mozilla/5.0 (iPhone; CPU iPhone OS 13_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1 Mobile/15E148 Safari/604.1",
                        "375x667",
                        "502567",
                        "beb2cacb-20af-4f05-9c03-c98e54a1b71a",
                        "1.0",
                        "12",
                        "2020-06-04 12:21:27",
                        "https://www.glamira.fr/glamira-pendant-viktor.html?alloy=yellow-375",
                        "https://www.glamira.fr/men-s-necklaces/",
                        "pereira.vivien@yahoo.fr",
                        "false",
                        False,
                        False,
                        False,
                        "view_product_detail",
                        "110474"
                    )
                ]
            ))
            
    def test_convert_to_event_log_wrong_type(self):
        with TestPipeline() as p:
            request_data = {
                "time_stamp":"1591266092", #Wrong here
                "ip":"37.170.17.183",
                "user_agent":"Mozilla/5.0 (iPhone; CPU iPhone OS 13_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1 Mobile/15E148 Safari/604.1",
                "resolution":"375x667",
                "user_id_db":"502567",
                "device_id":"beb2cacb-20af-4f05-9c03-c98e54a1b71a",
                "api_version":"1.0",
                "store_id":"12",
                "local_time":"2020-06-04 12:21:27",
                "show_recommendation":"false",
                "current_url":"https://www.glamira.fr/glamira-pendant-viktor.html?alloy=yellow-375",
                "referrer_url":"https://www.glamira.fr/men-s-necklaces/",
                "email_address":"pereira.vivien@yahoo.fr",
                "recommendation":False,
                "utm_source":False,
                "utm_medium":False,
                "collection":"view_product_detail",
                "product_id":"110474"
            }
            message = json.dumps(request_data)
            message = message.encode("utf-8")
            input_lines = p | beam.Create([message])
            output = (input_lines | beam.ParDo(ConvertToEventLogFn()).with_outputs('parsed_row', 'unparsed_row').with_output_types(EventLog))
            self.assertTrue(output.unparsed_row is not None)
            assert_that(
                output.parsed_row,
                equal_to([
                    EventLog(
                        "1591266092", 
                        "37.170.17.183", 
                        "Mozilla/5.0 (iPhone; CPU iPhone OS 13_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1 Mobile/15E148 Safari/604.1",
                        "375x667",
                        "502567",
                        "beb2cacb-20af-4f05-9c03-c98e54a1b71a",
                        "1.0",
                        "12",
                        "2020-06-04 12:21:27",
                        "https://www.glamira.fr/glamira-pendant-viktor.html?alloy=yellow-375",
                        "https://www.glamira.fr/men-s-necklaces/",
                        "pereira.vivien@yahoo.fr",
                        "false",
                        False,
                        False,
                        False,
                        "view_product_detail",
                        "110474"
                    )
                ]
            ))

    def test_convert_to_event_log_failed_not_same_schema(self):
        with TestPipeline() as p:
            request_data = {"time_stamp":1591266092}
            message = json.dumps(request_data)
            message = message.encode("utf-8")
            input_lines = p | beam.Create([message])
            output = (input_lines | beam.ParDo(ConvertToEventLogFn()).with_outputs('parsed_row', 'unparsed_row').with_output_types(EventLog))
            self.assertTrue(output.unparsed_row is not None)
            assert_that(
                output.unparsed_row,
                equal_to([message.decode('utf-8')])
            )

    def test_convert_to_event_log_failed_not_json(self):
        with TestPipeline() as p:
            message = "aaa"
            message = message.encode("utf-8")
            input_lines = p | beam.Create([message])
            output = (input_lines | beam.ParDo(ConvertToEventLogFn()).with_outputs('parsed_row', 'unparsed_row').with_output_types(EventLog))
            self.assertTrue(output.unparsed_row is not None)
            assert_that(
                output.unparsed_row,
                equal_to([message.decode('utf-8')])
            )

    def test_convert_to_event_log_failed_message_none(self):
        with TestPipeline() as p:
            message = None
            input_lines = p | beam.Create([message])
            output = (input_lines | beam.ParDo(ConvertToEventLogFn()).with_outputs('parsed_row', 'unparsed_row').with_output_types(EventLog))
            self.assertTrue(output.unparsed_row is not None)
            assert_that(
                output.unparsed_row,
                equal_to([""])
            )

class TransformBeforeToMongoDBFnTest(unittest.TestCase):
    def test_convert_event_log_to_dict(self):
        with TestPipeline() as p:
            request_data = EventLog(
                1591266092, 
                "37.170.17.183", 
                "Mozilla/5.0 (iPhone; CPU iPhone OS 13_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1 Mobile/15E148 Safari/604.1",
                "375x667",
                "502567",
                "beb2cacb-20af-4f05-9c03-c98e54a1b71a",
                "1.0",
                "12",
                "2020-06-04 12:21:27",
                "https://www.glamira.fr/glamira-pendant-viktor.html?alloy=yellow-375",
                "https://www.glamira.fr/men-s-necklaces/",
                "pereira.vivien@yahoo.fr",
                "false",
                False,
                False,
                False,
                "view_product_detail",
                "110474"
            )
            input_lines = p | beam.Create([request_data])
            output = (input_lines | beam.ParDo(TransformBeforeToMongoDBFn()))
            self.assertTrue(output is not None)
            assert_that(
                output,
                equal_to([
                    {
                        "time_stamp":1591266092,
                        "ip":"37.170.17.183",
                        "user_agent":"Mozilla/5.0 (iPhone; CPU iPhone OS 13_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1 Mobile/15E148 Safari/604.1",
                        "resolution":"375x667",
                        "user_id_db":"502567",
                        "device_id":"beb2cacb-20af-4f05-9c03-c98e54a1b71a",
                        "api_version":"1.0",
                        "store_id":"12",
                        "local_time":"2020-06-04 12:21:27",
                        "show_recommendation":"false",
                        "current_url":"https://www.glamira.fr/glamira-pendant-viktor.html?alloy=yellow-375",
                        "referrer_url":"https://www.glamira.fr/men-s-necklaces/",
                        "email_address":"pereira.vivien@yahoo.fr",
                        "recommendation":False,
                        "utm_source":False,
                        "utm_medium":False,
                        "collection":"view_product_detail",
                        "product_id":"110474"
                    }
                ]
            ))

    def test_convert_event_log_to_dict_failed_missing(self):
        with TestPipeline() as p:
            with self.assertRaises(TypeError) as context:
                request_data = EventLog(
                    1591266092
                )
                input_lines = p | beam.Create([request_data])
                output = (input_lines | beam.ParDo(TransformBeforeToMongoDBFn()))

if __name__ == '__main__':
    unittest.main(verbosity=2)
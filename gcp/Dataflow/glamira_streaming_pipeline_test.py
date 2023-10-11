import logging
import json
import unittest
import sys

import apache_beam as beam

from glamira_streaming_pipeline import *
from apache_beam.testing.test_pipeline import TestPipeline
from apache_beam.testing.util import BeamAssertException
from apache_beam.testing.util import assert_that, equal_to_per_window
from apache_beam.testing.test_stream import TestStream
from apache_beam.transforms.window import TimestampedValue, IntervalWindow
from apache_beam.options.pipeline_options import PipelineOptions, StandardOptions

def main(out = sys.stderr, verbosity = 2):
    loader = unittest.TestLoader()
  
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    unittest.TextTestRunner(out, verbosity = verbosity).run(suite)

if __name__ == '__main__':
    with open('testing.out', 'w') as f:
        main(f)
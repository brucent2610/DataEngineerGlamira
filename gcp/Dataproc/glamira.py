#!/usr/bin/python

# Run Test
# spark-submit glamira.py '{"time_stamp": 1591266092, "ip": "37.170.17.183", "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1 Mobile/15E148 Safari/604.1", "resolution": "375x667", "user_id_db": "502567", "device_id": "beb2cacb-20af-4f05-9c03-c98e54a1b71a", "api_version": "1.0", "store_id": "12", "local_time": "2020-06-04 12:21:27", "show_recommendation": "false", "current_url": "https://www.glamira.fr/glamira-pendant-viktor.html?alloy=yellow-375", "referrer_url": "https://www.glamira.fr/men-s-necklaces/", "email_address": "pereira.vivien@yahoo.fr", "recommendation": false, "utm_source": false, "utm_medium": false, "collection": "view_product_detail", "product_id": "110474", "option": [{"option_label": "alloy", "option_id": "332084", "value_label": "", "value_id": "3279318"}, {"option_label": "diamond", "option_id": "", "value_label": "", "value_id": ""}]}'

import sys
import json

# Imports
from pyspark.sql import SparkSession

# Create SparkSession
spark = SparkSession.builder.appName('GlamiraStreaming').getOrCreate()

sc = spark.sparkContext

spark

def run():
    data = sys.argv[1]

    df = spark.read.json(sc.parallelize([data]))
    df.show(truncate=False)

run()
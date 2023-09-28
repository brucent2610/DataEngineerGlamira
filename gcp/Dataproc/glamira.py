#!/usr/bin/python
import pyspark
import sys

sc = pyspark.SparkContext()
rdd = sc.parallelize(['Hello,', 'world!'])
words = sorted(rdd.collect())
print(words)

data = sys.argv[1]
print(data)
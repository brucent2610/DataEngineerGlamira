#!/usr/bin/python
import pyspark
import sys

sc = pyspark.SparkContext()
rdd = sc.parallelize(['Hello,', 'world!'])
words = sorted(rdd.collect())
print(words)

n = int(sys.argv[1])
a = 2
for _ in range(n):
    print(a, sys.argv[a])
    a += 1
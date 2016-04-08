__author__ = 'Peeratham'

from pyspark import SparkContext

logFile = 'C:/Users/Peeratham/Downloads/spark-1.6.1-bin-hadoop2.6/README.md'  # Should be some file on your system
sc = SparkContext("local", "Simple App")
logData = sc.textFile(logFile).cache()

numAs = logData.filter(lambda s: 'a' in s).count()
numBs = logData.filter(lambda s: 'b' in s).count()

print("Lines with a: %i, lines with b: %i" % (numAs, numBs))

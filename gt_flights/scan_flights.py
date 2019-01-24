from __future__ import print_function
import boto3
import time
import csv
import sys

def item_count(tablename,region):
    dynamodb = boto3.resource('dynamodb', region_name=region)
    dynamodb_table = dynamodb.Table(tablename)
    itemcount = 0
    response = dynamodb_table.scan()
    itemcount += response['Count']

    while 'LastEvaluatedKey' in response:
        response = dynamodb_table.scan()
        itemcount += response['Count']
    return itemcount

if __name__ == "__main__":
    args = sys.argv[1:]
    tablename = args[0]
    region = args[1]
    print('Scanning table %s to get the total items' %(tablename))
    begin_time = time.time()
    total_count = item_count(tablename, region)
    print ('Total item count of table %s are %s  in %s seconds' % (tablename, total_count, time.time() - begin_time))



from __future__ import print_function
import boto3
from boto3.dynamodb.conditions import Key, Attr
import time
import sys

Query_attempt = 0

def query_gsi(tableName,attribute,value,):
    dynamodb = boto3.resource('dynamodb', region_name=region)
    table = dynamodb.Table(tableName)

    if attribute == 'name':
        ke = Key('colA').eq('master') & Key('name').eq(value)
    else:
        ke = "colA = :f"
        ke = Key('colA').eq(attribute + ":" + value)

    response = table.query(
        IndexName='gsi_of_gt',
        KeyConditionExpression=ke
        )

    print('List of employees with %s in the attribute %s:' % (value,attribute))
    for i in response['Items']:
        print('\tEmployee name: %s - hire date: %s' % (i['name'],i['hire_date']))

    return response['Count']

if __name__ == "__main__":
    args = sys.argv[1:]
    tableName = args[0]
    attribute = args[1]
    value = args[2]
    region = args[3]

    begin_time = time.time()
    Query_attempt += 1
    count = query_gsi(tableName,attribute,value)
    end_time = time.time()
    print ('Total no. of employees in %s attempt: %s. Query Start time: %s. End time: %s. Execution time: %s seconds' % (Query_attempt, count, begin_time, end_time, (end_time - begin_time)))


#

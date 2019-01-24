'''
### Sample data to query:
id:       5603280670,26806130,9902917690,1079996,2907581914,53600600,282027328,421920151,534890387,658410767
airlines: Quatar,British,Emirates,JetBlue,Delta,UnitedAirlines,Alaska,spirit,Republic,southwest
'''

from __future__ import print_function
import boto3
import time
import datetime
import csv
import sys

def query_flights(tablename, region):
    dynamodb = boto3.client('dynamodb', region_name=region)
    mypk_list = [5603280670, 26806130, 9902917690, 1079996, 2907581914, 53600600, 282027328, 421920151, 534890387,
                 658410767]
    for i in range(len(mypk_list)):
        value = str(mypk_list[i])
        eav = {":mypk": {"N": value}}
        my_query = dynamodb.query(
            TableName='flights',
            ConsistentRead=False,
            ProjectionExpression="flight_id, airlines_name, available_seats",
            KeyConditionExpression='flight_id= :mypk',
            ExpressionAttributeValues=eav
        )

        while 'LastEvaluatedKey' in my_query:
            my_query = dynamodb.query(
                TableName='flights',
                ConsistentRead=False,
                ProjectionExpression="flight_id, airlines_name, available_seats",
                KeyConditionExpression='flight_id= :mypk',
                ExpressionAttributeValues=eav)
        name = my_query['Items'][0]['airlines_name']['S']
        f_id = my_query['Items'][0]['flight_id']['N']
        seats = my_query['Items'][0]['available_seats']['N']
        print("Available seats in the %s flight %s are %s " % (name, f_id, seats))
    return my_query

if __name__ == "__main__":
    args = sys.argv[1:]
    tablename = args[0]
    region = args[1]
    start_time = time.time()
    query_result = query_flights(tablename, region)
    end_time = time.time()
    print('\nQuery start time: %s \nEndtime: %s \nTotal query time in seconds: %s. ' % (datetime.datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S'), datetime.datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S'), (end_time - start_time)))


from __future__ import print_function
import boto3
import time
import datetime
import csv
import sys

def update_flights_1(tablename, x, region_1):

    dynamodb = boto3.resource('dynamodb', region_name=region_1)
    dynamodb_table = dynamodb.Table(tablename)

    mypk_list = [5603280670, 26806130, 9902917690, 1079996, 2907581914, 53600600, 282027328, 421920151, 534890387, 658410767]
    mysk_list = ["Quatar", "British", "Emirates", "JetBlue", "Delta", "UnitedAirlines", "Alaska", "spirit", "Republic", "southwest"]

    i = 0
    for i in range(len(mypk_list)):
        mypk = mypk_list[i]
        mysk = mysk_list[i]
        my_update = dynamodb_table.update_item(
            Key={'flight_id': mypk, 'airlines_name': mysk},
            UpdateExpression="set available_seats = :seats",
            ExpressionAttributeValues={':seats': int(x)},
            ReturnValues="UPDATED_NEW"
        )
        print("Updated seat availability for flight:%s to %s" % (mypk, my_update['Attributes']['available_seats']))
    print("Flight availability Updated successfully")



def query_flights_1(tablename, region_1):
    dynamodb2 = boto3.client('dynamodb', region_name=region_1)
    mypk_list2 = [5603280670, 26806130, 9902917690, 1079996, 2907581914, 53600600, 282027328, 421920151, 534890387,
                 658410767]
    for i in range(len(mypk_list2)):
        value = str(mypk_list2[i])
        eav = {":mypk2": {"N": value}}
        my_query = dynamodb2.query(
            TableName='flights',
            ConsistentRead=False,
            ProjectionExpression="flight_id, airlines_name, available_seats",
            KeyConditionExpression='flight_id= :mypk2',
            ExpressionAttributeValues=eav
        )

        while 'LastEvaluatedKey' in my_query:
            my_query = dynamodb2.query(
                TableName='flights',
                ConsistentRead=False,
                ProjectionExpression="flight_id, airlines_name, available_seats",
                KeyConditionExpression='flight_id= :mypk2',
                ExpressionAttributeValues=eav)
        name = my_query['Items'][0]['airlines_name']['S']
        f_id = my_query['Items'][0]['flight_id']['N']
        seats = my_query['Items'][0]['available_seats']['N']
        print("Available seats in the %s flight %s are %s " % (name, f_id, seats))
    return my_query


if __name__ == "__main__":
    args = sys.argv[1:]
    tablename = args[0]
    x = args[1]
    region_1 = args[2]
    y = args[3]
    region_2 = args[4]

    ## Update region_1 with value xxx
    print("Updating flights table in region:", region_1)
    print("input value used for updating flights", x)
    start_time1 = time.time()
    count = update_flights_1(tablename, x, region_1)
    end_time1 = time.time()
    print('\nUpdate start time: %s \nUpdate end time: %s \nTotal time to update in seconds: %s.' % (datetime.datetime.fromtimestamp(start_time1).strftime('%Y-%m-%d %H:%M:%S'), datetime.datetime.fromtimestamp(end_time1).strftime('%Y-%m-%d %H:%M:%S'), (end_time1 - start_time1)))
    print("-----------------------------------\n")

    ## Update region_2 with value yyy
    print("Updating flights table in region:", region_2)
    print("input value used for updating", y)
    start_time2 = time.time()
    count = update_flights_1(tablename, y, region_2)
    end_time2 = time.time()
    print('\nUpdate start time: %s \nUpdate end time: %s \nTotal time to update in seconds: %s' % (datetime.datetime.fromtimestamp(start_time2).strftime('%Y-%m-%d %H:%M:%S'), datetime.datetime.fromtimestamp(end_time2).strftime('%Y-%m-%d %H:%M:%S'), (end_time2 - start_time2)))
    print("-----------------------------------\n")

    # Query region_1
    print("### Starting to QUERY table %s from %s ### \n" % (tablename, region_1))
    start_time3 = time.time()
    query_result = query_flights_1(tablename, region_1)
    end_time3 = time.time()
    print('\nQuery start time: %s \nQuery end time: %s \nTotal query time in seconds: %s. ' % (datetime.datetime.fromtimestamp(start_time2).strftime('%Y-%m-%d %H:%M:%S'), datetime.datetime.fromtimestamp(end_time2).strftime('%Y-%m-%d %H:%M:%S'), (end_time2 - start_time2)))
    print("-----------------------------------\n")

    print("Retrying the QUERY AFTER SLEEPING for 2 seconds...\n")
    time.sleep(2)

    ## Query region_1
    print("###  Starting to QUERY table %s from %s  ### \n" % (tablename, region_1))
    start_time4 = time.time()
    query_result = query_flights_1(tablename, region_1)
    end_time4 = time.time()
    print('\nQuery start time: %s \nQuery end time: %s \nTotal query time in seconds: %s. ' % (datetime.datetime.fromtimestamp(start_time4).strftime('%Y-%m-%d %H:%M:%S'), datetime.datetime.fromtimestamp(end_time4).strftime('%Y-%m-%d %H:%M:%S'), (end_time4 - start_time4)))

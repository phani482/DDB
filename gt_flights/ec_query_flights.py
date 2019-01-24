##



from __future__ import print_function
import boto3
import time
import datetime
import csv
import sys

def update_flights(tablename, x, region_1):

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

def query_flights(tablename, region_2):
    dynamodb2 = boto3.client('dynamodb', region_name=region_2)
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
        #print("\nAvailable seats in the %s flight %s are %s " % (my_query['Items'][0]['airlines_name']['S'], my_query['Items'][0]['flight_id']['N'], my_query['Items'][0]['available_seats']['S']))

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
    region_2 = args[3]

    print("\n## Starting to Update table %s from %s with %s ##\n" % (tablename, region_1, x))
    start_time = time.time()
    count = update_flights(tablename, x, region_1)
    end_time = time.time()
    print('\nUpdate start time: %s \nUpdate endtime: %s \nTotal time to update in seconds: %s' % (datetime.datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S'),datetime.datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S'), (end_time - start_time)))
    print("-----------------------------------\n")

    print("## Starting to Query table %s from %s  ##\n" % (tablename, region_2))
    start_time2 = time.time()
    query_result = query_flights(tablename, region_2)
    end_time2 = time.time()
    print('\nQuery start time: %s \nEndtime: %s \nTotal query time in seconds: %s. ' % (datetime.datetime.fromtimestamp(start_time2).strftime('%Y-%m-%d %H:%M:%S'), datetime.datetime.fromtimestamp(end_time2).strftime('%Y-%m-%d %H:%M:%S'), (end_time2 - start_time2)))

    print("-----------------------------------\n")
    print("## Retrying the QUERY AFTER SLEEPING for 1 second... ##\n")
    time.sleep(1)
    start_time3 = time.time()
    query_result = query_flights(tablename, region_2)
    end_time3 = time.time()
    print('\nQuery start time: %s \nEndtime: %s \nTotal query time in seconds: %s. ' % (
    datetime.datetime.fromtimestamp(start_time3).strftime('%Y-%m-%d %H:%M:%S'),
    datetime.datetime.fromtimestamp(end_time3).strftime('%Y-%m-%d %H:%M:%S'), (end_time3 - start_time3)))

'''
### Sample data to update:
id:       5603280670,26806130,9902917690,1079996,2907581914,53600600,282027328,421920151,534890387,658410767
airlines: Quatar,British,Emirates,JetBlue,Delta,UnitedAirlines,Alaska,spirit,Republic,southwest
'''

from __future__ import print_function
import boto3
import time
import datetime
import csv
import sys


def update_flights(tablename, x, region):

    dynamodb = boto3.resource('dynamodb', region_name=region)
    dynamodb_table = dynamodb.Table(tablename)

    myPk_list = [5603280670, 26806130, 9902917690, 1079996, 2907581914, 53600600, 282027328, 421920151, 534890387, 658410767]
    mySk_list = ["Quatar", "British", "Emirates", "JetBlue", "Delta", "UnitedAirlines", "Alaska", "spirit", "Republic", "southwest"]

    i = 0
    for i in range(len(myPk_list)):
        mypk = myPk_list[i]
        mysk = mySk_list[i]
        my_update = dynamodb_table.update_item(
            Key={'flight_id': mypk, 'airlines_name': mysk},
            UpdateExpression="set available_seats = :seats",
            ExpressionAttributeValues={':seats': int(x)},
            ReturnValues="UPDATED_NEW"
        )
        print("Updated seat availability for flight:%s to %s" % (mypk, my_update['Attributes']['available_seats']))
    print("Flight availability Updated successfully")


if __name__ == "__main__":
    args = sys.argv[1:]
    tablename = args[0]
    x = args[1]
    region = args[2]
    start_time = time.time()
    count = update_flights(tablename, x, region)
    end_time = time.time()
    print('\nUpdate start time: %s \nUpdate endtime: %s \nTotal query time in seconds: %s. \n' % (datetime.datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S'), datetime.datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S'), (end_time - start_time)))

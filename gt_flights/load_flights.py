'''
### Sample data ####
flight_id,airlines_name,available_seats,seat_type,support,phone,from,to,date,time
2452052965,American,502,FirstClass,fhryniewicki6y@jigsy.com,(943) 8641482,New Zealand,Denmark,2/14/19,9:56
'''

from __future__ import print_function
import boto3
import time
import csv
import sys

def load_data(tablename, filename, region):

    dynamodb = boto3.resource('dynamodb', region_name=region)
    dynamodb_table = dynamodb.Table(tablename)
    count = 0
    with open(filename, 'rb') as flights:
        flight = csv.reader(flights, delimiter=',', quotechar='|')
        for row in flight:
            count += 1
            # convert row to a dictionary
            each_flight={}
            each_flight['flight_id'] = int(row[0])
            each_flight['airlines_name'] = str(row[1])
            each_flight['available_seats'] = int(row[2])
            each_flight['seat_type'] = row[3]
            each_flight['support'] = row[4]
            each_flight['phone'] = row[5]
            each_flight['from'] = row[6]
            each_flight['to'] = row[7]
            each_flight['date'] = row[8]
            dynamodb_table.put_item(Item=each_flight)
            if count % 250 == 0:
                batch_time = (time.time() - start_time)
                print("Processed %s items in %s seconds" % (count, batch_time))

    return count

if __name__ == "__main__":
    args = sys.argv[1:]
    tablename = args[0]
    filename = args[1]
    region = args[2]
    start_time = time.time()
    count = load_data(tablename, filename, region)
    print('TotalRowCount: %s, Total seconds: %s' % (count, (time.time() - start_time)))
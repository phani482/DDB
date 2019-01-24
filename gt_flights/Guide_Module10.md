## Exercise 10 - DynamoDB Global Tables

DynamoDB global tables provide a fully managed solution for deploying a multi-region, multi-master database, without having to build and maintain your own replication solution.

We will use following scripts for this exercise:
  
  1. load_flights.py [# loads the 'flights_data.csv' data-set]
  2. scan_flights.py [# scans a table in single region]
  3. query_flights.py [# Query a table in single region]
  4. ec_query_flights.py [# Sends Updates to region_1 and Queries to region_2 ]
  5. multi_update_flights.py [# Sends Updates to region_1, region_2 respectively and Queries region_1 twice with a pause of 2 seconds]
  

#### Step 1 - Requirements:  

* There are certain requirements to be aware of before getting started wit Global Tables > https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/globaltables_reqs_bestpractices.html#globaltables_reqs_bestpractices.requirements

* DynamoDB automatically creates a service-linked role 'AWSServiceRoleForDynamoDBReplication' for you

#### Step2 - Create a new table (flights) in US East (Ohio), with DynamoDB Streams enabled (NEW_AND_OLD_IMAGES):

* Create table in us-east-2
```
aws dynamodb create-table --table-name flights \
--attribute-definitions AttributeName=flight_id,AttributeType=N AttributeName=airlines_name,AttributeType=S \
--key-schema AttributeName=flight_id,KeyType=HASH AttributeName=airlines_name,KeyType=RANGE \
--provisioned-throughput ReadCapacityUnits=30,WriteCapacityUnits=30 \
--stream-specification StreamEnabled=true,StreamViewType=NEW_AND_OLD_IMAGES \
--region us-east-2
```
* Create table in eu-west-1

```
aws dynamodb create-table --table-name flights \
--attribute-definitions AttributeName=flight_id,AttributeType=N AttributeName=airlines_name,AttributeType=S \
--key-schema AttributeName=flight_id,KeyType=HASH AttributeName=airlines_name,KeyType=RANGE \
--provisioned-throughput ReadCapacityUnits=30,WriteCapacityUnits=30 \
--stream-specification StreamEnabled=true,StreamViewType=NEW_AND_OLD_IMAGES \
--region eu-west-1
```
* Adding flights table in us-east-2 and eu-west-1 to the replica group:

```
aws dynamodb create-global-table \
    --global-table-name flights \
    --replication-group RegionName=us-east-2 RegionName=eu-west-1 
```

### Step 3 - Importance of using auto-scaling to update the capacity on a global table

* Discuss Significance of enabling auto-scaling vs On-Demand with Global Table
https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/globaltables_reqs_bestpractices.html#globaltables_reqs_bestpractices.tables.autoscaling

* If auto scaling doesn't satisfy your application's capacity changes (unpredictable workload) or if you don't want to configure its settings (target settings for minimum, maximum, or utilization threshold), you can use on-demand mode to manage capacity for your global tables. For more information, see On-Demand Mode.

* If you enable on-demand mode on a global table, your consumption of replicated write request units (rWCUs) will be consistent with how rWCUs are provisioned. For example, if you perform 10 writes to a local table that is replicated in two additional Regions, you will consume 60 write request units (10 + 10 + 10 = 30; 30 x 2 = 60). 

* If you opt to use Provisioned mode on a global table, you can use UpdateGlobalTableSettings api or AWS console to update the capacity or enable/disable auto-scaling 


### Step 4 - Demonstrate Global Table Replication

* Any new or updates item in any replica table will be replicated to all of the other replicas within the same global table. In a global table, a newly-written item is usually propagated to all replica tables within seconds.

* DynamoDB does not support partial replication of only some of the items.


* Sample data of flights_data.csv looks as below(no headers in the data-set)

```
 ### Sample data ####
flight_id,airlines_name,available_seats,seat_type,support,phone,from,to,date,time
2452052965,American,502,FirstClass,fhryniewicki6y@jigsy.com,(943) 8641482,New Zealand,Denmark,2/14/19,9:56
```

* Load the flights data-set to DynamoDB table in us-east-2 region by running load_flights.py as below

``` 
python load_flights.py flights ./data/flights_data.csv us-east-2

```

Output:

``` 
Processed 250 items in 13.9410619736 seconds
Processed 500 items in 27.4421260357 seconds
Processed 750 items in 41.3043510914 seconds
Processed 1000 items in 56.578758955 seconds
Processed 1250 items in 70.2204880714 seconds
Processed 1500 items in 83.9283220768 seconds
Processed 1750 items in 100.255409002 seconds
Processed 2000 items in 115.713709116 seconds
Processed 2250 items in 129.657588959 seconds
Processed 2500 items in 143.136796951 seconds
TotalRowCount: 2500, Total seconds: 143.137362003
```

* Now, validate the item count on the replica table in eu-west-1 by running scan_flights.py script as below

``` 
python scan_flights.py flights eu-west-1

```
Output:

``` 
Scanning table flights to get the total items
Total item count of table flights are 2500  in 5.89269590378 seconds
```

### Step 5  - Eventual Consistency Reads in GT. (only issues reads against one replica)

An application can read and write data to any replica table. If your application only uses eventually consistent reads, and only issues reads against one AWS region, then it will work without any modification.

* Query the table on us-east-2 using the query_flights.py script. In this example, we are using flight id's to query the items and fetch the respective 'available_seats' values for each flight id

* Sample flight_id's and the airline used in the query_flights.py script:
flight_id:5603280670,26806130,9902917690,1079996,2907581914,53600600,282027328,421920151,534890387,658410767

``` 
$ python query_flights.py flights us-east-2

```
Output:
```
Available seats in the Quatar flight 5603280670 are 266
Available seats in the British flight 26806130 are 828
Available seats in the Emirates flight 9902917690 are 491
Available seats in the JetBlue flight 1079996 are 978
Available seats in the Delta flight 2907581914 are 277
Available seats in the UnitedAirlines flight 53600600 are 623
Available seats in the Alaska flight 282027328 are 677
Available seats in the spirit flight 421920151 are 304
Available seats in the Republic flight 534890387 are 944
Available seats in the southwest flight 658410767 are 580

Query start time: 2019-01-23 17:07:58
Endtime: 2019-01-23 17:08:00
Total query time in seconds: 1.58885908127.
```

* Let us assume a sample app runs in various regions constantly updates the flights availability_seats
* ec_query_flights.py script will first call update api to modify the 'flights' table in us-east-2 region to update the seat availability (to a random value 222. You can try a number of your choice) of the flights we issued query in the above step. 
* Once the update is complete, this script internally calls a query api immediately to the replica table in region eu-west-1.

  Note: You may have to rerun the below script more than once (with a NEW value every time) to see the eventual consistent behavior

* From the output you can see that replication takes place in eventual consistent manner. 

```
$ python ec_query_flights.py flights 222 us-east-2 eu-west-1

```
Output:

``` 
## Starting to Update table flights from us-east-2 with 222 ##

Updated seat availability for flight:5603280670 to 222
Updated seat availability for flight:26806130 to 222
Updated seat availability for flight:9902917690 to 222
Updated seat availability for flight:1079996 to 222
Updated seat availability for flight:2907581914 to 222
Updated seat availability for flight:53600600 to 222
Updated seat availability for flight:282027328 to 222
Updated seat availability for flight:421920151 to 222
Updated seat availability for flight:534890387 to 222
Updated seat availability for flight:658410767 to 222
Flight availability Updated successfully

Update start time: 2019-01-23 19:57:25
Update endtime: 2019-01-23 19:57:26
Total time to update in seconds: 0.902311086655
-----------------------------------

## Starting to Query table flights from eu-west-1  ##

Available seats in the Quatar flight 5603280670 are 266
Available seats in the British flight 26806130 are 828
Available seats in the Emirates flight 9902917690 are 222
Available seats in the JetBlue flight 1079996 are 222
Available seats in the Delta flight 2907581914 are 222
Available seats in the UnitedAirlines flight 53600600 are 222
Available seats in the Alaska flight 282027328 are 222
Available seats in the spirit flight 421920151 are 222
Available seats in the Republic flight 534890387 are 222
Available seats in the southwest flight 658410767 are 222

Query start time: 2019-01-23 19:57:26
Endtime: 2019-01-23 19:57:27
Total query time in seconds: 1.49783086777.
-----------------------------------

## Retrying the QUERY AFTER SLEEPING for 1 second... ##

Available seats in the Quatar flight 5603280670 are 222
Available seats in the British flight 26806130 are 222
Available seats in the Emirates flight 9902917690 are 222
Available seats in the JetBlue flight 1079996 are 222
Available seats in the Delta flight 2907581914 are 222
Available seats in the UnitedAirlines flight 53600600 are 222
Available seats in the Alaska flight 282027328 are 222
Available seats in the spirit flight 421920151 are 222
Available seats in the Republic flight 534890387 are 222
Available seats in the southwest flight 658410767 are 222

Query start time: 2019-01-23 19:57:28
Endtime: 2019-01-23 19:57:30
Total query time in seconds: 1.40652298927.
```

### Step 6 - Monitoring
You can monitor the replication using the below mentioned cloud watch metrics
* ReplicationLatency
* PendingReplicationCount

https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/globaltables_monitoring.html

### Step 7 - Multi Master Replication

* Let's update the seat availability of same flight id's above from two different regions one after the other. To do this, lets run the multi_update_flights.py script below
* This scripts requires the arguments as per the example below and the updates to region1 will be called first with value1 followed by updates to region2 using value2 as the input arguments.

   Example: python multi_update_flights.py <tablename> <value1> <region1> <value2> <region2>

Run the following script :
``` 
$ python multi_update_flights.py flights 111 us-east-2 000 eu-west-1
```

Output:

```
Updating flights table in region: us-east-2
input value used for updating flights 111
Updated seat availability for flight:5603280670 to 111
Updated seat availability for flight:26806130 to 111
Updated seat availability for flight:9902917690 to 111
Updated seat availability for flight:1079996 to 111
Updated seat availability for flight:2907581914 to 111
Updated seat availability for flight:53600600 to 111
Updated seat availability for flight:282027328 to 111
Updated seat availability for flight:421920151 to 111
Updated seat availability for flight:534890387 to 111
Updated seat availability for flight:658410767 to 111
Flight availability Updated successfully

Update start time: 2019-01-23 20:01:20
Update end time: 2019-01-23 20:01:21
Total time to update in seconds: 0.885948896408.
-----------------------------------

Updating flights table in region: eu-west-1
input value used for updating 000
Updated seat availability for flight:5603280670 to 0
Updated seat availability for flight:26806130 to 0
Updated seat availability for flight:9902917690 to 0
Updated seat availability for flight:1079996 to 0
Updated seat availability for flight:2907581914 to 0
Updated seat availability for flight:53600600 to 0
Updated seat availability for flight:282027328 to 0
Updated seat availability for flight:421920151 to 0
Updated seat availability for flight:534890387 to 0
Updated seat availability for flight:658410767 to 0
Flight availability Updated successfully

Update start time: 2019-01-23 20:01:21
Update end time: 2019-01-23 20:01:23
Total time to update in seconds: 1.59334993362
-----------------------------------

### Starting to QUERY table flights from us-east-2 ###

Available seats in the Quatar flight 5603280670 are 111
Available seats in the British flight 26806130 are 111
Available seats in the Emirates flight 9902917690 are 111
Available seats in the JetBlue flight 1079996 are 111
Available seats in the Delta flight 2907581914 are 111
Available seats in the UnitedAirlines flight 53600600 are 111
Available seats in the Alaska flight 282027328 are 111
Available seats in the spirit flight 421920151 are 111
Available seats in the Republic flight 534890387 are 111
Available seats in the southwest flight 658410767 are 111

Query start time: 2019-01-23 20:01:21
Query end time: 2019-01-23 20:01:23
Total query time in seconds: 1.59334993362.
-----------------------------------

Retrying the QUERY AFTER SLEEPING for 2 seconds...

###  Starting to QUERY table flights from us-east-2  ###

Available seats in the Quatar flight 5603280670 are 0
Available seats in the British flight 26806130 are 0
Available seats in the Emirates flight 9902917690 are 0
Available seats in the JetBlue flight 1079996 are 0
Available seats in the Delta flight 2907581914 are 0
Available seats in the UnitedAirlines flight 53600600 are 0
Available seats in the Alaska flight 282027328 are 0
Available seats in the spirit flight 421920151 are 0
Available seats in the Republic flight 534890387 are 0
Available seats in the southwest flight 658410767 are 0

Query start time: 2019-01-23 20:01:25
Query end time: 2019-01-23 20:01:26
Total query time in seconds: 0.687509059906.

```

* From the above output, it is clear that the last writer wins. In this example the last writer to Update the seat availability is the update that suceeded on eu-west-1 (ireland).
After the last update you can see that the availability got updated in second(s).

* In this example the writes/updates are made on both the tables which serve the traffic  to multi-master flights table.  

In my project I have following files:
•	server3.py – This is the python script which receives the streams of data over websockets. The script connects with the Kafka server and publishes on the topics depending on the symbol of the currency. Since there are three symbols, three topics are published. It also stores the data in Cassendra using Keyspace: ‘binance’ and creates three tables each for every symbol of currency
•	runscripts.py – This contains the script to consider the test output from unit test and run all the containers once the result is successful. Otherwise, error message is printed on the console
•	test_server.py – This contains a simple unit test for my application
•	Dockerfile  - Using this file Docker image is built. I have containerized my application. 
                Here the necessary dependencies are also provided so that the container can work in a standalone way. My application server3.py is copied to the docker image here.
•	Docker-compose.yml – This has been used to run all the three containers, namely: Cassandra, Kafka and the one which runs my application. 
                       It also defines the internal network through which all the docker containers are connected. In this file local volume is also mounted to the container to help the development process

To run the application, please install python3 and run the script runscripts.py. The script will pull the images for Cassandra and Kafka and use the local Dockerfile for my application. 
At the end all the containers will run and communicate with each other. ‘cqlsh’ can be used to see the values stored in the respective tables. 
All the three tables which are generated are called: btcusdt_node  ethusdt_node  bnbusdt_node. The table outputs have also been provided in the files.
The ‘Kafka’ topics can also be consumed by listening on the respective topics. For that use the command ‘docker exec –it kafka /bin/bash’ and  navigate to the directory /opt/kafka/bin and execute the command:
./kafka-console-consumer.sh --bootstrap-server 'kafka':9092 --topic BTCUSDT_agg_trades --from-beginning. The output in kafka for one topic has also been provided with the code. 

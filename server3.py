import asyncio
import json
import websockets
from confluent_kafka import Producer
from cassandra.cluster import Cluster
from cassandra.policies import ExponentialReconnectionPolicy, RoundRobinPolicy, RetryPolicy

async def subscribe_to_agg_trade_feed(symbol, producer, session):
    uri = f"wss://fstream.binance.com/ws/{symbol.lower()}@aggTrade"
    async with websockets.connect(uri) as websocket:
        while True:
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=5.0)  #timeout
                trade_data = json.loads(message)
                await asyncio.gather(
                    publish_via_kafka(symbol, trade_data, producer),
                    store_in_cassandra(symbol, trade_data, session)
                )
            except asyncio.TimeoutError:
                print("timeout has been occured...")
                continue
            except websockets.ConnectionClosedError:
                print("Websockets connection has been closed")
                await asyncio.sleep(6)  
                break  

async def publish_via_kafka(symbol, trade_data, producer):
    topic = f"{symbol}_agg_trades"
    producer.produce(topic, json.dumps(trade_data))
    producer.flush()

async def store_in_cassandra(symbol, trade_data, session):
    try:
        table_name = symbol + '_Node'
        session.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name}
            (
                symbol text,
                id text,
                time timestamp,
                price decimal,
                quantity decimal,
                first_trade_id bigint,
                last_trade_id text,
                timestamp bigint,
                is_buyer_maker boolean,
                PRIMARY KEY ((symbol), id)
            )
        """)

        insert_query = f"""
            INSERT INTO {table_name} (symbol, id, time, price, quantity, first_trade_id, last_trade_id, timestamp, is_buyer_maker)
            VALUES ('{symbol}', '{str(trade_data['E'])}', '{str(trade_data['a'])}', 
                {trade_data['p']}, {trade_data['q']}, {int(trade_data['f'])}, '{trade_data['l']}', {trade_data['T']}, {trade_data['m']})
        """
        session.execute(insert_query)

    except Exception as e:
        print("Failed to store in Cassandra:", e)

async def main(symbols, producer, session):
    tasks = [subscribe_to_agg_trade_feed(symbol, producer, session) for symbol in symbols]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']
    
    statusConnection = False

    # In the start of cassandra service, it is quite possible that
    # cassandra has not yet initialized and the this application
    # starts before that. For that it is important to poll the connection
    # status

    while not statusConnection:
        try:
            cluster = Cluster(['cassandra'])
            cluster.default_retry_policy = RetryPolicy()
            cluster.reconnection_policy = ExponentialReconnectionPolicy(1.0, 60.0)

            create_keyspace_query = f"CREATE KEYSPACE IF NOT EXISTS {'binance'}" \
                                    f" WITH replication = {{'class': 'SimpleStrategy', 'replication_factor': 1  }}"

            session = cluster.connect()
            session.execute(create_keyspace_query)
            session = cluster.connect('binance')

            statusConnection = bool(session.execute("SELECT * FROM system_schema.keyspaces WHERE keyspace_name='binance'"))

            print("connection to Cassandra has been established..")
        
            session.load_balancing_policy = RoundRobinPolicy()

            producer_conf = {'bootstrap.servers': 'kafka'}
            producer = Producer(producer_conf)

            print("Now going to continuously publish and store")
            loop = asyncio.get_event_loop()
            loop.run_until_complete(main(symbols, producer, session))

            break

        except Exception as e:

            print(f"Failed to connect to Cassandra, waiting ..........: {e}")

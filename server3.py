import asyncio
import json
import time
import websockets
from confluent_kafka import Producer
from cassandra.cluster import Cluster
from cassandra.policies import ExponentialReconnectionPolicy, RoundRobinPolicy, RetryPolicy


async def subscribe_to_agg_trade_feed(symbol, producer, session):
    uri = f"wss://fstream.binance.com/ws/{symbol.lower()}@aggTrade"
    async with websockets.connect(uri) as websocket:
        while True:
            message = await websocket.recv()
            trade_data = json.loads(message)
            await publish_via_kafka(symbol, trade_data, producer)
            await store_in_cassadra(symbol, trade_data, session)


async def publish_via_kafka(symbol, trade_data, producer):
    topic = f"{symbol}_agg_trades"
    producer.produce(topic, json.dumps(trade_data))
    producer.flush()


async def store_in_cassadra(symbol, trade_data, session):
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
        print("Failed to interact with Cassandra:", e)


async def main(symbols):
    retry_policy = RetryPolicy()
    reconnection_policy = ExponentialReconnectionPolicy(1.0, 60.0)
    load_balancing_policy = RoundRobinPolicy()

    # Cassandra initialization may take some time, so sleep for 20 seconds
    await asyncio.sleep(20)
    while True:
        try:
            cluster = Cluster(['cassandra'])
            cluster.default_retry_policy = RetryPolicy()
            cluster.reconnection_policy = reconnection_policy

            session = cluster.connect('binance_usd')
            session.load_balancing_policy = load_balancing_policy

            producer_conf = {'bootstrap.servers': 'kafka'}
            producer = Producer(producer_conf)

            tasks = [subscribe_to_agg_trade_feed(symbol, producer, session) for symbol in symbols]
            await asyncio.gather(*tasks)

            break

        except Exception as e:
            print(f"Failed to connect to Cassandra: {e}")
            print("Retrying in 5 seconds...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']
    print("Waiting for Cassandra to start....")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(symbols))

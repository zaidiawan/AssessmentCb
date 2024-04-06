import unittest

import asyncio

import json

from unittest.mock import MagicMock, patch

from server3 import subscribe_to_agg_trade_feed


class TestSubscribeToAggTradeFeed(unittest.TestCase):

    @patch('server3.publish_via_kafka')

    @patch('server3.save_to_cassandra')

    async def test_subscribe_to_agg_trade_feed(self, mock_save_to_cassandra, mock_publish_to_kafka):

        # Create mock websocket data

        websocket_data = {

            'E': 'timestamp',

            'a': 'time',

            'p': 80.0,

            'q': 7.0,

            'f': 12654,

            'l': 'last_trade_id',

            'T': 1234765786,

            'm': True

        }

        # Create mock for websocket

        websocket = MagicMock()

        websocket.recv = MagicMock(return_value=json.dumps(websocket_data))

        # Create mock producer and session

        producer = MagicMock()

        session = MagicMock()

        

        # Run subscribe_to_agg_trade_feed

        await subscribe_to_agg_trade_feed('BTCUSDT', producer, session)



        # Check if publish_to_kafka and save_to_cassandra were called with the correct arguments

        mock_publish_via_kafka.assert_called_once_with('BTCUSDT', websocket_data, producer)

        mock_store_in_cassadra.assert_called_once_with('BTCUSDT', websocket_data, session)





if __name__ == '__main__':

     asyncio.run(unittest.main())

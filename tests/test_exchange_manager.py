import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
from modules.exchange_manager import ExchangeManager

class TestExchangeManager(unittest.TestCase):
    def setUp(self):
        self.manager = ExchangeManager()

    @patch('modules.exchange_manager.ccxt')
    def test_connect_success(self, mock_ccxt):
        # Mock the exchange class
        mock_exchange = MagicMock()
        mock_exchange.checkRequiredCredentials.return_value = True
        mock_exchange.load_markets.return_value = {'BTC/USDT': {}}

        # Configure the getattr on ccxt to return our mock class
        mock_ccxt.binance.return_value = mock_exchange

        success, msg = self.manager.connect('binance', 'key', 'secret')

        self.assertTrue(success)
        self.assertIn("Successfully connected", msg)
        self.assertIsNotNone(self.manager.exchange)

    @patch('modules.exchange_manager.ccxt')
    def test_connect_failure(self, mock_ccxt):
        # Simulate an exception during connection
        mock_ccxt.binance.side_effect = Exception("Connection failed")

        success, msg = self.manager.connect('binance', 'key', 'secret')

        self.assertFalse(success)
        self.assertIn("Connection error", msg)
        self.assertIsNone(self.manager.exchange)

    def test_get_balance_no_connection(self):
        df, err = self.manager.get_balance()
        self.assertIsNone(df)
        self.assertEqual(err, "Not connected to any exchange.")

    def test_create_order_no_connection(self):
        order, msg = self.manager.create_order('BTC/USDT', 'limit', 'buy', 1.0, 50000)
        self.assertIsNone(order)
        self.assertEqual(msg, "Not connected.")

    @patch('modules.exchange_manager.ccxt')
    def test_connect_with_password(self, mock_ccxt):
        mock_exchange = MagicMock()
        mock_exchange.checkRequiredCredentials.return_value = True
        mock_exchange.load_markets.return_value = {'BTC/USDT': {}}
        mock_ccxt.binance.return_value = mock_exchange

        success, msg = self.manager.connect('binance', 'key', 'secret', 'password123')

        self.assertTrue(success)
        self.assertIn("Successfully connected", msg)

    def test_getstate(self):
        self.manager.exchange = MagicMock()
        self.manager.exchange_id = 'binance'

        state = self.manager.__getstate__()

        self.assertEqual(state['exchange'], 'Exchange object hidden')
        self.assertEqual(state['exchange_id'], 'binance')

    def test_get_balance_success(self):
        mock_exchange = MagicMock()
        mock_exchange.fetch_balance.return_value = {
            'total': {'BTC': 1.5, 'ETH': 10.0, 'USDT': 0.0},
            'free': {'BTC': 1.0, 'ETH': 5.0, 'USDT': 0.0},
            'used': {'BTC': 0.5, 'ETH': 5.0, 'USDT': 0.0}
        }
        self.manager.exchange = mock_exchange

        import pandas as pd
        df, msg = self.manager.get_balance()

        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 2)  # USDT is 0, so should be filtered
        self.assertIsNone(msg)

    def test_get_balance_error(self):
        mock_exchange = MagicMock()
        mock_exchange.fetch_balance.side_effect = Exception("API error")
        self.manager.exchange = mock_exchange

        df, msg = self.manager.get_balance()

        self.assertIsNone(df)
        self.assertIn("API error", msg)

    def test_fetch_open_orders_no_connection(self):
        orders, msg = self.manager.fetch_open_orders('BTC/USDT')
        self.assertIsNone(orders)
        self.assertEqual(msg, "Not connected.")

    def test_fetch_open_orders_success(self):
        mock_exchange = MagicMock()
        mock_exchange.fetch_open_orders.return_value = [{'id': '123', 'datetime': '2023', 'symbol': 'BTC', 'type': 'limit', 'side': 'buy', 'price': 100, 'amount': 1, 'filled': 0, 'status': 'open'}]
        self.manager.exchange = mock_exchange

        orders, msg = self.manager.fetch_open_orders('BTC/USDT')

        self.assertEqual(len(orders), 1)
        self.assertIsNone(msg)

    def test_fetch_open_orders_error(self):
        mock_exchange = MagicMock()
        mock_exchange.fetch_open_orders.side_effect = Exception("Failed to fetch")
        self.manager.exchange = mock_exchange

        orders, msg = self.manager.fetch_open_orders('BTC/USDT')

        self.assertIsNone(orders)
        self.assertIn("Failed to fetch", msg)

    def test_create_order_success(self):
        mock_exchange = MagicMock()
        mock_exchange.markets = {'BTC/USDT': {}}
        mock_exchange.create_order.return_value = {'id': '789'}
        self.manager.exchange = mock_exchange

        order, msg = self.manager.create_order('BTC/USDT', 'market', 'buy', 1.5)

        self.assertEqual(order['id'], '789')
        self.assertEqual(msg, "Order placed successfully!")

    def test_create_order_error(self):
        mock_exchange = MagicMock()
        mock_exchange.markets = {'BTC/USDT': {}}
        mock_exchange.create_order.side_effect = Exception("Insufficient funds")
        self.manager.exchange = mock_exchange

        order, msg = self.manager.create_order('BTC/USDT', 'market', 'buy', 1000.0)

        self.assertIsNone(order)
        self.assertIn("Insufficient funds", msg)

    def test_get_order_book_no_connection(self):
        order_book, msg = self.manager.get_order_book('BTC/USDT')
        self.assertIsNone(order_book)
        self.assertEqual(msg, "Not connected to any exchange.")

    def test_get_order_book_success(self):
        mock_exchange = MagicMock()
        mock_exchange.fetch_order_book.return_value = {'bids': [[50000, 1]], 'asks': [[50001, 1]]}
        self.manager.exchange = mock_exchange

        order_book, msg = self.manager.get_order_book('BTC/USDT')

        self.assertIsNotNone(order_book)
        self.assertEqual(len(order_book['bids']), 1)
        self.assertEqual(msg, "Success")

    def test_get_order_book_error(self):
        mock_exchange = MagicMock()
        mock_exchange.fetch_order_book.side_effect = Exception("Order book error")
        self.manager.exchange = mock_exchange
        self.manager.logger = MagicMock()

        order_book, msg = self.manager.get_order_book('BTC/USDT')

        self.assertIsNone(order_book)
        self.assertIn("Failed to fetch order book: Order book error", msg)
        self.manager.logger.error.assert_called_once()

    def test_get_balance_empty(self):
        mock_exchange = MagicMock()
        mock_exchange.fetch_balance.return_value = {
            'total': {'BTC': 0.0, 'ETH': 0.0, 'USDT': 0.0},
            'free': {},
            'used': {}
        }
        self.manager.exchange = mock_exchange

        import pandas as pd
        df, msg = self.manager.get_balance()

        self.assertIsInstance(df, pd.DataFrame)
        self.assertTrue(df.empty)
        self.assertIsNone(msg)

    def test_fetch_open_orders_empty(self):
        mock_exchange = MagicMock()
        mock_exchange.fetch_open_orders.return_value = []
        self.manager.exchange = mock_exchange

        import pandas as pd
        df, msg = self.manager.fetch_open_orders('BTC/USDT')

        self.assertIsInstance(df, pd.DataFrame)
        self.assertTrue(df.empty)
        self.assertIsNone(msg)

    def test_create_order_limit_no_price(self):
        mock_exchange = MagicMock()
        mock_exchange.markets = {'BTC/USDT': {}}
        self.manager.exchange = mock_exchange

        order, msg = self.manager.create_order('BTC/USDT', 'limit', 'buy', 1.0)

        self.assertIsNone(order)
        self.assertEqual(msg, "Price is required for limit orders.")

    def test_create_order_limit_success(self):
        mock_exchange = MagicMock()
        mock_exchange.markets = {'BTC/USDT': {}}
        mock_exchange.create_order.return_value = {'id': '999'}
        self.manager.exchange = mock_exchange

        order, msg = self.manager.create_order('BTC/USDT', 'limit', 'buy', 1.0, 50000)

        self.assertEqual(order['id'], '999')
        self.assertEqual(msg, "Order placed successfully!")

    def test_create_order_invalid_symbol(self):
        mock_exchange = MagicMock()
        mock_exchange.markets = {'ETH/USDT': {}}
        self.manager.exchange_id = 'binance'
        self.manager.exchange = mock_exchange

        order, msg = self.manager.create_order('BTC/USDT', 'limit', 'buy', 1.0, 50000)

        self.assertIsNone(order)
        self.assertIn("Symbol BTC/USDT not found on binance.", msg)

    def test___str___and___repr__(self):
        self.manager.exchange = None
        self.manager.exchange_id = None
        self.assertEqual(str(self.manager), "ExchangeManager(status='Disconnected', exchange_id='None')")

        self.manager.exchange = MagicMock()
        self.manager.exchange_id = "kucoin"
        self.assertEqual(repr(self.manager), "ExchangeManager(status='Connected', exchange_id='kucoin')")

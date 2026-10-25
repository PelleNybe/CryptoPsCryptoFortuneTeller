import unittest
from unittest.mock import MagicMock, patch
from modules.freqtrade_manager import FreqtradeManager

class TestFreqtradeManager(unittest.TestCase):
    def setUp(self):
        self.manager = FreqtradeManager("http://localhost:8080", "user", "pass")

    @patch('modules.freqtrade_manager.requests.post')
    def test_login_success(self, mock_post):
        # Mock successful login response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"access_token": "fake_token", "refresh_token": "fake_refresh"}
        mock_post.return_value = mock_response

        success, msg = self.manager.login()

        self.assertTrue(success)
        self.assertEqual(self.manager._access_token, "fake_token")

    @patch('modules.freqtrade_manager.requests.post')
    def test_login_failure(self, mock_post):
        # Mock failed login response
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_post.return_value = mock_response

        success, msg = self.manager.login()

        self.assertFalse(success)
        self.assertIn("Login failed", msg)

    @patch('modules.freqtrade_manager.requests.get')
    def test_get_status_success(self, mock_get):
        self.manager._access_token = "fake_token"

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"state": "running"}
        mock_get.return_value = mock_response

        status, err = self.manager.get_status()

        self.assertEqual(status, {"state": "running"})
        self.assertIsNone(err)

    @patch('modules.freqtrade_manager.requests.post')
    def test_start_bot_success(self, mock_post):
        self.manager._access_token = "fake_token"

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "started"}
        mock_post.return_value = mock_response

        res, msg = self.manager.start_bot()

        self.assertEqual(res, {"status": "started"})

    @patch('modules.freqtrade_manager.requests.post')
    def test_login_exception(self, mock_post):
        mock_post.side_effect = Exception("Connection Timeout")
        success, msg = self.manager.login()
        self.assertFalse(success)
        self.assertIn("Connection error: Connection Timeout", msg)

    @patch('modules.freqtrade_manager.requests.get')
    def test_get_status_error_code(self, mock_get):
        self.manager._access_token = "fake_token"
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        status, err = self.manager.get_status()
        self.assertIsNone(status)
        self.assertEqual(err, "Error: 404")

    @patch('modules.freqtrade_manager.requests.get')
    def test_get_status_exception(self, mock_get):
        mock_get.side_effect = Exception("Network Error")
        status, err = self.manager.get_status()
        self.assertIsNone(status)
        self.assertEqual(err, "Network Error")

    @patch('modules.freqtrade_manager.requests.post')
    def test_start_bot_error_code(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"status": "Internal Server Error"}
        mock_post.return_value = mock_response

        res, msg = self.manager.start_bot()
        self.assertIsNone(res)
        self.assertEqual(msg, "Error: Internal Server Error")

    @patch('modules.freqtrade_manager.requests.post')
    def test_start_bot_exception(self, mock_post):
        mock_post.side_effect = Exception("Crash")
        res, msg = self.manager.start_bot()
        self.assertIsNone(res)
        self.assertEqual(msg, "Crash")

    @patch('modules.freqtrade_manager.requests.post')
    def test_stop_bot_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "stopped"}
        mock_post.return_value = mock_response

        res, msg = self.manager.stop_bot()
        self.assertEqual(res, {"status": "stopped"})
        self.assertEqual(msg, "Bot stopped")

    @patch('modules.freqtrade_manager.requests.post')
    def test_stop_bot_error_code(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"status": "Bad Request"}
        mock_post.return_value = mock_response

        res, msg = self.manager.stop_bot()
        self.assertIsNone(res)
        self.assertEqual(msg, "Error: Bad Request")

    @patch('modules.freqtrade_manager.requests.post')
    def test_stop_bot_exception(self, mock_post):
        mock_post.side_effect = Exception("Timeout")
        res, msg = self.manager.stop_bot()
        self.assertIsNone(res)
        self.assertEqual(msg, "Timeout")

    @patch('modules.freqtrade_manager.requests.get')
    def test_get_profit_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"profit_all_coin": 1.5}
        mock_get.return_value = mock_response

        res, err = self.manager.get_profit()
        self.assertEqual(res, {"profit_all_coin": 1.5})
        self.assertIsNone(err)

    @patch('modules.freqtrade_manager.requests.get')
    def test_get_profit_error_code(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_get.return_value = mock_response

        res, err = self.manager.get_profit()
        self.assertIsNone(res)
        self.assertEqual(err, "Error: 403")

    @patch('modules.freqtrade_manager.requests.get')
    def test_get_profit_exception(self, mock_get):
        mock_get.side_effect = Exception("Fetch Fail")
        res, err = self.manager.get_profit()
        self.assertIsNone(res)
        self.assertEqual(err, "Fetch Fail")

    @patch('modules.freqtrade_manager.requests.get')
    def test_get_whitelist_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"whitelist": ["BTC/USDT"]}
        mock_get.return_value = mock_response

        res, err = self.manager.get_whitelist()
        self.assertEqual(res, ["BTC/USDT"])
        self.assertIsNone(err)

    @patch('modules.freqtrade_manager.requests.get')
    def test_get_whitelist_error_code(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 502
        mock_get.return_value = mock_response

        res, err = self.manager.get_whitelist()
        self.assertIsNone(res)
        self.assertEqual(err, "Error: 502")

    @patch('modules.freqtrade_manager.requests.get')
    def test_get_whitelist_exception(self, mock_get):
        mock_get.side_effect = Exception("No Connection")
        res, err = self.manager.get_whitelist()
        self.assertIsNone(res)
        self.assertEqual(err, "No Connection")

    def test_headers_empty(self):
        self.assertEqual(self.manager._headers(), {})

    def test___str___and___repr__(self):
        self.assertEqual(str(self.manager), "FreqtradeManager(api_url='http://localhost:8080', username='user', access_token=None)")
        self.manager._access_token = 'fake_token'
        self.assertEqual(repr(self.manager), "FreqtradeManager(api_url='http://localhost:8080', username='user', access_token=Set)")

    def test_getstate(self):
        self.manager._access_token = 'fake_token'
        state = self.manager.__getstate__()
        self.assertEqual(state['_password'], '***')
        self.assertEqual(state['_access_token'], '***')

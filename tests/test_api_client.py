
import unittest
from unittest.mock import Mock, patch

import requests

from api_client import fetch_users


class TestFetchUsers(unittest.TestCase):

    @patch("api_client.time.sleep")
    @patch("api_client.requests.get")
    def test_fetch_users_success(self, mock_get, mock_sleep):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"id": 1, "name": "Kartik", "email": "kartik@example.com"}
        ]
        mock_get.return_value = mock_response

        result = fetch_users()

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], 1)
        mock_get.assert_called_once()
        mock_sleep.assert_not_called()

    @patch("api_client.time.sleep")
    @patch("api_client.requests.get")
    def test_retries_connection_error(self, mock_get, mock_sleep):
        mock_get.side_effect = requests.ConnectionError("Network unavailable")

        with self.assertRaises(requests.ConnectionError):
            fetch_users()

        self.assertEqual(mock_get.call_count, 3)
        self.assertEqual(mock_sleep.call_count, 2)
        mock_sleep.assert_any_call(1)
        mock_sleep.assert_any_call(2)
    
    @patch("api_client.time.sleep")
    @patch("api_client.requests.get")
    def test_does_not_retry_404(self, mock_get, mock_sleep):
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = (
            requests.HTTPError("404 Not Found")
        )
        mock_get.return_value = mock_response

        with self.assertRaises(requests.HTTPError):
            fetch_users()

        mock_get.assert_called_once()
        mock_sleep.assert_not_called()


if __name__ == "__main__":
    unittest.main()

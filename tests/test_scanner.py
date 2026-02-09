import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent directory to path so we can import scanner
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import scanner

class TestGloaksScanner(unittest.TestCase):

    @patch('scanner.socket.gethostbyname')
    def test_get_ip_success(self, mock_gethostbyname):
        """Test that a valid domain resolves to an IP."""
        mock_gethostbyname.return_value = "192.168.1.1"
        result = scanner.get_ip("example.com")
        self.assertEqual(result, "192.168.1.1")

    @patch('scanner.socket.gethostbyname')
    def test_get_ip_failure(self, mock_gethostbyname):
        """Test that an invalid domain returns None."""
        mock_gethostbyname.side_effect = scanner.socket.gaierror
        result = scanner.get_ip("invalid-domain-xyz.com")
        self.assertIsNone(result)

    @patch('scanner.check_port')
    def test_scan_port_open(self, mock_check_port):
        """Test that scan_ports returns correct open ports."""
        # mock_check_port side_effect will determine what check_port returns
        # If we pass [80], we want check_port to return 80.
        
        def side_effect(ip, port):
            return port if port == 80 else None
            
        mock_check_port.side_effect = side_effect
        
        result = scanner.scan_ports("127.0.0.1", [80, 22])
        self.assertEqual(result, [80])

    @patch('scanner.requests.get')
    def test_scan_headers(self, mock_get):
        """Test header scanning returns a dict."""
        mock_response = MagicMock()
        mock_response.headers = {'Server': 'nginx'}
        mock_get.return_value = mock_response
        
        result = scanner.scan_headers("example.com")
        self.assertEqual(result, {'Server': 'nginx'})

    @patch('scanner.requests.get')
    def test_geo_locate(self, mock_get):
        """Test geo location returns a dict with expected keys."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'isp': 'Google',
            'city': 'Mountain View',
            'country': 'USA',
            'lat': 37.4,
            'lon': -122.0
        }
        mock_get.return_value = mock_response
        
        result = scanner.geo_locate("8.8.8.8")
        self.assertEqual(result['isp'], 'Google')
        self.assertEqual(result['city'], 'Mountain View')

if __name__ == '__main__':
    unittest.main()
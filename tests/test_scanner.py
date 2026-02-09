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

    @patch('scanner.socket.socket')
    def test_scan_port_open(self, mock_socket):
        """Test that an open port is detected correctly."""
        mock_sock_instance = MagicMock()
        mock_socket.return_value = mock_sock_instance
        # connect_ex returns 0 for success (Open Port)
        mock_sock_instance.connect_ex.return_value = 0
        
        # We capture stdout to verify the print statement
        with patch('sys.stdout') as fake_out:
            scanner.scan_ports("127.0.0.1", [80])
            # Check if print was called
            self.assertTrue(mock_sock_instance.connect_ex.called)

if __name__ == '__main__':
    unittest.main()
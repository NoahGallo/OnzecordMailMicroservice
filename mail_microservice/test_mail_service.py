import unittest
from unittest.mock import patch, MagicMock
from mail_service import get_credentials, send_email, create_message, send_message

class TestMailService(unittest.TestCase):

    @patch('os.path.exists')
    @patch('mail_service.Credentials.from_authorized_user_file')
    @patch('mail_service.Credentials')
    @patch('mail_service.Request')
    @patch('mail_service.InstalledAppFlow')
    def test_get_credentials(self, mock_flow, mock_request, mock_credentials, mock_from_authorized_user_file, mock_path_exists):
        # Mock the os.path.exists to return True, simulating the existence of 'token.json'
        mock_path_exists.return_value = True
        # Mock the Credentials.from_authorized_user_file to return a mock credentials object
        mock_credentials_instance = MagicMock()
        mock_credentials_instance.valid = True
        mock_from_authorized_user_file.return_value = mock_credentials_instance
        # Call get_credentials and assert the returned value is the mock credentials instance
        self.assertEqual(get_credentials(), mock_credentials_instance)

    @patch('mail_service.build')
    @patch('mail_service.get_credentials')
    def test_send_email(self, mock_get_credentials, mock_build):
        # Mock get_credentials to return a credentials instance
        mock_creds = MagicMock()
        mock_get_credentials.return_value = mock_creds
        # Mock build to return a service instance
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        # Mock the create_message function to return a test message
        test_message = {'raw': 'test_message'}
        with patch('mail_service.create_message', return_value=test_message):
            # Call send_email and assert it returns True
            self.assertTrue(send_email('test@example.com', 'Test Subject', 'Test Message'))

    def test_create_message(self):
        # Call create_message and assert the returned dictionary has the correct structure
        message = create_message('test@example.com', 'Test Subject', 'Test Message')
        self.assertIn('raw', message)
        self.assertIsInstance(message['raw'], str)

    @patch('mail_service.build')
    def test_send_message(self, mock_build):
        # Mock the service.users().messages().send() method to return a successful response
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        mock_service.users().messages().send().execute.return_value = {'id': 'testid'}
        # Call send_message and assert it returns True
        self.assertTrue(send_message(mock_service, 'me', {'raw': 'test_message'}))

if __name__ == '__main__':
    unittest.main(verbosity=2)

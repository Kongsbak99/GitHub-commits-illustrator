# test_main.py
import unittest
from unittest.mock import patch, Mock
from main import main
from service import Service

class TestService(unittest.TestCase):
    @patch('service.Client')
    def test_getClient_success(self, mock_client):
        token = 'test-token'
        service = Service(token, 'repo_name', 'owner', False)
        client = service.getClient()
        mock_client.assert_called_once()
        self.assertIsNotNone(client)

    @patch('service.Client')
    def test_fetchCommits_success(self, mock_client):
        token = 'test-token'
        mock_client_instance = mock_client.return_value
        mock_client_instance.execute.return_value = {
            'repository': {
                'defaultBranchRef': {
                    'target': {
                        'history': {
                            'nodes': [{'oid': '123', 'message': 'Test commit', 'parents': {'nodes': []}}]
                        }
                    }
                }
            }
        }

        service = Service(token, 'repo_name', 'owner', False)
        commits = service.fetchCommits(mock_client_instance)
        mock_client_instance.execute.assert_called_once()
        self.assertIsInstance(commits, list)


@patch('main.Service')
@patch('builtins.input', side_effect=['repo_name', 'owner', 'y'])
@patch('os.getenv', return_value='test-token')
class TestMainFunction(unittest.TestCase):
    def test_main_success(self, mock_getenv, mock_input, mock_service):
        mock_service_instance = mock_service.return_value
        mock_service_instance.verifyAcyclic.return_value = True
        mock_service_instance.fetchCommits.return_value = []
        mock_service_instance.buildGraph.return_value = (Mock(), {})

        main('repo_name', 'owner', 'test-token', 'y')
        mock_service_instance.verifyAcyclic.assert_called_once()
        mock_service.assert_called_once_with('test-token', 'repo_name', 'owner', True)

    def test_main_failure(self, mock_getenv, mock_input, mock_service):
        mock_service_instance = mock_service.return_value
        mock_service_instance.verifyAcyclic.return_value = False
        mock_service_instance.fetchCommits.return_value = []
        mock_service_instance.buildGraph.return_value = (Mock(), {})

        main('repo_name', 'owner', 'test-token', 'n')
        mock_service_instance.verifyAcyclic.assert_called_once()
        mock_service.assert_called_once_with('test-token', 'repo_name', 'owner', False)

if __name__ == '__main__':
    unittest.main()

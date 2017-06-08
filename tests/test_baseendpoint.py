import unittest
import ujson as json
from tests import mock
from requests.exceptions import ConnectionError

from betfairlightweight import APIClient
from betfairlightweight.endpoints.baseendpoint import BaseEndpoint, RestEndpoint
from betfairlightweight.exceptions import APIError

from tests.tools import create_mock_json


class BaseEndPointTest(unittest.TestCase):

    def setUp(self):
        self.client = APIClient('username', 'password', 'app_key', 'UK')
        self.base_endpoint = BaseEndpoint(self.client)

    def test_init(self):
        assert self.base_endpoint.connect_timeout == 3.05
        assert self.base_endpoint.read_timeout == 16
        assert self.base_endpoint._error == APIError
        assert self.base_endpoint.client == self.client
        assert self.base_endpoint.URI is None
        assert self.base_endpoint.METHOD is None

    def test_base_endpoint_create_req(self):
        payload = {'jsonrpc': '2.0',
                   'method': 'test',
                   'params': 'empty',
                   'id': 1}
        assert self.base_endpoint.create_req('test', 'empty') == json.dumps(payload)

    @mock.patch('betfairlightweight.endpoints.baseendpoint.BaseEndpoint.create_req')
    @mock.patch('betfairlightweight.baseclient.BaseClient.cert')
    @mock.patch('betfairlightweight.baseclient.BaseClient.request_headers')
    @mock.patch('betfairlightweight.baseclient.requests.post')
    def test_request(self, mock_post, mock_request_headers, mock_cert, mock_create_req):
        mock_response = create_mock_json('tests/resources/login_success.json')
        mock_post.return_value = mock_response

        mock_client_cert = mock.Mock()
        mock_client_cert.return_value = []
        mock_cert.return_value = mock_client_cert

        url = 'https://api.betfair.com/exchange/None'
        response = self.base_endpoint.request(None, None, None)

        mock_post.assert_called_once_with(url, data=mock_create_req(),
                                          headers=mock_request_headers, timeout=(3.05, 16))
        assert response[0] == mock_response.json()
        assert isinstance(response[1], float)

    @mock.patch('betfairlightweight.endpoints.baseendpoint.BaseEndpoint.create_req')
    @mock.patch('betfairlightweight.baseclient.BaseClient.cert')
    @mock.patch('betfairlightweight.baseclient.BaseClient.request_headers')
    @mock.patch('betfairlightweight.baseclient.requests.post')
    def test_request_error(self, mock_post, mock_request_headers, mock_cert, mock_create_req):
        mock_post.side_effect = ConnectionError()
        with self.assertRaises(APIError):
            self.base_endpoint.request(None, None, None)

        mock_post.side_effect = ValueError()
        with self.assertRaises(APIError):
            self.base_endpoint.request(None, None, None)

    def test_base_endpoint_error_handler(self):
        mock_response = create_mock_json('tests/resources/base_endpoint_success.json')
        assert self.base_endpoint._error_handler(mock_response.json()) is None

        mock_response = create_mock_json('tests/resources/base_endpoint_fail.json')
        with self.assertRaises(APIError):
            self.base_endpoint._error_handler(mock_response.json())

    def test_base_endpoint_process_response(self):
        mock_resource = mock.Mock()

        response_list = [{}, {}]
        response = self.base_endpoint.process_response(response_list, mock_resource, None, False)
        assert type(response) == list
        assert response[0] == mock_resource()

        response_result_list = {'result': [{}, {}]}
        response = self.base_endpoint.process_response(response_result_list, mock_resource, None, False)
        assert type(response) == list
        assert response[0] == mock_resource()

        response_result = {'result': {}}
        response = self.base_endpoint.process_response(response_result, mock_resource, None, False)
        assert response == mock_resource()

        # lightweight tests
        response_list = [{}, {}]
        response = self.base_endpoint.process_response(response_list, mock_resource, None, True)
        assert response == response_list

        client = APIClient('username', 'password', 'app_key', lightweight=True)
        base_endpoint = BaseEndpoint(client)
        response_list = [{}, {}]
        response = base_endpoint.process_response(response_list, mock_resource, None, False)
        assert type(response) == list
        assert response[0] == mock_resource()

    def test_base_endpoint_url(self):
        assert self.base_endpoint.url == '%s%s' % (self.base_endpoint.client.api_uri, self.base_endpoint.URI)


class RestEndpointTest(unittest.TestCase):

    def setUp(self):
        self.client = APIClient('username', 'password', 'app_key', 'UK')
        self.rest_endpoint = RestEndpoint(self.client)

    def test_init(self):
        assert self.rest_endpoint.connect_timeout == 3.05
        assert self.rest_endpoint.read_timeout == 16
        assert self.rest_endpoint._error is None
        assert self.rest_endpoint.client == self.client
        assert self.rest_endpoint.URI is None
        assert self.rest_endpoint.METHOD is None

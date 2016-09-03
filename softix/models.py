import sessions
import json
from . import exceptions

class SoftixCore(object):
    """
    Base class for all Softix objects.
    """

    def __init__(self):
        self.access_token = ''
        self.session = sessions.Session()

    def build_url(self, *urls, **kwargs):
        """
        Build a url

        :param string urls: A string of URIS
        :returns `string`
        """

        return self.session.build_url(*urls, **kwargs)

    def authenticate(self, username, password):
        """
        Generate access token and update the session headers.
        """
        creds = (username, password)
        url = self.build_url('oauth2', 'accesstoken')

        data = {
            'grant_type': 'client_credentials'
        }

        response = self.session.post(url, auth=creds, data=data)
        response.raise_for_status()
        self.access_token = response.json().get('access_token')

    def create_customer(self, seller_code, **customer):
        """
        Create a new customer.

        :param string seller_code: (required) Seller code provided by Dubai government
        :returns: int id
        """
        url = self.build_url('customers?sellerCode={0}'.format(seller_code))
        headers = {
            'Authorization': 'Bearer {0}'.format(self.access_token),
            'Content-Type': 'application/json'
        }
        data = self._json(self._post(url, data=json.dumps(customer), headers=headers), 200)
        return data['ID']

    def performance_prices(self, seller_code):
        """
        Retrieve performance prices. Although I do not know, currently,
        what the hell a performance price is.
        """
        url = self.build_url('performances', 'ETES2JN', 'prices')
        headers = {
            'Authorization': 'Bearer {0}'.format(self.access_token),
            'Content-Type': 'application/json'
        }
        data = {'channel': 'W', 'sellerCode': seller_code}
        prices = self._json(self._get(url, params=data, headers=headers), 200)
        return prices

    def _get(self, url, **kwargs):
        return self.session.get(url, **kwargs)

    def _post(self, url, **kwargs):
        return self.session.post(url, **kwargs)

    def _json(self, response, status_code):
        data = None
        if self.is_response_successful(response, 200):
            data = response.json()
        return data
    def is_response_successful(self, response, expected_status_code):
        """
        Validate response and return True if request was expected.
        """
        if response is not None:
            if response.status_code == expected_status_code:
                return True
            if response.status_code >= 400:
                raise exceptions.SoftixError(response.json().get('Message'))
        return False

    def raise_response_error(self, response):
        """
        Raise an exception based off of the error code.
        """

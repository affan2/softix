import sessions
import json

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
        Generate access token for remainder of session
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
        response = self.session.post(url, data=json.dumps(customer), headers=headers)
        response.raise_for_status()
        content = json.loads(response.content)
        return content['ID']

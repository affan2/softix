import sessions

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

        base_url = kwargs.get('base_url') or self.session.base_url
        url = base_url + '/'.join(urls)
        return url

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

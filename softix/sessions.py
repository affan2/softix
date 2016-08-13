import requests


class Session(requests.sessions.Session):


    def __init__(self):
        super(Session, self).__init__() 
        self.base_url = 'https://api.etixdubai.com/'

        headers = {
            'Accept': 'application/vnd.softix.api-v1.0+json',
            'Accept-Language': 'en_US',
        }

        self.headers.update(headers)

    def build_url(self, *urls, **kwargs):
        """
        Build a valid URL.
        """
        base_url = kwargs.get('base_url') or self.base_url
        url = base_url + '/'.join(urls)
        return url

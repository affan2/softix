import requests


class Session(requests.sessions.Session):

    session = requests.sessions.Session()

    headers = {
        'Accept': 'application/vnd.softix.api-v1.0+json',
        'Accept-Language': 'en_US',
    }

    def __init__(self):
        self.base_url = 'https://api.etixdubai.com/'


    def post(self, url, *args, **kwargs):
        """
        Send HTTP POST
        """
        return self.session.post(url, headers=self.headers, *args, **kwargs)

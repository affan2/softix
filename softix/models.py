import os
import datetime
import sessions
import json
from . import exceptions


def uppercase_keys(item, *keys):
    item_copy = item.copy()
    for key in keys:
        if key in item_copy:
            item_copy[key] = item_copy.get(key, '').upper()
    return item_copy

def validate_customer(customer):
    required_fields = (
        'salutation',
        'firstname',
        'lastname',
        'nationality',
        'email',
        'dateofbirth',
        'internationalcode',
        'areacode',
        'phonenumber',
        'addressline1',
        'addressline2',
        'addressline3',
        'city',
        'countrycode',
        'state',
    )
    for field in required_fields:
        if field not in customer:
            raise exceptions.MissingRequiredCustomerField(
                'Missing "{0}"'.format(field)
            )
    if not two_characters_long(customer.get('countrycode')):
        raise exceptions.InvalidCustomerField(
            '{0} needs to be a 2 characters'.format('countrycode')
            )
    if not two_characters_long(customer.get('nationality')):
        raise exceptions.InvalidCustomerField(
            '{0} needs to be a 2 characters'.format('nationality')
            )

def two_characters_long(data):
    return True if len(data) == 2 else False

class SoftixCore(object):
    """
    Base class for all Softix objects.
    """

    def __init__(self):
        self.access_token = ''
        self.session = sessions.Session()

    def basket(self, seller_code, basket_id):
        """
        Get basket.

        An exception may raise if the basket has expired:
          'No basket found for the requested basket id'
        """
        url = self.build_url('baskets', basket_id)
        headers = {
            'Authorization': 'Bearer {0}'.format(self.access_token),
            'Content-Type': 'application/json'
        }
        data = self._json(self._get(url, params={'sellerCode': seller_code}, headers=headers), 200)
        return data

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

        We update the default response from the API to include an
        expiration_date to allow us to create new tokens
        """
        creds = (username, password)
        url = self.build_url('oauth2', 'accesstoken')

        data = {
            'grant_type': 'client_credentials'
        }

        response = self._json(self._post(url, auth=creds, data=data), 200)
        now = datetime.datetime.utcnow()
        access_token = response['access_token']
        expires_in = response['expires_in']
        expiration_date = datetime.datetime.utcnow() + datetime.timedelta(0, expires_in)
        authentication_data = response.copy()
        authentication_data.update({
            'expiration_date': expiration_date.isoformat()
        })
        try:
            self.access_token = response['access_token']
            return authentication_data
        except KeyError:
            raise exceptions.AuthenticationError('Missing access_token from API')


    def create_basket(self, seller_code, performance_code, section, demands, fees):
        """
        Create a new basket.

        Section/Area is the group of seats
        """
        url = self.build_url('baskets')
        headers = {
            'Authorization': 'Bearer {0}'.format(self.access_token),
            'Content-Type': 'application/json'
        }
        data = {
            'Channel': 'W',
            'Seller': seller_code,
            'Performancecode': performance_code,
            'Area': section,
            'holdcode': '',
            'Demand': [ self.build_demand_request(d) for d in demands],
            'Fees': [self.build_fee_request(f) for f in fees]
        }
        response = self._json(self._post(url, data=json.dumps(data), headers=headers), 201)
        return response

    def create_customer(self, seller_code, **customer):
        """
        Create a new customer.

        :param string seller_code: (required) Seller code provided by Dubai government
        :returns: int id
        """
        validate_customer(customer)
        customer = uppercase_keys(customer, 'nationality', 'countrycode')
        url = self.build_url('customers?sellerCode={0}'.format(seller_code))
        headers = {
            'Authorization': 'Bearer {0}'.format(self.access_token),
            'Content-Type': 'application/json'
        }
        data = self._json(self._post(url, data=json.dumps(customer), headers=headers), 200)
        return data['ID']

    def performance_availabilities(self, seller_code, performance_code):
        """
        Retrieve performance price availibilties.
        """
        url = self.build_url('performances', performance_code, 'availabilities')
        headers = {
            'Authorization': 'Bearer {0}'.format(self.access_token),
            'Content-Type': 'application/json'
        }
        data = {'channel': 'W', 'sellerCode': seller_code}
        availabilities = self._json(self._get(url, params=data, headers=headers), 200)
        return availabilities

    def performance_prices(self, seller_code, performance_code):
        """
        Retrieve performance prices. 
        """
        url = self.build_url('performances', performance_code, 'prices')
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
        if self.is_response_successful(response, status_code):
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

    def build_demand_request(self, demand):
        demand_request = {
            'PriceTypeCode': demand.price_type_code,
            'Quantity': demand.quantity,
            'Admits': demand.admits,
            'Customer': {}
        }
        return demand_request

    def build_fee_request(self, fee):
        fee_request = {
            'Type': fee.type,
            'Code': fee.code,
        }
        return fee_request

class Demand(object):

    def __init__(self, price_type_code, quantity, admits):
        self.price_type_code = str(price_type_code)
        self.quantity = int(quantity)
        self.admits = int(admits)


class DemandRequest(dict):
    def __init__(self, demand):
        self.PriceTypeCode = demand.price_type_code
        self.Quantity = demand.quantity


class Fee(object):

    def __init__(self, fee_type, code):
        self.type = fee_type
        self.code = code

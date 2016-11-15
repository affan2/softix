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
        data = self._json(self._get(url, params={'sellerCode': seller_code}), 200)
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

        response = self._json(self._post(url, auth=creds, headers=None, data=data), 200)
        authentication = Authentication(response)
        self.access_token = authentication.access_token
        return authentication


    def add_offer(self, seller_code, basket_id, performance_code, section, demands, fees):
        """
        Add an offer to an existing basket

        Section/Area is the group of seats
        """
        url = self.build_url('baskets', basket_id, 'offers')
        data = {
            'Channel': 'W',
            'Seller': seller_code,
            'Performancecode': performance_code,
            'Area': section,
            'holdcode': '',
            'Demand': [demand.to_request() for demand in demands],
            'Fees': [fee.to_request() for fee in fees]
        }
        response = self._json(self._post(url, data=json.dumps(data)), 201)
        return response

    def create_basket(self, seller_code, performance_code, section, demands, fees):
        """
        Create a new basket.

        Section/Area is the group of seats
        """
        url = self.build_url('baskets')
        data = {
            'Channel': 'W',
            'Seller': seller_code,
            'Performancecode': performance_code,
            'Area': section,
            'holdcode': '',
            'Demand': [demand.to_request() for demand in demands],
            'Fees': [fee.to_request() for fee in fees]
        }
        response = self._json(self._post(url, data=json.dumps(data)), 201)
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
        data = self._json(self._post(url, data=json.dumps(customer)), 200)
        return data

    def order(self, seller_code, order_id):
        """
        View order details.
        """
        url = self.build_url('orders', order_id)
        data = {
            'sellerCode': seller_code
        }
        order = self._json(self._get(url, params=data), 200)
        return order

    def performance_availabilities(self, seller_code, performance_code):
        """
        Retrieve performance price availibilties.
        """
        url = self.build_url('performances', performance_code, 'availabilities')
        data = {'channel': 'W', 'sellerCode': seller_code}
        availabilities = self._json(self._get(url, params=data), 200)
        return availabilities

    def performance_prices(self, seller_code, performance_code):
        """
        Retrieve performance prices. 
        """
        url = self.build_url('performances', performance_code, 'prices')
        data = {'channel': 'W', 'sellerCode': seller_code}
        prices = self._json(self._get(url, params=data), 200)
        return prices

    def purchase_basket(self, seller_code, basket_id):
        """
        Purchase a basket.
        """
        url = self.build_url('Baskets', basket_id, 'purchase')
        basket = Basket(self.basket(seller_code, basket_id))
        data = {
            'Seller': seller_code,
            'Payments': [Payment(basket.total).to_request()]
        }
        response = self._json(self._post(url, data=json.dumps(data)), 201)
        return response

    def _get(self, url, **kwargs):
        default_headers = {
            'Authorization': 'Bearer {0}'.format(self.access_token),
            'Content-Type': 'application/json'
        }
        kwargs['headers'] = kwargs.get('headers', default_headers)
        return self.session.get(url, **kwargs)

    def _post(self, url, **kwargs):
        default_headers = {
            'Authorization': 'Bearer {0}'.format(self.access_token),
            'Content-Type': 'application/json'
        }
        kwargs['headers'] = kwargs.get('headers', default_headers)
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

class Demand(object):

    def __init__(self, price_type_code, quantity, admits):
        self.price_type_code = str(price_type_code)
        self.quantity = int(quantity)
        self.admits = int(admits)

    def to_request(self):
        request = {
            'PriceTypeCode': self.price_type_code,
            'Quantity': self.quantity,
            'Admits': self.admits,
            'Customer': {}
        }
        return request


class Fee(object):

    def __init__(self, fee_type, code):
        self.type = fee_type
        self.code = code

    def to_request(self):
        fee = {
            'Type': self.type,
            'Code': self.code,
        }
        return fee

class Payment(object):
    def __init__(self, amount, means_of_payment='EXTERNAL'):
        self.amount = amount
        self.means_of_payment = means_of_payment

    def to_request(self):
        request = {
            'Amount': self.amount,
            'MeansOfPayment': self.means_of_payment
        }
        return request

class Authentication(dict):

    def __init__(self, data):
        super(Authentication, self).__init__(data)
        if 'access_token' not in data:
            raise exceptions.AuthenticationError('Missing access_token from API')
        now = datetime.datetime.utcnow()
        expires_in = data['expires_in']
        expiration_date = datetime.datetime.utcnow() + datetime.timedelta(0, expires_in)
        self.update({
            'expiration_date': expiration_date.isoformat()
        })

    @property
    def access_token(self):
        return self['access_token']

class Customer(object):
    def __init__(self, customer_data):
        self.customer_data = customer_data

class Basket(dict):
    def __init__(self, data):
        super(Basket, self).__init__(data)

    @property
    def offers(self):
        return self['Offers']


    @property
    def total(self):
        if len(self.offers) == 1:
            return self.net(self.offers[0])
        else:
            return reduce((lambda x, y: self.net(x), + self.net(y)), self.offers)

    def net(self, offer):
        return offer['Demand'][0]['Prices'][0]['Net']

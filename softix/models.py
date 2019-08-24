import datetime
import json

import sessions
from . import exceptions
from . helpers import remove_none


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
    """Base class for all Softix objects."""

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
        data = {
            'sellerCode': seller_code
        }
        response = self._json(self._get(url, params=data), 200)
        return response

    def build_url(self, *urls, **kwargs):
        """Build a url.

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

        response = self._json(self._post(url, auth=creds, headers=None,
                                         data=data), 200)
        authentication = Authentication(response)
        self.access_token = authentication.access_token
        return authentication

    def add_offer(self, seller_code, basket_id, performance_code, section,
                  demands, fees):
        """Add an offer to an existing basket.

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

    def add_offer_with_seats(self, seller_code, basket_id, performance_code,
                             section, demands, fees, seat):
        """Add an offer to an existing basket.

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
            'Fees': [fee.to_request() for fee in fees],
            'Seats': seat.to_request(),
        }
        response = self._json(self._post(url, data=json.dumps(data)), 201)
        return response

    def create_basket(self, seller_code, performance_code, section, demands,
                      fees, customer_id=None):
        """Create a new basket.

        Section/Area is the group of seats
        """
        customer = self.customer(seller_code, customer_id).to_request() if customer_id else None  # NOQA
        url = self.build_url('baskets')
        data = {
            'Channel': 'W',
            'Seller': seller_code,
            'Performancecode': performance_code,
            'Area': section,
            'holdcode': '',
            'Demand': [demand.to_request() for demand in demands],
            'Fees': [fee.to_request() for fee in fees],
            'Customer': customer
        }
        remove_none(data)
        response = self._json(self._post(url, data=json.dumps(data)), 201)
        return response

    def create_basket_with_seat(self, seller_code, performance_code, section,
                                demands, fees, seat, customer_id=None):
        """Create a new basket.

        Section/Area is the group of seats
        """
        customer = self.customer(seller_code, customer_id).to_request() if customer_id else None  # NOQA
        url = self.build_url('baskets')
        data = {
            'Channel': 'W',
            'Seller': seller_code,
            'Performancecode': performance_code,
            'Area': section,
            'holdcode': '',
            'Demand': [demand.to_request() for demand in demands],
            'Fees': [fee.to_request() for fee in fees],
            'Seats': seat.to_request(),
            'Customer': customer
        }
        remove_none(data)
        response = self._json(self._post(url, data=json.dumps(data)), 201)
        return response

    def create_customer(self, seller_code, **customer):
        """Create a new customer.

        :param string seller_code: (required) Seller code provided by DTCM
        :returns: int id
        """
        validate_customer(customer)
        customer = uppercase_keys(customer, 'nationality', 'countrycode')
        url = self.build_url('customers?sellerCode={0}'.format(seller_code))
        data = self._json(self._post(url, data=json.dumps(customer)), 200)
        return data

    def customer(self, seller_code, customer_id):
        url = self.build_url('customers', customer_id)
        data = {
            'sellerCode': seller_code
        }
        data = self._json(self._get(url, params=data), 200)
        return Customer(data)

    def order(self, seller_code, order_id):
        """View order details."""
        url = self.build_url('orders', order_id)
        data = {
            'sellerCode': seller_code
        }
        order = self._json(self._get(url, params=data), 200)
        return order

    def transaction_sync(self, seller_code, from_date, to_date):
        """Get transactions list."""
        url = self.build_url('dcal', 'transync', from_date, to_date)
        data = {
            'sellerCode': seller_code
        }
        transactions = self._json(self._get(url, params=data), 200)
        return transactions

    def performance_availabilities(self, seller_code, performance_code):
        """Retrieve performance price availabilities."""
        url = self.build_url('performances', performance_code,
                             'availabilities')
        data = {'channel': 'W', 'sellerCode': seller_code}
        availabilities = self._json(self._get(url, params=data), 200)
        return availabilities

    def performance_prices(self, seller_code, performance_code):
        """Retrieve performance prices."""
        url = self.build_url('performances', performance_code, 'prices')
        data = {'channel': 'W', 'sellerCode': seller_code}
        prices = self._json(self._get(url, params=data), 200)
        return prices

    def purchase_basket(self, seller_code, basket_id, customer_id=None):
        """Purchase a basket."""
        url = self.build_url('Baskets', basket_id, 'purchase')
        basket = Basket(self.basket(seller_code, basket_id))
        customer = self.customer(seller_code, customer_id).to_request() if customer_id else None  # NOQA
        data = {
            'Seller': seller_code,
            'Payments': [Payment(basket.total).to_request()],
            'customer': customer
        }
        remove_none(data)
        response = self._json(self._post(url, data=json.dumps(data)), 201)
        return response

    def reverse_order(self, seller_code, order_id, total):
        """Reverse an order that was once purchased."""
        # order = Order(self.order(seller_code, order_id))
        url = self.build_url('orders', order_id, 'reverse')
        data = {
            'Seller': seller_code,
            # 'refunds': [Payment(order.total).to_request()]
            'refunds': total
        }
        response = self._post(url, data=json.dumps(data))
        self.is_response_successful(response, 204)
        return

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
        """Validate response and return True if request was expected."""
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


class Seat(object):

    def __init__(self, section, row, seats):
        self.section = section
        self.row = row
        self.seats = seats

    def to_request(self):
        request = {
            'Section': self.section,
            'Row': self.row,
            'Seats': self.seats,
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
            raise exceptions.AuthenticationError('Missing access_token from API')  # NOQA
        now = datetime.datetime.utcnow()
        expires_in = data['expires_in']
        expiration_date = now + datetime.timedelta(0, expires_in)
        self.update({
            'expiration_date': expiration_date.isoformat()
        })

    @property
    def access_token(self):
        return self['access_token']


class Customer(dict):
    def __init__(self, data):
        super(Customer, self).__init__(data)

    @classmethod
    def from_id(cls, customer_id):
        return cls({'ID': customer_id})

    @property
    def account(self):
        return self['Account']

    @property
    def afile(self):
        return self['AFile']

    @property
    def id(self):
        return self['ID']

    def to_request(self):
        if not self:
            return {}
        return {"ID": self.id, "Account": self.account, "AFile": self.afile}


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
            return sum(self.net(offer) for offer in self.offers)

    def net(self, offer):
        return offer['Demand'][0]['Prices'][0]['Net']


class Order(dict):
    def __init__(self, data):
        super(Order, self).__init__(data)

    @property
    def line_items(self):
        return self['OrderItems'][0]['OrderLineItems']

    @property
    def total(self):
        if len(self.line_items) == 1:
            return self['OrderItems'][0]['OrderLineItems'][0]['Price']['Net']
        else:
            return sum(self.net(line_item) for line_item in self.line_items)

    def net(self, line_item):
        return line_item['Price']['Net']

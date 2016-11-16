import os
from datetime import datetime
import softix
import collections
import betamax
import pytest

@pytest.fixture
def seller_code():
    return os.environ.get('SOFTIX_SELLER_CODE', 'ANMFZ1')

def test_create_customer(seller_code):
    """
    Test creating a customer.
    """
    st = softix.SoftixCore()
    customer = {
        'salutation': '-',
        'firstname': 'ajilan',
        'lastname': 'MA',
        'nationality': 'IN',
        'email': 'unknown@unknown.com',
        'dateofbirth': '4-23-2015',
        'internationalcode': '971',
        'areacode': 'unknown',
        'phonenumber': '507156120',
        'addressline1': '-',
        'addressline2': '-',
        'addressline3': '-',
        'city': 'dubai',
        'countrycode': 'IN',
        'state': 'dubai'
    }
    recorder = betamax.Betamax(st.session)
    match_on = ['uri', 'method', 'json-body']
    cassette_name = 'SoftixCore_create_customer'
    st.access_token = os.environ.get('SOFTIX_TOKEN', '')

    with recorder.use_cassette(cassette_name, match_requests_on=match_on):

        assert isinstance(st.create_customer(seller_code, **customer), dict)

        invalid_customer = customer.copy()
        invalid_customer.pop('state', None)

        with pytest.raises(softix.exceptions.MissingRequiredCustomerField):
            st.create_customer(seller_code, **invalid_customer)


def test_performance_availabilities(seller_code):
    st = softix.SoftixCore()
    recorder = betamax.Betamax(st.session)
    cassette_name = 'SoftixCore_performance_availabilities'
    match_on = ['uri', 'method', 'body']
    st.access_token = os.environ.get('SOFTIX_TOKEN', '')

    with recorder.use_cassette(cassette_name, match_requests_on=match_on):
        availabilities = st.performance_availabilities(seller_code, 'ETES2JN')
        assert availabilities

def test_performance_prices(seller_code):
    st = softix.SoftixCore()
    recorder = betamax.Betamax(st.session)
    cassette_name = 'SoftixCore_performance_prices'
    match_on = ['uri', 'method', 'body']
    st.access_token = os.environ.get('SOFTIX_TOKEN', '')

    with recorder.use_cassette(cassette_name, match_requests_on=match_on):
        performance_prices = st.performance_prices(seller_code, 'ETES2JN')
        assert performance_prices
        assert isinstance(performance_prices, dict)

def test_create_basket(seller_code):
    st = softix.SoftixCore()
    recorder = betamax.Betamax(st.session)
    cassette_name = 'SoftixCore_create_basket'
    match_on = ['uri', 'method', 'json-body']
    st.access_token = os.environ.get('SOFTIX_TOKEN', '')

    with recorder.use_cassette(cassette_name, match_requests_on=match_on):
        demands = [softix.models.Demand(price_type_code='Q', quantity=1, admits=1)]
        fees = [softix.Fee('5', 'W')]
        basket = st.create_basket(seller_code, 'ETES0000004EL', 'SGA', demands, fees)
        assert basket
        assert isinstance(basket, dict)


def test_purchase_basket(seller_code):
    st = softix.SoftixCore()
    recorder = betamax.Betamax(st.session)
    cassette_name = 'SoftixCore_purchase_basket'
    match_on = ['uri', 'method', 'json-body']
    st.access_token = os.environ.get('SOFTIX_TOKEN', '')

    with recorder.use_cassette(cassette_name, match_requests_on=match_on):
        order = st.purchase_basket(seller_code, '2587-34722766')
        assert order
        assert isinstance(order, dict)


def test_view_order(seller_code):
    st = softix.SoftixCore()
    recorder = betamax.Betamax(st.session)
    cassette_name = 'SoftixCore_view_order'
    match_on = ['uri', 'method', 'json-body']
    st.access_token = os.environ.get('SOFTIX_TOKEN', '')

    with recorder.use_cassette(cassette_name, match_requests_on=match_on):
        order = st.order(seller_code, '20161116,1023')
        assert order
        assert isinstance(order, dict)

import os
import softix
import collections
import betamax
import pytest

def test_authentication():
    """
    Test generating a token.
    """
    st = softix.SoftixCore()
    username = os.environ.get('CLIENT_ID', 'foo')
    password = os.environ.get('SECRET', 'bar')
    recorder = betamax.Betamax(st.session)
    match_on = ['uri', 'method', 'body', 'headers']
    with recorder.use_cassette('SoftixCore_authenticate', match_requests_on=match_on):
        st.authenticate(username, password)
    assert st.access_token


def test_create_customer_():
    """
    Test creating a customer.
    """
    st = softix.SoftixCore()
    username = os.environ.get('CLIENT_ID')
    password = os.environ.get('SECRET')
    seller_code = os.environ.get('SELLER_CODE')
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
    match_on = ['uri', 'method', 'body', 'headers']
    cassette_name = 'SoftixCore_create_customer'

    with recorder.use_cassette(cassette_name, match_requests_on=match_on):
        st.authenticate(username, password)

        assert isinstance(st.create_customer(seller_code, **customer), int)

        invalid_customer = customer.copy()
        invalid_customer.pop('state', None)

        with pytest.raises(softix.exceptions.SoftixError):
            st.create_customer(seller_code, **invalid_customer)


def test_performance_availabilities():
    st = softix.SoftixCore()
    username = os.environ.get('SOFTIX_CLIENT_ID')
    password = os.environ.get('SOFTIX_SECRET')
    seller_code = os.environ.get('SOFTIX_SELLER_CODE')
    recorder = betamax.Betamax(st.session)
    cassette_name = 'SoftixCore_performance_availabilities'
    match_on = ['uri', 'method', 'body', 'headers']

    with recorder.use_cassette(cassette_name, match_requests_on=match_on):
        st.authenticate(username, password)
        availabilities = st.performance_availabilities(seller_code, 'ETES2JN')
        assert availabilities

def test_performance_prices():
    st = softix.SoftixCore()
    username = os.environ.get('SOFTIX_CLIENT_ID')
    password = os.environ.get('SOFTIX_SECRET')
    seller_code = os.environ.get('SOFTIX_SELLER_CODE')
    recorder = betamax.Betamax(st.session)
    cassette_name = 'SoftixCore_performance_prices'
    match_on = ['uri', 'method', 'body', 'headers']

    with recorder.use_cassette(cassette_name, match_requests_on=match_on):
        st.authenticate(username, password)
        performance_prices = st.performance_prices(seller_code, 'ETES2JN')
        assert performance_prices

def test_create_basket():
    st = softix.SoftixCore()
    username = os.environ.get('SOFTIX_CLIENT_ID')
    password = os.environ.get('SOFTIX_SECRET')
    seller_code = os.environ.get('SOFTIX_SELLER_CODE')
    recorder = betamax.Betamax(st.session)
    cassette_name = 'SoftixCore_create_basket'
    match_on = ['uri', 'method', 'body', 'headers']
    basket = {
        'Area': 'SGA'
    }

    with recorder.use_cassette(cassette_name, match_requests_on=match_on):
        st.authenticate(username, password)
        performance_prices = st.create_basket(seller_code, 'ETES2JN', **basket)
        assert performance_prices


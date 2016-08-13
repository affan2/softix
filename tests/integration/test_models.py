import os
import softix
import collections
import betamax

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


def test_create_customer(recorder):
    """
    Test creating a customer.
    """
    st = softix.SoftixCore()
    username = os.environ.get('CLIENT_ID')
    password = os.environ.get('SECRET')
    seller_code = os.environ.get('SELLER_CODE')
    st.authenticate(username, password)
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
    assert isinstance(st.create_customer(seller_code, **customer), int)

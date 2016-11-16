import softix
import pytest
import mock

@pytest.fixture
def auth_headers():
    return {'Content-Type': 'application/json', 'Authorization': 'Bearer '}

def test_authenticate(softixcore):
    """
    Verify authentication is called correctly.
    """
    with mock.patch.object(softix.models, 'Authentication') as auth:
        softixcore.authenticate('my-username', 'my-password')
    url = 'https://api.etixdubai.com/oauth2/accesstoken'
    softixcore.session.post.assert_called_once_with(
        url,
        auth=('my-username', 'my-password'),
        data={'grant_type': 'client_credentials'},
        headers=None
    )

def test_order(softixcore, auth_headers):
    """
    Verify the URL called.
    """

    #reset auth
    softixcore.access_token = ''
    softixcore.order('seller-code', '863-145')
    data = {'sellerCode': 'seller-code'}
    url = 'https://api.etixdubai.com/orders/863-145'
    softixcore.session.get.assert_called_once_with(
        url,
        params=data,
        headers=auth_headers
    )

def test_performance_prices(softixcore, auth_headers):
    """
    Verify the URL called.
    """

    #reset auth
    softixcore.access_token = ''
    softixcore.performance_prices('seller-code', 'ETES2JN')
    data = {'channel': 'W', 'sellerCode': 'seller-code'}
    url = 'https://api.etixdubai.com/performances/ETES2JN/prices'
    softixcore.session.get.assert_called_once_with(
        url,
        params=data,
        headers=auth_headers
    )


def test_performance_availabilities(softixcore, auth_headers):
    """
    Verify the URL called.
    """

    #reset auth
    softixcore.access_token = ''
    softixcore.performance_availabilities('seller-code', 'ETES2JN')
    data = {'channel': 'W', 'sellerCode': 'seller-code'}
    url = 'https://api.etixdubai.com/performances/ETES2JN/availabilities'
    softixcore.session.get.assert_called_once_with(
        url,
        params=data,
        headers=auth_headers
    )

def test_uppercase_keys():
    mydict = {
        'nationality': 'in',
        'countrycode': 'ae',
        'firstname': 'matt'
    }
    expected_dict = {
        'nationality': 'IN',
        'countrycode': 'AE',
        'firstname': 'matt'
    }

    assert softix.models.uppercase_keys(mydict, 'nationality', 'countrycode') == expected_dict

def test_validate_customer(valid_customer):
    assert softix.models.validate_customer(valid_customer) is None

def test_validate_customer_missing_required_field(valid_customer):
    with pytest.raises(softix.exceptions.MissingRequiredCustomerField) as exception:
        customer_missing_email = valid_customer.copy().pop('email')
        softix.models.validate_customer(customer_missing_email)

def test_validate_customer_invalid_country_code(valid_customer):
    customer = valid_customer.copy()
    customer['countrycode'] = 'more_than_two_characters'
    with pytest.raises(softix.exceptions.InvalidCustomerField) as exception:
        softix.models.validate_customer(customer)

def test_validate_customer_invalid_nationality(valid_customer):
    customer = valid_customer.copy()
    customer['nationality'] = 'more_than_two_characters'
    with pytest.raises(softix.exceptions.InvalidCustomerField) as exception:
        softix.models.validate_customer(customer)

import softix
import pytest

def test_authenticate(softixcore):
    """
    Verify authentication is called correctly.
    """
    softixcore.authenticate('my-username', 'my-password')
    url = 'https://api.etixdubai.com/oauth2/accesstoken'
    softixcore.session.post.assert_called_once_with(
        url,
        auth=('my-username', 'my-password'),
        data={'grant_type': 'client_credentials'}
    )

def test_performance_prices(softixcore):
    """
    Verify the URL called.
    """
    softixcore.performance_prices('seller-code', 'ETES2JN')
    data = {'channel': 'W', 'sellerCode': 'seller-code'}
    url = 'https://api.etixdubai.com/performances/ETES2JN/prices'
    headers = {
        'Authorization': 'Bearer ',
        'Content-Type': 'application/json'
    }
    softixcore.session.get.assert_called_once_with(
        url,
        params=data,
        headers=headers
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

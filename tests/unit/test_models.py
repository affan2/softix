import softix

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
    softixcore.performance_prices('fake_seller_code')
    data = {'channel': 'W', 'sellerCode': 'fake_seller_code'}
    url = 'https://api.etixdubai.com/performances/ETES2JN/prices'
    softixcore.session.get.assert_called_once_with(
        url,
        data=data
    )

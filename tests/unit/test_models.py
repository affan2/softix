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

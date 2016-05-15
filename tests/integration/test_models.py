import os
import softix

def test_authentication():
    """
    Test generating a token.
    """
    st = softix.SoftixCore()
    username = os.environ.get('CLIENT_ID')
    password = os.environ.get('SECRET')
    st.authenticate(username, password)
    assert st.access_token

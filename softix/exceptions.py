class SoftixException(Exception):
    def __init__(self):
        super(SoftixException, self).__init__()

class CustomerException(Exception):
    pass

class CreateCustomerException(Exception):
    pass

class SoftixError(Exception):
    pass

class MissingRequiredCustomerField(SoftixError):
    pass

class InvalidCustomerField(SoftixError):
    pass

class AuthenticationError(SoftixError):
    pass

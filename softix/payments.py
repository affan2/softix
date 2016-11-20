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

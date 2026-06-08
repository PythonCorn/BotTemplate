class PaymentException(Exception):
    pass


class NotTokenException(PaymentException):
    pass


class InvalidSignatureException(PaymentException):
    pass


class InvalidAmountException(PaymentException):
    pass

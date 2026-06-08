class PaymentException(Exception):
    pass


class NotTokenException(PaymentException):
    pass


class InvalidSignatureException(PaymentException):
    pass


class InvalidAmountException(PaymentException):
    pass


class PaymentProviderNameIsEmpty(PaymentException):
    pass


class PaymentContainerIsNotSet(PaymentException):
    pass


class PaymentProviderIsNotFound(PaymentException):
    pass

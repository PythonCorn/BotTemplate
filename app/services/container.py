from functools import cached_property

from app.database.unit_of_work import UnitOfWork
from app.services.payment_service import PaymentService
from app.services.user_service import UserService


class ServiceContainer:
    """
    A container providing access to various services within an application.

    This class is designed to serve as a central access point for managing and retrieving
    instances of different services. It ensures that each service is initialized and provided
    with the necessary dependencies, such as the unit of work. Cached properties are utilized
    to initialize services only once and reuse the same instance for subsequent requests.

    Attributes:
        uow (UnitOfWork): The unit of work instance used for managing transactions across
        different services.

    """

    def __init__(
        self,
        uow: UnitOfWork,
    ) -> None:
        """
        Initializes the object with the provided Unit of Work instance.

        Attributes:
        uow (UnitOfWork): The UnitOfWork instance used for managing transactions and operations.

        Args:
        uow: UnitOfWork instance that provides transactional context for operations.
        """
        self.uow = uow

    @cached_property
    def users(self) -> UserService:
        """
        Represents a cached property that provides access to the UserService instance.

        This property initializes and returns an instance of the UserService class, using
        the unit of work (uow) provided by the containing object. The value is computed
        once and subsequently cached for future access.

        Returns:
            UserService: An instance of the UserService class.
        """
        return UserService(self.uow)

    @cached_property
    def payments(self) -> PaymentService:
        """
        Returns an instance of the PaymentService class.

        This property method initializes a PaymentService object with the
        unit of work (uow) associated with the current context. The object
        is cached upon its first access, allowing subsequent calls to
        retrieve the same instance, avoiding redundant reinitializations.

        Returns:
            PaymentService: An instance of the PaymentService class configured
            with the current unit of work (uow).
        """
        return PaymentService(self.uow)

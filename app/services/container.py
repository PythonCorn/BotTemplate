from app.database.unit_of_work import UnitOfWork
from app.services.payment_service import PaymentService
from app.services.user_service import UserService


class Services:
    @property
    def users(self):
        return UserService(self.uow)

    @property
    def payments(self):
        return PaymentService(self.uow)

    def __call__(self, uow: UnitOfWork):
        self.uow = uow
        return self

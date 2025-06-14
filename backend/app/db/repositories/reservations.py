from app.db.models import Reservation
from app.db.repositories import Repository


class ReservationRepository(Repository[Reservation]):
    model = Reservation

from sqlalchemy.orm import Session


class Service:
    """Base service holding the transaction-scoped database session."""

    def __init__(self, session: Session) -> None:
        self.session = session

from sqlalchemy.orm.session import Session

from db import CallToActions


def store_cta(
    timestamp: int,
    collateral_token: str,
    debt_token: str,
    message: str,
    session: Session,
):
    session.add(
        CallToActions(
            timestamp=timestamp,
            collateral_token=collateral_token,
            debt_token=debt_token,
            message=message,
        )
    )
    session.commit()

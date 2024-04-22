from flask import abort
import sqlalchemy
from api.extensions import cache
from api.extensions import db
from db import DexNormalizedLiquidity


def fetch_data_from_database():
    try:
        # Subquery to find the maximum timestamp
        max_timestamp_subquery = db.session.query(
            sqlalchemy.func.max(DexNormalizedLiquidity.timestamp).label("max_timestamp")
        ).subquery()

        # Main query to fetch all records with the maximum timestamp
        result = (
            db.session.query(DexNormalizedLiquidity)
            .join(
                max_timestamp_subquery,
                DexNormalizedLiquidity.timestamp
                == max_timestamp_subquery.c.max_timestamp,
            )
            .all()
        )

        # Serialize the result into a list of dictionaries
        data = [
            {
                column.name: getattr(record, column.name)
                for column in DexNormalizedLiquidity.__table__.columns
            }
            for record in result
        ]
        return data

    except ValueError:
        abort(500, description="Failed getting data")


def get_pair_key(x: str, y: str) -> str:
    return f"{x}-{y}"


@cache.cached(timeout=300, key_prefix="liquidity_map")
def get_cached_liquidity():
    data = fetch_data_from_database()
    pair_map: dict[str, dict] = {}
    for item in data:
        key = get_pair_key(item["token_x_address"], item["token_y_address"])
        value = {
            "bids": item["bids"],
            "asks": item["asks"],
        }
        pair_map[key] = value

    return pair_map

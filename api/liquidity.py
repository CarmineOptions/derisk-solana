from flask import abort
import sqlalchemy
from api.cache import cache
from api.db import db_session

def fetch_data_from_database():
    try:
        query = """
        WITH MaxValue AS (
            SELECT MAX(timestamp) AS max_timestamp
            FROM public.dex_normalized_liquidity
        )
        SELECT *
        FROM public.dex_normalized_liquidity, MaxValue
        WHERE timestamp = max_timestamp;
        """
        result = db_session.execute(sqlalchemy.text(query))
        keys = result.keys()
        data = list(
            map(
                lambda arr: dict(zip(keys, arr)),
                result,
            )
        )
        return data

    except ValueError as e:
        print("Failed:", e)
        abort(
            500,
            description="failed getting data",
        )

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

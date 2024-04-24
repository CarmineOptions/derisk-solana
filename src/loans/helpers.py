import os
import time

import pandas
import solana.rpc.api
from solana.exceptions import SolanaRpcException

import src.database


solana_client = solana.rpc.api.Client(os.getenv('RPC_URL'))


def get_account_info(pubkey):
    try:
        response = solana_client.get_account_info_json_parsed(
            solana.rpc.api.Pubkey.from_string(pubkey)
        )
        return response
    except SolanaRpcException as e:
        time.sleep(0.1)
        return get_account_info(pubkey)


def get_decimals(pubkey):
    response = get_account_info(pubkey)
#     print(response)
    return response.value.data.parsed['info']['decimals']


def get_events(
    table: str,
    event_names: tuple[str, ...],
    event_column: str = 'event_name',
    start_block_number: int = 0,
) -> pandas.DataFrame:
    connection = src.database.establish_connection()
    events = pandas.read_sql(
        sql=f"""
            SELECT
                *
            FROM
                {table}
            WHERE
                {event_column} IN {event_names}
            AND
                block >= {start_block_number}
            ORDER BY
                block, transaction_id ASC;
        """,
        con=connection,
    )
    connection.close()
    return events.set_index("id")
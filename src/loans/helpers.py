import pandas

import src.database



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
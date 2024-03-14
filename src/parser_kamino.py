from anchorpy import Program, Idl
import json
from solana.rpc.async_api import AsyncClient, Pubkey
from solders.signature import Signature
import base58
import base64
from anchorpy.program.event import EventParser

from anchorpy.provider import Provider, Wallet, Keypair


def print_out(input):
    return print("Result: ", input)

# Load your IDL file
with open('protocols/idls/yvaults.json', 'r') as fp:
    dict_data = json.load(fp)
    json_str = json.dumps(dict_data)
    idl = Idl.from_json(json_str)

program_id = Pubkey.from_string('KLend2g3cP87fffoy8q1mQqGKjrxjC8boSyAYavgmjD')

solana_client = AsyncClient('https://mainnet.helius-rpc.com/?api-key=efee52f7-fc55-4473-ae58-25a66e70fd6f')
program = Program(idl, program_id, Provider(solana_client, Wallet(Keypair())))
DATA_SUBSTRING = 'Program data: '


# Define a function to fetch and parse transactions
async def fetch_and_parse_transactions():
    # This is a placeholder for fetching transactions. You'll need to implement
    # the logic for fetching transactions based on your requirements. This might
    # include fetching transactions by signature, by account, or other criteria.

    res = await solana_client.get_signatures_for_address(
        program_id,  # Address
        limit=20,
        before = Signature.from_string("5BHgvP9pDzZ5S4cMPpteQVDNHPtpDpvjGWUhv6yxaQh18g34faGy9Ln6c4FbbbAh9JLzq62MnzsQzh7Bpr3noHk6")
    )
    signatures = [i.signature for i in res.value]

    program.idl = await program.fetch_raw_idl(program_id, Provider(solana_client, Wallet(Keypair())))

    for sig in signatures:
        print(f"======={sig}=========")
        # Fetch the transaction details
        transaction = await solana_client.get_transaction(
            sig,
            'jsonParsed',
            max_supported_transaction_version=0
        )
        log_messages = transaction.value.transaction.meta.log_messages

        ep = EventParser(program_id, program.coder)
        ep.parse_logs(log_messages, print_out)

        for i in log_messages:
            print(i)


if __name__ == "__main__":
    import asyncio

    asyncio.run(fetch_and_parse_transactions())

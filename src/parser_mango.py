from anchorpy import Program, Idl
import json
from solana.rpc.async_api import AsyncClient, Pubkey
from solders.signature import Signature
import base58
import base64
from anchorpy.program.event import EventParser
from anchorpy.provider import Provider, Wallet, Keypair



# Load your IDL file
with open('../mango_v4.json', 'r') as fp:
    dict_data = json.load(fp)
    json_str = json.dumps(dict_data)
    idl = Idl.from_json(json_str)

program_id = Pubkey.from_string("4MangoMjqJ2firMokCjjGgoK8d4MXcrgL7XJaL3w6fVg")

solana_client = AsyncClient('https://mainnet.helius-rpc.com/?api-key=efee52f7-fc55-4473-ae58-25a66e70fd6f')
program = Program(idl, program_id, solana_client)
DATA_SUBSTRING = 'Program data: '

# Define a function to fetch and parse transactions
async def fetch_and_parse_transactions():
    # This is a placeholder for fetching transactions. You'll need to implement
    # the logic for fetching transactions based on your requirements. This might
    # include fetching transactions by signature, by account, or other criteria.

    res = await solana_client.get_signatures_for_address(
        Pubkey.from_string("4MangoMjqJ2firMokCjjGgoK8d4MXcrgL7XJaL3w6fVg"),  # Address
        limit=20,
        # before =  # pass some signature here to fetch txs before that one (when fetching more distant history)
    )
    # signatures = [i.signature for i in res.value]
    signatures = [Signature.from_string("5S1sZe41vHq8FBT8aMNY9vBtAqx4BADSQ6J6AHFUL1WeECCMj1YCQP4HTTRXHCtNGqGYNuQvaY8XrVSS4cqWKZp7")]

    for sig in signatures:
        print(sig)
        # Fetch the transaction details
        transaction = await solana_client.get_transaction(
            sig,
            'jsonParsed',
            max_supported_transaction_version=0
        )
        log_messages = transaction.value.transaction.meta.log_messages

        program_data = next((i for i in log_messages if i.startswith('Program data: ')))
        encoded_data = program_data.split(' ')[-1]

        print(f'{DATA_SUBSTRING} {encoded_data}')

        decoded_data = base64.b64decode(encoded_data)

        ep = EventParser(program_id, program.coder)
        ep.parse_logs(log_messages, print)

        # decode instructions:
        # for instruction in transaction.value.transaction.transaction.message.instructions:
        #     print(instruction)
        #     instr_data = instruction.data
        #     decoded_data = base58.b58decode(instr_data)
        #     print(decoded_data)
        #     instruction_data = program.coder.instruction._decode(decoded_data, '', '')
        #     print('instruction:', instruction_data)


if __name__ == "__main__":
    import asyncio

    asyncio.run(fetch_and_parse_transactions())

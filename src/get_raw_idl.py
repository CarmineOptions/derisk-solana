import asyncio
import os

from anchorpy import Program, Idl
import json
from solana.rpc.async_api import AsyncClient, Pubkey
from solders.signature import Signature
import base58
import base64
from anchorpy.program.event import EventParser
from anchorpy.provider import Provider, Wallet, Keypair
from anchorpy.error import IdlNotFoundError


# Load your IDL file
with open('../mango_v4.json', 'r') as fp:
    dict_data = json.load(fp)
    json_str = json.dumps(dict_data)
    idl = Idl.from_json(json_str)

program_id = Pubkey.from_string("MFv2hWf31Z9kbCa1snEPYctwafyhdvnV7FZnsebVacA")

solana_client = AsyncClient(os.getenv("RPC_URL"))
program = Program(idl, program_id, Provider(solana_client, Wallet(Keypair())))
DATA_SUBSTRING = 'Program data: '


async def main():
    for program_id in [
        'KLend2g3cP87fffoy8q1mQqGKjrxjC8boSyAYavgmjD',
        "MFv2hWf31Z9kbCa1snEPYctwafyhdvnV7FZnsebVacA",
        '4MangoMjqJ2firMokCjjGgoK8d4MXcrgL7XJaL3w6fVg',
        'So1endDq2YkqhipRh3WViPa8hdiSpxWy6z3Z6tMCpAo'
    ]:
        try:
            raw_idl = await program.fetch_raw_idl(Pubkey.from_string(program_id), Provider(solana_client, Wallet(Keypair())))
            print(program_id, raw_idl[:100])
        except IdlNotFoundError:
            print(program_id, '- idl not found')

if __name__ == "__main__":
    asyncio.run(main())


import os


# Paths to IDLs which help with parsing transactions.
# Get the absolute path of the current file's directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
print(BASE_DIR)

SOLEND_IDL_PATH: str = os.path.join(BASE_DIR, '')  # Solend is not anchor program
# Source: https://github.com/blockworks-foundation/mango-v4/blob/dev/mango_v4.json.
MANGO_IDL_PATH: str = os.path.join(BASE_DIR, 'idls/mango_v4.json')
# Source: https://explorer.solana.com/address/KLend2g3cP87fffoy8q1mQqGKjrxjC8boSyAYavgmjD/anchor-program
KAMINO_IDL_PATH: str = os.path.join(BASE_DIR, 'idls/kamino_idl.json')
# Source: https://explorer.solana.com/address/MFv2hWf31Z9kbCa1snEPYctwafyhdvnV7FZnsebVacA/anchor-program
MARGINFI_IDL_PATH: str = os.path.join(BASE_DIR, 'idls/marginfi_idl.json')

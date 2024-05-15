import os

# TODO: Use everywhere 
def get_authenticated_rpc_url() -> str:
    """
    Reads Solana RPC url from environment. 
    Raises ValueError if no url is present.
    """
    authenticated_rpc_url = os.environ.get("AUTHENTICATED_RPC_URL")
    if authenticated_rpc_url is None:
        raise ValueError("No AUTHENTICATED_RPC_URL env var")
    return authenticated_rpc_url




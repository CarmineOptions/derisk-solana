import typing
from dataclasses import dataclass
from solders.pubkey import Pubkey
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Commitment
import borsh_construct as borsh
from anchorpy.coder.accounts import ACCOUNT_DISCRIMINATOR_SIZE
from anchorpy.error import AccountInvalidDiscriminator
from anchorpy.utils.rpc import get_multiple_accounts
from anchorpy.borsh_extension import BorshPubkey
from ..program_id import PROGRAM_ID


class StateJSON(typing.TypedDict):
    admin: str
    program_authority: str
    bump: int
    nonce: int


@dataclass
class State:
    discriminator: typing.ClassVar = b"\xd8\x92k^hK\xb6\xb1"
    layout: typing.ClassVar = borsh.CStruct(
        "admin" / BorshPubkey,
        "program_authority" / BorshPubkey,
        "bump" / borsh.U8,
        "nonce" / borsh.U8,
    )
    admin: Pubkey
    program_authority: Pubkey
    bump: int
    nonce: int

    @classmethod
    async def fetch(
        cls,
        conn: AsyncClient,
        address: Pubkey,
        commitment: typing.Optional[Commitment] = None,
        program_id: Pubkey = PROGRAM_ID,
    ) -> typing.Optional["State"]:
        resp = await conn.get_account_info(address, commitment=commitment)
        info = resp.value
        if info is None:
            return None
        if info.owner != program_id:
            raise ValueError("Account does not belong to this program")
        bytes_data = info.data
        return cls.decode(bytes_data)

    @classmethod
    async def fetch_multiple(
        cls,
        conn: AsyncClient,
        addresses: list[Pubkey],
        commitment: typing.Optional[Commitment] = None,
        program_id: Pubkey = PROGRAM_ID,
    ) -> typing.List[typing.Optional["State"]]:
        infos = await get_multiple_accounts(conn, addresses, commitment=commitment)
        res: typing.List[typing.Optional["State"]] = []
        for info in infos:
            if info is None:
                res.append(None)
                continue
            if info.account.owner != program_id:
                raise ValueError("Account does not belong to this program")
            res.append(cls.decode(info.account.data))
        return res

    @classmethod
    def decode(cls, data: bytes) -> "State":
        if data[:ACCOUNT_DISCRIMINATOR_SIZE] != cls.discriminator:
            raise AccountInvalidDiscriminator(
                "The discriminator for this account is invalid"
            )
        dec = State.layout.parse(data[ACCOUNT_DISCRIMINATOR_SIZE:])
        return cls(
            admin=dec.admin,
            program_authority=dec.program_authority,
            bump=dec.bump,
            nonce=dec.nonce,
        )

    def to_json(self) -> StateJSON:
        return {
            "admin": str(self.admin),
            "program_authority": str(self.program_authority),
            "bump": self.bump,
            "nonce": self.nonce,
        }

    @classmethod
    def from_json(cls, obj: StateJSON) -> "State":
        return cls(
            admin=Pubkey.from_string(obj["admin"]),
            program_authority=Pubkey.from_string(obj["program_authority"]),
            bump=obj["bump"],
            nonce=obj["nonce"],
        )

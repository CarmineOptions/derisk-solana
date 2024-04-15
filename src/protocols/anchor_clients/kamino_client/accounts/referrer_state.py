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


class ReferrerStateJSON(typing.TypedDict):
    short_url: str
    owner: str


@dataclass
class ReferrerState:
    discriminator: typing.ClassVar = b"\xc2Q\xd9g\x0c\x13\x0cB"
    layout: typing.ClassVar = borsh.CStruct(
        "short_url" / BorshPubkey, "owner" / BorshPubkey
    )
    short_url: Pubkey
    owner: Pubkey

    @classmethod
    async def fetch(
        cls,
        conn: AsyncClient,
        address: Pubkey,
        commitment: typing.Optional[Commitment] = None,
        program_id: Pubkey = PROGRAM_ID,
    ) -> typing.Optional["ReferrerState"]:
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
    ) -> typing.List[typing.Optional["ReferrerState"]]:
        infos = await get_multiple_accounts(conn, addresses, commitment=commitment)
        res: typing.List[typing.Optional["ReferrerState"]] = []
        for info in infos:
            if info is None:
                res.append(None)
                continue
            if info.account.owner != program_id:
                raise ValueError("Account does not belong to this program")
            res.append(cls.decode(info.account.data))
        return res

    @classmethod
    def decode(cls, data: bytes) -> "ReferrerState":
        if data[:ACCOUNT_DISCRIMINATOR_SIZE] != cls.discriminator:
            raise AccountInvalidDiscriminator(
                "The discriminator for this account is invalid"
            )
        dec = ReferrerState.layout.parse(data[ACCOUNT_DISCRIMINATOR_SIZE:])
        return cls(
            short_url=dec.short_url,
            owner=dec.owner,
        )

    def to_json(self) -> ReferrerStateJSON:
        return {
            "short_url": str(self.short_url),
            "owner": str(self.owner),
        }

    @classmethod
    def from_json(cls, obj: ReferrerStateJSON) -> "ReferrerState":
        return cls(
            short_url=Pubkey.from_string(obj["short_url"]),
            owner=Pubkey.from_string(obj["owner"]),
        )

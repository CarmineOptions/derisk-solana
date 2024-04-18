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


class UserMetadataJSON(typing.TypedDict):
    referrer: str
    bump: int
    user_lookup_table: str
    owner: str
    padding1: list[int]
    padding2: list[int]


@dataclass
class UserMetadata:
    discriminator: typing.ClassVar = b"\x9d\xd6\xdc\xebb\x87\xab\x1c"
    layout: typing.ClassVar = borsh.CStruct(
        "referrer" / BorshPubkey,
        "bump" / borsh.U64,
        "user_lookup_table" / BorshPubkey,
        "owner" / BorshPubkey,
        "padding1" / borsh.U64[51],
        "padding2" / borsh.U64[64],
    )
    referrer: Pubkey
    bump: int
    user_lookup_table: Pubkey
    owner: Pubkey
    padding1: list[int]
    padding2: list[int]

    @classmethod
    async def fetch(
        cls,
        conn: AsyncClient,
        address: Pubkey,
        commitment: typing.Optional[Commitment] = None,
        program_id: Pubkey = PROGRAM_ID,
    ) -> typing.Optional["UserMetadata"]:
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
    ) -> typing.List[typing.Optional["UserMetadata"]]:
        infos = await get_multiple_accounts(conn, addresses, commitment=commitment)
        res: typing.List[typing.Optional["UserMetadata"]] = []
        for info in infos:
            if info is None:
                res.append(None)
                continue
            if info.account.owner != program_id:
                raise ValueError("Account does not belong to this program")
            res.append(cls.decode(info.account.data))
        return res

    @classmethod
    def decode(cls, data: bytes) -> "UserMetadata":
        if data[:ACCOUNT_DISCRIMINATOR_SIZE] != cls.discriminator:
            raise AccountInvalidDiscriminator(
                "The discriminator for this account is invalid"
            )
        dec = UserMetadata.layout.parse(data[ACCOUNT_DISCRIMINATOR_SIZE:])
        return cls(
            referrer=dec.referrer,
            bump=dec.bump,
            user_lookup_table=dec.user_lookup_table,
            owner=dec.owner,
            padding1=dec.padding1,
            padding2=dec.padding2,
        )

    def to_json(self) -> UserMetadataJSON:
        return {
            "referrer": str(self.referrer),
            "bump": self.bump,
            "user_lookup_table": str(self.user_lookup_table),
            "owner": str(self.owner),
            "padding1": self.padding1,
            "padding2": self.padding2,
        }

    @classmethod
    def from_json(cls, obj: UserMetadataJSON) -> "UserMetadata":
        return cls(
            referrer=Pubkey.from_string(obj["referrer"]),
            bump=obj["bump"],
            user_lookup_table=Pubkey.from_string(obj["user_lookup_table"]),
            owner=Pubkey.from_string(obj["owner"]),
            padding1=obj["padding1"],
            padding2=obj["padding2"],
        )

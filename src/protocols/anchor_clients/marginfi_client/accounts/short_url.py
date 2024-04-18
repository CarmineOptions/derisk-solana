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


class ShortUrlJSON(typing.TypedDict):
    referrer: str
    short_url: str


@dataclass
class ShortUrl:
    discriminator: typing.ClassVar = b"\x1cY\xae\x19\xe2|~\xd4"
    layout: typing.ClassVar = borsh.CStruct(
        "referrer" / BorshPubkey, "short_url" / borsh.String
    )
    referrer: Pubkey
    short_url: str

    @classmethod
    async def fetch(
        cls,
        conn: AsyncClient,
        address: Pubkey,
        commitment: typing.Optional[Commitment] = None,
        program_id: Pubkey = PROGRAM_ID,
    ) -> typing.Optional["ShortUrl"]:
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
    ) -> typing.List[typing.Optional["ShortUrl"]]:
        infos = await get_multiple_accounts(conn, addresses, commitment=commitment)
        res: typing.List[typing.Optional["ShortUrl"]] = []
        for info in infos:
            if info is None:
                res.append(None)
                continue
            if info.account.owner != program_id:
                raise ValueError("Account does not belong to this program")
            res.append(cls.decode(info.account.data))
        return res

    @classmethod
    def decode(cls, data: bytes) -> "ShortUrl":
        if data[:ACCOUNT_DISCRIMINATOR_SIZE] != cls.discriminator:
            raise AccountInvalidDiscriminator(
                "The discriminator for this account is invalid"
            )
        dec = ShortUrl.layout.parse(data[ACCOUNT_DISCRIMINATOR_SIZE:])
        return cls(
            referrer=dec.referrer,
            short_url=dec.short_url,
        )

    def to_json(self) -> ShortUrlJSON:
        return {
            "referrer": str(self.referrer),
            "short_url": self.short_url,
        }

    @classmethod
    def from_json(cls, obj: ShortUrlJSON) -> "ShortUrl":
        return cls(
            referrer=Pubkey.from_string(obj["referrer"]),
            short_url=obj["short_url"],
        )

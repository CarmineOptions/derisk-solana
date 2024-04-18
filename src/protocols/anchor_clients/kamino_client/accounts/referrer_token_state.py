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


class ReferrerTokenStateJSON(typing.TypedDict):
    referrer: str
    mint: str
    amount_unclaimed_sf: int
    amount_cumulative_sf: int
    bump: int
    padding: list[int]


@dataclass
class ReferrerTokenState:
    discriminator: typing.ClassVar = b"'\x0f\xd0M \xc3i8"
    layout: typing.ClassVar = borsh.CStruct(
        "referrer" / BorshPubkey,
        "mint" / BorshPubkey,
        "amount_unclaimed_sf" / borsh.U128,
        "amount_cumulative_sf" / borsh.U128,
        "bump" / borsh.U64,
        "padding" / borsh.U64[31],
    )
    referrer: Pubkey
    mint: Pubkey
    amount_unclaimed_sf: int
    amount_cumulative_sf: int
    bump: int
    padding: list[int]

    @classmethod
    async def fetch(
        cls,
        conn: AsyncClient,
        address: Pubkey,
        commitment: typing.Optional[Commitment] = None,
        program_id: Pubkey = PROGRAM_ID,
    ) -> typing.Optional["ReferrerTokenState"]:
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
    ) -> typing.List[typing.Optional["ReferrerTokenState"]]:
        infos = await get_multiple_accounts(conn, addresses, commitment=commitment)
        res: typing.List[typing.Optional["ReferrerTokenState"]] = []
        for info in infos:
            if info is None:
                res.append(None)
                continue
            if info.account.owner != program_id:
                raise ValueError("Account does not belong to this program")
            res.append(cls.decode(info.account.data))
        return res

    @classmethod
    def decode(cls, data: bytes) -> "ReferrerTokenState":
        if data[:ACCOUNT_DISCRIMINATOR_SIZE] != cls.discriminator:
            raise AccountInvalidDiscriminator(
                "The discriminator for this account is invalid"
            )
        dec = ReferrerTokenState.layout.parse(data[ACCOUNT_DISCRIMINATOR_SIZE:])
        return cls(
            referrer=dec.referrer,
            mint=dec.mint,
            amount_unclaimed_sf=dec.amount_unclaimed_sf,
            amount_cumulative_sf=dec.amount_cumulative_sf,
            bump=dec.bump,
            padding=dec.padding,
        )

    def to_json(self) -> ReferrerTokenStateJSON:
        return {
            "referrer": str(self.referrer),
            "mint": str(self.mint),
            "amount_unclaimed_sf": self.amount_unclaimed_sf,
            "amount_cumulative_sf": self.amount_cumulative_sf,
            "bump": self.bump,
            "padding": self.padding,
        }

    @classmethod
    def from_json(cls, obj: ReferrerTokenStateJSON) -> "ReferrerTokenState":
        return cls(
            referrer=Pubkey.from_string(obj["referrer"]),
            mint=Pubkey.from_string(obj["mint"]),
            amount_unclaimed_sf=obj["amount_unclaimed_sf"],
            amount_cumulative_sf=obj["amount_cumulative_sf"],
            bump=obj["bump"],
            padding=obj["padding"],
        )

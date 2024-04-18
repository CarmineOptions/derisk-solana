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


class OpenbookV2MarketIndexReservationJSON(typing.TypedDict):
    group: str
    market_index: int
    reserved: list[int]


@dataclass
class OpenbookV2MarketIndexReservation:
    discriminator: typing.ClassVar = b"\xd1\xc2\xf7\x1f\xa8\x1e\x83\x81"
    layout: typing.ClassVar = borsh.CStruct(
        "group" / BorshPubkey, "market_index" / borsh.U16, "reserved" / borsh.U8[38]
    )
    group: Pubkey
    market_index: int
    reserved: list[int]

    @classmethod
    async def fetch(
        cls,
        conn: AsyncClient,
        address: Pubkey,
        commitment: typing.Optional[Commitment] = None,
        program_id: Pubkey = PROGRAM_ID,
    ) -> typing.Optional["OpenbookV2MarketIndexReservation"]:
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
    ) -> typing.List[typing.Optional["OpenbookV2MarketIndexReservation"]]:
        infos = await get_multiple_accounts(conn, addresses, commitment=commitment)
        res: typing.List[typing.Optional["OpenbookV2MarketIndexReservation"]] = []
        for info in infos:
            if info is None:
                res.append(None)
                continue
            if info.account.owner != program_id:
                raise ValueError("Account does not belong to this program")
            res.append(cls.decode(info.account.data))
        return res

    @classmethod
    def decode(cls, data: bytes) -> "OpenbookV2MarketIndexReservation":
        if data[:ACCOUNT_DISCRIMINATOR_SIZE] != cls.discriminator:
            raise AccountInvalidDiscriminator(
                "The discriminator for this account is invalid"
            )
        dec = OpenbookV2MarketIndexReservation.layout.parse(
            data[ACCOUNT_DISCRIMINATOR_SIZE:]
        )
        return cls(
            group=dec.group,
            market_index=dec.market_index,
            reserved=dec.reserved,
        )

    def to_json(self) -> OpenbookV2MarketIndexReservationJSON:
        return {
            "group": str(self.group),
            "market_index": self.market_index,
            "reserved": self.reserved,
        }

    @classmethod
    def from_json(
        cls, obj: OpenbookV2MarketIndexReservationJSON
    ) -> "OpenbookV2MarketIndexReservation":
        return cls(
            group=Pubkey.from_string(obj["group"]),
            market_index=obj["market_index"],
            reserved=obj["reserved"],
        )

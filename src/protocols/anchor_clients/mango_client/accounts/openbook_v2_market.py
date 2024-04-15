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


class OpenbookV2MarketJSON(typing.TypedDict):
    group: str
    base_token_index: int
    quote_token_index: int
    reduce_only: int
    force_close: int
    padding1: list[int]
    name: list[int]
    openbook_v2_program: str
    openbook_v2_market_external: str
    market_index: int
    bump: int
    padding2: list[int]
    registration_time: int
    reserved: list[int]


@dataclass
class OpenbookV2Market:
    discriminator: typing.ClassVar = b"3\xdb\xa8<\xe4\xac\x07["
    layout: typing.ClassVar = borsh.CStruct(
        "group" / BorshPubkey,
        "base_token_index" / borsh.U16,
        "quote_token_index" / borsh.U16,
        "reduce_only" / borsh.U8,
        "force_close" / borsh.U8,
        "padding1" / borsh.U8[2],
        "name" / borsh.U8[16],
        "openbook_v2_program" / BorshPubkey,
        "openbook_v2_market_external" / BorshPubkey,
        "market_index" / borsh.U16,
        "bump" / borsh.U8,
        "padding2" / borsh.U8[5],
        "registration_time" / borsh.U64,
        "reserved" / borsh.U8[512],
    )
    group: Pubkey
    base_token_index: int
    quote_token_index: int
    reduce_only: int
    force_close: int
    padding1: list[int]
    name: list[int]
    openbook_v2_program: Pubkey
    openbook_v2_market_external: Pubkey
    market_index: int
    bump: int
    padding2: list[int]
    registration_time: int
    reserved: list[int]

    @classmethod
    async def fetch(
        cls,
        conn: AsyncClient,
        address: Pubkey,
        commitment: typing.Optional[Commitment] = None,
        program_id: Pubkey = PROGRAM_ID,
    ) -> typing.Optional["OpenbookV2Market"]:
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
    ) -> typing.List[typing.Optional["OpenbookV2Market"]]:
        infos = await get_multiple_accounts(conn, addresses, commitment=commitment)
        res: typing.List[typing.Optional["OpenbookV2Market"]] = []
        for info in infos:
            if info is None:
                res.append(None)
                continue
            if info.account.owner != program_id:
                raise ValueError("Account does not belong to this program")
            res.append(cls.decode(info.account.data))
        return res

    @classmethod
    def decode(cls, data: bytes) -> "OpenbookV2Market":
        if data[:ACCOUNT_DISCRIMINATOR_SIZE] != cls.discriminator:
            raise AccountInvalidDiscriminator(
                "The discriminator for this account is invalid"
            )
        dec = OpenbookV2Market.layout.parse(data[ACCOUNT_DISCRIMINATOR_SIZE:])
        return cls(
            group=dec.group,
            base_token_index=dec.base_token_index,
            quote_token_index=dec.quote_token_index,
            reduce_only=dec.reduce_only,
            force_close=dec.force_close,
            padding1=dec.padding1,
            name=dec.name,
            openbook_v2_program=dec.openbook_v2_program,
            openbook_v2_market_external=dec.openbook_v2_market_external,
            market_index=dec.market_index,
            bump=dec.bump,
            padding2=dec.padding2,
            registration_time=dec.registration_time,
            reserved=dec.reserved,
        )

    def to_json(self) -> OpenbookV2MarketJSON:
        return {
            "group": str(self.group),
            "base_token_index": self.base_token_index,
            "quote_token_index": self.quote_token_index,
            "reduce_only": self.reduce_only,
            "force_close": self.force_close,
            "padding1": self.padding1,
            "name": self.name,
            "openbook_v2_program": str(self.openbook_v2_program),
            "openbook_v2_market_external": str(self.openbook_v2_market_external),
            "market_index": self.market_index,
            "bump": self.bump,
            "padding2": self.padding2,
            "registration_time": self.registration_time,
            "reserved": self.reserved,
        }

    @classmethod
    def from_json(cls, obj: OpenbookV2MarketJSON) -> "OpenbookV2Market":
        return cls(
            group=Pubkey.from_string(obj["group"]),
            base_token_index=obj["base_token_index"],
            quote_token_index=obj["quote_token_index"],
            reduce_only=obj["reduce_only"],
            force_close=obj["force_close"],
            padding1=obj["padding1"],
            name=obj["name"],
            openbook_v2_program=Pubkey.from_string(obj["openbook_v2_program"]),
            openbook_v2_market_external=Pubkey.from_string(
                obj["openbook_v2_market_external"]
            ),
            market_index=obj["market_index"],
            bump=obj["bump"],
            padding2=obj["padding2"],
            registration_time=obj["registration_time"],
            reserved=obj["reserved"],
        )

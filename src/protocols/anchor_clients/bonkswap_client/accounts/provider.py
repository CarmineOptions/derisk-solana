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
from .. import types


class ProviderJSON(typing.TypedDict):
    token_x: str
    token_y: str
    owner: str
    shares: types.token.TokenJSON
    last_fee_accumulator_x: types.fixed_point.FixedPointJSON
    last_fee_accumulator_y: types.fixed_point.FixedPointJSON
    last_seconds_per_share: types.fixed_point.FixedPointJSON
    last_withdraw_time: int
    tokens_owed_x: types.token.TokenJSON
    tokens_owed_y: types.token.TokenJSON
    current_farm_count: int
    bump: int


@dataclass
class Provider:
    discriminator: typing.ClassVar = b"\xa4\xb4G\x11K\xd8P\xc3"
    layout: typing.ClassVar = borsh.CStruct(
        "token_x" / BorshPubkey,
        "token_y" / BorshPubkey,
        "owner" / BorshPubkey,
        "shares" / types.token.Token.layout,
        "last_fee_accumulator_x" / types.fixed_point.FixedPoint.layout,
        "last_fee_accumulator_y" / types.fixed_point.FixedPoint.layout,
        "last_seconds_per_share" / types.fixed_point.FixedPoint.layout,
        "last_withdraw_time" / borsh.U64,
        "tokens_owed_x" / types.token.Token.layout,
        "tokens_owed_y" / types.token.Token.layout,
        "current_farm_count" / borsh.U64,
        "bump" / borsh.U8,
    )
    token_x: Pubkey
    token_y: Pubkey
    owner: Pubkey
    shares: types.token.Token
    last_fee_accumulator_x: types.fixed_point.FixedPoint
    last_fee_accumulator_y: types.fixed_point.FixedPoint
    last_seconds_per_share: types.fixed_point.FixedPoint
    last_withdraw_time: int
    tokens_owed_x: types.token.Token
    tokens_owed_y: types.token.Token
    current_farm_count: int
    bump: int

    @classmethod
    async def fetch(
        cls,
        conn: AsyncClient,
        address: Pubkey,
        commitment: typing.Optional[Commitment] = None,
        program_id: Pubkey = PROGRAM_ID,
    ) -> typing.Optional["Provider"]:
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
    ) -> typing.List[typing.Optional["Provider"]]:
        infos = await get_multiple_accounts(conn, addresses, commitment=commitment)
        res: typing.List[typing.Optional["Provider"]] = []
        for info in infos:
            if info is None:
                res.append(None)
                continue
            if info.account.owner != program_id:
                raise ValueError("Account does not belong to this program")
            res.append(cls.decode(info.account.data))
        return res

    @classmethod
    def decode(cls, data: bytes) -> "Provider":
        if data[:ACCOUNT_DISCRIMINATOR_SIZE] != cls.discriminator:
            raise AccountInvalidDiscriminator(
                "The discriminator for this account is invalid"
            )
        dec = Provider.layout.parse(data[ACCOUNT_DISCRIMINATOR_SIZE:])
        return cls(
            token_x=dec.token_x,
            token_y=dec.token_y,
            owner=dec.owner,
            shares=types.token.Token.from_decoded(dec.shares),
            last_fee_accumulator_x=types.fixed_point.FixedPoint.from_decoded(
                dec.last_fee_accumulator_x
            ),
            last_fee_accumulator_y=types.fixed_point.FixedPoint.from_decoded(
                dec.last_fee_accumulator_y
            ),
            last_seconds_per_share=types.fixed_point.FixedPoint.from_decoded(
                dec.last_seconds_per_share
            ),
            last_withdraw_time=dec.last_withdraw_time,
            tokens_owed_x=types.token.Token.from_decoded(dec.tokens_owed_x),
            tokens_owed_y=types.token.Token.from_decoded(dec.tokens_owed_y),
            current_farm_count=dec.current_farm_count,
            bump=dec.bump,
        )

    def to_json(self) -> ProviderJSON:
        return {
            "token_x": str(self.token_x),
            "token_y": str(self.token_y),
            "owner": str(self.owner),
            "shares": self.shares.to_json(),
            "last_fee_accumulator_x": self.last_fee_accumulator_x.to_json(),
            "last_fee_accumulator_y": self.last_fee_accumulator_y.to_json(),
            "last_seconds_per_share": self.last_seconds_per_share.to_json(),
            "last_withdraw_time": self.last_withdraw_time,
            "tokens_owed_x": self.tokens_owed_x.to_json(),
            "tokens_owed_y": self.tokens_owed_y.to_json(),
            "current_farm_count": self.current_farm_count,
            "bump": self.bump,
        }

    @classmethod
    def from_json(cls, obj: ProviderJSON) -> "Provider":
        return cls(
            token_x=Pubkey.from_string(obj["token_x"]),
            token_y=Pubkey.from_string(obj["token_y"]),
            owner=Pubkey.from_string(obj["owner"]),
            shares=types.token.Token.from_json(obj["shares"]),
            last_fee_accumulator_x=types.fixed_point.FixedPoint.from_json(
                obj["last_fee_accumulator_x"]
            ),
            last_fee_accumulator_y=types.fixed_point.FixedPoint.from_json(
                obj["last_fee_accumulator_y"]
            ),
            last_seconds_per_share=types.fixed_point.FixedPoint.from_json(
                obj["last_seconds_per_share"]
            ),
            last_withdraw_time=obj["last_withdraw_time"],
            tokens_owed_x=types.token.Token.from_json(obj["tokens_owed_x"]),
            tokens_owed_y=types.token.Token.from_json(obj["tokens_owed_y"]),
            current_farm_count=obj["current_farm_count"],
            bump=obj["bump"],
        )

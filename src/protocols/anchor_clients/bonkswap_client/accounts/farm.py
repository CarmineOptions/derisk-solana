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


class FarmJSON(typing.TypedDict):
    pool: str
    tokens: list[str]
    token_accounts: list[str]
    supply: list[types.token.TokenJSON]
    supply_left: list[types.token.TokenJSON]
    accumulated_seconds_per_share: types.fixed_point.FixedPointJSON
    offset_seconds_per_share: types.fixed_point.FixedPointJSON
    start_time: int
    end_time: int
    last_update: int
    bump: int
    farm_type: types.farm_type.FarmTypeJSON


@dataclass
class Farm:
    discriminator: typing.ClassVar = b"\xa1\x9c\xd3\xfd\xfa@5\xfa"
    layout: typing.ClassVar = borsh.CStruct(
        "pool" / BorshPubkey,
        "tokens" / BorshPubkey[3],
        "token_accounts" / BorshPubkey[3],
        "supply" / types.token.Token.layout[3],
        "supply_left" / types.token.Token.layout[3],
        "accumulated_seconds_per_share" / types.fixed_point.FixedPoint.layout,
        "offset_seconds_per_share" / types.fixed_point.FixedPoint.layout,
        "start_time" / borsh.U64,
        "end_time" / borsh.U64,
        "last_update" / borsh.U64,
        "bump" / borsh.U8,
        "farm_type" / types.farm_type.layout,
    )
    pool: Pubkey
    tokens: list[Pubkey]
    token_accounts: list[Pubkey]
    supply: list[types.token.Token]
    supply_left: list[types.token.Token]
    accumulated_seconds_per_share: types.fixed_point.FixedPoint
    offset_seconds_per_share: types.fixed_point.FixedPoint
    start_time: int
    end_time: int
    last_update: int
    bump: int
    farm_type: types.farm_type.FarmTypeKind

    @classmethod
    async def fetch(
        cls,
        conn: AsyncClient,
        address: Pubkey,
        commitment: typing.Optional[Commitment] = None,
        program_id: Pubkey = PROGRAM_ID,
    ) -> typing.Optional["Farm"]:
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
    ) -> typing.List[typing.Optional["Farm"]]:
        infos = await get_multiple_accounts(conn, addresses, commitment=commitment)
        res: typing.List[typing.Optional["Farm"]] = []
        for info in infos:
            if info is None:
                res.append(None)
                continue
            if info.account.owner != program_id:
                raise ValueError("Account does not belong to this program")
            res.append(cls.decode(info.account.data))
        return res

    @classmethod
    def decode(cls, data: bytes) -> "Farm":
        if data[:ACCOUNT_DISCRIMINATOR_SIZE] != cls.discriminator:
            raise AccountInvalidDiscriminator(
                "The discriminator for this account is invalid"
            )
        dec = Farm.layout.parse(data[ACCOUNT_DISCRIMINATOR_SIZE:])
        return cls(
            pool=dec.pool,
            tokens=dec.tokens,
            token_accounts=dec.token_accounts,
            supply=list(
                map(lambda item: types.token.Token.from_decoded(item), dec.supply)
            ),
            supply_left=list(
                map(lambda item: types.token.Token.from_decoded(item), dec.supply_left)
            ),
            accumulated_seconds_per_share=types.fixed_point.FixedPoint.from_decoded(
                dec.accumulated_seconds_per_share
            ),
            offset_seconds_per_share=types.fixed_point.FixedPoint.from_decoded(
                dec.offset_seconds_per_share
            ),
            start_time=dec.start_time,
            end_time=dec.end_time,
            last_update=dec.last_update,
            bump=dec.bump,
            farm_type=types.farm_type.from_decoded(dec.farm_type),
        )

    def to_json(self) -> FarmJSON:
        return {
            "pool": str(self.pool),
            "tokens": list(map(lambda item: str(item), self.tokens)),
            "token_accounts": list(map(lambda item: str(item), self.token_accounts)),
            "supply": list(map(lambda item: item.to_json(), self.supply)),
            "supply_left": list(map(lambda item: item.to_json(), self.supply_left)),
            "accumulated_seconds_per_share": self.accumulated_seconds_per_share.to_json(),
            "offset_seconds_per_share": self.offset_seconds_per_share.to_json(),
            "start_time": self.start_time,
            "end_time": self.end_time,
            "last_update": self.last_update,
            "bump": self.bump,
            "farm_type": self.farm_type.to_json(),
        }

    @classmethod
    def from_json(cls, obj: FarmJSON) -> "Farm":
        return cls(
            pool=Pubkey.from_string(obj["pool"]),
            tokens=list(map(lambda item: Pubkey.from_string(item), obj["tokens"])),
            token_accounts=list(
                map(lambda item: Pubkey.from_string(item), obj["token_accounts"])
            ),
            supply=list(
                map(lambda item: types.token.Token.from_json(item), obj["supply"])
            ),
            supply_left=list(
                map(lambda item: types.token.Token.from_json(item), obj["supply_left"])
            ),
            accumulated_seconds_per_share=types.fixed_point.FixedPoint.from_json(
                obj["accumulated_seconds_per_share"]
            ),
            offset_seconds_per_share=types.fixed_point.FixedPoint.from_json(
                obj["offset_seconds_per_share"]
            ),
            start_time=obj["start_time"],
            end_time=obj["end_time"],
            last_update=obj["last_update"],
            bump=obj["bump"],
            farm_type=types.farm_type.from_json(obj["farm_type"]),
        )

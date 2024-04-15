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


class ReserveJSON(typing.TypedDict):
    version: int
    last_update: types.last_update.LastUpdateJSON
    lending_market: str
    farm_collateral: str
    farm_debt: str
    liquidity: types.reserve_liquidity.ReserveLiquidityJSON
    reserve_liquidity_padding: list[int]
    collateral: types.reserve_collateral.ReserveCollateralJSON
    reserve_collateral_padding: list[int]
    config: types.reserve_config.ReserveConfigJSON
    config_padding: list[int]
    padding: list[int]


@dataclass
class Reserve:
    discriminator: typing.ClassVar = b"+\xf2\xcc\xca\x1a\xf7;\x7f"
    layout: typing.ClassVar = borsh.CStruct(
        "version" / borsh.U64,
        "last_update" / types.last_update.LastUpdate.layout,
        "lending_market" / BorshPubkey,
        "farm_collateral" / BorshPubkey,
        "farm_debt" / BorshPubkey,
        "liquidity" / types.reserve_liquidity.ReserveLiquidity.layout,
        "reserve_liquidity_padding" / borsh.U64[150],
        "collateral" / types.reserve_collateral.ReserveCollateral.layout,
        "reserve_collateral_padding" / borsh.U64[150],
        "config" / types.reserve_config.ReserveConfig.layout,
        "config_padding" / borsh.U64[150],
        "padding" / borsh.U64[240],
    )
    version: int
    last_update: types.last_update.LastUpdate
    lending_market: Pubkey
    farm_collateral: Pubkey
    farm_debt: Pubkey
    liquidity: types.reserve_liquidity.ReserveLiquidity
    reserve_liquidity_padding: list[int]
    collateral: types.reserve_collateral.ReserveCollateral
    reserve_collateral_padding: list[int]
    config: types.reserve_config.ReserveConfig
    config_padding: list[int]
    padding: list[int]

    @classmethod
    async def fetch(
        cls,
        conn: AsyncClient,
        address: Pubkey,
        commitment: typing.Optional[Commitment] = None,
        program_id: Pubkey = PROGRAM_ID,
    ) -> typing.Optional["Reserve"]:
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
    ) -> typing.List[typing.Optional["Reserve"]]:
        infos = await get_multiple_accounts(conn, addresses, commitment=commitment)
        res: typing.List[typing.Optional["Reserve"]] = []
        for info in infos:
            if info is None:
                res.append(None)
                continue
            if info.account.owner != program_id:
                raise ValueError("Account does not belong to this program")
            res.append(cls.decode(info.account.data))
        return res

    @classmethod
    def decode(cls, data: bytes) -> "Reserve":
        if data[:ACCOUNT_DISCRIMINATOR_SIZE] != cls.discriminator:
            raise AccountInvalidDiscriminator(
                "The discriminator for this account is invalid"
            )
        dec = Reserve.layout.parse(data[ACCOUNT_DISCRIMINATOR_SIZE:])
        return cls(
            version=dec.version,
            last_update=types.last_update.LastUpdate.from_decoded(dec.last_update),
            lending_market=dec.lending_market,
            farm_collateral=dec.farm_collateral,
            farm_debt=dec.farm_debt,
            liquidity=types.reserve_liquidity.ReserveLiquidity.from_decoded(
                dec.liquidity
            ),
            reserve_liquidity_padding=dec.reserve_liquidity_padding,
            collateral=types.reserve_collateral.ReserveCollateral.from_decoded(
                dec.collateral
            ),
            reserve_collateral_padding=dec.reserve_collateral_padding,
            config=types.reserve_config.ReserveConfig.from_decoded(dec.config),
            config_padding=dec.config_padding,
            padding=dec.padding,
        )

    def to_json(self) -> ReserveJSON:
        return {
            "version": self.version,
            "last_update": self.last_update.to_json(),
            "lending_market": str(self.lending_market),
            "farm_collateral": str(self.farm_collateral),
            "farm_debt": str(self.farm_debt),
            "liquidity": self.liquidity.to_json(),
            "reserve_liquidity_padding": self.reserve_liquidity_padding,
            "collateral": self.collateral.to_json(),
            "reserve_collateral_padding": self.reserve_collateral_padding,
            "config": self.config.to_json(),
            "config_padding": self.config_padding,
            "padding": self.padding,
        }

    @classmethod
    def from_json(cls, obj: ReserveJSON) -> "Reserve":
        return cls(
            version=obj["version"],
            last_update=types.last_update.LastUpdate.from_json(obj["last_update"]),
            lending_market=Pubkey.from_string(obj["lending_market"]),
            farm_collateral=Pubkey.from_string(obj["farm_collateral"]),
            farm_debt=Pubkey.from_string(obj["farm_debt"]),
            liquidity=types.reserve_liquidity.ReserveLiquidity.from_json(
                obj["liquidity"]
            ),
            reserve_liquidity_padding=obj["reserve_liquidity_padding"],
            collateral=types.reserve_collateral.ReserveCollateral.from_json(
                obj["collateral"]
            ),
            reserve_collateral_padding=obj["reserve_collateral_padding"],
            config=types.reserve_config.ReserveConfig.from_json(obj["config"]),
            config_padding=obj["config_padding"],
            padding=obj["padding"],
        )

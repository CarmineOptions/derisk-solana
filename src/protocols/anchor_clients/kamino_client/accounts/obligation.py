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


class ObligationJSON(typing.TypedDict):
    tag: int
    last_update: types.last_update.LastUpdateJSON
    lending_market: str
    owner: str
    deposits: list[types.obligation_collateral.ObligationCollateralJSON]
    lowest_reserve_deposit_ltv: int
    deposited_value_sf: int
    borrows: list[types.obligation_liquidity.ObligationLiquidityJSON]
    borrow_factor_adjusted_debt_value_sf: int
    borrowed_assets_market_value_sf: int
    allowed_borrow_value_sf: int
    unhealthy_borrow_value_sf: int
    deposits_asset_tiers: list[int]
    borrows_asset_tiers: list[int]
    elevation_group: int
    num_of_obsolete_reserves: int
    has_debt: int
    referrer: str
    padding3: list[int]


@dataclass
class Obligation:
    discriminator: typing.ClassVar = b"\xa8\xce\x8djXL\xac\xa7"
    layout: typing.ClassVar = borsh.CStruct(
        "tag" / borsh.U64,
        "last_update" / types.last_update.LastUpdate.layout,
        "lending_market" / BorshPubkey,
        "owner" / BorshPubkey,
        "deposits" / types.obligation_collateral.ObligationCollateral.layout[8],
        "lowest_reserve_deposit_ltv" / borsh.U64,
        "deposited_value_sf" / borsh.U128,
        "borrows" / types.obligation_liquidity.ObligationLiquidity.layout[5],
        "borrow_factor_adjusted_debt_value_sf" / borsh.U128,
        "borrowed_assets_market_value_sf" / borsh.U128,
        "allowed_borrow_value_sf" / borsh.U128,
        "unhealthy_borrow_value_sf" / borsh.U128,
        "deposits_asset_tiers" / borsh.U8[8],
        "borrows_asset_tiers" / borsh.U8[5],
        "elevation_group" / borsh.U8,
        "num_of_obsolete_reserves" / borsh.U8,
        "has_debt" / borsh.U8,
        "referrer" / BorshPubkey,
        "padding3" / borsh.U64[128],
    )
    tag: int
    last_update: types.last_update.LastUpdate
    lending_market: Pubkey
    owner: Pubkey
    deposits: list[types.obligation_collateral.ObligationCollateral]
    lowest_reserve_deposit_ltv: int
    deposited_value_sf: int
    borrows: list[types.obligation_liquidity.ObligationLiquidity]
    borrow_factor_adjusted_debt_value_sf: int
    borrowed_assets_market_value_sf: int
    allowed_borrow_value_sf: int
    unhealthy_borrow_value_sf: int
    deposits_asset_tiers: list[int]
    borrows_asset_tiers: list[int]
    elevation_group: int
    num_of_obsolete_reserves: int
    has_debt: int
    referrer: Pubkey
    padding3: list[int]

    @classmethod
    async def fetch(
        cls,
        conn: AsyncClient,
        address: Pubkey,
        commitment: typing.Optional[Commitment] = None,
        program_id: Pubkey = PROGRAM_ID,
    ) -> typing.Optional["Obligation"]:
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
    ) -> typing.List[typing.Optional["Obligation"]]:
        infos = await get_multiple_accounts(conn, addresses, commitment=commitment)
        res: typing.List[typing.Optional["Obligation"]] = []
        for info in infos:
            if info is None:
                res.append(None)
                continue
            if info.account.owner != program_id:
                raise ValueError("Account does not belong to this program")
            res.append(cls.decode(info.account.data))
        return res

    @classmethod
    def decode(cls, data: bytes) -> "Obligation":
        if data[:ACCOUNT_DISCRIMINATOR_SIZE] != cls.discriminator:
            raise AccountInvalidDiscriminator(
                "The discriminator for this account is invalid"
            )
        dec = Obligation.layout.parse(data[ACCOUNT_DISCRIMINATOR_SIZE:])
        return cls(
            tag=dec.tag,
            last_update=types.last_update.LastUpdate.from_decoded(dec.last_update),
            lending_market=dec.lending_market,
            owner=dec.owner,
            deposits=list(
                map(
                    lambda item: types.obligation_collateral.ObligationCollateral.from_decoded(
                        item
                    ),
                    dec.deposits,
                )
            ),
            lowest_reserve_deposit_ltv=dec.lowest_reserve_deposit_ltv,
            deposited_value_sf=dec.deposited_value_sf,
            borrows=list(
                map(
                    lambda item: types.obligation_liquidity.ObligationLiquidity.from_decoded(
                        item
                    ),
                    dec.borrows,
                )
            ),
            borrow_factor_adjusted_debt_value_sf=dec.borrow_factor_adjusted_debt_value_sf,
            borrowed_assets_market_value_sf=dec.borrowed_assets_market_value_sf,
            allowed_borrow_value_sf=dec.allowed_borrow_value_sf,
            unhealthy_borrow_value_sf=dec.unhealthy_borrow_value_sf,
            deposits_asset_tiers=dec.deposits_asset_tiers,
            borrows_asset_tiers=dec.borrows_asset_tiers,
            elevation_group=dec.elevation_group,
            num_of_obsolete_reserves=dec.num_of_obsolete_reserves,
            has_debt=dec.has_debt,
            referrer=dec.referrer,
            padding3=dec.padding3,
        )

    def to_json(self) -> ObligationJSON:
        return {
            "tag": self.tag,
            "last_update": self.last_update.to_json(),
            "lending_market": str(self.lending_market),
            "owner": str(self.owner),
            "deposits": list(map(lambda item: item.to_json(), self.deposits)),
            "lowest_reserve_deposit_ltv": self.lowest_reserve_deposit_ltv,
            "deposited_value_sf": self.deposited_value_sf,
            "borrows": list(map(lambda item: item.to_json(), self.borrows)),
            "borrow_factor_adjusted_debt_value_sf": self.borrow_factor_adjusted_debt_value_sf,
            "borrowed_assets_market_value_sf": self.borrowed_assets_market_value_sf,
            "allowed_borrow_value_sf": self.allowed_borrow_value_sf,
            "unhealthy_borrow_value_sf": self.unhealthy_borrow_value_sf,
            "deposits_asset_tiers": self.deposits_asset_tiers,
            "borrows_asset_tiers": self.borrows_asset_tiers,
            "elevation_group": self.elevation_group,
            "num_of_obsolete_reserves": self.num_of_obsolete_reserves,
            "has_debt": self.has_debt,
            "referrer": str(self.referrer),
            "padding3": self.padding3,
        }

    @classmethod
    def from_json(cls, obj: ObligationJSON) -> "Obligation":
        return cls(
            tag=obj["tag"],
            last_update=types.last_update.LastUpdate.from_json(obj["last_update"]),
            lending_market=Pubkey.from_string(obj["lending_market"]),
            owner=Pubkey.from_string(obj["owner"]),
            deposits=list(
                map(
                    lambda item: types.obligation_collateral.ObligationCollateral.from_json(
                        item
                    ),
                    obj["deposits"],
                )
            ),
            lowest_reserve_deposit_ltv=obj["lowest_reserve_deposit_ltv"],
            deposited_value_sf=obj["deposited_value_sf"],
            borrows=list(
                map(
                    lambda item: types.obligation_liquidity.ObligationLiquidity.from_json(
                        item
                    ),
                    obj["borrows"],
                )
            ),
            borrow_factor_adjusted_debt_value_sf=obj[
                "borrow_factor_adjusted_debt_value_sf"
            ],
            borrowed_assets_market_value_sf=obj["borrowed_assets_market_value_sf"],
            allowed_borrow_value_sf=obj["allowed_borrow_value_sf"],
            unhealthy_borrow_value_sf=obj["unhealthy_borrow_value_sf"],
            deposits_asset_tiers=obj["deposits_asset_tiers"],
            borrows_asset_tiers=obj["borrows_asset_tiers"],
            elevation_group=obj["elevation_group"],
            num_of_obsolete_reserves=obj["num_of_obsolete_reserves"],
            has_debt=obj["has_debt"],
            referrer=Pubkey.from_string(obj["referrer"]),
            padding3=obj["padding3"],
        )

import logging
import time
import typing
from dataclasses import dataclass

from solana.exceptions import SolanaRpcException
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


LOGGER = logging.getLogger(__name__)


class LendingMarketJSON(typing.TypedDict):
    version: int
    bump_seed: int
    lending_market_owner: str
    lending_market_owner_cached: str
    quote_currency: list[int]
    referral_fee_bps: int
    emergency_mode: int
    autodeleverage_enabled: int
    reserved: list[int]
    price_refresh_trigger_to_max_age_pct: int
    liquidation_max_debt_close_factor_pct: int
    insolvency_risk_unhealthy_ltv_pct: int
    min_full_liquidation_value_threshold: int
    max_liquidatable_debt_market_value_at_once: int
    global_unhealthy_borrow_value: int
    global_allowed_borrow_value: int
    risk_council: str
    multiplier_points_tag_boost: list[int]
    elevation_groups: list[types.elevation_group.ElevationGroupJSON]
    elevation_group_padding: list[int]
    padding1: list[int]


@dataclass
class LendingMarket:
    discriminator: typing.ClassVar = b"\xf6r2bH\x9d\x1cx"
    layout: typing.ClassVar = borsh.CStruct(
        "version" / borsh.U64,
        "bump_seed" / borsh.U64,
        "lending_market_owner" / BorshPubkey,
        "lending_market_owner_cached" / BorshPubkey,
        "quote_currency" / borsh.U8[32],
        "referral_fee_bps" / borsh.U16,
        "emergency_mode" / borsh.U8,
        "autodeleverage_enabled" / borsh.U8,
        "reserved" / borsh.U8[1],
        "price_refresh_trigger_to_max_age_pct" / borsh.U8,
        "liquidation_max_debt_close_factor_pct" / borsh.U8,
        "insolvency_risk_unhealthy_ltv_pct" / borsh.U8,
        "min_full_liquidation_value_threshold" / borsh.U64,
        "max_liquidatable_debt_market_value_at_once" / borsh.U64,
        "global_unhealthy_borrow_value" / borsh.U64,
        "global_allowed_borrow_value" / borsh.U64,
        "risk_council" / BorshPubkey,
        "multiplier_points_tag_boost" / borsh.U8[8],
        "elevation_groups" / types.elevation_group.ElevationGroup.layout[32],
        "elevation_group_padding" / borsh.U64[90],
        "padding1" / borsh.U64[180],
    )
    version: int
    bump_seed: int
    lending_market_owner: Pubkey
    lending_market_owner_cached: Pubkey
    quote_currency: list[int]
    referral_fee_bps: int
    emergency_mode: int
    autodeleverage_enabled: int
    reserved: list[int]
    price_refresh_trigger_to_max_age_pct: int
    liquidation_max_debt_close_factor_pct: int
    insolvency_risk_unhealthy_ltv_pct: int
    min_full_liquidation_value_threshold: int
    max_liquidatable_debt_market_value_at_once: int
    global_unhealthy_borrow_value: int
    global_allowed_borrow_value: int
    risk_council: Pubkey
    multiplier_points_tag_boost: list[int]
    elevation_groups: list[types.elevation_group.ElevationGroup]
    elevation_group_padding: list[int]
    padding1: list[int]

    @classmethod
    async def fetch(
        cls,
        conn: AsyncClient,
        address: Pubkey,
        commitment: typing.Optional[Commitment] = None,
        program_id: Pubkey = PROGRAM_ID,
    ) -> typing.Optional["LendingMarket"]:
        try:
            resp = await conn.get_account_info(address, commitment=commitment)
            info = resp.value
            if info is None:
                return None
            if info.owner != program_id:
                raise ValueError("Account does not belong to this program")
            bytes_data = info.data
            return cls.decode(bytes_data)

        except SolanaRpcException as e:
            LOGGER.error(f"SolanaRpcException: {e}")
            time.sleep(1)
            return await cls.fetch(conn, address, commitment, program_id)

    @classmethod
    async def fetch_multiple(
        cls,
        conn: AsyncClient,
        addresses: list[Pubkey],
        commitment: typing.Optional[Commitment] = None,
        program_id: Pubkey = PROGRAM_ID,
    ) -> typing.List[typing.Optional["LendingMarket"]]:
        infos = await get_multiple_accounts(conn, addresses, commitment=commitment)
        res: typing.List[typing.Optional["LendingMarket"]] = []
        for info in infos:
            if info is None:
                res.append(None)
                continue
            if info.account.owner != program_id:
                raise ValueError("Account does not belong to this program")
            res.append(cls.decode(info.account.data))
        return res

    @classmethod
    def decode(cls, data: bytes) -> "LendingMarket":
        if data[:ACCOUNT_DISCRIMINATOR_SIZE] != cls.discriminator:
            raise AccountInvalidDiscriminator(
                "The discriminator for this account is invalid"
            )
        dec = LendingMarket.layout.parse(data[ACCOUNT_DISCRIMINATOR_SIZE:])
        return cls(
            version=dec.version,
            bump_seed=dec.bump_seed,
            lending_market_owner=dec.lending_market_owner,
            lending_market_owner_cached=dec.lending_market_owner_cached,
            quote_currency=dec.quote_currency,
            referral_fee_bps=dec.referral_fee_bps,
            emergency_mode=dec.emergency_mode,
            autodeleverage_enabled=dec.autodeleverage_enabled,
            reserved=dec.reserved,
            price_refresh_trigger_to_max_age_pct=dec.price_refresh_trigger_to_max_age_pct,
            liquidation_max_debt_close_factor_pct=dec.liquidation_max_debt_close_factor_pct,
            insolvency_risk_unhealthy_ltv_pct=dec.insolvency_risk_unhealthy_ltv_pct,
            min_full_liquidation_value_threshold=dec.min_full_liquidation_value_threshold,
            max_liquidatable_debt_market_value_at_once=dec.max_liquidatable_debt_market_value_at_once,
            global_unhealthy_borrow_value=dec.global_unhealthy_borrow_value,
            global_allowed_borrow_value=dec.global_allowed_borrow_value,
            risk_council=dec.risk_council,
            multiplier_points_tag_boost=dec.multiplier_points_tag_boost,
            elevation_groups=list(
                map(
                    lambda item: types.elevation_group.ElevationGroup.from_decoded(
                        item
                    ),
                    dec.elevation_groups,
                )
            ),
            elevation_group_padding=dec.elevation_group_padding,
            padding1=dec.padding1,
        )

    def to_json(self) -> LendingMarketJSON:
        return {
            "version": self.version,
            "bump_seed": self.bump_seed,
            "lending_market_owner": str(self.lending_market_owner),
            "lending_market_owner_cached": str(self.lending_market_owner_cached),
            "quote_currency": self.quote_currency,
            "referral_fee_bps": self.referral_fee_bps,
            "emergency_mode": self.emergency_mode,
            "autodeleverage_enabled": self.autodeleverage_enabled,
            "reserved": self.reserved,
            "price_refresh_trigger_to_max_age_pct": self.price_refresh_trigger_to_max_age_pct,
            "liquidation_max_debt_close_factor_pct": self.liquidation_max_debt_close_factor_pct,
            "insolvency_risk_unhealthy_ltv_pct": self.insolvency_risk_unhealthy_ltv_pct,
            "min_full_liquidation_value_threshold": self.min_full_liquidation_value_threshold,
            "max_liquidatable_debt_market_value_at_once": self.max_liquidatable_debt_market_value_at_once,
            "global_unhealthy_borrow_value": self.global_unhealthy_borrow_value,
            "global_allowed_borrow_value": self.global_allowed_borrow_value,
            "risk_council": str(self.risk_council),
            "multiplier_points_tag_boost": self.multiplier_points_tag_boost,
            "elevation_groups": list(
                map(lambda item: item.to_json(), self.elevation_groups)
            ),
            "elevation_group_padding": self.elevation_group_padding,
            "padding1": self.padding1,
        }

    @classmethod
    def from_json(cls, obj: LendingMarketJSON) -> "LendingMarket":
        return cls(
            version=obj["version"],
            bump_seed=obj["bump_seed"],
            lending_market_owner=Pubkey.from_string(obj["lending_market_owner"]),
            lending_market_owner_cached=Pubkey.from_string(
                obj["lending_market_owner_cached"]
            ),
            quote_currency=obj["quote_currency"],
            referral_fee_bps=obj["referral_fee_bps"],
            emergency_mode=obj["emergency_mode"],
            autodeleverage_enabled=obj["autodeleverage_enabled"],
            reserved=obj["reserved"],
            price_refresh_trigger_to_max_age_pct=obj[
                "price_refresh_trigger_to_max_age_pct"
            ],
            liquidation_max_debt_close_factor_pct=obj[
                "liquidation_max_debt_close_factor_pct"
            ],
            insolvency_risk_unhealthy_ltv_pct=obj["insolvency_risk_unhealthy_ltv_pct"],
            min_full_liquidation_value_threshold=obj[
                "min_full_liquidation_value_threshold"
            ],
            max_liquidatable_debt_market_value_at_once=obj[
                "max_liquidatable_debt_market_value_at_once"
            ],
            global_unhealthy_borrow_value=obj["global_unhealthy_borrow_value"],
            global_allowed_borrow_value=obj["global_allowed_borrow_value"],
            risk_council=Pubkey.from_string(obj["risk_council"]),
            multiplier_points_tag_boost=obj["multiplier_points_tag_boost"],
            elevation_groups=list(
                map(
                    lambda item: types.elevation_group.ElevationGroup.from_json(item),
                    obj["elevation_groups"],
                )
            ),
            elevation_group_padding=obj["elevation_group_padding"],
            padding1=obj["padding1"],
        )

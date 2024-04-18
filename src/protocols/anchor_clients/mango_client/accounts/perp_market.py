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


class PerpMarketJSON(typing.TypedDict):
    group: str
    settle_token_index: int
    perp_market_index: int
    blocked1: int
    group_insurance_fund: int
    bump: int
    base_decimals: int
    name: list[int]
    bids: str
    asks: str
    event_queue: str
    oracle: str
    oracle_config: types.oracle_config.OracleConfigJSON
    stable_price_model: types.stable_price_model.StablePriceModelJSON
    quote_lot_size: int
    base_lot_size: int
    maint_base_asset_weight: types.i80f48.I80F48JSON
    init_base_asset_weight: types.i80f48.I80F48JSON
    maint_base_liab_weight: types.i80f48.I80F48JSON
    init_base_liab_weight: types.i80f48.I80F48JSON
    open_interest: int
    seq_num: int
    registration_time: int
    min_funding: types.i80f48.I80F48JSON
    max_funding: types.i80f48.I80F48JSON
    impact_quantity: int
    long_funding: types.i80f48.I80F48JSON
    short_funding: types.i80f48.I80F48JSON
    funding_last_updated: int
    base_liquidation_fee: types.i80f48.I80F48JSON
    maker_fee: types.i80f48.I80F48JSON
    taker_fee: types.i80f48.I80F48JSON
    fees_accrued: types.i80f48.I80F48JSON
    fees_settled: types.i80f48.I80F48JSON
    fee_penalty: float
    settle_fee_flat: float
    settle_fee_amount_threshold: float
    settle_fee_fraction_low_health: float
    settle_pnl_limit_factor: float
    padding3: list[int]
    settle_pnl_limit_window_size_ts: int
    reduce_only: int
    force_close: int
    padding4: list[int]
    maint_overall_asset_weight: types.i80f48.I80F48JSON
    init_overall_asset_weight: types.i80f48.I80F48JSON
    positive_pnl_liquidation_fee: types.i80f48.I80F48JSON
    fees_withdrawn: int
    platform_liquidation_fee: types.i80f48.I80F48JSON
    accrued_liquidation_fees: types.i80f48.I80F48JSON
    reserved: list[int]


@dataclass
class PerpMarket:
    discriminator: typing.ClassVar = b"\n\xdf\x0c,k\xf57\xf7"
    layout: typing.ClassVar = borsh.CStruct(
        "group" / BorshPubkey,
        "settle_token_index" / borsh.U16,
        "perp_market_index" / borsh.U16,
        "blocked1" / borsh.U8,
        "group_insurance_fund" / borsh.U8,
        "bump" / borsh.U8,
        "base_decimals" / borsh.U8,
        "name" / borsh.U8[16],
        "bids" / BorshPubkey,
        "asks" / BorshPubkey,
        "event_queue" / BorshPubkey,
        "oracle" / BorshPubkey,
        "oracle_config" / types.oracle_config.OracleConfig.layout,
        "stable_price_model" / types.stable_price_model.StablePriceModel.layout,
        "quote_lot_size" / borsh.I64,
        "base_lot_size" / borsh.I64,
        "maint_base_asset_weight" / types.i80f48.I80F48.layout,
        "init_base_asset_weight" / types.i80f48.I80F48.layout,
        "maint_base_liab_weight" / types.i80f48.I80F48.layout,
        "init_base_liab_weight" / types.i80f48.I80F48.layout,
        "open_interest" / borsh.I64,
        "seq_num" / borsh.U64,
        "registration_time" / borsh.U64,
        "min_funding" / types.i80f48.I80F48.layout,
        "max_funding" / types.i80f48.I80F48.layout,
        "impact_quantity" / borsh.I64,
        "long_funding" / types.i80f48.I80F48.layout,
        "short_funding" / types.i80f48.I80F48.layout,
        "funding_last_updated" / borsh.U64,
        "base_liquidation_fee" / types.i80f48.I80F48.layout,
        "maker_fee" / types.i80f48.I80F48.layout,
        "taker_fee" / types.i80f48.I80F48.layout,
        "fees_accrued" / types.i80f48.I80F48.layout,
        "fees_settled" / types.i80f48.I80F48.layout,
        "fee_penalty" / borsh.F32,
        "settle_fee_flat" / borsh.F32,
        "settle_fee_amount_threshold" / borsh.F32,
        "settle_fee_fraction_low_health" / borsh.F32,
        "settle_pnl_limit_factor" / borsh.F32,
        "padding3" / borsh.U8[4],
        "settle_pnl_limit_window_size_ts" / borsh.U64,
        "reduce_only" / borsh.U8,
        "force_close" / borsh.U8,
        "padding4" / borsh.U8[6],
        "maint_overall_asset_weight" / types.i80f48.I80F48.layout,
        "init_overall_asset_weight" / types.i80f48.I80F48.layout,
        "positive_pnl_liquidation_fee" / types.i80f48.I80F48.layout,
        "fees_withdrawn" / borsh.U64,
        "platform_liquidation_fee" / types.i80f48.I80F48.layout,
        "accrued_liquidation_fees" / types.i80f48.I80F48.layout,
        "reserved" / borsh.U8[1848],
    )
    group: Pubkey
    settle_token_index: int
    perp_market_index: int
    blocked1: int
    group_insurance_fund: int
    bump: int
    base_decimals: int
    name: list[int]
    bids: Pubkey
    asks: Pubkey
    event_queue: Pubkey
    oracle: Pubkey
    oracle_config: types.oracle_config.OracleConfig
    stable_price_model: types.stable_price_model.StablePriceModel
    quote_lot_size: int
    base_lot_size: int
    maint_base_asset_weight: types.i80f48.I80F48
    init_base_asset_weight: types.i80f48.I80F48
    maint_base_liab_weight: types.i80f48.I80F48
    init_base_liab_weight: types.i80f48.I80F48
    open_interest: int
    seq_num: int
    registration_time: int
    min_funding: types.i80f48.I80F48
    max_funding: types.i80f48.I80F48
    impact_quantity: int
    long_funding: types.i80f48.I80F48
    short_funding: types.i80f48.I80F48
    funding_last_updated: int
    base_liquidation_fee: types.i80f48.I80F48
    maker_fee: types.i80f48.I80F48
    taker_fee: types.i80f48.I80F48
    fees_accrued: types.i80f48.I80F48
    fees_settled: types.i80f48.I80F48
    fee_penalty: float
    settle_fee_flat: float
    settle_fee_amount_threshold: float
    settle_fee_fraction_low_health: float
    settle_pnl_limit_factor: float
    padding3: list[int]
    settle_pnl_limit_window_size_ts: int
    reduce_only: int
    force_close: int
    padding4: list[int]
    maint_overall_asset_weight: types.i80f48.I80F48
    init_overall_asset_weight: types.i80f48.I80F48
    positive_pnl_liquidation_fee: types.i80f48.I80F48
    fees_withdrawn: int
    platform_liquidation_fee: types.i80f48.I80F48
    accrued_liquidation_fees: types.i80f48.I80F48
    reserved: list[int]

    @classmethod
    async def fetch(
        cls,
        conn: AsyncClient,
        address: Pubkey,
        commitment: typing.Optional[Commitment] = None,
        program_id: Pubkey = PROGRAM_ID,
    ) -> typing.Optional["PerpMarket"]:
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
    ) -> typing.List[typing.Optional["PerpMarket"]]:
        infos = await get_multiple_accounts(conn, addresses, commitment=commitment)
        res: typing.List[typing.Optional["PerpMarket"]] = []
        for info in infos:
            if info is None:
                res.append(None)
                continue
            if info.account.owner != program_id:
                raise ValueError("Account does not belong to this program")
            res.append(cls.decode(info.account.data))
        return res

    @classmethod
    def decode(cls, data: bytes) -> "PerpMarket":
        if data[:ACCOUNT_DISCRIMINATOR_SIZE] != cls.discriminator:
            raise AccountInvalidDiscriminator(
                "The discriminator for this account is invalid"
            )
        dec = PerpMarket.layout.parse(data[ACCOUNT_DISCRIMINATOR_SIZE:])
        return cls(
            group=dec.group,
            settle_token_index=dec.settle_token_index,
            perp_market_index=dec.perp_market_index,
            blocked1=dec.blocked1,
            group_insurance_fund=dec.group_insurance_fund,
            bump=dec.bump,
            base_decimals=dec.base_decimals,
            name=dec.name,
            bids=dec.bids,
            asks=dec.asks,
            event_queue=dec.event_queue,
            oracle=dec.oracle,
            oracle_config=types.oracle_config.OracleConfig.from_decoded(
                dec.oracle_config
            ),
            stable_price_model=types.stable_price_model.StablePriceModel.from_decoded(
                dec.stable_price_model
            ),
            quote_lot_size=dec.quote_lot_size,
            base_lot_size=dec.base_lot_size,
            maint_base_asset_weight=types.i80f48.I80F48.from_decoded(
                dec.maint_base_asset_weight
            ),
            init_base_asset_weight=types.i80f48.I80F48.from_decoded(
                dec.init_base_asset_weight
            ),
            maint_base_liab_weight=types.i80f48.I80F48.from_decoded(
                dec.maint_base_liab_weight
            ),
            init_base_liab_weight=types.i80f48.I80F48.from_decoded(
                dec.init_base_liab_weight
            ),
            open_interest=dec.open_interest,
            seq_num=dec.seq_num,
            registration_time=dec.registration_time,
            min_funding=types.i80f48.I80F48.from_decoded(dec.min_funding),
            max_funding=types.i80f48.I80F48.from_decoded(dec.max_funding),
            impact_quantity=dec.impact_quantity,
            long_funding=types.i80f48.I80F48.from_decoded(dec.long_funding),
            short_funding=types.i80f48.I80F48.from_decoded(dec.short_funding),
            funding_last_updated=dec.funding_last_updated,
            base_liquidation_fee=types.i80f48.I80F48.from_decoded(
                dec.base_liquidation_fee
            ),
            maker_fee=types.i80f48.I80F48.from_decoded(dec.maker_fee),
            taker_fee=types.i80f48.I80F48.from_decoded(dec.taker_fee),
            fees_accrued=types.i80f48.I80F48.from_decoded(dec.fees_accrued),
            fees_settled=types.i80f48.I80F48.from_decoded(dec.fees_settled),
            fee_penalty=dec.fee_penalty,
            settle_fee_flat=dec.settle_fee_flat,
            settle_fee_amount_threshold=dec.settle_fee_amount_threshold,
            settle_fee_fraction_low_health=dec.settle_fee_fraction_low_health,
            settle_pnl_limit_factor=dec.settle_pnl_limit_factor,
            padding3=dec.padding3,
            settle_pnl_limit_window_size_ts=dec.settle_pnl_limit_window_size_ts,
            reduce_only=dec.reduce_only,
            force_close=dec.force_close,
            padding4=dec.padding4,
            maint_overall_asset_weight=types.i80f48.I80F48.from_decoded(
                dec.maint_overall_asset_weight
            ),
            init_overall_asset_weight=types.i80f48.I80F48.from_decoded(
                dec.init_overall_asset_weight
            ),
            positive_pnl_liquidation_fee=types.i80f48.I80F48.from_decoded(
                dec.positive_pnl_liquidation_fee
            ),
            fees_withdrawn=dec.fees_withdrawn,
            platform_liquidation_fee=types.i80f48.I80F48.from_decoded(
                dec.platform_liquidation_fee
            ),
            accrued_liquidation_fees=types.i80f48.I80F48.from_decoded(
                dec.accrued_liquidation_fees
            ),
            reserved=dec.reserved,
        )

    def to_json(self) -> PerpMarketJSON:
        return {
            "group": str(self.group),
            "settle_token_index": self.settle_token_index,
            "perp_market_index": self.perp_market_index,
            "blocked1": self.blocked1,
            "group_insurance_fund": self.group_insurance_fund,
            "bump": self.bump,
            "base_decimals": self.base_decimals,
            "name": self.name,
            "bids": str(self.bids),
            "asks": str(self.asks),
            "event_queue": str(self.event_queue),
            "oracle": str(self.oracle),
            "oracle_config": self.oracle_config.to_json(),
            "stable_price_model": self.stable_price_model.to_json(),
            "quote_lot_size": self.quote_lot_size,
            "base_lot_size": self.base_lot_size,
            "maint_base_asset_weight": self.maint_base_asset_weight.to_json(),
            "init_base_asset_weight": self.init_base_asset_weight.to_json(),
            "maint_base_liab_weight": self.maint_base_liab_weight.to_json(),
            "init_base_liab_weight": self.init_base_liab_weight.to_json(),
            "open_interest": self.open_interest,
            "seq_num": self.seq_num,
            "registration_time": self.registration_time,
            "min_funding": self.min_funding.to_json(),
            "max_funding": self.max_funding.to_json(),
            "impact_quantity": self.impact_quantity,
            "long_funding": self.long_funding.to_json(),
            "short_funding": self.short_funding.to_json(),
            "funding_last_updated": self.funding_last_updated,
            "base_liquidation_fee": self.base_liquidation_fee.to_json(),
            "maker_fee": self.maker_fee.to_json(),
            "taker_fee": self.taker_fee.to_json(),
            "fees_accrued": self.fees_accrued.to_json(),
            "fees_settled": self.fees_settled.to_json(),
            "fee_penalty": self.fee_penalty,
            "settle_fee_flat": self.settle_fee_flat,
            "settle_fee_amount_threshold": self.settle_fee_amount_threshold,
            "settle_fee_fraction_low_health": self.settle_fee_fraction_low_health,
            "settle_pnl_limit_factor": self.settle_pnl_limit_factor,
            "padding3": self.padding3,
            "settle_pnl_limit_window_size_ts": self.settle_pnl_limit_window_size_ts,
            "reduce_only": self.reduce_only,
            "force_close": self.force_close,
            "padding4": self.padding4,
            "maint_overall_asset_weight": self.maint_overall_asset_weight.to_json(),
            "init_overall_asset_weight": self.init_overall_asset_weight.to_json(),
            "positive_pnl_liquidation_fee": self.positive_pnl_liquidation_fee.to_json(),
            "fees_withdrawn": self.fees_withdrawn,
            "platform_liquidation_fee": self.platform_liquidation_fee.to_json(),
            "accrued_liquidation_fees": self.accrued_liquidation_fees.to_json(),
            "reserved": self.reserved,
        }

    @classmethod
    def from_json(cls, obj: PerpMarketJSON) -> "PerpMarket":
        return cls(
            group=Pubkey.from_string(obj["group"]),
            settle_token_index=obj["settle_token_index"],
            perp_market_index=obj["perp_market_index"],
            blocked1=obj["blocked1"],
            group_insurance_fund=obj["group_insurance_fund"],
            bump=obj["bump"],
            base_decimals=obj["base_decimals"],
            name=obj["name"],
            bids=Pubkey.from_string(obj["bids"]),
            asks=Pubkey.from_string(obj["asks"]),
            event_queue=Pubkey.from_string(obj["event_queue"]),
            oracle=Pubkey.from_string(obj["oracle"]),
            oracle_config=types.oracle_config.OracleConfig.from_json(
                obj["oracle_config"]
            ),
            stable_price_model=types.stable_price_model.StablePriceModel.from_json(
                obj["stable_price_model"]
            ),
            quote_lot_size=obj["quote_lot_size"],
            base_lot_size=obj["base_lot_size"],
            maint_base_asset_weight=types.i80f48.I80F48.from_json(
                obj["maint_base_asset_weight"]
            ),
            init_base_asset_weight=types.i80f48.I80F48.from_json(
                obj["init_base_asset_weight"]
            ),
            maint_base_liab_weight=types.i80f48.I80F48.from_json(
                obj["maint_base_liab_weight"]
            ),
            init_base_liab_weight=types.i80f48.I80F48.from_json(
                obj["init_base_liab_weight"]
            ),
            open_interest=obj["open_interest"],
            seq_num=obj["seq_num"],
            registration_time=obj["registration_time"],
            min_funding=types.i80f48.I80F48.from_json(obj["min_funding"]),
            max_funding=types.i80f48.I80F48.from_json(obj["max_funding"]),
            impact_quantity=obj["impact_quantity"],
            long_funding=types.i80f48.I80F48.from_json(obj["long_funding"]),
            short_funding=types.i80f48.I80F48.from_json(obj["short_funding"]),
            funding_last_updated=obj["funding_last_updated"],
            base_liquidation_fee=types.i80f48.I80F48.from_json(
                obj["base_liquidation_fee"]
            ),
            maker_fee=types.i80f48.I80F48.from_json(obj["maker_fee"]),
            taker_fee=types.i80f48.I80F48.from_json(obj["taker_fee"]),
            fees_accrued=types.i80f48.I80F48.from_json(obj["fees_accrued"]),
            fees_settled=types.i80f48.I80F48.from_json(obj["fees_settled"]),
            fee_penalty=obj["fee_penalty"],
            settle_fee_flat=obj["settle_fee_flat"],
            settle_fee_amount_threshold=obj["settle_fee_amount_threshold"],
            settle_fee_fraction_low_health=obj["settle_fee_fraction_low_health"],
            settle_pnl_limit_factor=obj["settle_pnl_limit_factor"],
            padding3=obj["padding3"],
            settle_pnl_limit_window_size_ts=obj["settle_pnl_limit_window_size_ts"],
            reduce_only=obj["reduce_only"],
            force_close=obj["force_close"],
            padding4=obj["padding4"],
            maint_overall_asset_weight=types.i80f48.I80F48.from_json(
                obj["maint_overall_asset_weight"]
            ),
            init_overall_asset_weight=types.i80f48.I80F48.from_json(
                obj["init_overall_asset_weight"]
            ),
            positive_pnl_liquidation_fee=types.i80f48.I80F48.from_json(
                obj["positive_pnl_liquidation_fee"]
            ),
            fees_withdrawn=obj["fees_withdrawn"],
            platform_liquidation_fee=types.i80f48.I80F48.from_json(
                obj["platform_liquidation_fee"]
            ),
            accrued_liquidation_fees=types.i80f48.I80F48.from_json(
                obj["accrued_liquidation_fees"]
            ),
            reserved=obj["reserved"],
        )

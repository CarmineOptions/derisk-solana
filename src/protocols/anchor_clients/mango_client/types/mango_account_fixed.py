from __future__ import annotations
import typing
from dataclasses import dataclass
from construct import Container
from solders.pubkey import Pubkey
from anchorpy.borsh_extension import BorshPubkey
import borsh_construct as borsh


class MangoAccountFixedJSON(typing.TypedDict):
    group: str
    owner: str
    name: list[int]
    delegate: str
    account_num: int
    being_liquidated: int
    in_health_region: int
    bump: int
    padding: list[int]
    net_deposits: int
    perp_spot_transfers: int
    health_region_begin_init_health: int
    frozen_until: int
    buyback_fees_accrued_current: int
    buyback_fees_accrued_previous: int
    buyback_fees_expiry_timestamp: int
    next_token_conditional_swap_id: int
    temporary_delegate: str
    temporary_delegate_expiry: int
    last_collateral_fee_charge: int
    reserved: list[int]


@dataclass
class MangoAccountFixed:
    layout: typing.ClassVar = borsh.CStruct(
        "group" / BorshPubkey,
        "owner" / BorshPubkey,
        "name" / borsh.U8[32],
        "delegate" / BorshPubkey,
        "account_num" / borsh.U32,
        "being_liquidated" / borsh.U8,
        "in_health_region" / borsh.U8,
        "bump" / borsh.U8,
        "padding" / borsh.U8[1],
        "net_deposits" / borsh.I64,
        "perp_spot_transfers" / borsh.I64,
        "health_region_begin_init_health" / borsh.I64,
        "frozen_until" / borsh.U64,
        "buyback_fees_accrued_current" / borsh.U64,
        "buyback_fees_accrued_previous" / borsh.U64,
        "buyback_fees_expiry_timestamp" / borsh.U64,
        "next_token_conditional_swap_id" / borsh.U64,
        "temporary_delegate" / BorshPubkey,
        "temporary_delegate_expiry" / borsh.U64,
        "last_collateral_fee_charge" / borsh.U64,
        "reserved" / borsh.U8[152],
    )
    group: Pubkey
    owner: Pubkey
    name: list[int]
    delegate: Pubkey
    account_num: int
    being_liquidated: int
    in_health_region: int
    bump: int
    padding: list[int]
    net_deposits: int
    perp_spot_transfers: int
    health_region_begin_init_health: int
    frozen_until: int
    buyback_fees_accrued_current: int
    buyback_fees_accrued_previous: int
    buyback_fees_expiry_timestamp: int
    next_token_conditional_swap_id: int
    temporary_delegate: Pubkey
    temporary_delegate_expiry: int
    last_collateral_fee_charge: int
    reserved: list[int]

    @classmethod
    def from_decoded(cls, obj: Container) -> "MangoAccountFixed":
        return cls(
            group=obj.group,
            owner=obj.owner,
            name=obj.name,
            delegate=obj.delegate,
            account_num=obj.account_num,
            being_liquidated=obj.being_liquidated,
            in_health_region=obj.in_health_region,
            bump=obj.bump,
            padding=obj.padding,
            net_deposits=obj.net_deposits,
            perp_spot_transfers=obj.perp_spot_transfers,
            health_region_begin_init_health=obj.health_region_begin_init_health,
            frozen_until=obj.frozen_until,
            buyback_fees_accrued_current=obj.buyback_fees_accrued_current,
            buyback_fees_accrued_previous=obj.buyback_fees_accrued_previous,
            buyback_fees_expiry_timestamp=obj.buyback_fees_expiry_timestamp,
            next_token_conditional_swap_id=obj.next_token_conditional_swap_id,
            temporary_delegate=obj.temporary_delegate,
            temporary_delegate_expiry=obj.temporary_delegate_expiry,
            last_collateral_fee_charge=obj.last_collateral_fee_charge,
            reserved=obj.reserved,
        )

    def to_encodable(self) -> dict[str, typing.Any]:
        return {
            "group": self.group,
            "owner": self.owner,
            "name": self.name,
            "delegate": self.delegate,
            "account_num": self.account_num,
            "being_liquidated": self.being_liquidated,
            "in_health_region": self.in_health_region,
            "bump": self.bump,
            "padding": self.padding,
            "net_deposits": self.net_deposits,
            "perp_spot_transfers": self.perp_spot_transfers,
            "health_region_begin_init_health": self.health_region_begin_init_health,
            "frozen_until": self.frozen_until,
            "buyback_fees_accrued_current": self.buyback_fees_accrued_current,
            "buyback_fees_accrued_previous": self.buyback_fees_accrued_previous,
            "buyback_fees_expiry_timestamp": self.buyback_fees_expiry_timestamp,
            "next_token_conditional_swap_id": self.next_token_conditional_swap_id,
            "temporary_delegate": self.temporary_delegate,
            "temporary_delegate_expiry": self.temporary_delegate_expiry,
            "last_collateral_fee_charge": self.last_collateral_fee_charge,
            "reserved": self.reserved,
        }

    def to_json(self) -> MangoAccountFixedJSON:
        return {
            "group": str(self.group),
            "owner": str(self.owner),
            "name": self.name,
            "delegate": str(self.delegate),
            "account_num": self.account_num,
            "being_liquidated": self.being_liquidated,
            "in_health_region": self.in_health_region,
            "bump": self.bump,
            "padding": self.padding,
            "net_deposits": self.net_deposits,
            "perp_spot_transfers": self.perp_spot_transfers,
            "health_region_begin_init_health": self.health_region_begin_init_health,
            "frozen_until": self.frozen_until,
            "buyback_fees_accrued_current": self.buyback_fees_accrued_current,
            "buyback_fees_accrued_previous": self.buyback_fees_accrued_previous,
            "buyback_fees_expiry_timestamp": self.buyback_fees_expiry_timestamp,
            "next_token_conditional_swap_id": self.next_token_conditional_swap_id,
            "temporary_delegate": str(self.temporary_delegate),
            "temporary_delegate_expiry": self.temporary_delegate_expiry,
            "last_collateral_fee_charge": self.last_collateral_fee_charge,
            "reserved": self.reserved,
        }

    @classmethod
    def from_json(cls, obj: MangoAccountFixedJSON) -> "MangoAccountFixed":
        return cls(
            group=Pubkey.from_string(obj["group"]),
            owner=Pubkey.from_string(obj["owner"]),
            name=obj["name"],
            delegate=Pubkey.from_string(obj["delegate"]),
            account_num=obj["account_num"],
            being_liquidated=obj["being_liquidated"],
            in_health_region=obj["in_health_region"],
            bump=obj["bump"],
            padding=obj["padding"],
            net_deposits=obj["net_deposits"],
            perp_spot_transfers=obj["perp_spot_transfers"],
            health_region_begin_init_health=obj["health_region_begin_init_health"],
            frozen_until=obj["frozen_until"],
            buyback_fees_accrued_current=obj["buyback_fees_accrued_current"],
            buyback_fees_accrued_previous=obj["buyback_fees_accrued_previous"],
            buyback_fees_expiry_timestamp=obj["buyback_fees_expiry_timestamp"],
            next_token_conditional_swap_id=obj["next_token_conditional_swap_id"],
            temporary_delegate=Pubkey.from_string(obj["temporary_delegate"]),
            temporary_delegate_expiry=obj["temporary_delegate_expiry"],
            last_collateral_fee_charge=obj["last_collateral_fee_charge"],
            reserved=obj["reserved"],
        )

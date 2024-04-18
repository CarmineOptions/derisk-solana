from __future__ import annotations
import typing
from dataclasses import dataclass
from construct import Container
from solders.pubkey import Pubkey
from anchorpy.borsh_extension import BorshPubkey
import borsh_construct as borsh


class SwitchboardConfigurationJSON(typing.TypedDict):
    price_aggregator: str
    twap_aggregator: str


@dataclass
class SwitchboardConfiguration:
    layout: typing.ClassVar = borsh.CStruct(
        "price_aggregator" / BorshPubkey, "twap_aggregator" / BorshPubkey
    )
    price_aggregator: Pubkey
    twap_aggregator: Pubkey

    @classmethod
    def from_decoded(cls, obj: Container) -> "SwitchboardConfiguration":
        return cls(
            price_aggregator=obj.price_aggregator, twap_aggregator=obj.twap_aggregator
        )

    def to_encodable(self) -> dict[str, typing.Any]:
        return {
            "price_aggregator": self.price_aggregator,
            "twap_aggregator": self.twap_aggregator,
        }

    def to_json(self) -> SwitchboardConfigurationJSON:
        return {
            "price_aggregator": str(self.price_aggregator),
            "twap_aggregator": str(self.twap_aggregator),
        }

    @classmethod
    def from_json(cls, obj: SwitchboardConfigurationJSON) -> "SwitchboardConfiguration":
        return cls(
            price_aggregator=Pubkey.from_string(obj["price_aggregator"]),
            twap_aggregator=Pubkey.from_string(obj["twap_aggregator"]),
        )

from __future__ import annotations
import typing
from dataclasses import dataclass
from construct import Container
from solders.pubkey import Pubkey
from anchorpy.borsh_extension import BorshPubkey
import borsh_construct as borsh


class ScopeConfigurationJSON(typing.TypedDict):
    price_feed: str
    price_chain: list[int]
    twap_chain: list[int]


@dataclass
class ScopeConfiguration:
    layout: typing.ClassVar = borsh.CStruct(
        "price_feed" / BorshPubkey,
        "price_chain" / borsh.U16[4],
        "twap_chain" / borsh.U16[4],
    )
    price_feed: Pubkey
    price_chain: list[int]
    twap_chain: list[int]

    @classmethod
    def from_decoded(cls, obj: Container) -> "ScopeConfiguration":
        return cls(
            price_feed=obj.price_feed,
            price_chain=obj.price_chain,
            twap_chain=obj.twap_chain,
        )

    def to_encodable(self) -> dict[str, typing.Any]:
        return {
            "price_feed": self.price_feed,
            "price_chain": self.price_chain,
            "twap_chain": self.twap_chain,
        }

    def to_json(self) -> ScopeConfigurationJSON:
        return {
            "price_feed": str(self.price_feed),
            "price_chain": self.price_chain,
            "twap_chain": self.twap_chain,
        }

    @classmethod
    def from_json(cls, obj: ScopeConfigurationJSON) -> "ScopeConfiguration":
        return cls(
            price_feed=Pubkey.from_string(obj["price_feed"]),
            price_chain=obj["price_chain"],
            twap_chain=obj["twap_chain"],
        )

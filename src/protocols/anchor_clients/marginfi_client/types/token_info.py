from __future__ import annotations
from . import (
    price_heuristic,
    scope_configuration,
    switchboard_configuration,
    pyth_configuration,
)
import typing
from dataclasses import dataclass
from construct import Container
import borsh_construct as borsh


class TokenInfoJSON(typing.TypedDict):
    name: list[int]
    heuristic: price_heuristic.PriceHeuristicJSON
    max_twap_divergence_bps: int
    max_age_price_seconds: int
    max_age_twap_seconds: int
    scope_configuration: scope_configuration.ScopeConfigurationJSON
    switchboard_configuration: switchboard_configuration.SwitchboardConfigurationJSON
    pyth_configuration: pyth_configuration.PythConfigurationJSON
    padding: list[int]


@dataclass
class TokenInfo:
    layout: typing.ClassVar = borsh.CStruct(
        "name" / borsh.U8[32],
        "heuristic" / price_heuristic.PriceHeuristic.layout,
        "max_twap_divergence_bps" / borsh.U64,
        "max_age_price_seconds" / borsh.U64,
        "max_age_twap_seconds" / borsh.U64,
        "scope_configuration" / scope_configuration.ScopeConfiguration.layout,
        "switchboard_configuration"
        / switchboard_configuration.SwitchboardConfiguration.layout,
        "pyth_configuration" / pyth_configuration.PythConfiguration.layout,
        "padding" / borsh.U64[20],
    )
    name: list[int]
    heuristic: price_heuristic.PriceHeuristic
    max_twap_divergence_bps: int
    max_age_price_seconds: int
    max_age_twap_seconds: int
    scope_configuration: scope_configuration.ScopeConfiguration
    switchboard_configuration: switchboard_configuration.SwitchboardConfiguration
    pyth_configuration: pyth_configuration.PythConfiguration
    padding: list[int]

    @classmethod
    def from_decoded(cls, obj: Container) -> "TokenInfo":
        return cls(
            name=obj.name,
            heuristic=price_heuristic.PriceHeuristic.from_decoded(obj.heuristic),
            max_twap_divergence_bps=obj.max_twap_divergence_bps,
            max_age_price_seconds=obj.max_age_price_seconds,
            max_age_twap_seconds=obj.max_age_twap_seconds,
            scope_configuration=scope_configuration.ScopeConfiguration.from_decoded(
                obj.scope_configuration
            ),
            switchboard_configuration=switchboard_configuration.SwitchboardConfiguration.from_decoded(
                obj.switchboard_configuration
            ),
            pyth_configuration=pyth_configuration.PythConfiguration.from_decoded(
                obj.pyth_configuration
            ),
            padding=obj.padding,
        )

    def to_encodable(self) -> dict[str, typing.Any]:
        return {
            "name": self.name,
            "heuristic": self.heuristic.to_encodable(),
            "max_twap_divergence_bps": self.max_twap_divergence_bps,
            "max_age_price_seconds": self.max_age_price_seconds,
            "max_age_twap_seconds": self.max_age_twap_seconds,
            "scope_configuration": self.scope_configuration.to_encodable(),
            "switchboard_configuration": self.switchboard_configuration.to_encodable(),
            "pyth_configuration": self.pyth_configuration.to_encodable(),
            "padding": self.padding,
        }

    def to_json(self) -> TokenInfoJSON:
        return {
            "name": self.name,
            "heuristic": self.heuristic.to_json(),
            "max_twap_divergence_bps": self.max_twap_divergence_bps,
            "max_age_price_seconds": self.max_age_price_seconds,
            "max_age_twap_seconds": self.max_age_twap_seconds,
            "scope_configuration": self.scope_configuration.to_json(),
            "switchboard_configuration": self.switchboard_configuration.to_json(),
            "pyth_configuration": self.pyth_configuration.to_json(),
            "padding": self.padding,
        }

    @classmethod
    def from_json(cls, obj: TokenInfoJSON) -> "TokenInfo":
        return cls(
            name=obj["name"],
            heuristic=price_heuristic.PriceHeuristic.from_json(obj["heuristic"]),
            max_twap_divergence_bps=obj["max_twap_divergence_bps"],
            max_age_price_seconds=obj["max_age_price_seconds"],
            max_age_twap_seconds=obj["max_age_twap_seconds"],
            scope_configuration=scope_configuration.ScopeConfiguration.from_json(
                obj["scope_configuration"]
            ),
            switchboard_configuration=switchboard_configuration.SwitchboardConfiguration.from_json(
                obj["switchboard_configuration"]
            ),
            pyth_configuration=pyth_configuration.PythConfiguration.from_json(
                obj["pyth_configuration"]
            ),
            padding=obj["padding"],
        )

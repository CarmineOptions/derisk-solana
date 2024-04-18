from __future__ import annotations
import typing
from dataclasses import dataclass
from anchorpy.borsh_extension import EnumForCodegen
import borsh_construct as borsh


class NoneJSON(typing.TypedDict):
    kind: typing.Literal["None"]


class PythEmaJSON(typing.TypedDict):
    kind: typing.Literal["PythEma"]


class SwitchboardV2JSON(typing.TypedDict):
    kind: typing.Literal["SwitchboardV2"]


@dataclass
class None_:
    discriminator: typing.ClassVar = 0
    kind: typing.ClassVar = "None"

    @classmethod
    def to_json(cls) -> NoneJSON:
        return NoneJSON(
            kind="None",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "None": {},
        }


@dataclass
class PythEma:
    discriminator: typing.ClassVar = 1
    kind: typing.ClassVar = "PythEma"

    @classmethod
    def to_json(cls) -> PythEmaJSON:
        return PythEmaJSON(
            kind="PythEma",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "PythEma": {},
        }


@dataclass
class SwitchboardV2:
    discriminator: typing.ClassVar = 2
    kind: typing.ClassVar = "SwitchboardV2"

    @classmethod
    def to_json(cls) -> SwitchboardV2JSON:
        return SwitchboardV2JSON(
            kind="SwitchboardV2",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "SwitchboardV2": {},
        }


OracleSetupKind = typing.Union[None_, PythEma, SwitchboardV2]
OracleSetupJSON = typing.Union[NoneJSON, PythEmaJSON, SwitchboardV2JSON]


def from_decoded(obj: dict) -> OracleSetupKind:
    if not isinstance(obj, dict):
        raise ValueError("Invalid enum object")
    if "None" in obj:
        return None_()
    if "PythEma" in obj:
        return PythEma()
    if "SwitchboardV2" in obj:
        return SwitchboardV2()
    raise ValueError("Invalid enum object")


def from_json(obj: OracleSetupJSON) -> OracleSetupKind:
    if obj["kind"] == "None":
        return None_()
    if obj["kind"] == "PythEma":
        return PythEma()
    if obj["kind"] == "SwitchboardV2":
        return SwitchboardV2()
    kind = obj["kind"]
    raise ValueError(f"Unrecognized enum kind: {kind}")


layout = EnumForCodegen(
    "None" / borsh.CStruct(),
    "PythEma" / borsh.CStruct(),
    "SwitchboardV2" / borsh.CStruct(),
)

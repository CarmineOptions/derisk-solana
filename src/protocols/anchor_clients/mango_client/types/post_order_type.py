from __future__ import annotations
import typing
from dataclasses import dataclass
from anchorpy.borsh_extension import EnumForCodegen
import borsh_construct as borsh


class LimitJSON(typing.TypedDict):
    kind: typing.Literal["Limit"]


class PostOnlyJSON(typing.TypedDict):
    kind: typing.Literal["PostOnly"]


class PostOnlySlideJSON(typing.TypedDict):
    kind: typing.Literal["PostOnlySlide"]


@dataclass
class Limit:
    discriminator: typing.ClassVar = 0
    kind: typing.ClassVar = "Limit"

    @classmethod
    def to_json(cls) -> LimitJSON:
        return LimitJSON(
            kind="Limit",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "Limit": {},
        }


@dataclass
class PostOnly:
    discriminator: typing.ClassVar = 1
    kind: typing.ClassVar = "PostOnly"

    @classmethod
    def to_json(cls) -> PostOnlyJSON:
        return PostOnlyJSON(
            kind="PostOnly",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "PostOnly": {},
        }


@dataclass
class PostOnlySlide:
    discriminator: typing.ClassVar = 2
    kind: typing.ClassVar = "PostOnlySlide"

    @classmethod
    def to_json(cls) -> PostOnlySlideJSON:
        return PostOnlySlideJSON(
            kind="PostOnlySlide",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "PostOnlySlide": {},
        }


PostOrderTypeKind = typing.Union[Limit, PostOnly, PostOnlySlide]
PostOrderTypeJSON = typing.Union[LimitJSON, PostOnlyJSON, PostOnlySlideJSON]


def from_decoded(obj: dict) -> PostOrderTypeKind:
    if not isinstance(obj, dict):
        raise ValueError("Invalid enum object")
    if "Limit" in obj:
        return Limit()
    if "PostOnly" in obj:
        return PostOnly()
    if "PostOnlySlide" in obj:
        return PostOnlySlide()
    raise ValueError("Invalid enum object")


def from_json(obj: PostOrderTypeJSON) -> PostOrderTypeKind:
    if obj["kind"] == "Limit":
        return Limit()
    if obj["kind"] == "PostOnly":
        return PostOnly()
    if obj["kind"] == "PostOnlySlide":
        return PostOnlySlide()
    kind = obj["kind"]
    raise ValueError(f"Unrecognized enum kind: {kind}")


layout = EnumForCodegen(
    "Limit" / borsh.CStruct(),
    "PostOnly" / borsh.CStruct(),
    "PostOnlySlide" / borsh.CStruct(),
)

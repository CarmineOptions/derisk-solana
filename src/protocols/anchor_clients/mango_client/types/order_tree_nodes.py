from __future__ import annotations
from . import (
    any_node,
)
import typing
from dataclasses import dataclass
from construct import Container
import borsh_construct as borsh


class OrderTreeNodesJSON(typing.TypedDict):
    order_tree_type: int
    padding: list[int]
    bump_index: int
    free_list_len: int
    free_list_head: int
    reserved: list[int]
    nodes: list[any_node.AnyNodeJSON]


@dataclass
class OrderTreeNodes:
    layout: typing.ClassVar = borsh.CStruct(
        "order_tree_type" / borsh.U8,
        "padding" / borsh.U8[3],
        "bump_index" / borsh.U32,
        "free_list_len" / borsh.U32,
        "free_list_head" / borsh.U32,
        "reserved" / borsh.U8[512],
        "nodes" / any_node.AnyNode.layout[1024],
    )
    order_tree_type: int
    padding: list[int]
    bump_index: int
    free_list_len: int
    free_list_head: int
    reserved: list[int]
    nodes: list[any_node.AnyNode]

    @classmethod
    def from_decoded(cls, obj: Container) -> "OrderTreeNodes":
        return cls(
            order_tree_type=obj.order_tree_type,
            padding=obj.padding,
            bump_index=obj.bump_index,
            free_list_len=obj.free_list_len,
            free_list_head=obj.free_list_head,
            reserved=obj.reserved,
            nodes=list(
                map(lambda item: any_node.AnyNode.from_decoded(item), obj.nodes)
            ),
        )

    def to_encodable(self) -> dict[str, typing.Any]:
        return {
            "order_tree_type": self.order_tree_type,
            "padding": self.padding,
            "bump_index": self.bump_index,
            "free_list_len": self.free_list_len,
            "free_list_head": self.free_list_head,
            "reserved": self.reserved,
            "nodes": list(map(lambda item: item.to_encodable(), self.nodes)),
        }

    def to_json(self) -> OrderTreeNodesJSON:
        return {
            "order_tree_type": self.order_tree_type,
            "padding": self.padding,
            "bump_index": self.bump_index,
            "free_list_len": self.free_list_len,
            "free_list_head": self.free_list_head,
            "reserved": self.reserved,
            "nodes": list(map(lambda item: item.to_json(), self.nodes)),
        }

    @classmethod
    def from_json(cls, obj: OrderTreeNodesJSON) -> "OrderTreeNodes":
        return cls(
            order_tree_type=obj["order_tree_type"],
            padding=obj["padding"],
            bump_index=obj["bump_index"],
            free_list_len=obj["free_list_len"],
            free_list_head=obj["free_list_head"],
            reserved=obj["reserved"],
            nodes=list(
                map(lambda item: any_node.AnyNode.from_json(item), obj["nodes"])
            ),
        )

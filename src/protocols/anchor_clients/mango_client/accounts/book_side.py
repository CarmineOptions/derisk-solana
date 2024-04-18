import typing
from dataclasses import dataclass
from solders.pubkey import Pubkey
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Commitment
import borsh_construct as borsh
from anchorpy.coder.accounts import ACCOUNT_DISCRIMINATOR_SIZE
from anchorpy.error import AccountInvalidDiscriminator
from anchorpy.utils.rpc import get_multiple_accounts
from ..program_id import PROGRAM_ID
from .. import types


class BookSideJSON(typing.TypedDict):
    roots: list[types.order_tree_root.OrderTreeRootJSON]
    reserved_roots: list[types.order_tree_root.OrderTreeRootJSON]
    reserved: list[int]
    nodes: types.order_tree_nodes.OrderTreeNodesJSON


@dataclass
class BookSide:
    discriminator: typing.ClassVar = b"H,\xe1\x8d\xb2\x82a9"
    layout: typing.ClassVar = borsh.CStruct(
        "roots" / types.order_tree_root.OrderTreeRoot.layout[2],
        "reserved_roots" / types.order_tree_root.OrderTreeRoot.layout[4],
        "reserved" / borsh.U8[256],
        "nodes" / types.order_tree_nodes.OrderTreeNodes.layout,
    )
    roots: list[types.order_tree_root.OrderTreeRoot]
    reserved_roots: list[types.order_tree_root.OrderTreeRoot]
    reserved: list[int]
    nodes: types.order_tree_nodes.OrderTreeNodes

    @classmethod
    async def fetch(
        cls,
        conn: AsyncClient,
        address: Pubkey,
        commitment: typing.Optional[Commitment] = None,
        program_id: Pubkey = PROGRAM_ID,
    ) -> typing.Optional["BookSide"]:
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
    ) -> typing.List[typing.Optional["BookSide"]]:
        infos = await get_multiple_accounts(conn, addresses, commitment=commitment)
        res: typing.List[typing.Optional["BookSide"]] = []
        for info in infos:
            if info is None:
                res.append(None)
                continue
            if info.account.owner != program_id:
                raise ValueError("Account does not belong to this program")
            res.append(cls.decode(info.account.data))
        return res

    @classmethod
    def decode(cls, data: bytes) -> "BookSide":
        if data[:ACCOUNT_DISCRIMINATOR_SIZE] != cls.discriminator:
            raise AccountInvalidDiscriminator(
                "The discriminator for this account is invalid"
            )
        dec = BookSide.layout.parse(data[ACCOUNT_DISCRIMINATOR_SIZE:])
        return cls(
            roots=list(
                map(
                    lambda item: types.order_tree_root.OrderTreeRoot.from_decoded(item),
                    dec.roots,
                )
            ),
            reserved_roots=list(
                map(
                    lambda item: types.order_tree_root.OrderTreeRoot.from_decoded(item),
                    dec.reserved_roots,
                )
            ),
            reserved=dec.reserved,
            nodes=types.order_tree_nodes.OrderTreeNodes.from_decoded(dec.nodes),
        )

    def to_json(self) -> BookSideJSON:
        return {
            "roots": list(map(lambda item: item.to_json(), self.roots)),
            "reserved_roots": list(
                map(lambda item: item.to_json(), self.reserved_roots)
            ),
            "reserved": self.reserved,
            "nodes": self.nodes.to_json(),
        }

    @classmethod
    def from_json(cls, obj: BookSideJSON) -> "BookSide":
        return cls(
            roots=list(
                map(
                    lambda item: types.order_tree_root.OrderTreeRoot.from_json(item),
                    obj["roots"],
                )
            ),
            reserved_roots=list(
                map(
                    lambda item: types.order_tree_root.OrderTreeRoot.from_json(item),
                    obj["reserved_roots"],
                )
            ),
            reserved=obj["reserved"],
            nodes=types.order_tree_nodes.OrderTreeNodes.from_json(obj["nodes"]),
        )

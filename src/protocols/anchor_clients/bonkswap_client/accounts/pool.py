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


class PoolJSON(typing.TypedDict):
    token_x: str
    token_y: str
    pool_x_account: str
    pool_y_account: str
    admin: str
    project_owner: str
    token_x_reserve: types.token.TokenJSON
    token_y_reserve: types.token.TokenJSON
    self_shares: types.token.TokenJSON
    all_shares: types.token.TokenJSON
    buyback_amount_x: types.token.TokenJSON
    buyback_amount_y: types.token.TokenJSON
    project_amount_x: types.token.TokenJSON
    project_amount_y: types.token.TokenJSON
    mercanti_amount_x: types.token.TokenJSON
    mercanti_amount_y: types.token.TokenJSON
    lp_accumulator_x: types.fixed_point.FixedPointJSON
    lp_accumulator_y: types.fixed_point.FixedPointJSON
    const_k: types.product.ProductJSON
    price: types.fixed_point.FixedPointJSON
    lp_fee: types.fixed_point.FixedPointJSON
    buyback_fee: types.fixed_point.FixedPointJSON
    project_fee: types.fixed_point.FixedPointJSON
    mercanti_fee: types.fixed_point.FixedPointJSON
    farm_count: int
    bump: int


@dataclass
class Pool:
    discriminator: typing.ClassVar = b"\xf1\x9am\x04\x11\xb1m\xbc"
    layout: typing.ClassVar = borsh.CStruct(
        "token_x" / BorshPubkey,
        "token_y" / BorshPubkey,
        "pool_x_account" / BorshPubkey,
        "pool_y_account" / BorshPubkey,
        "admin" / BorshPubkey,
        "project_owner" / BorshPubkey,
        "token_x_reserve" / types.token.Token.layout,
        "token_y_reserve" / types.token.Token.layout,
        "self_shares" / types.token.Token.layout,
        "all_shares" / types.token.Token.layout,
        "buyback_amount_x" / types.token.Token.layout,
        "buyback_amount_y" / types.token.Token.layout,
        "project_amount_x" / types.token.Token.layout,
        "project_amount_y" / types.token.Token.layout,
        "mercanti_amount_x" / types.token.Token.layout,
        "mercanti_amount_y" / types.token.Token.layout,
        "lp_accumulator_x" / types.fixed_point.FixedPoint.layout,
        "lp_accumulator_y" / types.fixed_point.FixedPoint.layout,
        "const_k" / types.product.Product.layout,
        "price" / types.fixed_point.FixedPoint.layout,
        "lp_fee" / types.fixed_point.FixedPoint.layout,
        "buyback_fee" / types.fixed_point.FixedPoint.layout,
        "project_fee" / types.fixed_point.FixedPoint.layout,
        "mercanti_fee" / types.fixed_point.FixedPoint.layout,
        "farm_count" / borsh.U64,
        "bump" / borsh.U8,
    )
    token_x: Pubkey
    token_y: Pubkey
    pool_x_account: Pubkey
    pool_y_account: Pubkey
    admin: Pubkey
    project_owner: Pubkey
    token_x_reserve: types.token.Token
    token_y_reserve: types.token.Token
    self_shares: types.token.Token
    all_shares: types.token.Token
    buyback_amount_x: types.token.Token
    buyback_amount_y: types.token.Token
    project_amount_x: types.token.Token
    project_amount_y: types.token.Token
    mercanti_amount_x: types.token.Token
    mercanti_amount_y: types.token.Token
    lp_accumulator_x: types.fixed_point.FixedPoint
    lp_accumulator_y: types.fixed_point.FixedPoint
    const_k: types.product.Product
    price: types.fixed_point.FixedPoint
    lp_fee: types.fixed_point.FixedPoint
    buyback_fee: types.fixed_point.FixedPoint
    project_fee: types.fixed_point.FixedPoint
    mercanti_fee: types.fixed_point.FixedPoint
    farm_count: int
    bump: int

    @classmethod
    async def fetch(
        cls,
        conn: AsyncClient,
        address: Pubkey,
        commitment: typing.Optional[Commitment] = None,
        program_id: Pubkey = PROGRAM_ID,
    ) -> typing.Optional["Pool"]:
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
    ) -> typing.List[typing.Optional["Pool"]]:
        infos = await get_multiple_accounts(conn, addresses, commitment=commitment)
        res: typing.List[typing.Optional["Pool"]] = []
        for info in infos:
            if info is None:
                res.append(None)
                continue
            if info.account.owner != program_id:
                raise ValueError("Account does not belong to this program")
            res.append(cls.decode(info.account.data))
        return res

    @classmethod
    def decode(cls, data: bytes) -> "Pool":
        if data[:ACCOUNT_DISCRIMINATOR_SIZE] != cls.discriminator:
            raise AccountInvalidDiscriminator(
                "The discriminator for this account is invalid"
            )
        dec = Pool.layout.parse(data[ACCOUNT_DISCRIMINATOR_SIZE:])
        return cls(
            token_x=dec.token_x,
            token_y=dec.token_y,
            pool_x_account=dec.pool_x_account,
            pool_y_account=dec.pool_y_account,
            admin=dec.admin,
            project_owner=dec.project_owner,
            token_x_reserve=types.token.Token.from_decoded(dec.token_x_reserve),
            token_y_reserve=types.token.Token.from_decoded(dec.token_y_reserve),
            self_shares=types.token.Token.from_decoded(dec.self_shares),
            all_shares=types.token.Token.from_decoded(dec.all_shares),
            buyback_amount_x=types.token.Token.from_decoded(dec.buyback_amount_x),
            buyback_amount_y=types.token.Token.from_decoded(dec.buyback_amount_y),
            project_amount_x=types.token.Token.from_decoded(dec.project_amount_x),
            project_amount_y=types.token.Token.from_decoded(dec.project_amount_y),
            mercanti_amount_x=types.token.Token.from_decoded(dec.mercanti_amount_x),
            mercanti_amount_y=types.token.Token.from_decoded(dec.mercanti_amount_y),
            lp_accumulator_x=types.fixed_point.FixedPoint.from_decoded(
                dec.lp_accumulator_x
            ),
            lp_accumulator_y=types.fixed_point.FixedPoint.from_decoded(
                dec.lp_accumulator_y
            ),
            const_k=types.product.Product.from_decoded(dec.const_k),
            price=types.fixed_point.FixedPoint.from_decoded(dec.price),
            lp_fee=types.fixed_point.FixedPoint.from_decoded(dec.lp_fee),
            buyback_fee=types.fixed_point.FixedPoint.from_decoded(dec.buyback_fee),
            project_fee=types.fixed_point.FixedPoint.from_decoded(dec.project_fee),
            mercanti_fee=types.fixed_point.FixedPoint.from_decoded(dec.mercanti_fee),
            farm_count=dec.farm_count,
            bump=dec.bump,
        )

    def to_json(self) -> PoolJSON:
        return {
            "token_x": str(self.token_x),
            "token_y": str(self.token_y),
            "pool_x_account": str(self.pool_x_account),
            "pool_y_account": str(self.pool_y_account),
            "admin": str(self.admin),
            "project_owner": str(self.project_owner),
            "token_x_reserve": self.token_x_reserve.to_json(),
            "token_y_reserve": self.token_y_reserve.to_json(),
            "self_shares": self.self_shares.to_json(),
            "all_shares": self.all_shares.to_json(),
            "buyback_amount_x": self.buyback_amount_x.to_json(),
            "buyback_amount_y": self.buyback_amount_y.to_json(),
            "project_amount_x": self.project_amount_x.to_json(),
            "project_amount_y": self.project_amount_y.to_json(),
            "mercanti_amount_x": self.mercanti_amount_x.to_json(),
            "mercanti_amount_y": self.mercanti_amount_y.to_json(),
            "lp_accumulator_x": self.lp_accumulator_x.to_json(),
            "lp_accumulator_y": self.lp_accumulator_y.to_json(),
            "const_k": self.const_k.to_json(),
            "price": self.price.to_json(),
            "lp_fee": self.lp_fee.to_json(),
            "buyback_fee": self.buyback_fee.to_json(),
            "project_fee": self.project_fee.to_json(),
            "mercanti_fee": self.mercanti_fee.to_json(),
            "farm_count": self.farm_count,
            "bump": self.bump,
        }

    @classmethod
    def from_json(cls, obj: PoolJSON) -> "Pool":
        return cls(
            token_x=Pubkey.from_string(obj["token_x"]),
            token_y=Pubkey.from_string(obj["token_y"]),
            pool_x_account=Pubkey.from_string(obj["pool_x_account"]),
            pool_y_account=Pubkey.from_string(obj["pool_y_account"]),
            admin=Pubkey.from_string(obj["admin"]),
            project_owner=Pubkey.from_string(obj["project_owner"]),
            token_x_reserve=types.token.Token.from_json(obj["token_x_reserve"]),
            token_y_reserve=types.token.Token.from_json(obj["token_y_reserve"]),
            self_shares=types.token.Token.from_json(obj["self_shares"]),
            all_shares=types.token.Token.from_json(obj["all_shares"]),
            buyback_amount_x=types.token.Token.from_json(obj["buyback_amount_x"]),
            buyback_amount_y=types.token.Token.from_json(obj["buyback_amount_y"]),
            project_amount_x=types.token.Token.from_json(obj["project_amount_x"]),
            project_amount_y=types.token.Token.from_json(obj["project_amount_y"]),
            mercanti_amount_x=types.token.Token.from_json(obj["mercanti_amount_x"]),
            mercanti_amount_y=types.token.Token.from_json(obj["mercanti_amount_y"]),
            lp_accumulator_x=types.fixed_point.FixedPoint.from_json(
                obj["lp_accumulator_x"]
            ),
            lp_accumulator_y=types.fixed_point.FixedPoint.from_json(
                obj["lp_accumulator_y"]
            ),
            const_k=types.product.Product.from_json(obj["const_k"]),
            price=types.fixed_point.FixedPoint.from_json(obj["price"]),
            lp_fee=types.fixed_point.FixedPoint.from_json(obj["lp_fee"]),
            buyback_fee=types.fixed_point.FixedPoint.from_json(obj["buyback_fee"]),
            project_fee=types.fixed_point.FixedPoint.from_json(obj["project_fee"]),
            mercanti_fee=types.fixed_point.FixedPoint.from_json(obj["mercanti_fee"]),
            farm_count=obj["farm_count"],
            bump=obj["bump"],
        )

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


class StubOracleJSON(typing.TypedDict):
    group: str
    mint: str
    price: types.i80f48.I80F48JSON
    last_update_ts: int
    last_update_slot: int
    deviation: types.i80f48.I80F48JSON
    reserved: list[int]


@dataclass
class StubOracle:
    discriminator: typing.ClassVar = b"\xe0\xfb\xfec\xb1\xae\x89\x04"
    layout: typing.ClassVar = borsh.CStruct(
        "group" / BorshPubkey,
        "mint" / BorshPubkey,
        "price" / types.i80f48.I80F48.layout,
        "last_update_ts" / borsh.I64,
        "last_update_slot" / borsh.U64,
        "deviation" / types.i80f48.I80F48.layout,
        "reserved" / borsh.U8[104],
    )
    group: Pubkey
    mint: Pubkey
    price: types.i80f48.I80F48
    last_update_ts: int
    last_update_slot: int
    deviation: types.i80f48.I80F48
    reserved: list[int]

    @classmethod
    async def fetch(
        cls,
        conn: AsyncClient,
        address: Pubkey,
        commitment: typing.Optional[Commitment] = None,
        program_id: Pubkey = PROGRAM_ID,
    ) -> typing.Optional["StubOracle"]:
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
    ) -> typing.List[typing.Optional["StubOracle"]]:
        infos = await get_multiple_accounts(conn, addresses, commitment=commitment)
        res: typing.List[typing.Optional["StubOracle"]] = []
        for info in infos:
            if info is None:
                res.append(None)
                continue
            if info.account.owner != program_id:
                raise ValueError("Account does not belong to this program")
            res.append(cls.decode(info.account.data))
        return res

    @classmethod
    def decode(cls, data: bytes) -> "StubOracle":
        if data[:ACCOUNT_DISCRIMINATOR_SIZE] != cls.discriminator:
            raise AccountInvalidDiscriminator(
                "The discriminator for this account is invalid"
            )
        dec = StubOracle.layout.parse(data[ACCOUNT_DISCRIMINATOR_SIZE:])
        return cls(
            group=dec.group,
            mint=dec.mint,
            price=types.i80f48.I80F48.from_decoded(dec.price),
            last_update_ts=dec.last_update_ts,
            last_update_slot=dec.last_update_slot,
            deviation=types.i80f48.I80F48.from_decoded(dec.deviation),
            reserved=dec.reserved,
        )

    def to_json(self) -> StubOracleJSON:
        return {
            "group": str(self.group),
            "mint": str(self.mint),
            "price": self.price.to_json(),
            "last_update_ts": self.last_update_ts,
            "last_update_slot": self.last_update_slot,
            "deviation": self.deviation.to_json(),
            "reserved": self.reserved,
        }

    @classmethod
    def from_json(cls, obj: StubOracleJSON) -> "StubOracle":
        return cls(
            group=Pubkey.from_string(obj["group"]),
            mint=Pubkey.from_string(obj["mint"]),
            price=types.i80f48.I80F48.from_json(obj["price"]),
            last_update_ts=obj["last_update_ts"],
            last_update_slot=obj["last_update_slot"],
            deviation=types.i80f48.I80F48.from_json(obj["deviation"]),
            reserved=obj["reserved"],
        )

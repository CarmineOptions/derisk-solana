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


class MintInfoJSON(typing.TypedDict):
    group: str
    token_index: int
    group_insurance_fund: int
    padding1: list[int]
    mint: str
    banks: list[str]
    vaults: list[str]
    oracle: str
    registration_time: int
    fallback_oracle: str
    reserved: list[int]


@dataclass
class MintInfo:
    discriminator: typing.ClassVar = b"\xc7s\xd5\xdd\xdb\x1d\x87\xae"
    layout: typing.ClassVar = borsh.CStruct(
        "group" / BorshPubkey,
        "token_index" / borsh.U16,
        "group_insurance_fund" / borsh.U8,
        "padding1" / borsh.U8[5],
        "mint" / BorshPubkey,
        "banks" / BorshPubkey[6],
        "vaults" / BorshPubkey[6],
        "oracle" / BorshPubkey,
        "registration_time" / borsh.U64,
        "fallback_oracle" / BorshPubkey,
        "reserved" / borsh.U8[2528],
    )
    group: Pubkey
    token_index: int
    group_insurance_fund: int
    padding1: list[int]
    mint: Pubkey
    banks: list[Pubkey]
    vaults: list[Pubkey]
    oracle: Pubkey
    registration_time: int
    fallback_oracle: Pubkey
    reserved: list[int]

    @classmethod
    async def fetch(
        cls,
        conn: AsyncClient,
        address: Pubkey,
        commitment: typing.Optional[Commitment] = None,
        program_id: Pubkey = PROGRAM_ID,
    ) -> typing.Optional["MintInfo"]:
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
    ) -> typing.List[typing.Optional["MintInfo"]]:
        infos = await get_multiple_accounts(conn, addresses, commitment=commitment)
        res: typing.List[typing.Optional["MintInfo"]] = []
        for info in infos:
            if info is None:
                res.append(None)
                continue
            if info.account.owner != program_id:
                raise ValueError("Account does not belong to this program")
            res.append(cls.decode(info.account.data))
        return res

    @classmethod
    def decode(cls, data: bytes) -> "MintInfo":
        if data[:ACCOUNT_DISCRIMINATOR_SIZE] != cls.discriminator:
            raise AccountInvalidDiscriminator(
                "The discriminator for this account is invalid"
            )
        dec = MintInfo.layout.parse(data[ACCOUNT_DISCRIMINATOR_SIZE:])
        return cls(
            group=dec.group,
            token_index=dec.token_index,
            group_insurance_fund=dec.group_insurance_fund,
            padding1=dec.padding1,
            mint=dec.mint,
            banks=dec.banks,
            vaults=dec.vaults,
            oracle=dec.oracle,
            registration_time=dec.registration_time,
            fallback_oracle=dec.fallback_oracle,
            reserved=dec.reserved,
        )

    def to_json(self) -> MintInfoJSON:
        return {
            "group": str(self.group),
            "token_index": self.token_index,
            "group_insurance_fund": self.group_insurance_fund,
            "padding1": self.padding1,
            "mint": str(self.mint),
            "banks": list(map(lambda item: str(item), self.banks)),
            "vaults": list(map(lambda item: str(item), self.vaults)),
            "oracle": str(self.oracle),
            "registration_time": self.registration_time,
            "fallback_oracle": str(self.fallback_oracle),
            "reserved": self.reserved,
        }

    @classmethod
    def from_json(cls, obj: MintInfoJSON) -> "MintInfo":
        return cls(
            group=Pubkey.from_string(obj["group"]),
            token_index=obj["token_index"],
            group_insurance_fund=obj["group_insurance_fund"],
            padding1=obj["padding1"],
            mint=Pubkey.from_string(obj["mint"]),
            banks=list(map(lambda item: Pubkey.from_string(item), obj["banks"])),
            vaults=list(map(lambda item: Pubkey.from_string(item), obj["vaults"])),
            oracle=Pubkey.from_string(obj["oracle"]),
            registration_time=obj["registration_time"],
            fallback_oracle=Pubkey.from_string(obj["fallback_oracle"]),
            reserved=obj["reserved"],
        )

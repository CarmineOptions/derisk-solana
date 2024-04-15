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


class GroupJSON(typing.TypedDict):
    creator: str
    group_num: int
    admin: str
    fast_listing_admin: str
    mngo_token_index: int
    padding: list[int]
    insurance_vault: str
    insurance_mint: str
    bump: int
    testing: int
    version: int
    buyback_fees: int
    buyback_fees_mngo_bonus_factor: float
    address_lookup_tables: list[str]
    security_admin: str
    deposit_limit_quote: int
    ix_gate: int
    buyback_fees_swap_mango_account: str
    buyback_fees_expiry_interval: int
    fast_listing_interval_start: int
    fast_listings_in_interval: int
    allowed_fast_listings_per_interval: int
    padding2: list[int]
    collateral_fee_interval: int
    reserved: list[int]


@dataclass
class Group:
    discriminator: typing.ClassVar = b"\xd1\xf9\xd0?\xb6Y\xba\xfe"
    layout: typing.ClassVar = borsh.CStruct(
        "creator" / BorshPubkey,
        "group_num" / borsh.U32,
        "admin" / BorshPubkey,
        "fast_listing_admin" / BorshPubkey,
        "mngo_token_index" / borsh.U16,
        "padding" / borsh.U8[2],
        "insurance_vault" / BorshPubkey,
        "insurance_mint" / BorshPubkey,
        "bump" / borsh.U8,
        "testing" / borsh.U8,
        "version" / borsh.U8,
        "buyback_fees" / borsh.U8,
        "buyback_fees_mngo_bonus_factor" / borsh.F32,
        "address_lookup_tables" / BorshPubkey[20],
        "security_admin" / BorshPubkey,
        "deposit_limit_quote" / borsh.U64,
        "ix_gate" / borsh.U128,
        "buyback_fees_swap_mango_account" / BorshPubkey,
        "buyback_fees_expiry_interval" / borsh.U64,
        "fast_listing_interval_start" / borsh.U64,
        "fast_listings_in_interval" / borsh.U16,
        "allowed_fast_listings_per_interval" / borsh.U16,
        "padding2" / borsh.U8[4],
        "collateral_fee_interval" / borsh.U64,
        "reserved" / borsh.U8[1800],
    )
    creator: Pubkey
    group_num: int
    admin: Pubkey
    fast_listing_admin: Pubkey
    mngo_token_index: int
    padding: list[int]
    insurance_vault: Pubkey
    insurance_mint: Pubkey
    bump: int
    testing: int
    version: int
    buyback_fees: int
    buyback_fees_mngo_bonus_factor: float
    address_lookup_tables: list[Pubkey]
    security_admin: Pubkey
    deposit_limit_quote: int
    ix_gate: int
    buyback_fees_swap_mango_account: Pubkey
    buyback_fees_expiry_interval: int
    fast_listing_interval_start: int
    fast_listings_in_interval: int
    allowed_fast_listings_per_interval: int
    padding2: list[int]
    collateral_fee_interval: int
    reserved: list[int]

    @classmethod
    async def fetch(
        cls,
        conn: AsyncClient,
        address: Pubkey,
        commitment: typing.Optional[Commitment] = None,
        program_id: Pubkey = PROGRAM_ID,
    ) -> typing.Optional["Group"]:
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
    ) -> typing.List[typing.Optional["Group"]]:
        infos = await get_multiple_accounts(conn, addresses, commitment=commitment)
        res: typing.List[typing.Optional["Group"]] = []
        for info in infos:
            if info is None:
                res.append(None)
                continue
            if info.account.owner != program_id:
                raise ValueError("Account does not belong to this program")
            res.append(cls.decode(info.account.data))
        return res

    @classmethod
    def decode(cls, data: bytes) -> "Group":
        if data[:ACCOUNT_DISCRIMINATOR_SIZE] != cls.discriminator:
            raise AccountInvalidDiscriminator(
                "The discriminator for this account is invalid"
            )
        dec = Group.layout.parse(data[ACCOUNT_DISCRIMINATOR_SIZE:])
        return cls(
            creator=dec.creator,
            group_num=dec.group_num,
            admin=dec.admin,
            fast_listing_admin=dec.fast_listing_admin,
            mngo_token_index=dec.mngo_token_index,
            padding=dec.padding,
            insurance_vault=dec.insurance_vault,
            insurance_mint=dec.insurance_mint,
            bump=dec.bump,
            testing=dec.testing,
            version=dec.version,
            buyback_fees=dec.buyback_fees,
            buyback_fees_mngo_bonus_factor=dec.buyback_fees_mngo_bonus_factor,
            address_lookup_tables=dec.address_lookup_tables,
            security_admin=dec.security_admin,
            deposit_limit_quote=dec.deposit_limit_quote,
            ix_gate=dec.ix_gate,
            buyback_fees_swap_mango_account=dec.buyback_fees_swap_mango_account,
            buyback_fees_expiry_interval=dec.buyback_fees_expiry_interval,
            fast_listing_interval_start=dec.fast_listing_interval_start,
            fast_listings_in_interval=dec.fast_listings_in_interval,
            allowed_fast_listings_per_interval=dec.allowed_fast_listings_per_interval,
            padding2=dec.padding2,
            collateral_fee_interval=dec.collateral_fee_interval,
            reserved=dec.reserved,
        )

    def to_json(self) -> GroupJSON:
        return {
            "creator": str(self.creator),
            "group_num": self.group_num,
            "admin": str(self.admin),
            "fast_listing_admin": str(self.fast_listing_admin),
            "mngo_token_index": self.mngo_token_index,
            "padding": self.padding,
            "insurance_vault": str(self.insurance_vault),
            "insurance_mint": str(self.insurance_mint),
            "bump": self.bump,
            "testing": self.testing,
            "version": self.version,
            "buyback_fees": self.buyback_fees,
            "buyback_fees_mngo_bonus_factor": self.buyback_fees_mngo_bonus_factor,
            "address_lookup_tables": list(
                map(lambda item: str(item), self.address_lookup_tables)
            ),
            "security_admin": str(self.security_admin),
            "deposit_limit_quote": self.deposit_limit_quote,
            "ix_gate": self.ix_gate,
            "buyback_fees_swap_mango_account": str(
                self.buyback_fees_swap_mango_account
            ),
            "buyback_fees_expiry_interval": self.buyback_fees_expiry_interval,
            "fast_listing_interval_start": self.fast_listing_interval_start,
            "fast_listings_in_interval": self.fast_listings_in_interval,
            "allowed_fast_listings_per_interval": self.allowed_fast_listings_per_interval,
            "padding2": self.padding2,
            "collateral_fee_interval": self.collateral_fee_interval,
            "reserved": self.reserved,
        }

    @classmethod
    def from_json(cls, obj: GroupJSON) -> "Group":
        return cls(
            creator=Pubkey.from_string(obj["creator"]),
            group_num=obj["group_num"],
            admin=Pubkey.from_string(obj["admin"]),
            fast_listing_admin=Pubkey.from_string(obj["fast_listing_admin"]),
            mngo_token_index=obj["mngo_token_index"],
            padding=obj["padding"],
            insurance_vault=Pubkey.from_string(obj["insurance_vault"]),
            insurance_mint=Pubkey.from_string(obj["insurance_mint"]),
            bump=obj["bump"],
            testing=obj["testing"],
            version=obj["version"],
            buyback_fees=obj["buyback_fees"],
            buyback_fees_mngo_bonus_factor=obj["buyback_fees_mngo_bonus_factor"],
            address_lookup_tables=list(
                map(lambda item: Pubkey.from_string(item), obj["address_lookup_tables"])
            ),
            security_admin=Pubkey.from_string(obj["security_admin"]),
            deposit_limit_quote=obj["deposit_limit_quote"],
            ix_gate=obj["ix_gate"],
            buyback_fees_swap_mango_account=Pubkey.from_string(
                obj["buyback_fees_swap_mango_account"]
            ),
            buyback_fees_expiry_interval=obj["buyback_fees_expiry_interval"],
            fast_listing_interval_start=obj["fast_listing_interval_start"],
            fast_listings_in_interval=obj["fast_listings_in_interval"],
            allowed_fast_listings_per_interval=obj[
                "allowed_fast_listings_per_interval"
            ],
            padding2=obj["padding2"],
            collateral_fee_interval=obj["collateral_fee_interval"],
            reserved=obj["reserved"],
        )

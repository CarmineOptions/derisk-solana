"""
Module containing functionality related to Postgres DB used throughout the repo.
"""
import os
import time
from enum import Enum

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    BigInteger,
    ForeignKey,
    PrimaryKeyConstraint,
    Float,
    DECIMAL,
    Boolean,
    inspect
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.types import Enum as SQLEnum
from sqlalchemy import Index
from sqlalchemy.dialects.postgresql import ARRAY as PG_ARRAY, JSONB
from db.utils import check_bigint

Base = declarative_base()

POSTGRES_USER = os.environ.get("POSTGRES_USER")
if POSTGRES_USER is None:
    raise ValueError("no POSTGRES_USER env var")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
if POSTGRES_PASSWORD is None:
    # if password not provided check for password file
    POSTGRES_PASSWORD_FILE = os.environ.get("POSTGRES_PASSWORD_FILE")
    if POSTGRES_PASSWORD_FILE is None:
        raise ValueError("no POSTGRES_PASSWORD env var")
    with open(POSTGRES_PASSWORD_FILE, "r") as secret_file:
        POSTGRES_PASSWORD = secret_file.read().strip()
POSTGRES_HOST = os.environ.get("POSTGRES_HOST")
if POSTGRES_HOST is None:
    raise ValueError("no POSTGRES_HOST env var")
POSTGRES_DB = os.environ.get("POSTGRES_DB")
if POSTGRES_DB is None:
    raise ValueError("no POSTGRES_DB env var")

CONN_STRING = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}"
SCHEMA = 'public'
SCHEMA_LENDERS = 'lenders'


def get_db_session() -> Session:
    """
    Initializes a session -> it must be closed manually!

    Returns:
        Returns a database session object that can be used to interact with the database.
    """
    session = sessionmaker(bind=create_engine(CONN_STRING))
    return session()


class CollectionStreamTypes(Enum):
    HISTORICAL = 'historical'
    CURRENT = 'current'
    SIGNATURE = 'signature'


class TransactionStatusWithSignature(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True)
    source = Column(String, ForeignKey(f'{SCHEMA_LENDERS}.protocols.public_key'), nullable=False)
    signature = Column(String, nullable=False)
    slot = Column(BigInteger, nullable=False)
    block_time = Column(BigInteger, nullable=False)
    transaction_data = Column(String, nullable=True)  # column to store json with transaction's data
    collection_stream = Column(SQLEnum(CollectionStreamTypes, name='collection_stream_types'), nullable=True)

    __table_args__ = (
        Index("ix_transactions_slot", "slot"),
        Index("ix_transactions_block_time", "block_time"),
        Index("ix_transactions_signature", "signature"),
        Index("ix_transactions_source", "source"),
        {"schema": SCHEMA_LENDERS},
    )

    def __repr__(self):
        return (
            f"<TransactionStatusWithSignature(signature='{self.signature}',"
            f" slot={self.slot}, block_time={self.block_time} )>"
        )


class TransactionStatusError(Base):
    __tablename__ = "tx_status_errors"
    __table_args__ = {"schema": SCHEMA_LENDERS}

    id = Column(Integer, primary_key=True)
    error_body = Column(String, nullable=False)
    tx_signatures_id = Column(Integer, ForeignKey(f'{SCHEMA_LENDERS}.transactions.id'), nullable=False)


class TransactionStatusMemo(Base):
    __tablename__ = "tx_status_memo"
    __table_args__ = {"schema": SCHEMA_LENDERS}

    id = Column(Integer, primary_key=True)
    memo_body = Column(String, nullable=False)
    tx_signatures_id = Column(Integer, ForeignKey(f'{SCHEMA_LENDERS}.transactions.id'), nullable=False)


class ParsedTransactions(Base):
    __abstract__ = True
    __tablename__ = "parsed_transactions"
    __table_args__ = {"schema": SCHEMA_LENDERS}

    id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_id = Column(String, nullable=True)
    instruction_name = Column(String, nullable=True)
    event_name = Column(String, nullable=True)
    event_number = Column(String, nullable=True)

    position = Column(SQLEnum('asset', 'liability', name='sqlenum', schema=SCHEMA_LENDERS), nullable=True)
    token = Column(String, nullable=True)
    amount = Column(BigInteger, nullable=True)
    amount_decimal = Column(Integer, nullable=True)

    bank = Column(String, nullable=True)
    account = Column(String, nullable=True)
    signer = Column(String, nullable=True)

    context = Column(String, nullable=True)

    block = Column(BigInteger, nullable=True)
    created_at = Column(BigInteger, nullable=True)

    def __repr__(self):
        return f"<ParsedTransactions(\n   id={self.id}, \n   transaction_id='{self.transaction_id}',\n" \
               f"\n   instruction_name='{self.instruction_name}', \n   event_name='{self.event_name}',\n " \
               f"\n   position='{self.position}', \n   token='{self.token}'," \
               f"\n   amount={self.amount}, \n   amount_decimal={self.amount_decimal}, \n   account='{self.account}', " \
               f"\n   bank=`{self.bank}`, \n   signer='{self.signer}', \n   created_at={self.created_at}"


class LendingAccounts(Base):
    __abstract__ = True
    __tablename__ = "lending_accounts"
    __table_args__ = {"schema": SCHEMA_LENDERS}

    id = Column(Integer, primary_key=True, autoincrement=True)
    authority = Column(String, nullable=True)
    address = Column(String, nullable=True)
    group = Column(String, nullable=True)
    action = Column(String, nullable=True)
    block = Column(BigInteger, nullable=True)
    created_at = Column(BigInteger, nullable=False)

    def __repr__(self):
        return f"<LendingAccounts(\n   id={self.id}, \n   authority='{self.authority}', " \
               f"\n   address='{self.address}', \n   group='{self.group}',\n   action='{self.action}'," \
               f"\n   created_at={self.created_at})>"


############### MANGO V2 ################
class MangoParsedEvents(Base):
    __tablename__ = "mango_parsed_transactions_v3"
    id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_id = Column(String, nullable=True)

    event_name = Column(String, nullable=True, index=True)
    event_data = Column(JSONB, nullable=True)

    block = Column(BigInteger, nullable=True, index=True)
    created_at = Column(BigInteger, nullable=True, index=True)
    __table_args__ = (  # type: ignore
        {"schema": SCHEMA_LENDERS},
    )


################ MARGINFI V2 ################################
class MarginfiParsedTransactionsV2(ParsedTransactions):
    __tablename__ = "marginfi_parsed_transactions_v5"
    source = Column(String, nullable=True)
    destination = Column(String, nullable=True)
    marginfi_group = Column(String, nullable = True)
    asset_bank = Column(String, nullable = True)
    liab_bank = Column(String, nullable = True)
    liquidator_marginfi_account = Column(String, nullable = True)
    liquidatee_marginfi_account = Column(String, nullable = True)
    instructed_amount = Column(String, nullable = True)
    __table_args__ = (  # type: ignore
        Index("ix_marginfi_parsed_transactions_v5_transaction_id", "transaction_id"),
        Index("ix_marginfi_parsed_transactions_v5_instruction_name", "instruction_name"),
        Index("ix_marginfi_parsed_transactions_v5_event_name", "event_name"),
        Index("ix_marginfi_parsed_transactions_v5_account", "account"),
        {"schema": SCHEMA_LENDERS},
    )

    def __repr__(self):
        attributes = vars(self)
        # Filter out attributes that are None
        attr_str = "\n".join(f"{key}: {value!r}" for key, value in attributes.items())  # if value is not None)
        return f"MarginfiParsedInstruction(\n{attr_str}\n)"


class MarginfiLendingAccountsV2(LendingAccounts):
    __tablename__ = "marginfi_lending_accounts_v5"
    __table_args__ = (  # type: ignore
        Index("ix_marginfi_lending_accounts_v5_address", "address"),
        Index("ix_marginfi_lending_accounts_v5_group", "group"),
        Index("ix_marginfi_lending_accounts_v5_authority", "authority"),
        {"schema": SCHEMA_LENDERS}
    )

    def __repr__(self):
        attributes = vars(self)
        # Filter out attributes that are None
        attr_str = "\n".join(f"{key}: {value!r}" for key, value in attributes.items()) # if value is not None)
        return f"MarginfiAccount(\n{attr_str}\n)"


class MarginfiBankV2(Base):
    __tablename__ = "marginfi_banks_v5"

    id = Column(Integer, primary_key=True)
    marginfi_group = Column(String)
    admin = Column(String)
    fee_payer = Column(String)
    bank_mint = Column(String)
    bank = Column(String, index=True)
    liquidity_vault_authority = Column(String)
    liquidity_vault = Column(String)
    insurance_vault_authority = Column(String)
    insurance_vault = Column(String)
    fee_vault_authority = Column(String)
    fee_vault = Column(String)
    rent = Column(String)
    __table_args__ = (  # type: ignore
        {"schema": SCHEMA_LENDERS}
    )

    def __repr__(self):
        attributes = vars(self)
        # Filter out attributes that are None
        attr_str = "\n".join(f"{key}: {value!r}" for key, value in attributes.items()) # if value is not None)
        return f"MarginfiBank(\n{attr_str}\n)"

################################## KAMINO V2 ###############
class KaminoParsedTransactionsV2(ParsedTransactions):
    __tablename__ = "kamino_parsed_transactions_v4"
    obligation = Column(String, nullable=True)
    source = Column(String, nullable=True)
    destination = Column(String, nullable=True)
    lending_market = Column(String, nullable = True)
    liquidator = Column(String, nullable = True)
    liquidity_amount = Column(String, nullable = True)
    repay_reserve = Column(String, nullable = True)
    withdraw_reserve = Column(String, nullable = True)
    __table_args__ = (  # type: ignore
        Index("ix_kamino_parsed_transactions_v4_transaction_id", "transaction_id"),
        Index("ix_kamino_parsed_transactions_v4_instruction_name", "instruction_name"),
        Index("ix_kamino_parsed_transactions_v4_event_name", "event_name"),
        Index("ix_kamino_parsed_transactions_v4_account", "account"),
        Index("ix_kamino_parsed_transactions_v4_obligation", "obligation"),
        {"schema": SCHEMA_LENDERS},
    )

    def __repr__(self):
        attributes = vars(self)
        # Filter out attributes that are None
        attr_str = "\n".join(f"{key}: {value!r}" for key, value in attributes.items())  # if value is not None)
        return f"KaminoParsedInstruction(\n{attr_str}\n)"


class KaminoObligationV2(LendingAccounts):
    __tablename__ = "kamino_lending_accounts_v4"
    __table_args__ = (  # type: ignore
        Index("ix_kamino_lending_accounts_v4_address", "address"),
        Index("ix_kamino_lending_accounts_v4_group", "group"),
        Index("ix_kamino_lending_accounts_v4_authority", "authority"),
        {"schema": SCHEMA_LENDERS}
    )

    def __repr__(self):
        attributes = vars(self)
        # Filter out attributes that are None
        attr_str = "\n".join(f"{key}: {value!r}" for key, value in attributes.items())
        return f"KaminoAccount(\n{attr_str}\n)"


class KaminoReserveV2(Base):
    __tablename__ = "kamino_reserves_v4"

    id = Column(Integer, primary_key=True)
    lending_market = Column(String)
    lending_market_owner = Column(String)
    reserve = Column(String)
    reserve_liquidity_mint = Column(String)
    reserve_liquidity_supply = Column(String)
    fee_receiver = Column(String)
    reserve_collateral_mint = Column(String)
    reserve_collateral_supply = Column(String)
    rent = Column(String)
    __table_args__ = (  # type: ignore
        {"schema": SCHEMA_LENDERS}
    )

    def __repr__(self):
        attributes = vars(self)
        # Filter out attributes that are None
        attr_str = "\n".join(f"{key}: {value!r}" for key, value in attributes.items())
        return f"KaminoReserve(\n{attr_str}\n)"


class SolendParsedTransactions(ParsedTransactions):
    __tablename__ = "solend_parsed_transactions_v2"
    source = Column(String, nullable=True)
    destination = Column(String, nullable=True)
    obligation = Column(String, nullable=True)
    authority = Column(String, nullable=True)
    __table_args__ = (
        Index("ix_solend_parsed_transactions_v2_transaction_id", "transaction_id"),
        Index("ix_solend_parsed_transactions_v2_instruction_name", "instruction_name"),
        Index("ix_solend_parsed_transactions_v2_event_name", "event_name"),
        Index("ix_solend_parsed_transactions_v2_obligation", "obligation"),
        Index("ix_solend_parsed_transactions_v2_token", "token"),
        {"schema": SCHEMA_LENDERS},
    )

    def __repr__(self):
        return f"<SolendParsedTransactions(\n   id={self.id}, \n   transaction_id='{self.transaction_id}'," \
               f"\n   instruction_name='{self.instruction_name}', \n   event_name='{self.event_name}', " \
               f"\n   event_num = {self.event_number}" \
               f"\n   position='{self.position}', \n   token='{self.token}'," \
               f"\n   source='{self.source}', \n   destination='{self.destination}'," \
               f"\n   amount={self.amount}, \n   amount_decimal={self.amount_decimal}, \n   account='{self.account}'," \
               f"\n   signer='{self.signer}', \n   created_at={self.created_at}, \n   obligation={self.obligation}" \
               f"\n   bank=`{self.bank}`, \n   authority='{self.authority}"


class SolendObligations(LendingAccounts):  # table to store obligations' data
    __tablename__ = "solend_lending_accounts_v2"
    __table_args__ = (  # type: ignore
        Index("ix_solend_lending_accounts_v2_address", "address"),
        Index("ix_solend_lending_accounts_v2_group", "group"),
        Index("ix_solend_lending_accounts_v2_authority", "authority"),
        {"schema": SCHEMA_LENDERS}
    )


class SolendReserves(Base):  # table to store reserves data
    __tablename__ = 'solend_reserves_v2'

    id = Column(Integer, primary_key=True)
    source_liquidity_pubkey = Column(String)
    destination_collateral_pubkey = Column(String)
    reserve_pubkey = Column(String, index=True)
    reserve_liquidity_mint_pubkey = Column(String)
    reserve_liquidity_supply_pubkey = Column(String)
    config_fee_receiver = Column(String)
    reserve_collateral_mint_pubkey = Column(String)
    reserve_collateral_supply_pubkey = Column(String)
    pyth_product_pubkey = Column(String)
    pyth_price_pubkey = Column(String)
    switchboard_feed_pubkey = Column(String)
    lending_market_pubkey = Column(String)
    lending_market_authority_pubkey = Column(String)
    lending_market_owner_pubkey = Column(String)
    user_transfer_authority_pubkey = Column(String)

    __table_args__ = (  # type: ignore
        {"schema": SCHEMA_LENDERS}
    )


class TransactionsList(Base):
    __abstract__ = True
    __tablename__ = 'hist_transaction_list'
    __table_args__ = {"schema": SCHEMA_LENDERS}
    id = Column(Integer, primary_key=True, autoincrement=True)
    signature = Column(String, index=True)
    block_time = Column(BigInteger)
    is_parsed = Column(Boolean, default=False)


class MarginfiTransactionsListV2(TransactionsList):
    __tablename__ = 'marginfi_hist_transaction_list_v2'
    __table_args__ = (  # type: ignore
        Index('idx_marginfi_transaction_list_v2_signature', 'signature'),
        {"schema": SCHEMA_LENDERS},
    )


class KaminoTransactionsList(TransactionsList):
    __tablename__ = 'kamino_hist_transaction_list_v3'
    __table_args__ = (  # type: ignore
        Index('idx_kamino_transaction_list_signature', 'signature'),
        {"schema": SCHEMA_LENDERS},
    )


class MangoTransactionsList(Base):
    __tablename__ = 'mango_hist_transaction_list_v3'
    id = Column(Integer, primary_key=True, autoincrement=True)
    signature = Column(String)
    block_time = Column(BigInteger)
    is_parsed = Column(Boolean, default=False)

    __table_args__ = (
        Index('idx_mango_transaction_list_signature', 'signature'),
        {"schema": SCHEMA_LENDERS},
    )


class SolendTransactionsList(TransactionsList):
    __tablename__ = 'solend_hist_transaction_list'
    __table_args__ = (  # type: ignore
        Index('idx_solend_transaction_list_signature', 'signature'),
        {"schema": SCHEMA_LENDERS},
    )


class CLOBLiqudity(Base):
    __tablename__ = "orderbook_liquidity"
    __table_args__ = (
        PrimaryKeyConstraint("dex", "pair", "market_address", "timestamp"),
        {"schema": SCHEMA},
    )

    timestamp = Column(BigInteger, nullable=False)
    dex = Column(String, nullable=False)
    pair = Column(String, nullable=False)
    market_address = Column(String, nullable=False)
    bids = Column(PG_ARRAY(Float), nullable=False)
    asks = Column(PG_ARRAY(Float), nullable=False)

    def __repr__(self):
        return (
            "CLOBLiqudity("
            f"timestamp={self.timestamp},"
            f"dex={self.dex},"
            f"pair={self.pair},"
            f"market_address={self.market_address},"
            f"bids={self.bids},"
            f"asks={self.asks})"
        )


class AmmLiquidity(Base):
    __tablename__ = 'amm_liquidity'
    __table_args__ = (
        PrimaryKeyConstraint("dex", "token_x_address", "token_y_address", "market_address", "timestamp"),
        {"schema": SCHEMA},
    )

    timestamp = Column(BigInteger)
    dex = Column(String, nullable=False)
    market_address = Column(String)
    token_x_amount = Column(BigInteger, default=-1)
    token_y_amount = Column(BigInteger, default=-1)
    token_x_address = Column(String)
    token_y_address = Column(String)
    additional_info = Column(String)

    def __repr__(self):
        return (
            "AmmLiqudity("
            f"timestamp={self.timestamp},"
            f"dex={self.dex},"
            f"market_address={self.market_address},"
            f"token_x_amount={self.token_x_amount },"
            f"token_y_amount={self.token_y_amount },"
            f"token_x_address={self.token_x_address},"
            f"token_y_address={self.token_y_address},"
            f"additional_info={self.additional_info},)"
        )


class DexNormalizedLiquidity(Base):
    __tablename__ = 'dex_normalized_liquidity'
    __table_args__ = (
        PrimaryKeyConstraint("dex", "token_x_address", "token_y_address", "market_address", "timestamp"),
        {"schema": SCHEMA},
    )

    timestamp = Column(BigInteger, nullable=False)
    dex = Column(String, nullable=False)
    market_address = Column(String, nullable=False)
    token_x_address = Column(String, nullable=False)
    token_y_address = Column(String, nullable=False)
    bids = Column(PG_ARRAY(Float), nullable=False)
    asks = Column(PG_ARRAY(Float), nullable=False)

    def __repr__(self):
        return (
            "DexNormalizedLiquidity("
            f"timestamp={self.timestamp},"
            f"dex={self.dex},"
            f"market_address={self.market_address},"
            f"token_x_address={self.token_x_address},"
            f"token_y_address={self.token_y_address},"
            f"bids={self.bids},"
            f"asks={self.asks})"
        )


class TokenLendingSupplies(Base):
    __tablename__ = 'token_lending_supplies'
    __table_args__ = (
        PrimaryKeyConstraint("timestamp", "protocol_id", 'vault'),
        {"schema": SCHEMA},
    )

    timestamp = Column(BigInteger, nullable = False)
    protocol_id = Column(String, nullable = False)
    market = Column(String)
    vault = Column(String, nullable = False)
    underlying_mint_address = Column(String, nullable = False)
    deposits_total = Column(DECIMAL, nullable = False)
    lent_total = Column(DECIMAL, nullable = False)
    available_to_borrow = Column(DECIMAL, nullable = False)

    def __repr__(self):
        return (
            "TokenLendingSupplies("
            f"timestamp={self.timestamp},"
            f"protocol_id={self.protocol_id},"
            f"market={self.market},"
            f"vault={self.vault},"
            f"underlying_mint_address={self.underlying_mint_address},"
            f"deposits_total={self.deposits_total},"
            f"lent_total={self.lent_total},"
            f"available_to_borrow={self.available_to_borrow})"
        )


class Protocols(Base):
    __tablename__ = 'protocols'
    __table_args__ = {'schema': SCHEMA_LENDERS}

    id = Column(Integer, primary_key=True)
    public_key = Column(String, unique=True, nullable=False)
    # watershed block, block that we assign as divider of historical and current data,
    # to define what collection stream to use for their collection.
    watershed_block = Column(Integer, nullable=False)
    last_block_collected = Column(Integer, nullable=True)


class LoanStates(Base):
    __abstract__ = True
    __tablename__ = 'loan_states'
    __table_args__ = {"schema": SCHEMA_LENDERS}

    slot = Column(BigInteger, primary_key=True, nullable=False)
    protocol = Column(String, primary_key=True, nullable=False)
    user = Column(String, primary_key=True, nullable=False)
    collateral = Column(JSONB, nullable=False)
    debt = Column(JSONB, nullable=False)
    is_disabled = Column(Boolean, default=False, nullable=False)

    def __repr__(self):
        return (
            "LoanStates("
            f"slot={self.slot},"
            f"protocol={self.protocol},"
            f"user={self.user},"
            f"collateral={self.collateral},"
            f"debt={self.debt})"
        )


class MarginfiLoanStates(LoanStates):
    __tablename__ = "marginfi_loan_states"


class KaminoLoanStates(LoanStates):
    __tablename__ = "kamino_loan_states"


class MangoLoanStates(LoanStates):
    __tablename__ = "mango_loan_states"


class SolendLoanStates(LoanStates):
    __tablename__ = "solend_loan_states"


class MarginfiLoanStatesEA(LoanStates):
    __tablename__ = "marginfi_loan_states_easy_access"


class KaminoLoanStatesEA(LoanStates):
    __tablename__ = "kamino_loan_states_easy_access"


class MangoLoanStatesEA(LoanStates):
    __tablename__ = "mango_loan_states_easy_access"


class SolendLoanStatesEA(LoanStates):
    __tablename__ = "solend_loan_states_easy_access"


class HealthRatio(Base):
    __abstract__ = True
    __tablename__ = "health_ratios"
    __table_args__ = {"schema": SCHEMA_LENDERS}
    slot = Column(BigInteger, primary_key=True, nullable=False)
    last_update = Column(BigInteger, index=True, nullable=True)
    user = Column(String, primary_key=True, nullable=False)
    health_factor = Column(String, index=True, nullable=True)
    std_health_factor = Column(String, index=True, nullable=True)
    collateral = Column(String, nullable=False)
    risk_adjusted_collateral = Column(String, nullable=False)
    debt = Column(String, nullable=False)
    risk_adjusted_debt = Column(String, nullable=False)
    timestamp = Column(BigInteger, default=lambda: int(time.time()), nullable=False)


class MangoHealthRatio(HealthRatio):
    __tablename__ = "mango_health_ratios"
    __table_args__ = {"schema": SCHEMA_LENDERS}
    protocol = Column(String, default='mango', nullable=False)


class MangoHealthRatioEA(HealthRatio):
    __tablename__ = "mango_health_ratios_easy_access"
    __table_args__ = {"schema": SCHEMA_LENDERS}
    protocol = Column(String, default='mango', nullable=False)


class MarginfiHealthRatio(HealthRatio):
    __tablename__ = "marginfi_health_ratios"
    __table_args__ = {"schema": SCHEMA_LENDERS}
    protocol = Column(String, default='marginfi', nullable=False)


class MarginfiHealthRatioEA(HealthRatio):
    __tablename__ = "marginfi_health_ratios_easy_access"
    __table_args__ = {"schema": SCHEMA_LENDERS}
    protocol = Column(String, default='marginfi', nullable=False)


class SolendHealthRatio(HealthRatio):
    __tablename__ = "solend_health_ratios"
    __table_args__ = {"schema": SCHEMA_LENDERS}
    protocol = Column(String, default='solend', nullable=False)


class SolendHealthRatioEA(HealthRatio):
    __tablename__ = "solend_health_ratios_easy_access"
    __table_args__ = {"schema": SCHEMA_LENDERS}
    protocol = Column(String, default='solend', nullable=False)


class KaminoHealthRatio(HealthRatio):
    __tablename__ = "kamino_health_ratios"
    __table_args__ = {"schema": SCHEMA_LENDERS}
    protocol = Column(String, default='kamino', nullable=False)


class KaminoHealthRatioEA(HealthRatio):
    __tablename__ = "kamino_health_ratios_easy_access"
    __table_args__ = {"schema": SCHEMA_LENDERS}
    protocol = Column(String, default='kamino', nullable=False)


class MarginfiLiquidableDebts(Base):
    __tablename__ = "marginfi_liquidable_debts"
    __table_args__ = {"schema": SCHEMA_LENDERS}

    slot = Column(BigInteger, primary_key=True, nullable=False)
    protocol = Column(String, primary_key=True, nullable=False)
    collateral_token = Column(String, primary_key=True, nullable=False)
    debt_token = Column(String, primary_key=True, nullable=False)
    collateral_token_price = Column(DECIMAL, primary_key=True, nullable=False)
    amount = Column(DECIMAL, nullable=False)

    def __repr__(self):
        return (
            "MarginfiLiquidableDebts("
            f"slot={self.slot},"
            f"protocol={self.protocol},"
            f"collateral_token={self.collateral_token},"
            f"debt_token={self.debt_token},"
            f"collateral_token_price={self.collateral_token_price},"
            f"amount={self.amount})"
        )


class KaminoLiquidableDebts(Base):
    __tablename__ = "kamino_liquidable_debts"
    __table_args__ = {"schema": SCHEMA_LENDERS}

    slot = Column(BigInteger, primary_key=True, nullable=False)
    protocol = Column(String, primary_key=True, nullable=False)
    collateral_token = Column(String, primary_key=True, nullable=False)
    debt_token = Column(String, primary_key=True, nullable=False)
    collateral_token_price = Column(DECIMAL, primary_key=True, nullable=False)
    amount = Column(DECIMAL, nullable=False)

    def __repr__(self):
        return (
            "KaminoLiquidableDebts("
            f"slot={self.slot},"
            f"protocol={self.protocol},"
            f"collateral_token={self.collateral_token},"
            f"debt_token={self.debt_token},"
            f"collateral_token_price={self.collateral_token_price},"
            f"amount={self.amount})"
        )


class MangoLiquidableDebts(Base):
    __tablename__ = "mango_liquidable_debts"
    __table_args__ = {"schema": SCHEMA_LENDERS}

    slot = Column(BigInteger, primary_key=True, nullable=False)
    protocol = Column(String, primary_key=True, nullable=False)
    collateral_token = Column(String, primary_key=True, nullable=False)
    debt_token = Column(String, primary_key=True, nullable=False)
    collateral_token_price = Column(DECIMAL, primary_key=True, nullable=False)
    amount = Column(DECIMAL, nullable=False)

    def __repr__(self):
        return (
            "MangoLiquidableDebts("
            f"slot={self.slot},"
            f"protocol={self.protocol},"
            f"collateral_token={self.collateral_token},"
            f"debt_token={self.debt_token},"
            f"collateral_token_price={self.collateral_token_price},"
            f"amount={self.amount})"
        )


class SolendLiquidableDebts(Base):
    __tablename__ = "solend_liquidable_debts"
    __table_args__ = {"schema": SCHEMA_LENDERS}

    slot = Column(BigInteger, primary_key=True, nullable=False)
    protocol = Column(String, primary_key=True, nullable=False)
    collateral_token = Column(String, primary_key=True, nullable=False)
    debt_token = Column(String, primary_key=True, nullable=False)
    collateral_token_price = Column(DECIMAL, primary_key=True, nullable=False)
    amount = Column(DECIMAL, nullable=False)

    def __repr__(self):
        return (
            "SolendLiquidableDebts("
            f"slot={self.slot},"
            f"protocol={self.protocol},"
            f"collateral_token={self.collateral_token},"
            f"debt_token={self.debt_token},"
            f"collateral_token_price={self.collateral_token_price},"
            f"amount={self.amount})"
        )


class CallToActions(Base):
    __tablename__ = "call_to_actions"
    __table_args__ = {"schema": SCHEMA_LENDERS}

    timestamp = Column(BigInteger, primary_key=True, nullable=False)
    collateral_token = Column(String, primary_key=True, nullable=False)
    debt_token = Column(String, primary_key=True, nullable=False)
    message = Column(String, nullable=False)

    def __repr__(self):
        return (
            "CallToActions("
            f"timestamp={self.timestamp},"
            f"collateral_token={self.collateral_token},"
            f"debt_token={self.debt_token},"
            f"message={self.message},"
        )


if __name__ == "__main__":
    # create the database engine
    ENGINE = create_engine(CONN_STRING)
    # create schema
    connection = ENGINE.raw_connection()
    cursor = connection.cursor()
    cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA};")

    Base.metadata.create_all(ENGINE)

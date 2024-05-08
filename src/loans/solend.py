import decimal
import logging
import warnings
from dataclasses import dataclass
from typing import Any, List, Dict

import numpy
import pandas
import requests

import db
import src.database
import src.loans.helpers
import src.loans.types
import src.loans.state
import src.solend_maps

from src.prices import get_prices_for_tokens

from src.protocols.dexes.amms.utils import get_tokens_address_to_info_map
# Ignore all warnings
warnings.filterwarnings('ignore')


# Keys are values of the "event_name" column in the database, values are the respective method names.
EVENTS_METHODS_MAPPING: dict[str, str] = {
    'borrow_obligation_liquidity': 'process_borrowing_event',
    'deposit_obligation_collateral': 'process_deposit_event',
    # 'deposit_reserve_liquidity': 'process_deposit_event',  # do not affect collateral or debt
    'deposit_reserve_liquidity_and_obligation_collateral': 'process_deposit_event',
    'liquidate_obligation': 'process_liquidation_event',
    'liquidate_obligation_and_redeem_reserve_collateral': 'process_liquidation_event',
    # 'redeem_reserve_collateral': 'process_withdrawal_event',  # do not affect collateral or debt
    'repay_obligation_liquidity': 'process_repayment_event',
    'withdraw_obligation_collateral': 'process_withdrawal_event',
    'withdraw_obligation_collateral_and_redeem_reserve_liquidity': 'process_withdrawal_event',
    # 'flash_borrow_reserve_liquidity': '',
    # 'flash_repay_reserve_liquidity': '',
}

WAD = 10**18


def get_events(start_block_number: int = 0) -> pandas.DataFrame:
    return src.loans.helpers.get_events(
        table='lenders.solend_parsed_transactions_v2',
        event_names=tuple(EVENTS_METHODS_MAPPING),
        start_block_number=start_block_number,
        event_column='instruction_name'
    )


@dataclass
class SolendCollateralPosition:
    reserve: str
    mint: str
    amount: float
    decimals: int | None = None
    ltv: float | None = None
    c_token_exchange_rate: float = ''
    underlying_asset_price_wad: str = ''
    liquidation_threshold: float | None = None
    liquidation_bonus: float | None = None

    def market_value(self):
        """ Position market value, USD """
        assert self.decimals is not None, f"Missing collateral mint decimals for {self.mint}"
        assert self.ltv is not None, f"Missing loan to value for {self.mint}"
        assert self.c_token_exchange_rate, f"Missing collateral token exchange rate: " \
                                           f"{self.c_token_exchange_rate} for {self.mint}"
        assert self.underlying_asset_price_wad, f"Missing asset price: {self.underlying_asset_price_wad} for {self.mint}"
        return (
            self.amount
            * float(self.c_token_exchange_rate)
            * int(self.underlying_asset_price_wad)
            / self.decimals
            / WAD
            * self.ltv
        )


@dataclass
class SolendDebtPosition:
    reserve: str
    mint: str
    raw_amount: float
    decimals: int | None = None
    cumulative_borrow_rate_wad: str = ''
    underlying_asset_price_wad: str = ''
    weight: float | None = None

    def market_value(self):
        """ Position market value, USD """
        assert self.decimals is not None, f"Missing collateral mint decimals for {self.reserve}"
        assert self.cumulative_borrow_rate_wad, f"Missing cumBorrowRate: {self.cumulative_borrow_rate_wad}" \
                                                f" for {self.reserve}"
        assert self.weight, f"Missing borrow rate: {self.weight} for {self.reserve}"
        assert self.underlying_asset_price_wad, f"Missing asset price: {self.underlying_asset_price_wad} for {self.reserve}"
        return (
            self.raw_amount
            * int(self.cumulative_borrow_rate_wad) / WAD
            * int(self.underlying_asset_price_wad) / WAD
            / self.decimals
            * self.weight
        )


class SolendLoanEntity:
    """ A class that describes the Solend loan entity. """

    def __init__(self, obligation: str, slot: int) -> None:
        self.collateral: List[SolendCollateralPosition] = list()
        self.debt: List[SolendDebtPosition] = list()
        self.obligation = obligation
        self.last_updated = slot

    @property
    def is_zero_debt(self):
        if not self.debt:
            return True
        return all([position.raw_amount == 0 for position in self.debt])

    @property
    def is_zero_deposit(self):
        if not self.collateral:
            return True
        return all([position.amount == 0 for position in self.collateral])

    def health_ratio(self) -> str:
        """
        Compute standardized health ratio:
            std_health_ratio = risk adjusted collateral / risk adjusted debt
        :return:
        """
        if self.is_zero_debt:
            return 'inf'
        if self.is_zero_deposit:
            return '0'
        deposited_value = sum([position.market_value() for position in self.collateral])
        borrowed_value = sum([position.market_value() for position in self.debt])
        return str(round(deposited_value / borrowed_value, 8))

    def get_unique_reserves(self) -> List[str]:
        reserves = []
        if self.debt:
            reserves.extend([position.reserve for position in self.debt])
        if self.collateral:
            reserves.extend([position.reserve for position in self.collateral])
        return list(set(reserves))

    def update_positions_from_reserve_config(self, reserve_configs: Dict[str, Any]):
        """ Fill missing data in position object with parameters from reserve configs. """
        # Update collateral positions
        for collateral in self.collateral:
            reserve_config = reserve_configs.get(collateral.reserve)
            if reserve_config:
                collateral.decimals = reserve_config['reserve']['liquidity']['mintDecimals']
                collateral.ltv = reserve_config['reserve']['config']['loanToValueRatio'] / 100
                collateral.c_token_exchange_rate = reserve_configs[collateral.reserve]['cTokenExchangeRate']
                collateral.underlying_asset_price_wad = reserve_config['reserve']['liquidity']['marketPrice']
                collateral.liquidation_threshold = reserve_config['reserve']['config']['liquidationThreshold'] / 100
                collateral.liquidation_bonus = reserve_config['reserve']['config']['liquidationBonus'] / 100

        # Update debt positions
        for debt in self.debt:
            reserve_config = reserve_configs.get(debt.reserve)
            if reserve_config:
                debt.decimals = reserve_config['reserve']['liquidity']['mintDecimals']
                debt.cumulative_borrow_rate_wad = reserve_config['reserve']['liquidity']['cumulativeBorrowRateWads']
                debt.underlying_asset_price_wad = reserve_config['reserve']['liquidity']['marketPrice']
                debt.weight = reserve_config['reserve']['config']['borrowWeight']


class SolendState(src.loans.state.State):
    """
    A class that describes the state of all MarginFi loan entities. It implements methods for correct processing of
    every relevant event.
    """
    EVENTS_METHODS_MAPPING: dict[str, str] = EVENTS_METHODS_MAPPING

    def __init__(
        self,
        verbose_users: set[str] | None = None,
        initial_loan_states: pandas.DataFrame = pandas.DataFrame(),
        slot: int = 0
    ) -> None:
        self.where = 0
        self.reserve = SolendState._fetch_reserves()  # TODO drop
        self.reserve_configs = dict()
        super().__init__(
            protocol='solend',
            loan_entity_class=SolendLoanEntity,
            verbose_users=verbose_users,
            initial_loan_states=initial_loan_states,
        )

    def set_initial_loan_states(self, initial_loan_states: pandas.DataFrame) -> None:
        # Iterate over each row in the DataFrame
        self.last_slot = initial_loan_states.slot.max()
        for index, row in initial_loan_states.iterrows():
            obligation = row['user']
            last_update = row['slot']

            if obligation not in self.loan_entities:
                self.loan_entities[obligation] = SolendLoanEntity(obligation, last_update)
            # Process collateral positions
            collateral_data = row['collateral']
            for mint, collateral_info in collateral_data.items():
                if collateral_info:  # Check if there is data present for the collateral
                    new_collateral_position = SolendCollateralPosition(
                        reserve=collateral_info['reserve'],
                        mint=mint,
                        amount=collateral_info['amount'],
                    )
                    self.loan_entities[obligation].collateral.append(new_collateral_position)

            # Process debt positions
            debt_data = row['debt']
            for mint, debt_info in debt_data.items():
                if debt_info:  # Check if there is data present for the debt
                    new_debt_position = SolendDebtPosition(
                        reserve=debt_info['reserve'],
                        mint=mint,
                        raw_amount=debt_info['rawAmount'],
                    )
                    self.loan_entities[obligation].debt.append(new_debt_position)

    def _get_reserve_configs(self):
        reserve_addresses = {
            reserve
            for loan_entity in self.loan_entities.values()
            for reserve in loan_entity.get_unique_reserves()
            if not loan_entity.is_zero_debt
        }
        ids = ",".join(reserve_addresses)
        url = f'https://api.solend.fi/v1/reserves/?ids={ids}'

        response = requests.get(url, timeout=15)
        self.reserve_configs = {
            reserve['reserve']['address']: reserve
            for reserve in response.json()['results']
        }

    def save_health_ratios(self):
        if not self.reserve_configs:
            self._get_reserve_configs()
        with db.get_db_session() as session:
            for loan_entity in self.loan_entities.values():
                loan_entity.update_positions_from_reserve_config(self.reserve_configs)
                new_health_ratio = db.SolendHealthRatio(
                    slot=self.last_slot,
                    user=loan_entity.obligation,
                    health_ratio=loan_entity.heath_ratio()
                )
                session.add(new_health_ratio)
            session.commit()


    @staticmethod
    def _fetch_reserves() -> pandas.DataFrame:
        connection = src.database.establish_connection()
        reserves = pandas.read_sql(
            sql=f"""
                select 
                    reserve_pubkey,
                    reserve_liquidity_mint_pubkey, 
                    reserve_liquidity_supply_pubkey,
                    reserve_collateral_mint_pubkey,
                    reserve_collateral_supply_pubkey
                from lenders.solend_reserves_v2;
                """,
            con=connection,
        )
        connection.close()
        return reserves

    def get_token_for_liquidity_supply(self, reserve_pubkey):
        return self.reserves[
            self.reserves['reserve_liquidity_supply_pubkey'] == reserve_pubkey
        ].reserve_liquidity_mint_pubkey.values[0]

    def get_token_for_collateral_supply(self, reserve_pubkey):
        return self.reserves[
            self.reserves['reserve_collateral_supply_pubkey'] == reserve_pubkey
        ].reserve_collateral_mint_pubkey.values[0]

    def get_reserve_for_liquidity_supply(self, reserve_pubkey):
        return self.reserves[
            self.reserves['reserve_liquidity_supply_pubkey'] == reserve_pubkey
        ].reserve_pubkey.values[0]

    def get_reserve_for_collateral_supply(self, reserve_pubkey):
        return self.reserves[
            self.reserves['reserve_collateral_supply_pubkey'] == reserve_pubkey
        ].reserve_pubkey.values[0]

    def get_unprocessed_events(self) -> None:
        self.unprocessed_events = src.loans.helpers.get_events(
            table='lenders.solend_parsed_transactions_v2',
            event_names=tuple(EVENTS_METHODS_MAPPING),
            event_column='instruction_name',
            start_block_number=self.last_slot + 1,
        )

    def process_event(self, event: pandas.DataFrame) -> None:
        min_slot = event["block"].min()

        assert min_slot >= self.last_slot
        event_name = event["instruction_name"].iloc[0]
        assert event["instruction_name"].nunique() == 1  # TODO: redundant?
        try:  # TODO
            getattr(self, self.EVENTS_METHODS_MAPPING[event_name])(event=event)
        except:
            logging.error(f'{event_name} {event}')  # TODO
            getattr(self, self.EVENTS_METHODS_MAPPING[event_name])(event=event)
        self.last_slot = min_slot

        if self.last_slot > self.where * 1000000:
            self.where = (self.last_slot - self.last_slot % 1000000) / 1000000 + 1
            logging.info("Processing {} slot.".format(self.last_slot))

    def process_deposit_event(self, event: pandas.DataFrame) -> None:
        transfer_event = event[event['event_name'].isin([
            'transfer-sourceCollateralPubkey-destinationCollateralPubkey',
            'transfer-userCollateralPubkey-destinationDepositCollateralPubkey'
        ])]
        assert len(transfer_event) > 0
        for _, individual_transfer_event in transfer_event.iterrows():
            user = individual_transfer_event["obligation"]
            token = individual_transfer_event["destination"]
            amount = decimal.Decimal(str(individual_transfer_event["amount"]))
            assert amount >= 0
            self.loan_entities[user].collateral.increase_value(token=token, value=amount)
            if user in self.verbose_users:
                logging.info(
                    "In block number = {}, user = {} deposited amount = {} of token = {}.".format(
                        individual_transfer_event["block"],
                        user,
                        amount,
                        token,
                    )
                )

    def process_withdrawal_event(self, event: pandas.DataFrame) -> None:
        transfer_event = event[
            event['event_name'] == 'transfer-sourceCollateralPubkey-destinationCollateralPubkey'
            ]
        assert len(transfer_event) > 0  # TODO
        for _, individual_transfer_event in transfer_event.iterrows():
            user = individual_transfer_event["obligation"]
            token = individual_transfer_event["source"]
            amount = decimal.Decimal(str(individual_transfer_event["amount"]))
            assert amount >= 0
            self.loan_entities[user].collateral.increase_value(token=token, value=-amount)
            if user in self.verbose_users:
                logging.info(
                    "In block number = {}, user = {} withdrew amount = {} of token = {}.".format(
                        individual_transfer_event["block"],
                        user,
                        amount,
                        token,
                    )
                )

    def process_borrowing_event(self, event: pandas.DataFrame) -> None:
        transfer_event = event[event['event_name'].str.startswith('transfer-sourceLiquidityPubkey-')]
        assert len(transfer_event) > 0
        for _, individual_transfer_event in transfer_event.iterrows():
            user = individual_transfer_event["obligation"]
            token = individual_transfer_event["source"]
            amount = decimal.Decimal(str(individual_transfer_event["amount"]))
            assert amount >= 0
            self.loan_entities[user].debt.increase_value(token=token, value=amount)
            if user in self.verbose_users:
                logging.info(
                    "In block number = {}, user = {} borrow / paid fee = {} of token = {}. \n current debt = {}".format(
                        individual_transfer_event["block"],
                        user,
                        amount,
                        token,
                        self.loan_entities[user].debt[token]
                    )
                )

    def process_repayment_event(self, event: pandas.DataFrame) -> None:
        transfer_event = event[event['event_name'] == 'transfer-sourceLiquidityPubkey-destinationLiquidityPubkey']
        assert len(transfer_event) > 0  # TODO
        # return
        for _, individual_transfer_event in transfer_event.iterrows():
            user = individual_transfer_event["obligation"]
            token = individual_transfer_event["destination"]
            amount = decimal.Decimal(str(individual_transfer_event["amount"]))
            assert amount >= 0
            self.loan_entities[user].debt.increase_value(token=token, value=-amount)
            paid_interest = 0

            if self.loan_entities[user].debt[token] < 0:
                paid_interest = -self.loan_entities[user].debt[token]
                amount = amount - paid_interest
                self.loan_entities[user].debt[token] += paid_interest
            if user in self.verbose_users:
                logging.info(
                    "In block number = {}, user = {} repayed amount = {} of "
                    "token = {}, \n paid interest = {} \n current debt = {}.".format(
                        individual_transfer_event["block"],
                        user,
                        amount,
                        token,
                        paid_interest,
                        self.loan_entities[user].debt[token]
                    )
                )

    def process_liquidation_event(self, event: pandas.DataFrame) -> None:
        # withdraw collateralprocess_unprocessed_events()
        transfer_event = event[
            event['event_name'] == 'transfer-withdrawReserveCollateralSupplyPubkey-destinationCollateralPubkey']
        assert len(transfer_event) > 0
        for _, individual_transfer_event in transfer_event.iterrows():
            user = individual_transfer_event["obligation"]
            assert user in self.loan_entities  # TODO
            # TODO: The very first liquidation events do not change the collateral.
            collateral_token = individual_transfer_event["source"]
            collateral_amount = decimal.Decimal(str(individual_transfer_event["amount"]))
            assert collateral_amount >= 0
            self.loan_entities[user].collateral.increase_value(token=collateral_token, value=-collateral_amount)

        # repay liquidity
        transfer_event = event[event['event_name'] == 'transfer-sourceLiquidityPubkey-repayReserveLiquiditySupplyPubkey']
        assert len(transfer_event) > 0  # TODO
        for _, individual_transfer_event in transfer_event.iterrows():
            user = individual_transfer_event["obligation"]
            assert user in self.loan_entities  # TODO
            # TODO: The very first liquidation events do not change the collateral.
            debt_token = individual_transfer_event["destination"]
            debt_amount = decimal.Decimal(str(individual_transfer_event["amount"]))
            paid_interest = 0
            assert debt_amount >= 0
            self.loan_entities[user].debt.increase_value(token=debt_token, value=-debt_amount)
            if self.loan_entities[user].debt[debt_token] < 0:
                paid_interest = -self.loan_entities[user].debt[debt_token]
                debt_amount -= paid_interest
                self.loan_entities[user].debt[debt_token] += paid_interest

        if user in self.verbose_users:
            logging.info(
                "In block number = {}, debt of raw amount = {} of token = {} and collateral of raw amount = {} of "
                "token = {} of user = {} were liquidated. \n paid interest = {} \n current debt = {}".format(
                    event["block"].iloc[0],
                    debt_amount,
                    debt_token,
                    collateral_amount,
                    collateral_token,
                    user,
                    paid_interest,
                    self.loan_entities[user].debt[debt_token]
                )
            )


def compute_liquidable_debt_at_price(
        state,
        loan_states: pandas.DataFrame,
        target_collateral_token_price: decimal.Decimal,
        collateral_token: str,
        debt_token: str,
        debt_data: list,
        collateral_data: list
) -> decimal.Decimal:
    # get current token price and liquidation params
    account = next(i for i in collateral_data if i['underlying_token'] == collateral_token)
    collateral_token_price = account['price']
    liquidation_threshold = account['config']['reserve']['config']['liquidationThreshold'] / 100
    liquidation_bonus = account['config']['reserve']['config']['liquidationBonus'] / 100
    # compute price ratio
    price_ratio = target_collateral_token_price / collateral_token_price

    # re-adjust price of collateral
    for supply_data in collateral_data:
        if supply_data['underlying_token'] == collateral_token:
            related_collateral_column = f"collateral_usd_{supply_data['supply_account']}"
            if related_collateral_column in loan_states.columns:
                loan_states[related_collateral_column] = loan_states[related_collateral_column] * price_ratio
                # re-adjust price of debt
    for supply_data in debt_data:
        if supply_data['token'] == collateral_token:
            related_debt_column = f"debt_usd_{supply_data['supply_account']}"
            if related_debt_column in loan_states.columns:
                loan_states[related_debt_column] = loan_states[related_debt_column] * price_ratio

    loan_states['total_collateral_usd'] = loan_states[[x for x in loan_states.columns if 'collateral_usd_' in x]].sum(
        axis=1)
    loan_states['total_debt_usd'] = loan_states[[x for x in loan_states.columns if 'debt_usd_' in x]].sum(axis=1)

    loan_states['loan_to_value'] = loan_states['total_debt_usd'] / loan_states['total_collateral_usd']
    loan_states['liquidable'] = loan_states['loan_to_value'] > liquidation_threshold

    # 20% of the debt value is liquidated.
    liquidable_debt_ratio = 0.2 + liquidation_bonus

    affected_debt_supply_accounts = [sa['supply_account'] for sa in debt_data if sa['token'] == debt_token]
    affected_debt_columns = [f"debt_usd_{account}" for account in affected_debt_supply_accounts]

    loan_states['affected_debt'] = loan_states[[
        x for x in loan_states.columns if x in affected_debt_columns
    ]].sum(axis=1)
    loan_states['debt_to_be_liquidated'] = liquidable_debt_ratio * loan_states['affected_debt'] * loan_states[
        'liquidable']

    return loan_states['debt_to_be_liquidated'].sum()


def get_reserves() -> pandas.DataFrame:
    connection = src.database.establish_connection()
    reserves = pandas.read_sql(
        sql=f"""
            select 
                reserve_pubkey,
                reserve_liquidity_mint_pubkey, 
                reserve_liquidity_supply_pubkey,
                reserve_collateral_mint_pubkey,
                reserve_collateral_supply_pubkey
            from lenders.solend_reserves_v2;
            """,
        con=connection,
    )
    connection.close()
    return reserves


def get_solend_user_stats_df(loan_states: pandas.DataFrame) -> pandas.DataFrame:
    reserves = get_reserves()
    r = {i['reserve_collateral_supply_pubkey']: i['reserve_liquidity_mint_pubkey'] for i in reserves.to_dict('records')}
    prices = get_prices_for_tokens([i for i in r.values()])

    collateral_tokens = {token for collateral in loan_states['collateral'] for token in collateral}
    debt_tokens = {token for debt in loan_states['debt'] for token in debt}
    tokens_info = get_tokens_address_to_info_map()


    for token in collateral_tokens:
        loan_states[f'collateral_{token}'] = loan_states['collateral'].apply(
            lambda x: x[token] if token in x else decimal.Decimal('0')
        )
    for token in debt_tokens:
        loan_states[f'debt_{token}'] = loan_states['debt'].apply(
            lambda x: x[token] if token in x else decimal.Decimal('0')
        )


    for token in collateral_tokens:
        if not token in token_to_ltv:
            continue
        if not r.get(token):
            continue
        mint = r[token]

        if not tokens_info.get(mint):
            # print('no info')
            continue

        ltv = token_to_ltv[token]

        decimals = tokens_info[mint]['decimals']
        loan_states[f'collateral_usd_{token}'] = (
            loan_states[f'collateral_{token}'].astype(float)
            / (10**decimals)
            * prices[mint]
        )
        
        loan_states[f'risk_adj_collateral_usd_{token}'] = (
            loan_states[f'collateral_{token}'].astype(float)
            / (10**decimals)
            * (ltv/100)
            * prices[mint]
        )

    for token in debt_tokens:
        if not src.solend_maps.debt_to_mint.get(token):
            continue
        mint = src.solend_maps.debt_to_mint[token]

        if not tokens_info.get(mint):
            continue

        decimals = tokens_info[mint]['decimals']
        loan_states[f'debt_usd_{token}'] = (
            loan_states[f'debt_{token}'].astype(float)
            / (10**decimals)
            * prices[mint]
        )
        
        loan_states[f'risk_adj_debt_usd_{token}'] = (
            loan_states[f'debt_{token}'].astype(float)
            / (10**decimals)
            * prices[mint]
        )

    loan_states['risk_adj_debt_usd'] = loan_states[[i for i in loan_states.columns if i.startswith('risk_adj_debt_usd_')]].sum(axis=1)
    loan_states['debt_usd'] = loan_states[[i for i in loan_states.columns if i.startswith('debt_usd_')]].sum(axis=1)

    loan_states['risk_adj_collateral_usd'] = loan_states[[i for i in loan_states.columns if i.startswith('risk_adj_collateral_usd_')]].sum(axis=1)
    loan_states['collateral_usd'] = loan_states[[i for i in loan_states.columns if i.startswith('collateral_usd_')]].sum(axis=1)

    loan_states['std_health'] = (loan_states['risk_adj_collateral_usd'] / loan_states['risk_adj_debt_usd']).fillna(numpy.inf)

    wanted_cols = [
        'protocol', 
        'user', 
        'std_health',
        'collateral_usd', 
        'risk_adj_collateral_usd',
        'debt_usd', 
        'risk_adj_debt_usd',
        'collateral',
        'debt',
    ]
    return loan_states[wanted_cols]


token_to_ltv = {'DGvRjXUL4N12eaYGJy9Pkcn2Rpmda4qhhsDXNivWfUce': 89,
 'EdsRBHJM7pfbayMFGnLGsvtqekDpcbrNwZDk1TSrXL3X': 80,
 'BEVqR772yceYJmMCYPyXHCNm163Zm77ae4NgAewqU5F7': 90,
 'AXUhJpZk7ZRyuH28cmiDxmmNx4nxZ2qEvqSeuuioP41g': 85,
 '8yM4CwKeur9Teso8zPtDoFkT7GizFL7q4DSzRuoRAmD1': 80,
 'Fa9kujq845ygegvezeGdvHJyiQW7rf1ZBiN9BLxyr7Wt': 0,
 'CvG6hmwZA6gUF7CKFpuhaXZsX558NjQN1kSGLdRrrVGX': 0,
 'CKHC5VNd9UXEwFoj8wtnBf36jes8iA6DpLpuMH4jC1K5': 75,
 '3VBrZBNPVG2tvoHsdWiKpRAt263krTHs38XwVy3XqxdM': 80,
 '8py8trSwRva7HXQ1x2q5Bgx2rkDMwXfFNt7qVSeYRcKk': 50,
 '7YCzReVwt9W6X3hX2Hq8w9cZeVeNBkjtP6FioA4gjkt2': 0,
 '7vWiQYodsuFBPZ9aFY3EQM5LXK8hD43kFeVRCNKdjxBn': 75,
 '97AFq1qdq5rWyyaQFybFCt2bkLSk5VWuC15LPbeFZZKV': 75,
 '8iRqYc7V2yW3SgmDHufeXxRbKxnqxajGT7oevgytkATa': 75,
 'C9UNmVdnV8vL2p8b39GNUdwaCYgkAXYVMkrorcw2YgC': 0,
 '7XBFNATnNXU4tAYqKg4CVCHNHu7fQ1Ln63vcCSc3bLDX': 0,
 'BPhX4N7r9z9HQTAVDyfvVcYWbjsWiL476vsWAYYFh5Lg': 0,
 '4EZBWKpBSnfwCPoqBQEaR4LXFp4TsigRLkvjg6Musfx4': 35,
 '8EkjzGAdPce45ss5WZ5rfgs22jE9qoTEZXraKEKRLwsu': 90,
 '2Yv6ZgZ9ccV8bCYD7T5t2kcAQYRbukMKha6NiPQ8cFAT': 0,
 '6Lr61RSmn8NZ5cEDmT94F7CV6vpQFo3wFFJw7F5ougcv': 45,
 '3GynM9cRtZsZ2s1SyoAuSgTDjx8ANcVZJXZayuWZbMpd': 59,
 'CeuaEJwGcLrAbUGaf3U3pyGpWyWujCTbVxc7bWJwBZnw': 0,
 '6jiE8jfymvrHKVnphSQhPy4HCK9qq2MUbpaQB8KHQCNb': 0,
 'BmY62w3HydkSuWX62X9znJ2iUwDU2VST3D8VNeQ9kx5T': 75,
 'BdjGeJQNEZhCLyW89RNWgxkn3hwRMsAxncc29QNuHvRf': 75,
 '4FYcSJbAx2WPAAtowfnTrkj3JNR9oQVinq9eVABFkTqX': 35,
 '9kxajX2rEZqHbHcBEqvUJmCmgNTs1oR25DP5LZmFEhEX': 35,
 'CLGLazK39414VobGs4MsidgbPfPvVmpLb73d8o91D5Pc': 75,
 '2Hn98Yby15Eqy8r8Xr6a26bkrHccRPLvqsN8dNTgboYL': 0,
 'DLMUG8bytjYT9RADJq6tDnR9vwJZ2QKD4iQqx3RGJK9n': 75,
 '5Xai7Eam7UHkgrok2Gsp2NC8NNeHJNnqGZJ3V66brn4': 0,
 'H4Z2n1wamM8Q3tmyimLn62VwFzjWu6CesnQqE12ZVNWA': 0,
 'D52HyVBEMWy2WBptV5zsPuYS8W8C62gYjYKuVzaK1ruM': 0,
 '8rxBxWpQv84mFZb71AaSdmTgjGq9TByZ3A4h1ouokUci': 89,
 'AJSkG29hrcLB6omKbzGknLNJd9wGnABdcvcj6Jbeb5ti': 65,
 'J4n1StDu99oUuW5w4pS16hbmj29xzn4e1FBAsaKcCyyf': 40,
 'GbNL16p5Pc4zkfTuthoSiHJNbVRc3qvtYyNPtDpPHvtC': 50,
 'H1xB9rW6W21dRah2KD1Fi6eusyP1YCStshMN7LcQwa9g': 35,
 '8YGu5iFMKHau2XjVBwKiyPjY2rYpbaLMyxfVhM916jPd': 75,
 '79nrG41BqmncnZDQ4sZo4aE8asu8EiJjRhsQfoGQUxfr': 35,
 '5Achj9wC4Dupx28sogjPrwHP9PUyMeKX5U8fJBgPmHS6': 75,
 '8K62hNGK6qFxrGshYVbmMPbB7gPApCz9BZaBj1XL9c2J': 50,
 'FG7yuhS6udX8v2LQYxqwpcsdC2J1pUREoGrRYsQjr1uh': 63,
 '4aqnTF7A8QoEG8PUn7JvBLCkLQCwaNYb1uVNqc8gW6JM': 35,
 'FNSjtrxho4v3WAfZmC2pCC9EeHbYGUhD3pUdTt3duQ9V': 85,
 '5YjjhzNHQoBdisyMrxhmt2nwy8yoQ9zA7o2ruUZg894g': 75,
 '8vy2oJnpfYRK1B52ZgcuiVuxjawtfXrn7TGD1soCtuvA': 35,
 'HbMugfk2UDNoCiBUqgXdPu75ksMZHvkJjRZ8YKrcPwz2': 0,
 '6uEjo58ecepRyYnKRLdAMRn8ic3oJJxnwMBH96ufMSXN': 0,
 '3E1Cinh4vYhqNKQmSBDTK8k6pxbLSr94eXWVDGvbatRP': 50,
 '49WgZFiqRMHqrTnv73bNr1UTkhsGTgbWFY4Nb9DAEW44': 35,
 'DEoAbKL942ugV3vhLFVVPbjfoBPpi9ohhGdHXS1csTzk': 35,
 '7z3bnv8unDjQZyCKSJvfhq4YqKHaAJBmueQv9NQ8kTDx': 75,
 '43rwbSgUaK2VXmGE9ZWiZzj6iYgxz4WgUMfEq3WXa9cB': 35,
 'E4vfKvKgtCKbiqQqRw8CsYbERx1U2AvHSaMqQSMAXjFQ': 35,
 '8e1UjdMjEQquhhBb5hh9nNtTUqqnd1AnGoB5vwCMtsdc': 75,
 'CpW1huMqpuLGyNv8oCKMFe29qA7gmUW5HMPvW4K4HVBz': 0,
 '8syAmgTD3WaQKnLxsn5vWRfrzyJAHcCpnS9DMKhw7vtZ': 75,
 '4FawVRnExQBCv7VDdSgMyTULpwoUKBY9nFX32ES28fpM': 90,
 'Dh3Yh36MrdeoXaiL3DFsz9NdyGZPmEwnfYYqAhYPcgJG': 35,
 '9zFjgmUY3iryXMLhVbMceNmCyn5npBkAc7CuoiBJvCYL': 50,
 '8gsRamhEcBMhrj71A18sexfq8cCkDgWT6DVU5zve8XWD': 75,
 'AmVdrQeciRQiuisGKuuQrno6ZpygGimBvqFUwBTdrAZn': 0,
 'HfpFY6RFaF2ikmvEq86fbNfDenUcZ2mAMa4SucX1SLsk': 85,
 '3Tuw8zzKcPgrTRaWAKMVE3Xq1d4FjnSBZ3kms3Pxg6JG': 50,
 '9NEEhgqRSAbTct82w5K4HrQiy9QMKuMZp1Egei3GZjiM': 20,
 'BoCAK4SChpsXf4UB3eBUnMgLngur3GbgmbsgbZeNUVKM': 70,
 'GoH22mhnQYTsik1z6NTxouYbGm7YAp3KUNJuBAa8a42Y': 0,
 'Cw43LkrYXWQUufbP11DKBJBikkxtXeseCuH1WMQDh6q': 0,
 '7GeuioxrRAthYL2YPJDubA3jgLQWwTLexh7Ds6hqX99m': 65,
 'E4WiMosPgrS3zig736YHFn6TnSHZTvrhAMBseXqjgfrM': 75,
 '49HFHN2waPusSTK6dib6Pr8gjgGGkTjziwNczq7kDeRx': 75,
 'G1FgoCSRjxPsvcdMsTgBVGixbpNkaphcu3yzw11CHMub': 65,
 'FELidXszawDEujYLV7A5u7XXFCsPCNvTHm1heJbnh36G': 0,
 '3sv71RVYiv1Hva4AydY2xipo6dj9Ho9mJXYVpUY5JF5h': 85,
 'DWidrdTwDXoAU3pDMmpPGqZqnn3L1ncEcQ9S6UNzcPmG': 75,
 '9TPjRmh239ezPrBC6qUuWL6FrX6kz9drL5XCjU2GQuiq': 89,
 'B4Gsh8FpAuxvVknRny2xSvdt3T1N15RAuDrt3Yg4FDVC': 0,
 'FTmQPeUUZzwFz1o2ENpjUqjqGi5wvtSJRencE6LSvVXq': 35,
 'CgddxhZaSKwYAbm6nNMag8HL36MetNG6Pj17No3e9aZW': 50,
 '2rMCDgDNN3eKaFJKw7wsMUqoG63LtCU8yh924Vvs2DtU': 0,
 '9pQLEx7SAbxKvj5NXzUmdnBkYMFDAftZAdM5yWp1EwHs': 50,
 'C1JPuzshhRVEcLpfURmTETCeodCCsNfMiWT47WAH2PC5': 75,
 '3ysAt1ky2YwCNLHCqvQDn23nYavW1Up6MkUKUgQgT5eB': 75,
 'G9Cw5Gm7USGJZBh94VZT3PeqhPXetgxYcHwwePf1Cth7': 50,
 'ECJtpWhPfG8R6qQVrps5cm9NqyNZPk1iE5wN8Cj3H6RG': 0,
 'fh6Bv7k29VBYTnXBRNJX9Gqk9pZVRxwj1vjcg6M2R3M': 0,
 '5LCf5Awq9UHcMEPEWUMRAv64BeE22CRTK89hWhbPXEF6': 0,
 '2XsH7uaFwwXQ1zpzzF2LztQ8Yx4gfFm11qKedkomnC59': 75,
 '6mM6bwUPaEG1ebhH9BD1hNZP8gH7QXufHhEhzevREQwh': 35,
 '5gurmwpjQTgcFAh8xR6ZePe2jNC6qnp4Y3EkY4Dm8iNm': 65,
 'EngQh4qKyFnw7n54iTdKw3hDkzgAewS1CSNBffVbMAKz': 0,
 'FuFEvCPuCkCPn9rW3uZ7bcmLERxFzFJPRfSSyAyZNLzb': 0,
 '4rvM2KttjDewbPg7A2Wk1xhjuDWWwtjhtU4wXRdFMwMe': 0,
 'JAwDW6CPsi3YhVSo4cJWqMEvC3GZzjV6VDeUykM2EzuW': 0,
 'BqRjT9J7JCNYBrArb5czvercS7sfVdPkARofCC6j2cKA': 0,
 '5UKmPuedvhPppv2DMqoG1GaTojP23vqPYSpxszCsHDLL': 80,
 '2WHngM1w2PzwFrhofmZBjgkUpTiXH9prfUGa396YiLk8': 0,
 '97iuRiw8Ysxod9SEq2njjyUaqBJE7oi569JpRU8Uo8GL': 35,
 'F8DDGg2eEWrQ3G5BJs63R2JutdRHQTHV9RqPsdDGeL7v': 45,
 '9PJCVs62fyRiQ1v9DqxD83TXDXqHabVeAUW2sHpsG13t': 0,
 '28u8y7A95Us59XmFxGPeLCojrtRvWKHtJuuXD8ypZUx4': 0,
 '7NJCWoLDngquvYcCPzUBLYfpS9F3eox4ibgivEGxXweU': 0,
 'CXDxj6cepVv9nWh4QYqWS2MpeoVKBLKJkMfo3c6Y1Lud': 70,
 'EFVkRhRPBp9qAQ4KpyVqn4JguZvBhhuTDYumerLVTq4W': 85,
 'B36VAoKV7YSTaXeHDGLBNDwinMbcBpY6ni6M7JXhRSGZ': 0,
 'HeNatLYe3gXZ6TYck6Xu9CDQWg9LcBTTUS3n6uWkEh3y': 0,
 '7cLLjBcWZcDNYtxrNzusZ1UkgbKzxzuSPAX5cecLsEDM': 35,
 'AV7D8PKyauD6yX5xvu6LsxC8beXTdRhGT2jPyADbD2E7': 95,
 '9MQAxBY3f3FFomZJtB6e35wSuwLU5jQGVheAordRbWnd': 89,
 'CEshUdNq4FLjjGuAXW1UT9eRvtt53w13mwWxXMtvTAnZ': 0,
 'BPXGcggJFjV27mLci3THahwzSpDxPfdF9txMjkAdbtCW': 89,
 '7nj6T11MrwUUv3d4fexpRF4Jq8BP4r6xLGbEjUfeVSdG': 65,
 '4GQfm6SPeW8xCDmrTsgQ5rXvLXzVMkuRJ6ZdtsZx2Ac4': 60,
 'CKzzNHHJhtva2aZkj3YNFU1X9N3zEBMGqjG7Ay3yUVdX': 75,
 '2NBT7CJNAVTnTFmzvh6tbGCEPaZSNETwQtAtnUhXVtdd': 0,
 '6FhG5WjjRSfDmNFoumSE9vVNpgLi1RyqkU2K29M8Fybf': 75,
 'A2HiDWcSxeWSR52Y1MRFnYU3Cd5MVidPHFz2hMPejvCN': 45,
 '8Pzt2bJqTaZeig5sw63GYRzRV8ggKejKqd3UNFHES2ie': 89,
 '7giJctQ5y3yh5a7UfQx1KB4kN5J4MeF9RaygCcGFtJUT': 50,
 'BEKC33gwGTwJEM3m7pHb5DfUGN7RM8F5SvA2dqwpLjxh': 0,
 'CobQ3pQjKfaydbawZy61XBVVWfC1QMroNrYMrpgSLhkq': 89,
 'HBs7Y23y6Fp9XLVmNmcqLPhVfKhsF3EihF2JvYWo9H7C': 75,
 'Hs7CRqCB1AFidcDZnCXGpA6d1Ad63J6gjA83qV3ZE5xw': 75,
 '637Sg5j5S2JcnNc58wDmby2iWmHdYQjMvqQYTgmuFK4Y': 0,
 'CoAKRsiTBt9vQK5irMS3HmLLRKEtSNuGLmb8RaxKnK7P': 0,
 '6iCKyD4NQT72BBFAvMcNsVkXDKc1iEScDeUxMsL4ejqZ': 35,
 'DyNMTn6V7pFmWHR4uUDgCbmiDSFp2rwSBcgEUTxW7C83': 75,
 '13kYktqGvSzo5pcxUqiSPA1zAAckvS6CHDWPCtYJ7ZVg': 89,
 'EPNB8NiL3vFDYQhSZY5LQAoW6AJYLdwFXezXeyqiPvEM': 0,
 'GUeJt6drPpSDrvzhUsBKyAZbDat8x6atvoupUd8mG9zA': 89,
 'UtRy8gcEu9fCkDuUrU8EmC7Uc6FZy5NCwttzG7i6nkw': 70,
 'GKdnVYutejtYkhaGDf9cVrPcH4RySB491J1fZ2ei68qx': 0,
 'HAe4tT7CWNEBdaqzmyxjQvuudjojTdEqpgwYqkBp9dN4': 75,
 'BtGoQiwEWUZQfNaxSxzBgRikfT1rx3hSkzjQEWvktEMe': 65,
 '7WPZ6ccnCdL2T8BMXrpu5DNy2MbnP2wZCCHf85hdr9bi': 0,
 'EkZuwSVLhPk5KuQf9e7p1u1Gw8EmwUMJTLihxpZdjn61': 10,
 '6Ebp13hrKh7cXhpQnaftgCzrXjLsyCYT9v1jk8CZD41d': 95,
 'BXDYoEBMMWm35B2KjpYtfpTc1Bs8RdDggEauQFrWcrsM': 75,
 'BTfSiwzg5bF1tmPr2tyRSeSY8NmUa78RrFdCoTqpgqTe': 75,
 '6z3W9pNcRtdXZa5REnC2kZZYjadgRsHxApBeKxZhMS5Y': 89,
 '4Kzbv1TdayST3KFWLsYnhCmpaLrdjuFE5dXsQU45znDA': 35,
 'PC2HzDAgoHZXgiyPg4zPuHHr3yecEPTELvmk6hLyNE6': 0,
 '3i6qK3hJyCXiLjMrwz5CUdLxphno1uPkwYFoihwqHV7h': 0,
 '5Jy5hKpzY9NtJGEPv5AC2ofu4M9DLnYzU3VkPq2T85cg': 0,
 '91myGX8zgP8LzbSaJoywoG8f1gyAeDSNAJKjkH3ouXbq': 0,
 '9wSy4XV4XN1hzp9nuC8TbCc78zDkWgu8tGNABH4cpBG5': 0,
 'CWQ7bFWm8m4TiMQmL45mnALXpFXBGKokoxbF2dC4jza8': 0,
 '2qLJ6LQkqywy87UXvozM6CW9qcfUN6ZM1mWcv768Jfhp': 90,
 'H229mF5WBrn2Jhd19pMJFymhc8i9yAE4UTbTSwgNAoCV': 89,
 '4Hee1ZhMLZtxvssEnMCmUtcRy4LdVBFq1HJ3JF9b8m8o': 35,
 'GwgRTfxfZhdMEb8endnuyq4sG3zgrd177wWc4GFe74Fj': 0,
 '8bAYWmUunU2W4CZJwv9yLLi5q3oQZzkV8dcLK34x7zhM': 90,
 'GiCYm5su62HUJUkpMyny7PNDe68hB4pBGKEL5W4pKh4a': 0,
 'GgLKhLVsJg8xCRsNJDkNFwTZ5P2XykpFctxyme5TJTmR': 75,
 'Cc8DRe9wagmkVBeeeLsjgkAk7fkpyZt7XF8Ts3ddyYXd': 0,
 'G7BBCmt9Ft5VqJYKU8E2UC3Yn27cPFTkcmecZUTai3Ge': 0,
 'GaYM9Rhm5bnnBdkCTKicLm2PyD592H2kfFCH64FdcViZ': 89,
 'Bz1SyMsoARe8gPDNqk7GTCCw7pcVSQbnKy84AugCnfd2': 75,
 '734df6ZLSzQhyDyqwk8YaKdG2rWPMP6fdsBfxDREZ1nf': 0,
 '7gGpgJg7Y79FnMXa4NiCnTWj2z8gfnEHDVfcfLG26Bne': 50,
 '7JF8e93t52SGFUHzMt5cD7vte4b8gWZHY99GLziAUeiP': 90,
 'G8hfeU4K6xPYgJ7gr1x4cKDi4hAEbVBcowaUAqiawedX': 35,
 'HY91tfEkHStprGuGxmtmtGkb4rKf5yszncinFj5a4ouM': 65,
 '14tWZht7372aFZfDuo2on9ivJmQ9kCXPQTeTC796avc9': 75,
 '9b25iMvfJMmvp78B53i7PYirzxMbbTyghQBLVukUkpbX': 65,
 'GwGEZ7iuookTDMzq3gWmboEmvrRCTYGJGimKTxefy12D': 0,
 'A7BwMhTw2jG6dokyZtV8GsB99qmqjnpAXbDDwYk3tSwG': 75,
 '3WKotLKSFoNjPAymuP3HdkkRmoQE7cY1JrL7vnTCMWRW': 0,
 'AcxqzAFZLgToZorqVaoktxkP7JzAjqsnLMD5noUiHA8N': 75,
 '4wKgt6WHsR8f8yU1AU74yYyPqvjHHXwga3Ed1pKz9xd4': 0,
 'DvD3VS38ao6RMQUbj3txbBMdC6jsNzXubLJMjw8xyzgv': 0,
 'AGsQi22RCBTkz6xhvhD5Y2ewM61MwK56ftbCfSuosHzX': 75,
 'FzxqRogc1vDP4351FzmUPMyheMvMEgsUZbfwhMuwue3H': 0,
 '3LGd2eo9PzS3NQ2kuuxxcW9Ufm55QCTprowQdZE686Q5': 35,
 '9yqdUhrqTDRrdf6qYKfsxxf9NsmWHnmhUUd86S2PTUfy': 75,
 'BVvfJzzRd4maJWq1AKwWDxPvXvpfhLGM4WuARBytQ7gp': 75,
 'AeWvq3kK2K2dZaPikKeWz6a85uFwsVKzGYvUnPbwmS8Y': 35,
 'Fsik6tS2f2qsuaVgQAnPFBj7pXoL3tfqVVnvPur59725': 0,
 '76xVXbVr3gC8TMN7owWe1yByFDufR8suogqiDmh26MoZ': 75,
 '4hHPJdFhoKA9y1PgoLcsiiPvsuWuF8LZ6MvQU6PNbu7m': 35,
 '4X9ZfaVqxcjmAnqHbY14vkcMWgXJPHyoP5YJU5s6E4rf': 75,
 '9EFkfpz3aoxXMiHKRB3TFQB2JRVaDiezmtPX9cNNMuvA': 75,
 '24c9A1BgCVmpLfE1qjn9aUpcweNajwTLDaY8E2zj5J1n': 89,
 'J5fFPm8BaavCNkyBT4vke8uFr6uHarp3eh1frxrwYBBV': 75,
 'GQn4v2Whct4HE2qzRVn1kA3HGZg2scvseXSXkjaDqmq9': 40,
 '7K3vMM6KvXX6Y8Q4YEMurb4D3QweMUW3s68w9r5RmKXt': 75,
 '3QhrshdCiAq9esA8Fny7UDkdN742psuXPNGXkUFjE4Fb': 75,
 'AyAxMfJhyteVZbYYnqygRXMyeJVyFU8KfeTKHhRX5YXZ': 50,
 '6RTTJkwZ7NuK4JaJnnaUgqU78gaW3A8McDTfiGsBBbLX': 0,
 '6qzGgnjXcrdMxh2x3PMMvNhv2Yehre4JD1KKjU7zLxyp': 54,
 '9XAa743iRdzCjo4Gdqna7bpZgyYtn2UFU57JD4dBnwrc': 75,
 '91mVeqDvPnrSRS9DgdpvD5RQViAyzZ9Uqf7VHAPj5x5f': 40,
 'B5aKJDFuooNd4kkYnMYwqS466wJh741e61d4YqN5RXoU': 0,
 'EVyM9hFUThM55PfMgSJtrTmnpt4pzifKrrLUDLtSsE3N': 50,
 '9LgyN4yyT7gYWm9MCFrRX7uapcqQ1v4CBUYcaeqU9eP2': 0,
 'Gg7bXWDbken3UofQaZNtpCzjxzTvPuvpMXKdArfJMTdR': 75,
 'A6LNEZaHnaQNyawxWnzMygVUMdQ6STt6AmawDbRjRvCA': 75,
 'Dieab9zBLL7zsb7nSa8KcgEzPBMRFPgtBHf5NpPHQrLz': 90,
 'EKnFN4ehqwdu8RDmZ2hKnsEMJvA2Jnaszbydae8axbMu': 0,
 'CHyeYnhUmLairBCPRE2GTNQgJiXpwgEyfU1fG5T187fD': 98,
 'HAFx2DUf4VBoQyBn5yAfTvkwGQ1VGXrJpvWEHV1gtYFA': 75,
 '5169uJFQg6UttxizDAmCXTumivvmWnmVApBkmFuCum3r': 0,
 'B1ATuYXNkacjjJS78MAmqu8Lu8PvEPt51u4oBasH1m1g': 65,
 '6EtKSz1BbkWEmeocBHHyF2eetXN8N9z8JtAfL3UECAoX': 75,
 'Dy5qNM5BsADBsaVhoLvFYpwAiyqm4RmJA7eS5jGBngzz': 89,
 '9HrQ9RuRsHjKXuAbZzMHMrYuyq62LjY3B7EBWkM4Uyke': 0,
 'DQLZFFdpFuWgRj8mpcyGJ6hRXHJnpvnkatyaSeRJFXCD': 65,
 '8MaWP9fsX9FrzPGLsxvUfNu8Sr5rR3M8rerwHAQpFxsn': 90,
 '9MBrzWjgw1sbca6X2M6YoUCQgN6udVeKp9oLFwuzPY2p': 63,
 'B8M4TGpsomVenYzivHQT5mQxo7MUqUSBV6AcdUFzg2f4': 0,
 '52ijsn8kcWMzFAzATSo1YBY15WPneNmxgadG237i51hx': 75,
 '9QqRewoWbePkSH919xXn826h67ea1EFAVXhTdiJArDnx': 75,
 'Gh9ueJbjei9L5ZRGs3JqqhMkbDL6BfeJt9JkVx2YC7z1': 65,
 'E6rsp99Fw7Y8zwibn3ebVWEeTxpeAiNut2jMVTgPdhf2': 0,
 '8WKHNjZ4Q5TFDq1BwFbxfpVte2Dz5sdXVywG6oPNW79n': 35,
 '5xZEBEXbNotta4zzENBjiTvcV1yk5ViXnqKQMi5Tc6Ko': 75,
 '5Sgzecs6W8dUmVhiGHJ2NfY9Q39B88HumvzPwXnFMTVV': 35,
 '5SQDiLTFeY725LFXnPJ7Hy68Np2rgdCGbPRcZRcKzQ3A': 75,
 '214BvfQTVWHSiHituvMVJcroTb5LPPBkBFKqSF6ZbN5h': 54,
 'HRQB2xtNZxLAstdz18nUi97YC9JKxouubeGpfLAsmCqu': 95,
 'Fx5Zc46dE7gVadRhVQsjHAMLuoLYedpcSBJotpv9LZfH': 35,
 '45mRaJEoG2y8TAdMKKqs9tmJPTejsKfLbX4hRSVbcbKA': 35,
 'DzERiPrzkwRi4pG5SsWaevVr2jSNhRkwNCibx5eP5K1g': 50,
 'GCagCmPq1uUV43DtWSd4rKh3eP8JdxE2XSKCUBJzyK2X': 50,
 '88EUHQZFCTczH2Z6aFENHgPzEpuqH2V7VXaywKseZgN8': 64,
 '4xRmRbur3HAc4nNLaAYKgZDXiEtCVc2a9wA5TSsmS1qP': 0,
 'EJ7GSUV1ZpdUvEHFXSFzMQdP3J3H1xprZvtLjZSPjyb': 0,
 'HBnL1YHRKVCW9ekP9j1sBDBKfPaTNQcmgZ4RfpxrA1y9': 35,
 '7N9L3hgSXjPT83etcVQrkvD6NDJf8WtP1b72vvKtkz1k': 0,
 '4HJnrm9GSwsw65RVpsBYGQr83MJF6KHVz6AM3PVj8q6N': 75,
 '7js8CsBgzW473PpJaXacmGLLSywP9mAR1KeD6QofXxFN': 90,
 '3ZT6KCf7xyYMjtCFmfnaBJb3fgedkXZ7QGMF9o87CtKz': 60,
 '4VDZMvxihqGggUYGiDbce2WTgsKDBeN47128Bkv72vsc': 0,
 '43VeUMvzrV3tyaiN2Uo7Nfzy649St786yBQhd5N1mgaU': 50,
 'GWy2DQyH9LkjJhxFtRjw8ZqE37vYZ8XpC3thoP569aRp': 75,
 '3TmYkdfGeeNtjRNoDdXXaTH2dFJseyREMuB6xDNZ6bnq': 75,
 'CDKEZFnqkYZSY51BjfhnRRN2WJ2Mr3SkVp7teYVN5g7K': 75,
 '8Q2ZrsHYDVCQzH7LRN15Xc9LbRziaR3uWcq7xYuhpwXT': 75,
 'D71NWrXjXa3uLWpjuqyisSTMJ6BAbsEgqL6nQxz1orSK': 85,
 '6LM7SCbwSyUa51PrpXwSzgBP2xmnAywURG8EPxJRY3d7': 0,
 '2877K885jCdVts6X5Kn7gPbezNPhXufEbheUbVwoZmAi': 0,
 'CeUHmjU5rF78xZkZUpuLchyT1Te8KKhmLobukjdpDL3R': 50,
 'FeWc3QLKQBYS3RbrzEzj4ADsdNtQStomNepajeubY9cW': 0,
 'ZWeSzpFMMu1GoE6iEUyrND4nqDFvKdXorbwiuL2J9PB': 75,
 'DCXkjNmhn8KFXHinE81ZmVjVQoEiE8xUFLLzwwfLTvFP': 0,
 '5SJitWkvjjq2dRd6NYLkZHs3eF4iLtq4wE73HWGNrqFw': 89,
 'Hsdzw9LYZwJgHVdbxVsBsr4GU54BSQ7qRk5wjS3ztEBn': 89,
 '3nfgTBPf1N1NPNTTYk2HpJABaL59db3XKnjgJ8JGwtHJ': 0,
 'Bx1knoCMkWrm3K59QefL9XNFRtWs3mhVWTgQZZ2GDT9u': 0,
 'GGvRDD452CYfp3QBo1CDNB74HgVZhmqCD2jKQwBoQxY2': 90,
 'HR85YRJa7Eb4c9puVEZJqXqaVk7xXzdubYC72DxzY2K9': 0,
 '9Q8ByQw4DgpGftdEpLt4JWdWPu9xFRLByyM6MeAoW2VA': 75,
 'MLvSPCiv2KXQ63WXGdMRrPu7DFz1NwSgpbLZSG97rMz': 35,
 'SoUP1n4stzpzTkyP37KLKr9kgnq4moDV1dKgKKp53YA': 60,
 '3ZyXPjoawGfCG29iUtQsmcR1fivy65m8d5hdYWHPfivg': 0,
 '42cRg9uXr34Kjiex5VWV3K8uMtpmBExtChe8kZ1Mj4pv': 75,
 '6f6DXSebFpt9SE35bD8EKu3BbErXsBM55mLSdiTKtKSw': 75,
 '6WqF7a2mwS31XuadKofizVdAUANxAUxF1pwFf5ALQP9Z': 90,
 'BdkqFjBR7M1qoBmmmVLWHE2YLugxi7SgEHfNaWXS9WYb': 60,
 'DTvg5nwjHboEoCRBJzmbcx7zggbCdxmaoMgDZF52udS5': 75,
 'ADXpQXHFSv3x7a9K74Xo5VJYYo1GG7H1XgiSP8WZnh4K': 75,
 '4HXDioboWL85gQocYNkWM62AB5ctrf8jVykSVco67Lzx': 0,
 '9iQhFzXeixhAi1NzgQs71WupsSjxTPyRq2FRVsUbhwu2': 0,
 'FSJtS1StkZ64ttDxjxczfcHSBQvaFKrUEHjxZ5gqyjTw': 75}





if __name__ == '__main__':
    state = src.loans.solend.SolendState(
        verbose_users={'D3H9aPp5SpYZbeJ2Xe21z2XGV4bsyT5aEd31KifBMTUT'},
    )
    state.get_unprocessed_events()
    print('success')
    # state.unprocessed_events
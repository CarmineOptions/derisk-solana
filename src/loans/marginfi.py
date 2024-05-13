import asyncio
import decimal
import logging
import os
import time

import pandas
import numpy
import solana.rpc.async_api
import solders.pubkey
import solders.rpc.responses

import src.loans.helpers
import src.loans.types
import src.loans.state
import src.marginfi_map
import src.protocols.addresses
import src.protocols.anchor_clients.marginfi_client.accounts.marginfi_account



# Keys are values of the "event_name" column in the database, values are the respective method names.
EVENTS_METHODS_MAPPING: dict[str, str] = {
    'lending_account_borrow': 'process_borrowing_event',
    'lending_account_deposit': 'process_deposit_event',
    'lending_account_liquidate': 'process_liquidation_event',
    'lending_account_repay': 'process_repayment_event',
    'lending_account_withdraw': 'process_withdrawal_event',
}


def get_events(start_block_number: int = 0) -> pandas.DataFrame:
    return src.loans.helpers.get_events(
        table='lenders.marginfi_parsed_transactions_v5',
        event_names=tuple(EVENTS_METHODS_MAPPING),
        start_block_number=start_block_number,
    )


def decode_account(
    account: solders.rpc.responses.RpcKeyedAccount,
) -> src.protocols.anchor_clients.marginfi_client.accounts.marginfi_account.MarginfiAccount | None:
    try:
        return src.protocols.anchor_clients.marginfi_client.accounts.MarginfiAccount.decode(account.account.data)
    except src.protocols.anchor_clients.marginfi_client.accounts.marginfi_account.AccountInvalidDiscriminator:
        return


class MarginFiLoanEntity(src.loans.state.LoanEntity):
    """ A class that describes the MarginFi loan entity. """

    def __init__(self) -> None:
        super().__init__()


class MarginFiState(src.loans.state.State):
    """
    A class that describes the state of all MarginFi loan entities. It implements methods for correct processing of
    every relevant event.
    """

    EVENTS_METHODS_MAPPING: dict[str, str] = EVENTS_METHODS_MAPPING

    def __init__(
        self,
        verbose_users: set[str] | None = None,
        initial_loan_states: pandas.DataFrame = pandas.DataFrame(),
    ) -> None:
        super().__init__(
            protocol='MarginFi',
            loan_entity_class=MarginFiLoanEntity,
            verbose_users=verbose_users,
            initial_loan_states=initial_loan_states,
        )
        self.accounts: list[solders.rpc.responses.RpcKeyedAccount] = []

    def get_unprocessed_events(self) -> None:
        # TODO: switch back to events when the issues are solved
        # self.unprocessed_events = src.loans.helpers.get_events(
        #     table='lenders.marginfi_parsed_transactions_v5',
        #     event_names=tuple(EVENTS_METHODS_MAPPING),
        #     event_column='instruction_name',
        #     start_block_number=self.last_slot + 1,
        # )
        AUTHENTICATED_RPC_URL = os.environ.get("AUTHENTICATED_RPC_URL")
        if AUTHENTICATED_RPC_URL is None:
            raise ValueError("no AUTHENTICATED_RPC_URL env var")
        # This is the only group we found.
        GROUP = '4qp6Fx6tnZkY5Wropq9wUYgtFxXKwE6viZxFHg3rdAG8'

        client = solana.rpc.async_api.AsyncClient(AUTHENTICATED_RPC_URL)

        accounts = asyncio.run(
            client.get_program_accounts(
                solders.pubkey.Pubkey.from_string(src.protocols.addresses.MARGINFI_ADDRESS),
                encoding='base64',
                filters=[solana.rpc.types.MemcmpOpts(8, GROUP)],
            )
        )
        self.accounts = accounts.value

    def process_unprocessed_events(self):
        for account in self.accounts:
            decoded_account = decode_account(account)
            if not decoded_account:
                continue

            user = str(account.pubkey)

            for balance in decoded_account.lending_account.balances:
                if not balance.active:
                    continue

                token = str(balance.bank_pk)
                collateral_amount = decimal.Decimal(str(int(balance.asset_shares.value / 2**48)))
                debt_amount = decimal.Decimal(str(int(balance.liability_shares.value / 2**48)))

                self.loan_entities[user].collateral.set_value(token=token, value=collateral_amount)
                self.loan_entities[user].debt.set_value(token=token, value=debt_amount)

        self.last_slot = int(time.time())

    def process_event(self, event: pandas.DataFrame) -> None:
        min_slot = event["block"].min()
        assert min_slot >= self.last_slot
        event_name = event["instruction_name"].iloc[0]
        getattr(self, self.EVENTS_METHODS_MAPPING[event_name])(event=event)
        self.last_slot = min_slot

    def process_deposit_event(self, event: pandas.DataFrame) -> None:
        transfer_event = event[event['event_name'] == 'transfer-signerTokenAccount-bankLiquidityVault']
        for _, individual_transfer_event in transfer_event.iterrows():
            user = individual_transfer_event["account"]
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
        transfer_event = event[event['event_name'] == 'transfer-bankLiquidityVault-destinationTokenAccount']
        for _, individual_transfer_event in transfer_event.iterrows():
            user = individual_transfer_event["account"]
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
        transfer_event = event[event['event_name'] == 'transfer-bankLiquidityVault-destinationTokenAccount']
        for _, individual_transfer_event in transfer_event.iterrows():
            user = individual_transfer_event["account"]
            token = individual_transfer_event["source"]
            amount = decimal.Decimal(str(individual_transfer_event["amount"]))
            assert amount >= 0
            self.loan_entities[user].debt.increase_value(token=token, value=amount)
            if user in self.verbose_users:
                logging.info(
                    "In block number = {}, user = {} borrowed amount = {} of token = {}.".format(
                        individual_transfer_event["block"],
                        user,
                        amount,
                        token,
                    )
                )

    def process_repayment_event(self, event: pandas.DataFrame) -> None:
        transfer_event = event[event['event_name'] == 'transfer-signerTokenAccount-bankLiquidityVault']
        for _, individual_transfer_event in transfer_event.iterrows():
            user = individual_transfer_event["account"]
            token = individual_transfer_event["destination"]
            amount = decimal.Decimal(str(individual_transfer_event["amount"]))
            assert amount >= 0
            self.loan_entities[user].debt.increase_value(token=token, value=-amount)
            if user in self.verbose_users:
                logging.info(
                    "In block number = {}, user = {} repaid amount = {} of token = {}.".format(
                        individual_transfer_event["block"],
                        user,
                        amount,
                        token,
                    )
                )

    def process_liquidation_event(self, event: pandas.DataFrame) -> None:
        # Under MarginFi, each liquidation event consists of a collateral transfer event, debt transfer event and fee
        # transfer event. The collateral transfer under the liquidation is handled as a separate withdrawal event, the
        # debt transfer event is handled as a separate repayment event and only the fee transfer event is handled here.
        transfer_event = event[event['event_name'] == 'transfer-bankLiquidityVault-bankInsuranceVault']
        for _, individual_transfer_event in transfer_event.iterrows():
            user = individual_transfer_event["liquidatee_marginfi_account"]
            assert user in self.loan_entities
            debt_token = individual_transfer_event["source"]
            debt_amount = decimal.Decimal(str(individual_transfer_event["amount"]))
            assert debt_amount >= 0
            self.loan_entities[user].debt.increase_value(token=debt_token, value=-debt_amount)
            if user in self.verbose_users:
                logging.info(
                    "In block number = {}, user = {} paid liquidation fee amount = {} of token = {}.".format(
                        event["block"].iloc[0],
                        user,
                        debt_amount,
                        debt_token,
                    )
                )


def compute_liquidable_debt_at_price(
    loan_states: pandas.DataFrame,
    token_prices: dict[str, float],
    mint_to_liquidity_vault_map: dict[str, str],
    collateral_token: str,
    target_collateral_token_price: decimal.Decimal,
    debt_token: str,
) -> decimal.Decimal:
    liquidity_vault_collateral_tokens = mint_to_liquidity_vault_map[collateral_token]
    liquidity_vault_debt_tokens = mint_to_liquidity_vault_map[debt_token]

    price_ratio = target_collateral_token_price / token_prices[collateral_token]
    for liquidity_vault_collateral_token in liquidity_vault_collateral_tokens:
        liquidity_vault_collateral_column = f'collateral_usd_{liquidity_vault_collateral_token}'
        if liquidity_vault_collateral_column in loan_states.columns:
            loan_states[liquidity_vault_collateral_column] = loan_states[liquidity_vault_collateral_column] * price_ratio
        liquidity_vault_debt_column = f'debt_usd_{liquidity_vault_collateral_token}'
        if liquidity_vault_debt_column in loan_states.columns:
            loan_states[liquidity_vault_debt_column] = loan_states[liquidity_vault_debt_column] * price_ratio
    loan_states['collateral_usd'] = loan_states[[x for x in loan_states.columns if 'collateral_usd_' in x]].sum(axis = 1)
    loan_states['debt_usd'] = loan_states[[x for x in loan_states.columns if 'debt_usd_' in x]].sum(axis = 1)
    loan_states['health'] = (loan_states['collateral_usd'] - loan_states['debt_usd']) / loan_states['collateral_usd']

    loan_states['liquidable'] = loan_states['health'] < 0
    # The debt is liquidated up to the liquidation_threshold.
    loan_states['debt_to_be_liquidated'] = (
        (loan_states[f'debt_usd_{liquidity_vault_debt_tokens[0]}'] - loan_states['collateral_usd'])
        * loan_states['liquidable']
    ).clip(lower = 0)
    return loan_states['debt_to_be_liquidated'].sum()


def get_marginfi_user_stats_df(loan_states: pandas.DataFrame) -> pandas.DataFrame:

    MINT_TO_LIQUIDITY_VAULT_MAPPING = {x['mint']: [] for x in src.marginfi_map.liquidity_vault_to_info_mapping.values()}
    for x, y in src.marginfi_map.liquidity_vault_to_info_mapping.items():
        MINT_TO_LIQUIDITY_VAULT_MAPPING[y['mint']].append(x)


    collateral_tokens = {token for collateral in loan_states['collateral'] for token in collateral}
    debt_tokens = {token for debt in loan_states['debt'] for token in debt}


    collateral_token_parameters = {
        token: src.marginfi_map.liquidity_vault_to_info_mapping[token]
        for token in collateral_tokens
        if token in src.marginfi_map.liquidity_vault_to_info_mapping
    }
    debt_token_parameters = {
        token: src.marginfi_map.liquidity_vault_to_info_mapping[token]
        for token in debt_tokens
        if token in src.marginfi_map.liquidity_vault_to_info_mapping
    }


    underlying_collateral_tokens = [
        x['mint']
        for x in collateral_token_parameters.values()
    ]
    underlying_debt_tokens = [
        x['mint']
        for x in debt_token_parameters.values()
    ]
    token_prices = src.prices.get_prices_for_tokens(underlying_collateral_tokens + underlying_debt_tokens)


    for token in collateral_tokens:
        loan_states[f'collateral_{token}'] = loan_states['collateral'].apply(
            lambda x: x[token] if token in x else decimal.Decimal('0')
        )
    for token in debt_tokens:
        loan_states[f'debt_{token}'] = loan_states['debt'].apply(
            lambda x: x[token] if token in x else decimal.Decimal('0')
        )


    for token in collateral_tokens:
        if not token in collateral_token_parameters:
            continue
        decimals = collateral_token_parameters[token]['decs']
        collateral_factor = collateral_token_parameters[token]['asset_weight_maint'] / 2**48
        underlying_token = collateral_token_parameters[token]['mint']
        loan_states[f'collateral_usd_{token}'] = (
            loan_states[f'collateral_{token}'].astype(float)
            / (10**decimals)
            * token_prices[underlying_token]
        )
        loan_states[f'risk_adj_collateral_usd_{token}'] = loan_states[f'collateral_usd_{token}'] * (collateral_factor)

    for token in debt_tokens:
        if not token in debt_token_parameters:
            continue
        decimals = debt_token_parameters[token]['decs']
        debt_factor = debt_token_parameters[token]['liability_weight_maint'] / 2**48
        underlying_token = debt_token_parameters[token]['mint']
        loan_states[f'debt_usd_{token}'] = (
            loan_states[f'debt_{token}'].astype(float)
            / (10**decimals)
            * token_prices[underlying_token]
        )

        loan_states[f'risk_adj_debt_usd_{token}'] = (
            loan_states[f'debt_usd_{token}'] * (1/debt_factor)
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


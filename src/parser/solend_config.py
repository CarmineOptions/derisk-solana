INSTRUCTION_ACCOUNT_MAP = {
    "deposit_reserve_liquidity": [
        "source_liquidity_pubkey",
        "destination_collateral_pubkey",
        "reserve_pubkey",
        "reserve_liquidity_supply_pubkey",
        "reserve_collateral_mint_pubkey",
        "lending_market_pubkey",  # readonly
        "lending_market_authority_pubkey",  # readonly (computed within function)
        "user_transfer_authority_pubkey",  # readonly
        "sysvar::clock",  # readonly (system variable)
        "spl_token",  # readonly (system variable)
    ],
    "redeem_reserve_collateral": [
        "source_collateral_pubkey",
        "destination_liquidity_pubkey",
        "reserve_pubkey",
        "reserve_collateral_mint_pubkey",
        "reserve_liquidity_supply_pubkey",
        "lending_market_pubkey",  # readonly
        "lending_market_authority_pubkey",  # readonly (computed within function)
        "user_transfer_authority_pubkey",  # readonly
        "sysvar::clock",  # readonly (system variable)
        "spl_token",  # readonly (system variable)
    ],
    'init_reserve': [
        "source_liquidity_pubkey",
        "destination_collateral_pubkey",
        "reserve_pubkey",
        "reserve_liquidity_mint_pubkey",
        "reserve_liquidity_supply_pubkey",
        "config.fee_receiver",
        "reserve_collateral_mint_pubkey",
        "reserve_collateral_supply_pubkey",
        "pyth_product_pubkey",
        "pyth_price_pubkey",
        "switchboard_feed_pubkey",
        "lending_market_pubkey",
        "lending_market_authority_pubkey",
        "lending_market_owner_pubkey",
        "user_transfer_authority_pubkey",
        "sysvar::rent",
        "spl_token"
    ],
    "init_obligation": [
        "obligation_pubkey",
        "lending_market_pubkey",  # readonly
        "obligation_owner_pubkey",  # readonly
        "sysvar::clock",  # readonly (system variable)
        "sysvar::rent",  # readonly (system variable)
        "spl_token",  # readonly (system variable)
    ],
    "deposit_obligation_collateral": [
        "source_collateral_pubkey",
        "destination_collateral_pubkey",
        "deposit_reserve_pubkey",  # readonly
        "obligation_pubkey",
        "lending_market_pubkey",  # readonly
        "obligation_owner_pubkey",  # readonly
        "user_transfer_authority_pubkey",  # readonly
        "sysvar::clock",  # readonly (system variable)
        "spl_token",  # readonly (system variable)
    ],
    "deposit_reserve_liquidity_and_obligation_collateral": [
        "source_liquidity_pubkey",
        "user_collateral_pubkey",
        "reserve_pubkey",
        "reserve_liquidity_supply_pubkey",
        "reserve_collateral_mint_pubkey",
        "lending_market_pubkey",  # readonly
        "lending_market_authority_pubkey",  # readonly (computed within function)
        "destination_deposit_collateral_pubkey",
        "obligation_pubkey",
        "obligation_owner_pubkey",  # readonly
        "reserve_liquidity_pyth_oracle_pubkey",  # readonly
        "reserve_liquidity_switchboard_oracle_pubkey",  # readonly
        "user_transfer_authority_pubkey",  # readonly
        "sysvar::clock",  # readonly (system variable)
        "spl_token",  # readonly (system variable)
    ],
    'withdraw_obligation_collateral_and_redeem_reserve_liquidity': [
        "source_collateral_pubkey",
        "destination_collateral_pubkey",
        "withdraw_reserve_pubkey",
        "obligation_pubkey",
        "lending_market_pubkey",
        "lending_market_authority_pubkey",
        "destination_liquidity_pubkey",
        "reserve_collateral_mint_pubkey",
        "reserve_liquidity_supply_pubkey",
        "obligation_owner_pubkey",
        "user_transfer_authority_pubkey",
        "spl_token"
    ],
    "withdraw_obligation_collateral": [
        "source_collateral_pubkey",
        "destination_collateral_pubkey",
        "withdraw_reserve_pubkey",  # readonly
        "obligation_pubkey",
        "lending_market_pubkey",  # readonly
        "lending_market_authority_pubkey",  # readonly (computed within function)
        "obligation_owner_pubkey",  # readonly
        "sysvar::clock",  # readonly (system variable)
        "spl_token",  # readonly (system variable)
    ],
    "borrow_obligation_liquidity": [
        "source_liquidity_pubkey",
        "destination_liquidity_pubkey",
        "borrow_reserve_pubkey",
        "borrow_reserve_liquidity_fee_receiver_pubkey",
        "obligation_pubkey",
        "lending_market_pubkey",  # readonly
        "lending_market_authority_pubkey",  # readonly (computed within function)
        "obligation_owner_pubkey",  # readonly
        "host_fee_receiver_pubkey",  # optional, not always present
        "sysvar::clock",  # readonly (system variable)
        "spl_token",  # readonly (system variable)
    ],
    "repay_obligation_liquidity": [
        "source_liquidity_pubkey",
        "destination_liquidity_pubkey",
        "repay_reserve_pubkey",
        "obligation_pubkey",
        "lending_market_pubkey",  # readonly
        "user_transfer_authority_pubkey",  # readonly
        "sysvar::clock",  # readonly (system variable)
        "spl_token",  # readonly (system variable)
    ],
    "liquidate_obligation": [
        "source_liquidity_pubkey",
        "destination_collateral_pubkey",
        "repay_reserve_pubkey",
        "repay_reserve_liquidity_supply_pubkey",
        "withdraw_reserve_pubkey",  # readonly
        "withdraw_reserve_collateral_supply_pubkey",
        "obligation_pubkey",
        "lending_market_pubkey",  # readonly
        "lending_market_authority_pubkey",  # readonly (computed within function)
        "user_transfer_authority_pubkey",  # readonly
        "sysvar::clock",  # readonly (system variable)
        "spl_token",  # readonly (system variable)
    ],
    "liquidate_obligation_and_redeem_reserve_collateral": [
        "source_liquidity_pubkey",
        "destination_collateral_pubkey",
        "destination_liquidity_pubkey",
        "repay_reserve_pubkey",
        "repay_reserve_liquidity_supply_pubkey",
        "withdraw_reserve_pubkey",
        "withdraw_reserve_collateral_mint_pubkey",
        "withdraw_reserve_collateral_supply_pubkey",
        "withdraw_reserve_liquidity_supply_pubkey",
        "withdraw_reserve_liquidity_fee_receiver_pubkey",
        "obligation_pubkey",
        "lending_market_pubkey",
        "lending_market_authority_pubkey",
        "user_transfer_authority_pubkey",
        "spl_token"
    ],
    "redeem_fees": [
        "reserve_pubkey",
        "reserve_liquidity_fee_receiver_pubkey",
        "reserve_supply_liquidity_pubkey",
        "lending_market_pubkey",
        "lending_market_authority_pubkey",
        "spl_token"
    ],
    "flash_borrow_reserve_liquidity": [
        "source_liquidity_pubkey",
        "destination_liquidity_pubkey",
        "reserve_pubkey",
        "lending_market_pubkey",
        "lending_market_authority_pubkey",
        "sysvar::instructions",
        "spl_token"
    ],
    "flash_repay_reserve_liquidity": [
        "source_liquidity_pubkey",
        "destination_liquidity_pubkey",
        "reserve_liquidity_fee_receiver_pubkey",
        "host_fee_receiver_pubkey",
        "reserve_pubkey",
        "lending_market_pubkey",
        "user_transfer_authority_pubkey",
        "sysvar::instructions",
        "spl_token"
    ],
    "forgive_debt": [
        "obligation_pubkey",
        "reserve_pubkey",
        "lending_market_pubkey",
        "lending_market_owner"
    ]
}

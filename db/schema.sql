
CREATE TABLE public.amm_liquidity (
    timestamp bigint NOT NULL,
    dex character varying NOT NULL, 
    market_address character varying NOT NULL,
    token_x_amount bigint NOT NULL, 
    token_y_amount bigint NOT NULL,
    token_x_address character varying NOT NULL,
    token_y_address character varying NOT NULL,
    additional_info character varying NOT NULL
);

CREATE TABLE public.orderbook_liquidity (
    timestamp bigint NOT NULL,
    dex character varying NOT NULL, 
    pair character varying NOT NULL,
    market_address character varying NOT NULL,
    bids float[][] NOT NULL,
    asks float[][] NOT NULL
);

CREATE TABLE public.tx_signatures (
    id integer NOT NULL,
    source character varying NOT NULL,
    signature character varying NOT NULL,
    slot bigint NOT NULL,
    block_time bigint NOT NULL,
    tx_raw text
);

CREATE SEQUENCE public.tx_signatures_id_seq AS integer START WITH 1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE CACHE 1;

ALTER SEQUENCE public.tx_signatures_id_seq OWNED BY public.tx_signatures.id;

CREATE TABLE public.tx_status_errors (
    id integer NOT NULL,
    error_body character varying NOT NULL,
    tx_signatures_id integer NOT NULL
);

CREATE SEQUENCE public.tx_status_errors_id_seq AS integer START WITH 1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE CACHE 1;

ALTER SEQUENCE public.tx_status_errors_id_seq OWNED BY public.tx_status_errors.id;

CREATE TABLE public.tx_status_memo (
    id integer NOT NULL,
    memo_body character varying NOT NULL,
    tx_signatures_id integer NOT NULL
);

CREATE SEQUENCE public.tx_status_memo_id_seq AS integer START WITH 1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE CACHE 1;

ALTER SEQUENCE public.tx_status_memo_id_seq OWNED BY public.tx_status_memo.id;

ALTER TABLE 
    ONLY public.orderbook_liquidity
ADD 
    CONSTRAINT orderbook_liquidity_pkey 
    PRIMARY KEY (dex, pair, market_address, timestamp);

ALTER TABLE 
    ONLY public.amm_liquidity
ADD 
    CONSTRAINT amm_liquidity_pkey 
    PRIMARY KEY (dex, token_x_address, token_y_address, market_address, timestamp);

ALTER TABLE
    ONLY public.tx_signatures
ALTER COLUMN
    id
SET
    DEFAULT nextval('public.tx_signatures_id_seq' :: regclass);

ALTER TABLE
    ONLY public.tx_status_errors
ALTER COLUMN
    id
SET
    DEFAULT nextval('public.tx_status_errors_id_seq' :: regclass);

ALTER TABLE
    ONLY public.tx_status_memo
ALTER COLUMN
    id
SET
    DEFAULT nextval('public.tx_status_memo_id_seq' :: regclass);

ALTER TABLE
    ONLY public.tx_signatures
ADD
    CONSTRAINT tx_signatures_pkey PRIMARY KEY (id);

ALTER TABLE
    ONLY public.tx_status_errors
ADD
    CONSTRAINT tx_status_errors_pkey PRIMARY KEY (id);

ALTER TABLE
    ONLY public.tx_status_memo
ADD
    CONSTRAINT tx_status_memo_pkey PRIMARY KEY (id);

CREATE INDEX ix_transactions_block_time ON public.tx_signatures USING btree (block_time);

CREATE INDEX ix_transactions_signature ON public.tx_signatures USING btree (signature);

CREATE INDEX ix_transactions_slot ON public.tx_signatures USING btree (slot);

CREATE INDEX ix_transactions_source ON public.tx_signatures USING btree (source);

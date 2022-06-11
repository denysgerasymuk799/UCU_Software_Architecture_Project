-- KEYSPACE
CREATE KEYSPACE bank WITH REPLICATION = {'class' : 'SingleRegionStrategy', 'replication_factor' : 3};

-- ORDINARY TABLES
CREATE TABLE bank.cards (
	card_id TEXT,
	credit_limit INT,
	PRIMARY KEY (card_id)
);

CREATE TABLE bank.unique_users_daily (
	card_id TEXT,
	date DATE,
	PRIMARY KEY ((date), card_id)
);

CREATE TABLE bank.transactions (
	transaction_id TEXT,
	card_id TEXT,
	receiver_card_id TEXT,
	amount INT,
	status TEXT,
	date DATE,
	PRIMARY KEY ((transaction_id), card_id, date) 
) WITH CLUSTERING ORDER BY (card_id ASC, date DESC);

CREATE TABLE bank.reserved_transactions (
	transaction_id TEXT,
	card_id TEXT,
	receiver_card_id TEXT,
	amount INT,
	date DATE,
	PRIMARY KEY ((card_id), transaction_id, date) 
) WITH CLUSTERING ORDER BY (transaction_id ASC, date ASC);

CREATE TABLE bank.successful_transactions_daily (
	transaction_id TEXT,
	card_id TEXT,
	receiver_card_id TEXT,
	amount INT,
	date DATE,
	PRIMARY KEY ((date), transaction_id)
);

-- PREAGGREGATION TABLES
CREATE TABLE bank.transactions_preaggregated_daily (
	card_id TEXT,
	total_amount DOUBLE,
	date DATE,
	PRIMARY KEY ((card_id), date)
) WITH CLUSTERING ORDER BY (date DESC);

CREATE TABLE bank.transactions_preaggregated_monthly (
	card_id TEXT,
	total_amount DOUBLE,
	date DATE,
	PRIMARY KEY ((card_id), date)
) WITH CLUSTERING ORDER BY (date DESC);

CREATE TABLE bank.bank_statistics_daily (
	number_transactions BIGINT,
	number_unique_users BIGINT,
	capital_turnover BIGINT,
	date DATE,
	PRIMARY KEY (date)
);
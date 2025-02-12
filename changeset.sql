CREATE SCHEMA augment;

CREATE OR REPLACE FUNCTION trigger_set_timestamp()
RETURNS TRIGGER AS
$$
BEGIN
    NEW.updated_date = NOW();
    RETURN NEW;
END;
$$ LANGUAGE 'plpgsql';


CREATE TABLE augment.funds (
    id BIGSERIAL PRIMARY KEY,
    reference_id UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),
    name text NOT NULL,
    units bigint NOT NULL,
    created_date timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_date timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER set_timestamp
BEFORE UPDATE ON augment.funds
FOR EACH ROW
EXECUTE PROCEDURE trigger_set_timestamp();


CREATE TABLE augment.users (
    id BIGSERIAL PRIMARY KEY,
    reference_id UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),
    name text NOT NULL,
    created_date timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_date timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER set_timestamp
BEFORE UPDATE ON augment.users
FOR EACH ROW
EXECUTE PROCEDURE trigger_set_timestamp();


CREATE TYPE transfer_type AS ENUM ('transfer', 'grant');

CREATE TABLE augment.transfers (
    id BIGSERIAL PRIMARY KEY,
    reference_id UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),
    sending_user UUID REFERENCES augment.users(reference_id),
    receiving_user UUID NOT NULL REFERENCES augment.users(reference_id),
    fund UUID NOT NULL REFERENCES augment.funds(reference_id),
    amount bigint NOT NULL,
    transfer_type transfer_type NOT NULL,
    created_date timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_date timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT nonnegative CHECK (amount > 0),
    CONSTRAINT receive_send_not_same CHECK (sending_user != receiving_user)
);

CREATE TRIGGER set_timestamp
BEFORE UPDATE ON augment.transfers
FOR EACH ROW
EXECUTE PROCEDURE trigger_set_timestamp();

CREATE OR REPLACE VIEW augment.cap_table AS
SELECT
    user_id,
    fund,
    SUM(amount) AS total_shares,
    MAX(updated_date) AS last_update
FROM (
    SELECT
        sending_user AS user_id,
        fund,
        -amount AS amount,
        updated_date
    FROM augment.transfers
    UNION ALL
    SELECT
        receiving_user AS user_id,
        fund,
        amount AS amount,
        updated_date
    FROM augment.transfers
) AS transfers_combined
WHERE user_id IS NOT NULL
GROUP BY
    user_id, fund;

CREATE OR REPLACE VIEW augment.available_shares AS
SELECT
    f.reference_id,
    f.units - COALESCE(SUM(t.amount), 0) AS available_shares
FROM augment.funds f
LEFT JOIN augment.transfers t ON t.fund = f.reference_id AND t.transfer_type = 'grant'
GROUP BY
    f.reference_id,
    f.units;
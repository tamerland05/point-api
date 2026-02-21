from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(_: BaseDBAsyncClient) -> str:
    return """
        CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE TABLE IF NOT EXISTS "assets" (
    "id" UUID NOT NULL PRIMARY KEY,
    "symbol" VARCHAR(16) NOT NULL UNIQUE,
    "name" VARCHAR(128) NOT NULL,
    "decimals" SMALLINT NOT NULL DEFAULT 9,
    "address" TEXT NOT NULL,
    "image_url" TEXT NOT NULL,
    "price" DECIMAL(64,32) NOT NULL DEFAULT 0,
    "priority" SMALLINT NOT NULL DEFAULT 0,
    "enabled" BOOL NOT NULL DEFAULT True,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS "establishment_types" (
    "id" UUID NOT NULL PRIMARY KEY,
    "name" VARCHAR(128) NOT NULL UNIQUE,
    "icon_hash" TEXT NOT NULL,
    "color_code" TEXT,
    "enabled" BOOL NOT NULL DEFAULT True,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS "establishments" (
    "id" UUID NOT NULL PRIMARY KEY,
    "external_id" BIGINT UNIQUE,
    "location" geography(Point, 4326) NOT NULL,
    "address" VARCHAR(128) NOT NULL,
    "service_wallet" TEXT,
    "service_wallet_seed" TEXT,
    "official_wallet" TEXT,
    "name" VARCHAR(128) NOT NULL,
    "description" VARCHAR(512) NOT NULL,
    "channel_link" VARCHAR(512),
    "icon_hash" TEXT NOT NULL,
    "photo_hash" TEXT NOT NULL,
    "gallery_hashes" JSONB NOT NULL,
    "rating_sum" BIGINT NOT NULL DEFAULT 0,
    "rating_count" BIGINT NOT NULL DEFAULT 0,
    "enabled" BOOL NOT NULL DEFAULT True,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "establishment_type_id" UUID NOT NULL REFERENCES "establishment_types" ("id") ON DELETE RESTRICT
);
CREATE INDEX IF NOT EXISTS idx_user_name_trgm ON establishments USING GIN (LOWER(name) gin_trgm_ops);
CREATE INDEX IF NOT EXISTS "idx_establishments_location_gist" ON "establishments" USING GIST ("location") WHERE enabled;
CREATE TABLE IF NOT EXISTS "employees" (
    "id" UUID NOT NULL PRIMARY KEY,
    "profession" VARCHAR(32) NOT NULL,
    "first_name" VARCHAR(32) NOT NULL,
    "last_name" VARCHAR(32) NOT NULL,
    "photo_hash" TEXT NOT NULL,
    "purpose" JSONB,
    "meta" JSONB NOT NULL,
    "enabled" BOOL NOT NULL DEFAULT True,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "job_place_id" UUID NOT NULL REFERENCES "establishments" ("id") ON DELETE RESTRICT
);
CREATE INDEX IF NOT EXISTS "idx_employees_job_pla_f9c8a1" ON "employees" ("job_place_id") WHERE enabled = true;
CREATE TABLE IF NOT EXISTS "invitations" (
    "user_id" BIGINT NOT NULL,
    "profession" VARCHAR(32) NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "establishment_id" UUID NOT NULL REFERENCES "establishments" ("id") ON DELETE CASCADE,
    PRIMARY KEY ("user_id", "establishment_id")
);
CREATE INDEX IF NOT EXISTS "idx_invitations_user_id_ebf60a" ON "invitations" ("user_id");
CREATE TABLE IF NOT EXISTS "menu_items" (
    "id" UUID NOT NULL PRIMARY KEY,
    "category" VARCHAR(32) NOT NULL,
    "title" VARCHAR(128) NOT NULL,
    "description" VARCHAR(512) NOT NULL,
    "photo_hash" TEXT,
    "amount" DECIMAL(64,18) NOT NULL,
    "currency" VARCHAR(8) NOT NULL,
    "enabled" BOOL NOT NULL DEFAULT True,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "establishment_id" UUID NOT NULL REFERENCES "establishments" ("id") ON DELETE RESTRICT,
    CONSTRAINT "uid_menu_items_title_2174d9" UNIQUE ("title", "description", "establishment_id")
);
CREATE INDEX IF NOT EXISTS "idx_menu_items_est_enabled_true" ON "menu_items" ("establishment_id") WHERE enabled;
CREATE TABLE IF NOT EXISTS "purpose_icons" (
    "id" UUID NOT NULL PRIMARY KEY,
    "preview_hash" TEXT NOT NULL,
    "icon_hash" TEXT NOT NULL,
    "enabled" BOOL NOT NULL DEFAULT True,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS "tasks" (
    "id" UUID NOT NULL PRIMARY KEY,
    "title" VARCHAR(128) NOT NULL,
    "description" VARCHAR(512) NOT NULL,
    "profit" BIGINT NOT NULL,
    "icon_hash" VARCHAR(128) NOT NULL,
    "link" VARCHAR(1024) NOT NULL,
    "integration_type" VARCHAR(7) NOT NULL,
    "enabled" BOOL NOT NULL DEFAULT True,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS "idx_tasks_enabled_true_profit" ON "tasks" ("id") WHERE enabled;
CREATE TABLE IF NOT EXISTS "users" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "first_name" TEXT,
    "last_name" TEXT,
    "username" TEXT,
    "language_code" TEXT,
    "photo_url" TEXT,
    "wallet" TEXT,
    "other_bonus_balance" BIGINT NOT NULL DEFAULT 0,
    "referrals_bonus_balance" BIGINT NOT NULL DEFAULT 0,
    "tips_left" DECIMAL(64,32) NOT NULL DEFAULT 0,
    "rank" BIGINT NOT NULL DEFAULT 0,
    "meta" JSONB NOT NULL,
    "enabled" BOOL NOT NULL DEFAULT True,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "employee_id" UUID REFERENCES "employees" ("id") ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS "idx_users_enabled_i41084" ON "users" ("id") WHERE enabled;
CREATE INDEX IF NOT EXISTS "idx_users_other_b_6b3f97" 
    ON "users" ((other_bonus_balance + referrals_bonus_balance) DESC, "id" ASC);
CREATE TABLE IF NOT EXISTS "completed_tasks" (
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "executor_id" BIGINT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE,
    "task_id" UUID NOT NULL REFERENCES "tasks" ("id") ON DELETE CASCADE,
    PRIMARY KEY ("task_id", "executor_id")
);
CREATE TABLE IF NOT EXISTS "establishment_ratings" (
    "mark" SMALLINT NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "establishment_id" UUID NOT NULL REFERENCES "establishments" ("id") ON DELETE CASCADE,
    "user_id" BIGINT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE,
    PRIMARY KEY ("establishment_id", "user_id", "created_at")
);
CREATE TABLE IF NOT EXISTS "referrals" (
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "referral_id" BIGINT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE,
    "referrer_id" BIGINT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE,
    PRIMARY KEY ("referrer_id", "referral_id")
);
CREATE TABLE IF NOT EXISTS "payments" (
    "id" UUID NOT NULL PRIMARY KEY,
    "tag" VARCHAR(32) NOT NULL,
    "done" BOOL NOT NULL DEFAULT False,
    "meta" JSONB NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "user_id" BIGINT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_payments_done_05a88d" ON "payments" ("done", "tag");
CREATE TABLE IF NOT EXISTS "tips" (
    "id" UUID NOT NULL PRIMARY KEY,
    "fee_transaction" JSONB NOT NULL,
    "tip_transaction" JSONB NOT NULL,
    "expired_at" TIMESTAMPTZ NOT NULL,
    "status" VARCHAR(8) NOT NULL DEFAULT 'created',
    "amount" BIGINT NOT NULL,
    "tips_left_amount" DECIMAL(64,32) NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "asset_id" UUID NOT NULL REFERENCES "assets" ("id") ON DELETE RESTRICT,
    "employee_id" UUID REFERENCES "employees" ("id") ON DELETE CASCADE,
    "establishment_id" UUID REFERENCES "establishments" ("id") ON DELETE CASCADE,
    "sender_id" BIGINT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE,
    CHECK (employee_id is null AND establishment_id is not null OR employee_id is not null AND establishment_id is null)
);
CREATE INDEX IF NOT EXISTS "idx_tips_status_b521b6" ON "tips" ("status");
CREATE TABLE IF NOT EXISTS "user_visits" (
    "visits" INT NOT NULL,
    "establishment_id" UUID NOT NULL REFERENCES "establishments" ("id") ON DELETE CASCADE,
    "user_id" BIGINT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE,
    PRIMARY KEY ("user_id", "establishment_id")
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(_: BaseDBAsyncClient) -> str:
    return """
        """


MODELS_STATE = (
    "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"
    "yPbgiZFA5o4sJ54Uj7PJ4+XX/wEYOLKi"
)

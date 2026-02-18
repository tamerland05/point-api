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
CREATE INDEX IF NOT EXISTS "idx_assets_enabled_28a156" ON "assets" ("enabled");
CREATE TABLE IF NOT EXISTS "establishment_types" (
    "id" UUID NOT NULL PRIMARY KEY,
    "name" VARCHAR(128) NOT NULL UNIQUE,
    "icon_hash" TEXT NOT NULL,
    "enabled" BOOL NOT NULL DEFAULT True,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS "idx_establishme_enabled_e074dc" ON "establishment_types" ("enabled");
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

CREATE INDEX IF NOT EXISTS "idx_establishme_enabled_90ab06" ON "establishments" ("enabled");
CREATE INDEX IF NOT EXISTS idx_user_name_trgm ON establishments USING gin (LOWER(name) gin_trgm_ops);
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
CREATE INDEX IF NOT EXISTS "idx_employees_enabled_ac4be2" ON "employees" ("enabled");
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
    CONSTRAINT "uid_menu_items_title_9a00bf" UNIQUE ("title", "establishment_id")
);
CREATE INDEX IF NOT EXISTS "idx_menu_items_enabled_2c09a4" ON "menu_items" ("enabled");
CREATE TABLE IF NOT EXISTS "payments" (
    "id" UUID NOT NULL PRIMARY KEY,
    "tag" VARCHAR(32) NOT NULL,
    "done" BOOL NOT NULL DEFAULT False,
    "meta" JSONB NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS "idx_payments_tag_72ef00" ON "payments" ("done", "tag");
CREATE TABLE IF NOT EXISTS "purpose_icons" (
    "id" UUID NOT NULL PRIMARY KEY,
    "preview_hash" TEXT NOT NULL,
    "icon_hash" TEXT NOT NULL,
    "enabled" BOOL NOT NULL DEFAULT True,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS "idx_purpose_ico_enabled_f0ab0d" ON "purpose_icons" ("enabled");
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
CREATE INDEX IF NOT EXISTS "idx_tasks_enabled_9d6ba4" ON "tasks" ("enabled");
COMMENT ON COLUMN "tasks"."integration_type" IS 'link: link
channel: channel';
CREATE TABLE IF NOT EXISTS "users" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "first_name" TEXT,
    "last_name" TEXT,
    "username" TEXT,
    "language_code" TEXT,
    "photo_url" TEXT,
    "wallet" TEXT,
    "bonus_balance" BIGINT NOT NULL DEFAULT 0,
    "tips_left" DECIMAL(64,32) NOT NULL DEFAULT 0,
    "rank" BIGINT NOT NULL DEFAULT 0,
    "meta" JSONB NOT NULL,
    "enabled" BOOL NOT NULL DEFAULT True,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "employee_id" UUID REFERENCES "employees" ("id") ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS "idx_users_enabled_e41084" ON "users" ("enabled");
CREATE INDEX IF NOT EXISTS "idx_users_bonus_balance_id" ON "users" (bonus_balance DESC, id ASC);
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
COMMENT ON COLUMN "tips"."status" IS 'created: created
accepted: accepted
failed: failed';
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
    "VyhLKjUUSO0HbkCK15BO7n/wFBcBju"
)

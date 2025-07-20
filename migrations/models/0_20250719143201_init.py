from tortoise import BaseDBAsyncClient


async def upgrade(_: BaseDBAsyncClient) -> str:
    return """
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
    "latitude" INT NOT NULL,
    "longitude" INT NOT NULL,
    "address" VARCHAR(128) NOT NULL,
    "service_wallet" TEXT,
    "service_wallet_seed" TEXT,
    "official_wallet" TEXT,
    "name" VARCHAR(128) NOT NULL,
    "description" VARCHAR(512) NOT NULL,
    "channel_link" VARCHAR(512) NOT NULL,
    "icon_hash" TEXT NOT NULL,
    "photo_hash" TEXT NOT NULL,
    "gallery_hashes" JSONB NOT NULL,
    "rating_count" BIGINT NOT NULL DEFAULT 0,
    "rating_sum" BIGINT NOT NULL DEFAULT 0,
    "enabled" BOOL NOT NULL DEFAULT True,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "establishment_type_id" UUID NOT NULL REFERENCES "establishment_types" ("id") ON DELETE RESTRICT
);
CREATE INDEX IF NOT EXISTS "idx_establishme_latitud_2c8a71" ON "establishments" ("latitude");
CREATE INDEX IF NOT EXISTS "idx_establishme_longitu_b41cdb" ON "establishments" ("longitude");
CREATE INDEX IF NOT EXISTS "idx_establishme_enabled_90ab06" ON "establishments" ("enabled");
CREATE TABLE IF NOT EXISTS "employers" (
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
CREATE INDEX IF NOT EXISTS "idx_employers_enabled_ac4be2" ON "employers" ("enabled");
CREATE TABLE IF NOT EXISTS "invitations" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "user_id" BIGINT NOT NULL,
    "profession" VARCHAR(32) NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "establishment_id" UUID NOT NULL REFERENCES "establishments" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_invitations_user_id_10cff6" UNIQUE ("user_id", "establishment_id")
);
CREATE INDEX IF NOT EXISTS "idx_invitations_user_id_ebf60a" ON "invitations" ("user_id");
CREATE TABLE IF NOT EXISTS "menu_items" (
    "id" UUID NOT NULL PRIMARY KEY,
    "category" VARCHAR(32) NOT NULL,
    "title" VARCHAR(128) NOT NULL,
    "description" VARCHAR(128) NOT NULL,
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
CREATE INDEX IF NOT EXISTS "idx_payments_tag_72ef00" ON "payments" ("tag");
CREATE INDEX IF NOT EXISTS "idx_payments_done_69e9fb" ON "payments" ("done");
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
COMMENT ON COLUMN "tasks"."integration_type" IS 'link: link\nchannel: channel';
CREATE TABLE IF NOT EXISTS "users" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "first_name" TEXT,
    "last_name" TEXT,
    "username" TEXT,
    "language_code" TEXT,
    "photo_url" TEXT,
    "wallet" TEXT,
    "bonus_balance" BIGINT NOT NULL DEFAULT 0,
    "tips_left" BIGINT NOT NULL DEFAULT 0,
    "meta" JSONB NOT NULL,
    "enabled" BOOL NOT NULL DEFAULT True,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "employee_id" UUID REFERENCES "employers" ("id") ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS "idx_users_bonus_b_7e88f8" ON "users" ("bonus_balance");
CREATE INDEX IF NOT EXISTS "idx_users_tips_le_b640c2" ON "users" ("tips_left");
CREATE INDEX IF NOT EXISTS "idx_users_enabled_e41084" ON "users" ("enabled");
CREATE TABLE IF NOT EXISTS "completed_tasks" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "executor_id" BIGINT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE,
    "task_id" UUID NOT NULL REFERENCES "tasks" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_completed_t_task_id_e2f118" UNIQUE ("task_id", "executor_id")
);
CREATE TABLE IF NOT EXISTS "establishment_ratings" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "mark" SMALLINT NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "establishment_id" UUID NOT NULL REFERENCES "establishments" ("id") ON DELETE CASCADE,
    "user_id" BIGINT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_establishme_establi_b66005" 
    ON "establishment_ratings" ("establishment_id", "user_id", "created_at" DESC);
CREATE TABLE IF NOT EXISTS "referrals" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "referral_id" BIGINT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE,
    "referrer_id" BIGINT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_referrals_referre_ec3a4e" UNIQUE ("referrer_id", "referral_id")
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
    "employee_id" UUID REFERENCES "employers" ("id") ON DELETE CASCADE,
    "establishment_id" UUID REFERENCES "establishments" ("id") ON DELETE CASCADE,
    "sender_id" BIGINT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE,
    CHECK (employee_id is null AND establishment_id is not null OR employee_id is not null AND establishment_id is null)
);
CREATE INDEX IF NOT EXISTS "idx_tips_status_b521b6" ON "tips" ("status");
COMMENT ON COLUMN "tips"."status" IS 'created: created\naccepted: accepted\nfailed: failed';
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(_: BaseDBAsyncClient) -> str:
    return """
        """

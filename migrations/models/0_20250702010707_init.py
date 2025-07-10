from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "assets" (
    "id" UUID NOT NULL PRIMARY KEY,
    "symbol" VARCHAR(16) NOT NULL UNIQUE,
    "name" VARCHAR(128) NOT NULL,
    "decimals" SMALLINT NOT NULL DEFAULT 9,
    "address" VARCHAR(128) NOT NULL,
    "image_url" TEXT NOT NULL,
    "ton_price" BIGINT NOT NULL DEFAULT 0,
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
    "latitude" DECIMAL(9,6) NOT NULL,
    "longitude" DECIMAL(9,6) NOT NULL,
    "address" VARCHAR(128) NOT NULL,
    "service_wallet" VARCHAR(128),
    "service_wallet_seed" TEXT,
    "official_wallet" VARCHAR(128),
    "name" VARCHAR(128) NOT NULL,
    "description" VARCHAR(512) NOT NULL,
    "channel_link" VARCHAR(512) NOT NULL,
    "icon_hash" TEXT NOT NULL,
    "photo_hash" TEXT NOT NULL,
    "gallery_hashes" JSONB NOT NULL,
    "rating" DECIMAL(3,2) NOT NULL DEFAULT 0,
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
    "purpose" JSONB NOT NULL,
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
CREATE TABLE IF NOT EXISTS "purpose_icons" (
    "id" UUID NOT NULL PRIMARY KEY,
    "preview_hash" TEXT NOT NULL,
    "icon_hash" TEXT NOT NULL,
    "enabled" BOOL NOT NULL DEFAULT True,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS "idx_purpose_ico_enabled_f0ab0d" ON "purpose_icons" ("enabled");
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
CREATE TABLE IF NOT EXISTS "place_ratings" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "mark" SMALLINT NOT NULL,
    "place_id" UUID NOT NULL REFERENCES "establishments" ("id") ON DELETE RESTRICT,
    "user_id" BIGINT NOT NULL REFERENCES "users" ("id") ON DELETE RESTRICT,
    CONSTRAINT "uid_place_ratin_user_id_ec145a" UNIQUE ("user_id", "place_id")
);
CREATE TABLE IF NOT EXISTS "tips" (
    "id" UUID NOT NULL PRIMARY KEY,
    "fee_transaction" JSONB NOT NULL,
    "tip_transaction" JSONB NOT NULL,
    "expired_at" TIMESTAMPTZ NOT NULL,
    "status" VARCHAR(8) NOT NULL DEFAULT 'created',
    "amount" BIGINT NOT NULL,
    "tips_left_amount" BIGINT NOT NULL,
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
);
CREATE TABLE IF NOT EXISTS "establishments_menu_items" (
    "establishments_id" UUID NOT NULL REFERENCES "establishments" ("id") ON DELETE CASCADE,
    "menuitem_id" UUID NOT NULL REFERENCES "menu_items" ("id") ON DELETE CASCADE
);
CREATE UNIQUE INDEX IF NOT EXISTS "uidx_establishme_establi_496c5b" ON "establishments_menu_items" ("establishments_id", "menuitem_id");"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """

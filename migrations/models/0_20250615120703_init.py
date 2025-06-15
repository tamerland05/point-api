from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
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
    "service_wallet" VARCHAR(128) NOT NULL,
    "service_wallet_seed" TEXT NOT NULL,
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
CREATE INDEX IF NOT EXISTS "idx_establishme_enabled_90ab06" ON "establishments" ("enabled");
CREATE TABLE IF NOT EXISTS "employers" (
    "id" UUID NOT NULL PRIMARY KEY,
    "purpose" JSONB,
    "meta" JSONB NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "job_place_id_id" UUID NOT NULL REFERENCES "establishments" ("id") ON DELETE RESTRICT
);
CREATE INDEX IF NOT EXISTS "idx_employers_job_pla_6113ba" ON "employers" ("job_place_id_id");
CREATE TABLE IF NOT EXISTS "menu_items" (
    "id" UUID NOT NULL PRIMARY KEY,
    "title" VARCHAR(128) NOT NULL,
    "description" VARCHAR(128) NOT NULL,
    "photo_hash" TEXT NOT NULL,
    "amount" DECIMAL(64,18) NOT NULL,
    "currency" VARCHAR(8) NOT NULL,
    "enabled" BOOL NOT NULL DEFAULT True,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "establishment_id" UUID NOT NULL REFERENCES "establishments" ("id") ON DELETE RESTRICT,
    CONSTRAINT "uid_menu_items_title_9a00bf" UNIQUE ("title", "establishment_id")
);
CREATE INDEX IF NOT EXISTS "idx_menu_items_enabled_2c09a4" ON "menu_items" ("enabled");
CREATE INDEX IF NOT EXISTS "idx_menu_items_establi_1ef563" ON "menu_items" ("establishment_id");
CREATE TABLE IF NOT EXISTS "users" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "first_name" TEXT NOT NULL,
    "last_name" TEXT NOT NULL,
    "username" TEXT NOT NULL,
    "language_code" TEXT,
    "photo_url" TEXT,
    "is_bot" BOOL NOT NULL,
    "is_premium" BOOL NOT NULL,
    "allows_write_to_pm" BOOL NOT NULL,
    "wallet" TEXT,
    "bonus_balance" BIGINT,
    "tips_left" BIGINT,
    "meta" JSONB NOT NULL,
    "enabled" BOOL NOT NULL DEFAULT True,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "account_id_id" UUID REFERENCES "employers" ("id") ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS "idx_users_enabled_e41084" ON "users" ("enabled");
CREATE TABLE IF NOT EXISTS "place_ratings" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "mark" SMALLINT NOT NULL,
    "place_id" UUID NOT NULL REFERENCES "establishments" ("id") ON DELETE RESTRICT,
    "user_id" BIGINT NOT NULL REFERENCES "users" ("id") ON DELETE RESTRICT,
    CONSTRAINT "uid_place_ratin_user_id_ec145a" UNIQUE ("user_id", "place_id")
);
CREATE INDEX IF NOT EXISTS "idx_place_ratin_place_i_11df0a" ON "place_ratings" ("place_id");
CREATE INDEX IF NOT EXISTS "idx_place_ratin_user_id_c90f7b" ON "place_ratings" ("user_id");
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

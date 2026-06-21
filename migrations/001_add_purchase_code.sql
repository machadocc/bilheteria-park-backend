-- Migration 001: adiciona coluna purchase_code na tabela sales
-- Execute uma vez no banco já existente:
--   psql $DATABASE_URL -f migrations/001_add_purchase_code.sql

DO $$
BEGIN
    -- Adiciona purchase_code se não existir
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'sales' AND column_name = 'purchase_code'
    ) THEN
        ALTER TABLE sales ADD COLUMN purchase_code VARCHAR(64);
        -- Preenche registros existentes com um código único
        UPDATE sales SET purchase_code = UPPER(SUBSTRING(MD5(RANDOM()::TEXT), 1, 12)) WHERE purchase_code IS NULL;
        ALTER TABLE sales ALTER COLUMN purchase_code SET NOT NULL;
        CREATE UNIQUE INDEX IF NOT EXISTS ix_sales_purchase_code ON sales(purchase_code);
    END IF;
END $$;

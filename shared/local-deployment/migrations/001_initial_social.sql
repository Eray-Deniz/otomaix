-- Migration: 001_initial_social.sql
-- Social schema: initial tables

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "vector";

-- Create schema
CREATE SCHEMA IF NOT EXISTS social;

-- 1. accounts
CREATE TABLE IF NOT EXISTS social.accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    name TEXT,
    plan_id TEXT DEFAULT 'starter',
    created_at TIMESTAMPTZ DEFAULT now(),
    last_login_at TIMESTAMPTZ
);

-- 2. workspaces
CREATE TABLE IF NOT EXISTS social.workspaces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID REFERENCES social.accounts(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 3. workspace_members
CREATE TABLE IF NOT EXISTS social.workspace_members (
    workspace_id UUID REFERENCES social.workspaces(id) ON DELETE CASCADE,
    account_id UUID REFERENCES social.accounts(id) ON DELETE CASCADE,
    role TEXT DEFAULT 'owner',
    PRIMARY KEY (workspace_id, account_id)
);

-- 4. brands
CREATE TABLE IF NOT EXISTS social.brands (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID REFERENCES social.workspaces(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    website_url TEXT,
    sector TEXT,
    brand_kit JSONB DEFAULT '{}',
    logo_light_url TEXT,
    logo_dark_url TEXT,
    intro_video_url TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 5. brand_documents
CREATE TABLE IF NOT EXISTS social.brand_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brand_id UUID REFERENCES social.brands(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    file_url TEXT NOT NULL,
    file_type TEXT,
    category TEXT,
    description TEXT,
    file_size_kb INTEGER,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 6. brand_media
CREATE TABLE IF NOT EXISTS social.brand_media (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brand_id UUID REFERENCES social.brands(id) ON DELETE CASCADE,
    name TEXT,
    file_url TEXT NOT NULL,
    media_type TEXT,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 7. brand_social_accounts
CREATE TABLE IF NOT EXISTS social.brand_social_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brand_id UUID REFERENCES social.brands(id) ON DELETE CASCADE,
    platform TEXT NOT NULL,
    account_name TEXT,
    upload_post_token TEXT,
    is_active BOOLEAN DEFAULT true,
    connected_at TIMESTAMPTZ DEFAULT now()
);

-- 8. posts
CREATE TABLE IF NOT EXISTS social.posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brand_id UUID REFERENCES social.brands(id) ON DELETE CASCADE,
    content_type TEXT,
    content_category TEXT,
    status TEXT DEFAULT 'draft',
    prompt TEXT,
    user_text TEXT,
    document_ids UUID[],
    media_ids UUID[],
    output_url TEXT,
    thumbnail_url TEXT,
    caption TEXT,
    hashtags TEXT[],
    aspect_ratio TEXT,
    platforms TEXT[],
    scheduled_at TIMESTAMPTZ,
    published_at TIMESTAMPTZ,
    fal_job_id TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- 9. public_holidays
CREATE TABLE IF NOT EXISTS social.public_holidays (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    year INTEGER NOT NULL,
    date DATE NOT NULL,
    name_tr TEXT NOT NULL,
    name_en TEXT,
    category TEXT,
    UNIQUE(year, date)
);

-- Vector column for brand_documents (RAG)
ALTER TABLE social.brand_documents ADD COLUMN IF NOT EXISTS embedding vector(1536);

-- updated_at trigger for posts
CREATE OR REPLACE FUNCTION social.set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS posts_updated_at ON social.posts;
CREATE TRIGGER posts_updated_at
    BEFORE UPDATE ON social.posts
    FOR EACH ROW EXECUTE FUNCTION social.set_updated_at();

-- Indexes
CREATE INDEX IF NOT EXISTS idx_brands_workspace_id ON social.brands(workspace_id);
CREATE INDEX IF NOT EXISTS idx_posts_brand_id ON social.posts(brand_id);
CREATE INDEX IF NOT EXISTS idx_posts_status ON social.posts(status);
CREATE INDEX IF NOT EXISTS idx_posts_scheduled_at ON social.posts(scheduled_at);

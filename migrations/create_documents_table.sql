-- ==============================================================================
-- AI-Enhanced Document Generator - Day 3 Database Migration
-- Table: documents
-- ==============================================================================

-- 1. Enable UUID Extension (standard in PostgreSQL / Supabase)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 2. Create documents table
CREATE TABLE IF NOT EXISTS public.documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    title TEXT NOT NULL CHECK (char_length(trim(title)) > 0),
    document_type TEXT NOT NULL CHECK (char_length(trim(document_type)) > 0),
    content JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'completed', 'archived'))
);

-- 3. Indexes for fast user-scoped retrieval and chronological ordering
CREATE INDEX IF NOT EXISTS idx_documents_user_id ON public.documents(user_id);
CREATE INDEX IF NOT EXISTS idx_documents_updated_at ON public.documents(updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_documents_user_updated ON public.documents(user_id, updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_documents_type ON public.documents(user_id, document_type);

-- 4. Automatic updated_at trigger function
CREATE OR REPLACE FUNCTION public.handle_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = timezone('utc'::text, now());
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 5. Attach trigger to documents table
DROP TRIGGER IF EXISTS trigger_documents_updated_at ON public.documents;
CREATE TRIGGER trigger_documents_updated_at
    BEFORE UPDATE ON public.documents
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_updated_at();

-- 6. Enable Row Level Security (RLS)
ALTER TABLE public.documents ENABLE ROW LEVEL SECURITY;

-- 7. Define RLS Policies (strictly user-scoped using auth.uid())

-- Policy 1: SELECT - Users can only view their own documents
DROP POLICY IF EXISTS "Users can read own documents" ON public.documents;
CREATE POLICY "Users can read own documents"
    ON public.documents
    FOR SELECT
    USING (auth.uid() = user_id);

-- Policy 2: INSERT - Users can only create documents owned by themselves
DROP POLICY IF EXISTS "Users can insert own documents" ON public.documents;
CREATE POLICY "Users can insert own documents"
    ON public.documents
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Policy 3: UPDATE - Users can only update their own documents
DROP POLICY IF EXISTS "Users can update own documents" ON public.documents;
CREATE POLICY "Users can update own documents"
    ON public.documents
    FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- Policy 4: DELETE - Users can only delete their own documents
DROP POLICY IF EXISTS "Users can delete own documents" ON public.documents;
CREATE POLICY "Users can delete own documents"
    ON public.documents
    FOR DELETE
    USING (auth.uid() = user_id);

-- Documentation comment on public.documents
COMMENT ON TABLE public.documents IS 'Stores AI-generated and user-edited documents with Row Level Security (RLS) enforced.';

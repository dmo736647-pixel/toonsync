-- Dev-only: allow anonymous access to storyboard-related tables

ALTER TABLE public.scenes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.generated_assets ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "dev_allow_all_scenes" ON public.scenes;
CREATE POLICY "dev_allow_all_scenes" ON public.scenes
  FOR ALL
  USING (true)
  WITH CHECK (true);

DROP POLICY IF EXISTS "dev_allow_all_generated_assets" ON public.generated_assets;
CREATE POLICY "dev_allow_all_generated_assets" ON public.generated_assets
  FOR ALL
  USING (true)
  WITH CHECK (true);


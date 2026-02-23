alter table public.characters
  add column if not exists consistency_model_url text;

alter table public.characters
  add column if not exists style text;

update public.characters
  set style = 'anime'
  where style is null;

alter table public.characters
  alter column style set default 'anime';

do $$
begin
  if not exists (
    select 1
    from pg_constraint
    where conname = 'characters_style_check'
  ) then
    alter table public.characters
      add constraint characters_style_check
      check (style in ('anime', 'realistic'));
  end if;
end $$;

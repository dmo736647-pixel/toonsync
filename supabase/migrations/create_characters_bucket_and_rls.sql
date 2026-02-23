-- Storage bucket: characters
insert into storage.buckets (id, name, public)
values ('characters', 'characters', true)
on conflict (id) do update set public = excluded.public;

-- RLS policies: public.characters
do $$
begin
  if not exists (
    select 1
    from pg_policies
    where schemaname = 'public'
      and tablename = 'characters'
      and policyname = 'characters_select_own_project'
  ) then
    create policy characters_select_own_project
      on public.characters
      for select
      to authenticated
      using (
        exists (
          select 1
          from public.projects p
          where p.id = public.characters.project_id
            and p.user_id = auth.uid()
        )
      );
  end if;

  if not exists (
    select 1
    from pg_policies
    where schemaname = 'public'
      and tablename = 'characters'
      and policyname = 'characters_insert_own_project'
  ) then
    create policy characters_insert_own_project
      on public.characters
      for insert
      to authenticated
      with check (
        exists (
          select 1
          from public.projects p
          where p.id = public.characters.project_id
            and p.user_id = auth.uid()
        )
      );
  end if;

  if not exists (
    select 1
    from pg_policies
    where schemaname = 'public'
      and tablename = 'characters'
      and policyname = 'characters_update_own_project'
  ) then
    create policy characters_update_own_project
      on public.characters
      for update
      to authenticated
      using (
        exists (
          select 1
          from public.projects p
          where p.id = public.characters.project_id
            and p.user_id = auth.uid()
        )
      )
      with check (
        exists (
          select 1
          from public.projects p
          where p.id = public.characters.project_id
            and p.user_id = auth.uid()
        )
      );
  end if;

  if not exists (
    select 1
    from pg_policies
    where schemaname = 'public'
      and tablename = 'characters'
      and policyname = 'characters_delete_own_project'
  ) then
    create policy characters_delete_own_project
      on public.characters
      for delete
      to authenticated
      using (
        exists (
          select 1
          from public.projects p
          where p.id = public.characters.project_id
            and p.user_id = auth.uid()
        )
      );
  end if;
end $$;

-- RLS policies: storage.objects for bucket 'characters'
do $$
begin
  if not exists (
    select 1
    from pg_policies
    where schemaname = 'storage'
      and tablename = 'objects'
      and policyname = 'characters_bucket_select_own_project'
  ) then
    create policy characters_bucket_select_own_project
      on storage.objects
      for select
      to authenticated
      using (
        bucket_id = 'characters'
        and exists (
          select 1
          from public.projects p
          where p.id = split_part(name, '/', 1)::uuid
            and p.user_id = auth.uid()
        )
      );
  end if;

  if not exists (
    select 1
    from pg_policies
    where schemaname = 'storage'
      and tablename = 'objects'
      and policyname = 'characters_bucket_insert_own_project'
  ) then
    create policy characters_bucket_insert_own_project
      on storage.objects
      for insert
      to authenticated
      with check (
        bucket_id = 'characters'
        and exists (
          select 1
          from public.projects p
          where p.id = split_part(name, '/', 1)::uuid
            and p.user_id = auth.uid()
        )
      );
  end if;

  if not exists (
    select 1
    from pg_policies
    where schemaname = 'storage'
      and tablename = 'objects'
      and policyname = 'characters_bucket_update_own_project'
  ) then
    create policy characters_bucket_update_own_project
      on storage.objects
      for update
      to authenticated
      using (
        bucket_id = 'characters'
        and exists (
          select 1
          from public.projects p
          where p.id = split_part(name, '/', 1)::uuid
            and p.user_id = auth.uid()
        )
      )
      with check (
        bucket_id = 'characters'
        and exists (
          select 1
          from public.projects p
          where p.id = split_part(name, '/', 1)::uuid
            and p.user_id = auth.uid()
        )
      );
  end if;

  if not exists (
    select 1
    from pg_policies
    where schemaname = 'storage'
      and tablename = 'objects'
      and policyname = 'characters_bucket_delete_own_project'
  ) then
    create policy characters_bucket_delete_own_project
      on storage.objects
      for delete
      to authenticated
      using (
        bucket_id = 'characters'
        and exists (
          select 1
          from public.projects p
          where p.id = split_part(name, '/', 1)::uuid
            and p.user_id = auth.uid()
        )
      );
  end if;
end $$;


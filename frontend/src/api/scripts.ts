import { supabase } from '@/lib/supabase';
import type { Script } from '../types';

export const scriptsApi = {
  async getScriptByProjectId(projectId: string): Promise<Script | null> {
    const { data, error } = await supabase
      .from('scripts')
      .select('*')
      .eq('project_id', projectId)
      .single();

    if (error && error.code !== 'PGRST116') { // PGRST116 is "The result contains 0 rows"
      throw error;
    }

    return data;
  },

  async createScript(projectId: string, content: string = ''): Promise<Script> {
    const { data, error } = await supabase
      .from('scripts')
      .insert([
        {
          project_id: projectId,
          content: content,
          version: 1
        }
      ])
      .select()
      .single();

    if (error) {
      throw error;
    }

    return data;
  },

  async updateScript(id: string, content: string): Promise<Script> {
    const { data, error } = await supabase
      .from('scripts')
      .update({
        content: content,
        updated_at: new Date().toISOString()
      })
      .eq('id', id)
      .select()
      .single();

    if (error) {
      throw error;
    }

    return data;
  }
};

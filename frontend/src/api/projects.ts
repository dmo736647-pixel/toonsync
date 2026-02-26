import { supabase } from '@/lib/supabase';
import type { Project } from '../types';

export interface CreateProjectRequest {
  title: string;
  description?: string;
  cover_image?: string;
}

export const projectsApi = {
  async getProjects(): Promise<Project[]> {
    const { data, error } = await supabase
      .from('projects')
      .select('*')
      .order('created_at', { ascending: false });

    if (error) {
      throw error;
    }

    return data || [];
  },

  async getProject(id: string): Promise<Project> {
    const { data, error } = await supabase
      .from('projects')
      .select('*')
      .eq('id', id)
      .single();

    if (error) {
      throw error;
    }

    return data;
  },

  async createProject(projectData: CreateProjectRequest): Promise<Project> {
    const { data: { user } } = await supabase.auth.getUser();
    
    if (!user) {
      throw new Error('User not authenticated');
    }

    const { data, error } = await supabase
      .from('projects')
      .insert([
        {
          title: projectData.title,
          description: projectData.description,
          cover_image: projectData.cover_image,
          user_id: user.id,
          status: 'draft'
        }
      ])
      .select()
      .single();

    if (error) {
      throw error;
    }

    return data;
  },

  async updateProject(id: string, updates: Partial<CreateProjectRequest>): Promise<Project> {
    const { data, error } = await supabase
      .from('projects')
      .update(updates)
      .eq('id', id)
      .select()
      .single();

    if (error) {
      throw error;
    }

    return data;
  },

  async deleteProject(id: string): Promise<void> {
    const { error } = await supabase
      .from('projects')
      .delete()
      .eq('id', id);

    if (error) {
      throw error;
    }
  },
};

import { supabase } from '../lib/supabase';
import apiClient from './client';
import type { Storyboard } from '../types';

export interface CreateStoryboardRequest {
  project_id: string;
  character_id?: string; // Optional in Scene
  description: string;
  style?: 'anime' | 'realistic';
}

export interface UpdateStoryboardRequest {
  description?: string;
  frame_number?: number;
}

export const storyboardApi = {
  async getStoryboards(projectId: string): Promise<Storyboard[]> {
    const { data: scenes, error } = await supabase
      .from('scenes')
      .select('*, generated_assets(url, created_at)')
      .eq('project_id', projectId)
      .order('sequence_number', { ascending: true });

    if (error) {
      throw error;
    }

    return scenes.map((scene: any) => {
      const assets = scene.generated_assets || [];
      const latestAsset = assets.sort((a: any, b: any) =>
        new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      )[0];

      return {
        id: scene.id,
        project_id: scene.project_id,
        frame_number: scene.sequence_number,
        description: scene.description,
        image_url: latestAsset?.url || '',
        created_at: scene.created_at
      };
    });
  },

  async getStoryboard(id: string): Promise<Storyboard> {
    const { data: scene, error } = await supabase
      .from('scenes')
      .select('*, generated_assets(url, created_at)')
      .eq('id', id)
      .single();

    if (error) {
      throw error;
    }

    const assets = scene.generated_assets || [];
    const latestAsset = assets.sort((a: any, b: any) =>
      new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    )[0];

    return {
      id: scene.id,
      project_id: scene.project_id,
      frame_number: scene.sequence_number,
      description: scene.description,
      image_url: latestAsset?.url || '',
      created_at: scene.created_at
    };
  },

  async createStoryboard(data: CreateStoryboardRequest): Promise<Storyboard> {
    const { data: maxSeq, error: maxSeqError } = await supabase
      .from('scenes')
      .select('sequence_number')
      .eq('project_id', data.project_id)
      .order('sequence_number', { ascending: false })
      .limit(1)
      .maybeSingle();

    if (maxSeqError) {
      throw maxSeqError;
    }

    const nextSeq = (maxSeq?.sequence_number || 0) + 1;

    const { data: newScene, error } = await supabase
      .from('scenes')
      .insert([
        {
          project_id: data.project_id,
          description: data.description,
          sequence_number: nextSeq,
          status: 'pending',
          character_ids: data.character_id ? [data.character_id] : []
        }
      ])
      .select()
      .single();

    if (error) {
      throw error;
    }

    return {
      id: newScene.id,
      project_id: newScene.project_id,
      frame_number: newScene.sequence_number,
      description: newScene.description,
      image_url: '',
      created_at: newScene.created_at
    };
  },

  async updateStoryboard(id: string, data: UpdateStoryboardRequest): Promise<Storyboard> {
    const updates: any = {};
    if (data.description) updates.description = data.description;
    if (data.frame_number) updates.sequence_number = data.frame_number;

    const { data: updatedScene, error } = await supabase
      .from('scenes')
      .update(updates)
      .eq('id', id)
      .select()
      .single();

    if (error) {
      throw error;
    }

    return {
      id: updatedScene.id,
      project_id: updatedScene.project_id,
      frame_number: updatedScene.sequence_number,
      description: updatedScene.description,
      image_url: '',
      created_at: updatedScene.created_at
    };
  },

  async deleteStoryboard(id: string): Promise<void> {
    const { error } = await supabase
      .from('scenes')
      .delete()
      .eq('id', id);

    if (error) {
      throw error;
    }
  },

  async reorderStoryboards(_projectId: string, frameOrders: { id: string; frame_number: number }[]): Promise<void> {
    // Supabase doesn't support bulk update easily in client, so we loop (not ideal for large lists but fine for MVP)
    // Or we could use an RPC function if we created one.
    
    const updates = frameOrders.map(({ id, frame_number }) => 
      supabase.from('scenes').update({ sequence_number: frame_number }).eq('id', id)
    );

    await Promise.all(updates);
  },

  async generateImage(id: string, characterId?: string, style: string = 'anime', referenceImageUrl?: string): Promise<{ image_url: string }> {
    const storyboard = await this.getStoryboard(id);

    const formData = new FormData();

    const charId = characterId;
    if (!charId) {
      throw new Error('Character ID is required');
    }

    formData.append('character_id', charId);
    formData.append('scene_description', storyboard.description);
    formData.append('style', style);
    if (referenceImageUrl) {
      formData.append('reference_image_url', referenceImageUrl);
    }

    const response = await apiClient.post('/character-consistency/generate-frame', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    const frameUrl = response.data.frame_url;

    const { error } = await supabase
      .from('generated_assets')
      .insert([
        {
          project_id: storyboard.project_id,
          scene_id: id,
          type: 'image',
          url: frameUrl,
          prompt: storyboard.description,
          model_used: 'character-consistency'
        }
      ]);

    if (error) {
      throw error;
    }

    await supabase.from('scenes').update({ status: 'completed' }).eq('id', id);

    return { image_url: frameUrl };
  },
};

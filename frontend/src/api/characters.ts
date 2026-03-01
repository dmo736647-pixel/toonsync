import { supabase } from '@/lib/supabase.ts';
import type { Character } from '../types';

export interface CreateCharacterRequest {
  name: string;
  project_id: string;
  description?: string;
  age?: number;
  gender?: string;
  image_file?: File;
}

export interface UpdateCharacterRequest {
  name?: string;
  description?: string;
  age?: number;
  gender?: string;
}

export const charactersApi = {
  async getCharacters(projectId?: string): Promise<Character[]> {
    let query = supabase.from('characters').select('*');
    
    if (projectId) {
      query = query.eq('project_id', projectId);
    }
    
    const { data, error } = await query.order('created_at', { ascending: false });

    if (error) {
      throw error;
    }

    return data || [];
  },

  async getCharacter(id: string): Promise<Character> {
    const { data, error } = await supabase
      .from('characters')
      .select('*')
      .eq('id', id)
      .single();

    if (error) {
      throw error;
    }

    return data;
  },

  async createCharacter(data: CreateCharacterRequest): Promise<Character> {
    let imageUrl = null;

    // Upload image if provided
    if (data.image_file) {
      try {
        const fileExt = data.image_file.name.split('.').pop();
        const id = typeof crypto !== 'undefined' && 'randomUUID' in crypto ? crypto.randomUUID() : String(Math.random()).slice(2);
        const fileName = `${id}.${fileExt}`;
        const filePath = `${data.project_id}/${fileName}`;

        const { error: uploadError } = await supabase.storage
          .from('characters')
          .upload(filePath, data.image_file, { contentType: data.image_file.type, upsert: false });

        if (uploadError) {
          console.error('Storage upload error:', uploadError);
          // 如果存储桶不存在，使用备用方案：将图片转为 base64 存储（不推荐用于生产）
          imageUrl = await new Promise((resolve) => {
            const reader = new FileReader();
            reader.onloadend = () => resolve(reader.result as string);
            reader.readAsDataURL(data.image_file!);
          });
        } else {
          const { data: { publicUrl } } = supabase.storage
            .from('characters')
            .getPublicUrl(filePath);
          imageUrl = publicUrl;
        }
      } catch (uploadErr) {
        console.error('Upload exception:', uploadErr);
        // 备用方案
        imageUrl = await new Promise((resolve) => {
          const reader = new FileReader();
          reader.onloadend = () => resolve(reader.result as string);
          reader.readAsDataURL(data.image_file!);
        });
      }
    }

    // 获取当前用户 ID
    const { data: { user } } = await supabase.auth.getUser();
    if (!user) {
      throw new Error('User not authenticated');
    }

    const { data: newCharacter, error } = await supabase
      .from('characters')
      .insert([
        {
          name: data.name,
          project_id: data.project_id,
          description: data.description,
          age: data.age,
          gender: data.gender,
          reference_image_url: imageUrl,
          user_id: user.id
        }
      ])
      .select()
      .single();

    if (error) {
      console.error('Character creation error:', error);
      throw error;
    }

    return newCharacter;
  },

  async updateCharacter(id: string, updates: UpdateCharacterRequest): Promise<Character> {
    const { data, error } = await supabase
      .from('characters')
      .update(updates)
      .eq('id', id)
      .select()
      .single();

    if (error) {
      throw error;
    }

    return data;
  },

  async deleteCharacter(id: string): Promise<void> {
    const { error } = await supabase
      .from('characters')
      .delete()
      .eq('id', id);

    if (error) {
      throw error;
    }
  },

  async extractFeatures(id: string): Promise<{ consistency_model_url: string }> {
    const { data: character, error: characterError } = await supabase
      .from('characters')
      .select('id, project_id, reference_image_url')
      .eq('id', id)
      .single();

    if (characterError) {
      throw characterError;
    }

    if (!character?.reference_image_url) {
      throw new Error('缺少角色参考图，无法提取特征');
    }

    const resp = await fetch(character.reference_image_url);
    if (!resp.ok) {
      throw new Error('下载参考图失败，无法提取特征');
    }

    const imageBlob = await resp.blob();

    const img = await new Promise<HTMLImageElement>((resolve, reject) => {
      const image = new Image();
      const objectUrl = URL.createObjectURL(imageBlob);
      image.crossOrigin = 'anonymous';
      image.onload = () => {
        URL.revokeObjectURL(objectUrl);
        resolve(image);
      };
      image.onerror = () => {
        URL.revokeObjectURL(objectUrl);
        reject(new Error('解析参考图失败，无法提取特征'));
      };
      image.src = objectUrl;
    });

    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    if (!ctx) {
      throw new Error('浏览器不支持Canvas，无法提取特征');
    }

    const targetSize = 256;
    canvas.width = targetSize;
    canvas.height = targetSize;
    ctx.drawImage(img, 0, 0, targetSize, targetSize);

    const { data } = ctx.getImageData(0, 0, targetSize, targetSize);
    let sumR = 0;
    let sumG = 0;
    let sumB = 0;
    let sumR2 = 0;
    let sumG2 = 0;
    let sumB2 = 0;
    const pixels = data.length / 4;

    for (let i = 0; i < data.length; i += 4) {
      const r = data[i];
      const g = data[i + 1];
      const b = data[i + 2];

      sumR += r;
      sumG += g;
      sumB += b;
      sumR2 += r * r;
      sumG2 += g * g;
      sumB2 += b * b;
    }

    const meanR = sumR / pixels;
    const meanG = sumG / pixels;
    const meanB = sumB / pixels;
    const stdR = Math.sqrt(sumR2 / pixels - meanR * meanR);
    const stdG = Math.sqrt(sumG2 / pixels - meanG * meanG);
    const stdB = Math.sqrt(sumB2 / pixels - meanB * meanB);

    const model = {
      character_id: character.id,
      reference_image_url: character.reference_image_url,
      style: 'anime',
      created_at: new Date().toISOString(),
      facial_features: {
        mean_color: [meanR, meanG, meanB],
        std_color: [stdR, stdG, stdB],
      },
      clothing_features: {
        color_palette: [
          [meanR, meanG, meanB],
        ],
      },
    };

    const modelPath = `${character.project_id}/models/${character.id}.json`;
    const { error: uploadError } = await supabase.storage
      .from('characters')
      .upload(modelPath, new Blob([JSON.stringify(model)], { type: 'application/json' }), {
        contentType: 'application/json',
        upsert: true,
      });

    if (uploadError) {
      throw uploadError;
    }

    const { data: publicUrlData } = supabase.storage
      .from('characters')
      .getPublicUrl(modelPath);

    const consistencyModelUrl = publicUrlData.publicUrl;

    const { error: updateError } = await supabase
      .from('characters')
      .update({ consistency_model_url: consistencyModelUrl, style: 'anime' })
      .eq('id', id);

    if (updateError) {
      throw updateError;
    }

    return { consistency_model_url: consistencyModelUrl };
  },
};

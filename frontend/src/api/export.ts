import apiClient from './client';

export interface ExportConfig {
  resolution: '720p' | '1080p' | '4k';
  format: 'mp4' | 'mov';
  aspect_ratio: '9:16' | '16:9' | '1:1';
}

export interface ExportHistory {
  id: string;
  created_at: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  config: ExportConfig;
  video_url?: string;
  duration?: number;
  file_size?: number;
  cost?: number;
}

export const exportApi = {
  async estimateCost(projectId: string, config: ExportConfig): Promise<{ estimated_cost: number }> {
    const response = await apiClient.post(`/projects/${projectId}/export/estimate`, config);
    return response.data;
  },

  async startExport(projectId: string, config: ExportConfig): Promise<{ export_id: string }> {
    const response = await apiClient.post(`/projects/${projectId}/export`, config);
    return response.data;
  },

  async getExportHistory(projectId: string): Promise<ExportHistory[]> {
    const response = await apiClient.get(`/projects/${projectId}/exports`);
    return response.data;
  },

  async getExport(exportId: string): Promise<ExportHistory> {
    const response = await apiClient.get(`/exports/${exportId}`);
    return response.data;
  },
};

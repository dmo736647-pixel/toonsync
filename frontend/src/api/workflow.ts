import apiClient from './client';
import type { Workflow } from '../types';

export interface StartWorkflowRequest {
  project_id: string;
}

export const workflowApi = {
  async getWorkflow(projectId: string): Promise<Workflow> {
    const response = await apiClient.get(`/projects/${projectId}/workflow`);
    return response.data;
  },

  async startWorkflow(data: StartWorkflowRequest): Promise<Workflow> {
    const response = await apiClient.post('/workflows/start_from_project', {
      project_id: data.project_id,
      auto_mode: true
    });
    return response.data;
  },

  async pauseWorkflow(workflowId: string): Promise<Workflow> {
    const response = await apiClient.post(`/workflows/${workflowId}/pause`);
    return response.data;
  },

  async resumeWorkflow(workflowId: string): Promise<Workflow> {
    const response = await apiClient.post(`/workflows/${workflowId}/resume`);
    return response.data;
  },

  async cancelWorkflow(workflowId: string): Promise<void> {
    await apiClient.post(`/workflows/${workflowId}/cancel`);
  },
};

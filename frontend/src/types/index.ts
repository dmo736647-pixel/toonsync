// 用户类型
export interface User {
  id: string;
  email: string;
  username: string;
  subscription_tier: 'free' | 'pay_as_you_go' | 'professional' | 'enterprise';
  created_at: string;
}

// 项目类型
export interface Project {
  id: string;
  user_id: string; // Changed from owner_id
  title: string;   // Changed from name
  name?: string;
  description?: string;
  cover_image?: string; // Added
  status: 'draft' | 'processing' | 'completed'; // Updated status values to match DB
  created_at: string;
  updated_at: string;
  
  // Optional fields for UI display that might be calculated or joined
  scenes_count?: number;
  duration?: string;
  thumbnail?: string; // Can map to cover_image
  gradient?: string;
}

// 角色类型
export interface Character {
  id: string;
  project_id: string;
  name: string;
  description?: string;
  age?: number;
  gender?: string;
  reference_image_url?: string;
  consistency_model_url?: string;
  style?: 'anime' | 'realistic';
  lora_model_id?: string;
  created_at: string;
}

// 剧本类型
export interface Script {
  id: string;
  project_id: string;
  content: any; // JSON or HTML
  version: number;
  created_at: string;
  updated_at: string;
}

// 场景类型
export interface Scene {
  id: string;
  project_id: string;
  script_id?: string;
  sequence_number: number;
  description: string;
  dialogue?: string;
  character_ids?: string[];
  background_desc?: string;
  status: 'pending' | 'generating' | 'completed' | 'failed';
  created_at: string;
}

export interface Storyboard {
  id: string;
  project_id: string;
  frame_number: number;
  description: string;
  image_url: string;
  created_at: string;
}

export interface Workflow {
  id: string;
  workflow_id: string;
  user_id: string;
  project_id?: string;
  created_at: string;
  updated_at: string;
  status: string;
  current_step: string;
  progress: number;
  config: any;
  error_message?: string | null;
}

// 生成资产类型
export interface GeneratedAsset {
  id: string;
  project_id: string;
  scene_id?: string;
  type: 'image' | 'video' | 'audio';
  url: string;
  prompt?: string;
  model_used?: string;
  duration?: number;
  created_at: string;
}

// 错误响应类型
export interface ErrorResponse {
  error: {
    code: number;
    message: string;
    category: string;
    details?: string;
    solutions?: Array<{
      title: string;
      description: string;
      steps?: string[];
      documentation_url?: string;
    }>;
  };
}

// WebSocket消息类型
export interface WebSocketMessage {
  type: 'progress' | 'status' | 'error' | 'success' | 'info';
  message: string;
  data?: any;
  error?: ErrorResponse['error'];
  timestamp: string;
}

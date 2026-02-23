import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { workflowApi } from '../../api/workflow';
import { projectsApi } from '../../api/projects';
import type { Workflow, Project } from '../../types';
import { ProgressBar } from '../../components/feedback/ProgressBar';
import { useWebSocket } from '../../hooks/useWebSocket';

const WORKFLOW_STEPS = [
  { id: 'script', name: '剧本解析', icon: '📝', description: '分析剧本内容' },
  { id: 'characters', name: '角色提取', icon: '👤', description: '提取角色特征' },
  { id: 'storyboard', name: '分镜生成', icon: '🎬', description: '生成分镜图像' },
  { id: 'lip_sync', name: '口型同步', icon: '🗣️', description: '同步音频和口型' },
  { id: 'sound_effects', name: '音效匹配', icon: '🎵', description: '添加背景音效' },
  { id: 'rendering', name: '视频渲染', icon: '🎥', description: '合成最终视频' },
  { id: 'export', name: '导出完成', icon: '✅', description: '准备下载' },
];

export function WorkflowPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();

  const [project, setProject] = useState<Project | null>(null);
  const [workflow, setWorkflow] = useState<Workflow | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const { messages, connected } = useWebSocket('/feedback');

  useEffect(() => {
    if (projectId) {
      loadData();
    }
  }, [projectId]);

  useEffect(() => {
    // Handle WebSocket updates
    messages.forEach(msg => {
      if (msg.type === 'progress' && msg.data?.workflow_id === workflow?.id) {
        setWorkflow(prev => prev ? {
          ...prev,
          progress: msg.data.percentage,
          current_step: msg.data.step,
        } : null);
      } else if (msg.type === 'status' && msg.data?.workflow_id === workflow?.id) {
        setWorkflow(prev => prev ? {
          ...prev,
          status: msg.data.status,
        } : null);
      }
    });
  }, [messages, workflow?.id]);

  const loadData = async () => {
    if (!projectId) return;

    try {
      const projectData = await projectsApi.getProject(projectId);
      setProject(projectData);

      try {
        const workflowData = await workflowApi.getWorkflow(projectId);
        setWorkflow(workflowData);
      } catch (err: any) {
        // Workflow might not exist yet
        if (err.response?.status !== 404) {
          throw err;
        }
      }
    } catch (err: any) {
      setError('加载失败');
    } finally {
      setLoading(false);
    }
  };

  const handleStart = async () => {
    if (!projectId) return;

    try {
      const newWorkflow = await workflowApi.startWorkflow({ project_id: projectId });
      setWorkflow(newWorkflow);
    } catch (err: any) {
      alert('启动失败：' + (err.response?.data?.detail || '未知错误'));
    }
  };

  const handlePause = async () => {
    if (!workflow) return;

    try {
      const updated = await workflowApi.pauseWorkflow(workflow.id);
      setWorkflow(updated);
    } catch (err: any) {
      alert('暂停失败：' + (err.response?.data?.detail || '未知错误'));
    }
  };

  const handleResume = async () => {
    if (!workflow) return;

    try {
      const updated = await workflowApi.resumeWorkflow(workflow.id);
      setWorkflow(updated);
    } catch (err: any) {
      alert('继续失败：' + (err.response?.data?.detail || '未知错误'));
    }
  };

  const handleCancel = async () => {
    if (!workflow || !confirm('确定要取消工作流吗？')) return;

    try {
      await workflowApi.cancelWorkflow(workflow.id);
      setWorkflow(prev => prev ? { ...prev, status: 'failed' } : null);
    } catch (err: any) {
      alert('取消失败：' + (err.response?.data?.detail || '未知错误'));
    }
  };

  const getCurrentStepIndex = () => {
    if (!workflow) return -1;
    return WORKFLOW_STEPS.findIndex(step => step.id === workflow.current_step);
  };

  const getStepStatus = (index: number) => {
    const currentIndex = getCurrentStepIndex();
    if (index < currentIndex) return 'completed';
    if (index === currentIndex) return 'current';
    return 'pending';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-600">加载中...</div>
      </div>
    );
  }

  if (error || !project) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {error || '项目不存在'}
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-5xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">{project.title || project.name} - 工作流</h1>
        <p className="text-gray-600 mt-2">自动化制作流程</p>
      </div>

      {/* WebSocket Connection Status */}
      {!connected && workflow?.status === 'in_progress' && (
        <div className="bg-yellow-50 border border-yellow-200 text-yellow-700 px-4 py-3 rounded-lg mb-6">
          ⚠️ 实时连接已断开，正在重新连接...
        </div>
      )}

      {/* Workflow Status Card */}
      <div className="bg-white rounded-xl shadow-md p-8 mb-8">
        {!workflow ? (
          <div className="text-center py-8">
            <div className="text-gray-400 text-6xl mb-4">🚀</div>
            <h3 className="text-xl font-semibold text-gray-700 mb-2">准备启动工作流</h3>
            <p className="text-gray-500 mb-6">
              工作流将自动完成从剧本到视频的全部制作流程
            </p>
            <button
              onClick={handleStart}
              className="bg-blue-600 text-white px-8 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors"
            >
              启动工作流
            </button>
          </div>
        ) : (
          <div>
            <div className="flex justify-between items-center mb-6">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">
                  {workflow.status === 'completed' ? '工作流已完成' :
                   workflow.status === 'failed' ? '工作流失败' :
                   workflow.status === 'in_progress' ? '工作流进行中' :
                   '工作流已暂停'}
                </h2>
                <p className="text-gray-600 mt-1">
                  创建于 {new Date(workflow.created_at).toLocaleString('zh-CN')}
                </p>
              </div>
              <div className="flex gap-3">
                {workflow.status === 'in_progress' && (
                  <>
                    <button
                      onClick={handlePause}
                      className="px-4 py-2 border border-gray-300 rounded-lg font-medium text-gray-700 hover:bg-gray-50 transition-colors"
                    >
                      ⏸️ 暂停
                    </button>
                    <button
                      onClick={handleCancel}
                      className="px-4 py-2 border border-red-300 rounded-lg font-medium text-red-700 hover:bg-red-50 transition-colors"
                    >
                      ✕ 取消
                    </button>
                  </>
                )}
                {workflow.status === 'pending' && (
                  <button
                    onClick={handleResume}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
                  >
                    ▶️ 继续
                  </button>
                )}
                {workflow.status === 'completed' && (
                  <button
                    onClick={() => navigate(`/export/${projectId}`)}
                    className="px-4 py-2 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 transition-colors"
                  >
                    查看导出 →
                  </button>
                )}
              </div>
            </div>

            {/* Overall Progress */}
            <div className="mb-8">
              <ProgressBar
                percentage={workflow.progress}
                status={workflow.status === 'completed' ? '已完成' :
                       workflow.status === 'failed' ? '失败' :
                       workflow.status === 'in_progress' ? '进行中' :
                       '已暂停'}
                description="总体进度"
              />
            </div>

            {/* Workflow Steps */}
            <div className="space-y-4">
              {WORKFLOW_STEPS.map((step, index) => {
                const status = getStepStatus(index);
                return (
                  <div
                    key={step.id}
                    className={`flex items-center p-4 rounded-lg border-2 transition-all ${
                      status === 'completed'
                        ? 'border-green-200 bg-green-50'
                        : status === 'current'
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 bg-gray-50'
                    }`}
                  >
                    <div className="text-4xl mr-4">{step.icon}</div>
                    <div className="flex-1">
                      <h3 className={`text-lg font-semibold ${
                        status === 'completed' ? 'text-green-900' :
                        status === 'current' ? 'text-blue-900' :
                        'text-gray-700'
                      }`}>
                        {step.name}
                      </h3>
                      <p className={`text-sm ${
                        status === 'completed' ? 'text-green-700' :
                        status === 'current' ? 'text-blue-700' :
                        'text-gray-500'
                      }`}>
                        {step.description}
                      </p>
                    </div>
                    <div>
                      {status === 'completed' && (
                        <span className="text-green-600 text-2xl">✓</span>
                      )}
                      {status === 'current' && workflow.status === 'in_progress' && (
                        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
                      )}
                      {status === 'pending' && (
                        <span className="text-gray-400 text-2xl">○</span>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {/* Info Card */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h4 className="font-medium text-blue-900 mb-3">💡 工作流说明</h4>
        <ul className="text-sm text-blue-800 space-y-2">
          <li>• <strong>自动执行</strong>：各环节自动触发，无需手动操作</li>
          <li>• <strong>数据传递</strong>：环节间自动传递数据</li>
          <li>• <strong>断点续传</strong>：可随时暂停和继续</li>
          <li>• <strong>实时反馈</strong>：通过WebSocket实时更新进度</li>
          <li>• <strong>错误处理</strong>：失败时会显示详细错误信息</li>
        </ul>
      </div>
    </div>
  );
}

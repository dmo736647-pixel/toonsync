import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { exportApi } from '../../api/export';
import { projectsApi } from '../../api/projects';
import type { Project } from '../../types';
import { ProgressBar } from '../../components/feedback/ProgressBar';
import { useWebSocket } from '../../hooks/useWebSocket';

interface ExportConfig {
  resolution: '720p' | '1080p' | '4k';
  format: 'mp4' | 'mov';
  aspect_ratio: '9:16' | '16:9' | '1:1';
}

interface ExportHistory {
  id: string;
  created_at: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  config: ExportConfig;
  video_url?: string;
  duration?: number;
  file_size?: number;
  cost?: number;
}

export function ExportPage() {
  const { projectId } = useParams<{ projectId: string }>();

  const [project, setProject] = useState<Project | null>(null);
  const [config, setConfig] = useState<ExportConfig>({
    resolution: '1080p',
    format: 'mp4',
    aspect_ratio: '9:16',
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [exporting, setExporting] = useState(false);
  const [progress, setProgress] = useState(0);
  const [estimatedCost, setEstimatedCost] = useState<number | null>(null);
  const [history, setHistory] = useState<ExportHistory[]>([]);

  const { messages } = useWebSocket('/feedback');

  useEffect(() => {
    if (projectId) {
      loadData();
    }
  }, [projectId]);

  useEffect(() => {
    messages.forEach(msg => {
      if (msg.type === 'progress' && msg.data?.export_id) {
        setProgress(msg.data.percentage);
      } else if (msg.type === 'success' && msg.data?.export_id) {
        setExporting(false);
        loadHistory();
      } else if (msg.type === 'error') {
        setExporting(false);
        setError(msg.error?.message || '导出失败');
      }
    });
  }, [messages]);

  const loadData = async () => {
    if (!projectId) return;

    try {
      const [projectData, historyData] = await Promise.all([
        projectsApi.getProject(projectId),
        exportApi.getExportHistory(projectId),
      ]);
      setProject(projectData);
      setHistory(historyData);
    } catch (err: any) {
      setError('加载失败');
    } finally {
      setLoading(false);
    }
  };

  const loadHistory = async () => {
    if (!projectId) return;
    try {
      const data = await exportApi.getExportHistory(projectId);
      setHistory(data);
    } catch (err) {
      console.error('Failed to load history:', err);
    }
  };

  const handleEstimate = async () => {
    if (!projectId) return;

    try {
      const result = await exportApi.estimateCost(projectId, config);
      setEstimatedCost(result.estimated_cost);
    } catch (err: any) {
      alert('估算失败：' + (err.response?.data?.detail || '未知错误'));
    }
  };

  const handleExport = async () => {
    if (!projectId) return;

    if (estimatedCost && !confirm(`预估费用：¥${estimatedCost.toFixed(2)}，确认导出？`)) {
      return;
    }

    setError('');
    setExporting(true);
    setProgress(0);

    try {
      await exportApi.startExport(projectId, config);
    } catch (err: any) {
      setError(err.response?.data?.detail || '导出失败');
      setExporting(false);
    }
  };

  const formatFileSize = (bytes?: number) => {
    if (!bytes) return '-';
    const mb = bytes / (1024 * 1024);
    return `${mb.toFixed(2)} MB`;
  };

  const formatDuration = (seconds?: number) => {
    if (!seconds) return '-';
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-600">加载中...</div>
      </div>
    );
  }

  if (error && !exporting) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {error}
        </div>
      </div>
    );
  }

  if (!project) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          项目不存在
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-5xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">{project.title || project.name} - 导出视频</h1>
        <p className="text-gray-600 mt-2">配置导出参数并生成最终视频</p>
      </div>

      {exporting && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-8">
          <h3 className="text-lg font-semibold text-blue-900 mb-4">正在导出视频...</h3>
          <ProgressBar
            percentage={progress}
            status={
              progress < 20 ? '准备素材...' :
              progress < 50 ? '渲染视频...' :
              progress < 80 ? '合成音频...' :
              '生成文件...'
            }
            description="导出进度"
          />
          <p className="text-sm text-blue-700 mt-4">
            这可能需要几分钟，请耐心等待
          </p>
        </div>
      )}

      <div className="grid md:grid-cols-2 gap-8 mb-8">
        <div className="bg-white rounded-xl shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">导出配置</h2>

          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">
                分辨率
              </label>
              <div className="grid grid-cols-3 gap-3">
                {(['720p', '1080p', '4k'] as const).map((res) => (
                  <button
                    key={res}
                    onClick={() => setConfig({ ...config, resolution: res })}
                    disabled={exporting}
                    className={`p-3 border-2 rounded-lg transition-all ${
                      config.resolution === res
                        ? 'border-blue-500 bg-blue-50 text-blue-900'
                        : 'border-gray-300 hover:border-gray-400 text-gray-700'
                    }`}
                  >
                    <div className="font-medium">{res.toUpperCase()}</div>
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">
                格式
              </label>
              <div className="grid grid-cols-2 gap-3">
                {(['mp4', 'mov'] as const).map((fmt) => (
                  <button
                    key={fmt}
                    onClick={() => setConfig({ ...config, format: fmt })}
                    disabled={exporting}
                    className={`p-3 border-2 rounded-lg transition-all ${
                      config.format === fmt
                        ? 'border-blue-500 bg-blue-50 text-blue-900'
                        : 'border-gray-300 hover:border-gray-400 text-gray-700'
                    }`}
                  >
                    <div className="font-medium">{fmt.toUpperCase()}</div>
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">
                画面比例
              </label>
              <div className="grid grid-cols-3 gap-3">
                {(['9:16', '16:9', '1:1'] as const).map((ratio) => (
                  <button
                    key={ratio}
                    onClick={() => setConfig({ ...config, aspect_ratio: ratio })}
                    disabled={exporting}
                    className={`p-3 border-2 rounded-lg transition-all ${
                      config.aspect_ratio === ratio
                        ? 'border-blue-500 bg-blue-50 text-blue-900'
                        : 'border-gray-300 hover:border-gray-400 text-gray-700'
                    }`}
                  >
                    <div className="font-medium">{ratio}</div>
                  </button>
                ))}
              </div>
            </div>
          </div>

          <div className="mt-6 pt-6 border-t border-gray-200">
            <button
              onClick={handleEstimate}
              disabled={exporting}
              className="w-full mb-3 px-6 py-3 border border-blue-600 text-blue-600 rounded-lg font-medium hover:bg-blue-50 transition-colors disabled:opacity-50"
            >
              估算费用
            </button>
            {estimatedCost !== null && (
              <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-3">
                <div className="text-sm text-green-700 mb-1">预估费用</div>
                <div className="text-2xl font-bold text-green-900">
                  ¥{estimatedCost.toFixed(2)}
                </div>
              </div>
            )}
            <button
              onClick={handleExport}
              disabled={exporting}
              className="w-full bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors disabled:opacity-50"
            >
              {exporting ? '导出中...' : '开始导出'}
            </button>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">预览</h2>
          <div className={`bg-gray-100 rounded-lg overflow-hidden ${
            config.aspect_ratio === '9:16' ? 'aspect-[9/16]' :
            config.aspect_ratio === '16:9' ? 'aspect-video' :
            'aspect-square'
          }`}>
            <div className="w-full h-full flex items-center justify-center text-gray-400 text-6xl">
              🎥
            </div>
          </div>
          <div className="mt-4 text-sm text-gray-600 space-y-2">
            <div className="flex justify-between">
              <span>分辨率：</span>
              <span className="font-medium">{config.resolution.toUpperCase()}</span>
            </div>
            <div className="flex justify-between">
              <span>格式：</span>
              <span className="font-medium">{config.format.toUpperCase()}</span>
            </div>
            <div className="flex justify-between">
              <span>比例：</span>
              <span className="font-medium">{config.aspect_ratio}</span>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-md p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-6">导出历史</h2>
        {history.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            还没有导出记录
          </div>
        ) : (
          <div className="space-y-4">
            {history.map((item) => (
              <div
                key={item.id}
                className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      item.status === 'completed' ? 'bg-green-100 text-green-800' :
                      item.status === 'processing' ? 'bg-blue-100 text-blue-800' :
                      item.status === 'failed' ? 'bg-red-100 text-red-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {item.status === 'completed' ? '已完成' :
                       item.status === 'processing' ? '处理中' :
                       item.status === 'failed' ? '失败' :
                       '等待中'}
                    </span>
                    <span className="text-sm text-gray-600">
                      {new Date(item.created_at).toLocaleString('zh-CN')}
                    </span>
                  </div>
                  <div className="text-sm text-gray-700">
                    {item.config.resolution.toUpperCase()} • {item.config.format.toUpperCase()} • {item.config.aspect_ratio}
                    {item.duration && ` • ${formatDuration(item.duration)}`}
                    {item.file_size && ` • ${formatFileSize(item.file_size)}`}
                    {item.cost && ` • ¥${item.cost.toFixed(2)}`}
                  </div>
                </div>
                {item.status === 'completed' && item.video_url && (
                  <a
                    href={item.video_url}
                    download
                    className="ml-4 bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors"
                  >
                    下载
                  </a>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

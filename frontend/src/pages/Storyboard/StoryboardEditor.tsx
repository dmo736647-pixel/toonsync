import { useEffect, useMemo, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { storyboardApi } from '../../api/storyboard';
import { projectsApi } from '../../api/projects';
import type { Storyboard, Project } from '../../types';
import { useWebSocket } from '../../hooks/useWebSocket';

export function StoryboardEditor() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();

  const [project, setProject] = useState<Project | null>(null);
  const [storyboards, setStoryboards] = useState<Storyboard[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedFrame, setSelectedFrame] = useState<Storyboard | null>(null);
  const [previewMode, setPreviewMode] = useState<'horizontal' | 'vertical'>('vertical');
  const [draggingId, setDraggingId] = useState<string | null>(null);
  const [editingDescription, setEditingDescription] = useState('');
  const [savingDescription, setSavingDescription] = useState(false);

  // WebSocket for real-time updates
  const { messages } = useWebSocket('/feedback');

  useEffect(() => {
    if (projectId) {
      loadData();
    }
  }, [projectId]);

  useEffect(() => {
    // Handle WebSocket messages for storyboard generation
    messages.forEach(msg => {
      if (msg.type === 'success' && msg.data?.storyboard_id) {
        loadStoryboards();
      }
    });
  }, [messages]);

  useEffect(() => {
    setEditingDescription(selectedFrame?.description || '');
  }, [selectedFrame?.id]);

  const projectTitle = useMemo(() => {
    return project?.title || project?.name || 'Project';
  }, [project?.name, project?.title]);

  const normalizeFrameNumbers = (items: Storyboard[]) => {
    return items
      .slice()
      .map((sb, idx) => ({ ...sb, frame_number: idx + 1 }));
  };

  const handleDragStart = (id: string) => {
    setDraggingId(id);
  };

  const handleDropOn = (targetId: string) => {
    if (!draggingId || draggingId === targetId) return;
    setStoryboards((prev) => {
      const fromIndex = prev.findIndex((s) => s.id === draggingId);
      const toIndex = prev.findIndex((s) => s.id === targetId);
      if (fromIndex < 0 || toIndex < 0) return prev;

      const next = prev.slice();
      const [moved] = next.splice(fromIndex, 1);
      next.splice(toIndex, 0, moved);
      return normalizeFrameNumbers(next);
    });
    setDraggingId(null);
  };

  const handleSaveDescription = async () => {
    if (!selectedFrame) return;
    setSavingDescription(true);
    try {
      const updated = await storyboardApi.updateStoryboard(selectedFrame.id, { description: editingDescription });
      setStoryboards((prev) => prev.map((sb) => (sb.id === updated.id ? updated : sb)));
      setSelectedFrame(updated);
    } catch (err: any) {
      alert('保存失败：' + (err.response?.data?.detail || err.message || '未知错误'));
    } finally {
      setSavingDescription(false);
    }
  };

  const loadData = async () => {
    if (!projectId) return;

    try {
      const [projectData, storyboardData] = await Promise.all([
        projectsApi.getProject(projectId),
        storyboardApi.getStoryboards(projectId),
      ]);
      setProject(projectData);
      setStoryboards(storyboardData.sort((a, b) => a.frame_number - b.frame_number));
    } catch (err: any) {
      setError('加载失败');
    } finally {
      setLoading(false);
    }
  };

  const loadStoryboards = async () => {
    if (!projectId) return;
    try {
      const data = await storyboardApi.getStoryboards(projectId);
      setStoryboards(data.sort((a, b) => a.frame_number - b.frame_number));
    } catch (err) {
      console.error('Failed to reload storyboards:', err);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('确定要删除这个分镜吗？')) return;

    try {
      await storyboardApi.deleteStoryboard(id);
      setStoryboards(storyboards.filter(s => s.id !== id));
      if (selectedFrame?.id === id) {
        setSelectedFrame(null);
      }
    } catch (err: any) {
      alert('删除失败：' + (err.response?.data?.detail || '未知错误'));
    }
  };

  const handleSaveOrder = async () => {
    if (!projectId) return;

    try {
      const frameOrders = storyboards.map(sb => ({
        id: sb.id,
        frame_number: sb.frame_number,
      }));
      await storyboardApi.reorderStoryboards(projectId, frameOrders);
      alert('顺序已保存');
    } catch (err: any) {
      alert('保存失败：' + (err.response?.data?.detail || '未知错误'));
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#05050a] flex items-center justify-center">
        <div className="w-16 h-16 bg-gradient-to-r from-cyan-500 to-blue-600 rounded-full animate-spin flex items-center justify-center shadow-lg shadow-cyan-500/20">
          <span className="text-white text-2xl">🎬</span>
        </div>
      </div>
    );
  }

  if (error || !project) {
    return (
      <div className="min-h-screen bg-[#05050a] flex items-center justify-center text-white">
        <div className="bg-red-500/10 border border-red-500/20 text-red-200 px-6 py-4 rounded-xl">
          {error || '项目不存在'}
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#05050a] relative overflow-hidden text-white">
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-cyan-500/10 rounded-full blur-[100px] opacity-30"></div>
        <div className="absolute bottom-0 right-1/4 w-[500px] h-[500px] bg-blue-600/10 rounded-full blur-[100px] opacity-30"></div>
      </div>

      <div className="relative z-10 container mx-auto px-6 py-10">
        <div className="flex justify-between items-center mb-8">
          <div>
            <div className="inline-block mb-4 px-3 py-1 rounded-full border border-cyan-500/30 bg-cyan-950/30 backdrop-blur-sm">
              <span className="text-cyan-400 text-xs font-bold uppercase tracking-wider">🎬 Storyboard</span>
            </div>
            <h1 className="text-3xl font-bold text-white tracking-tight">{projectTitle}</h1>
            <p className="text-slate-400 mt-2">创建和管理分镜（场景）</p>
          </div>
          <div className="flex gap-3">
            <div className="flex bg-white/5 border border-white/10 rounded-xl p-1">
              <button
                onClick={() => setPreviewMode('horizontal')}
                className={`px-4 py-2 rounded-lg text-sm font-bold transition-all ${
                  previewMode === 'horizontal'
                    ? 'bg-white/10 text-white shadow'
                    : 'text-slate-400 hover:text-white hover:bg-white/5'
                }`}
              >
                16:9 横屏
              </button>
              <button
                onClick={() => setPreviewMode('vertical')}
                className={`px-4 py-2 rounded-lg text-sm font-bold transition-all ${
                  previewMode === 'vertical'
                    ? 'bg-white/10 text-white shadow'
                    : 'text-slate-400 hover:text-white hover:bg-white/5'
                }`}
              >
                9:16 竖屏
              </button>
            </div>
            <button
              onClick={() => navigate(`/storyboard/new?project_id=${projectId}`)}
              className="bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white px-6 py-3 rounded-xl font-bold shadow-lg hover:shadow-cyan-500/25 transition-all transform hover:-translate-y-0.5"
            >
              + 新建分镜
            </button>
          </div>
        </div>

        {storyboards.length === 0 ? (
          <div className="text-center py-16">
            <div className="neo-glass bg-[#0f111a]/90 border border-white/10 rounded-3xl p-12 max-w-md mx-auto shadow-2xl shadow-cyan-900/10">
              <div className="text-6xl mb-6">🎬</div>
              <h3 className="text-2xl font-bold text-white mb-4">还没有分镜</h3>
              <p className="text-slate-400 mb-8">创建第一个分镜开始制作</p>
              <button
                onClick={() => navigate(`/storyboard/new?project_id=${projectId}`)}
                className="inline-block bg-gradient-to-r from-cyan-500 to-blue-600 text-white px-8 py-3 rounded-xl font-bold hover:shadow-lg hover:shadow-cyan-500/25 transition-all transform hover:scale-105"
              >
                创建分镜
              </button>
            </div>
          </div>
        ) : (
          <div className="space-y-6">
            <div className="neo-glass bg-[#0f111a]/90 border border-white/10 rounded-3xl p-6 shadow-2xl shadow-cyan-900/10">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold text-white">
                  分镜序列 ({storyboards.length} 个)
                </h2>
                <button
                  onClick={handleSaveOrder}
                  className="text-sm bg-white/5 border border-white/10 hover:bg-white/10 text-white px-4 py-2 rounded-lg font-bold transition-all"
                >
                  保存顺序
                </button>
              </div>

              <div className={`grid gap-4 ${
                previewMode === 'vertical'
                  ? 'grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5'
                  : 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3'
              }`}>
                {storyboards.map((storyboard, index) => (
                  <div
                    key={storyboard.id}
                    className={`bg-[#0b0d14] rounded-xl overflow-hidden border transition-all cursor-pointer ${
                      selectedFrame?.id === storyboard.id
                        ? 'border-cyan-500/60 shadow-lg shadow-cyan-500/10'
                        : 'border-white/5 hover:border-cyan-500/30'
                    }`}
                    onClick={() => setSelectedFrame(storyboard)}
                    draggable
                    onDragStart={() => handleDragStart(storyboard.id)}
                    onDragOver={(e) => e.preventDefault()}
                    onDrop={() => handleDropOn(storyboard.id)}
                  >
                    <div className={`relative bg-black/40 ${
                      previewMode === 'vertical' ? 'aspect-[9/16]' : 'aspect-video'
                    }`}>
                      {storyboard.image_url ? (
                        <img
                          src={storyboard.image_url}
                          alt={`分镜 ${storyboard.frame_number}`}
                          className="w-full h-full object-cover"
                        />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center text-white/20 text-4xl">
                          🎬
                        </div>
                      )}
                      <div className="absolute top-2 left-2 bg-black/60 backdrop-blur-sm text-white px-2 py-1 rounded-md text-xs font-medium border border-white/10">
                        #{storyboard.frame_number}
                      </div>
                    </div>
                    <div className="p-3">
                      <p className="text-sm text-slate-300 line-clamp-2">
                        {storyboard.description}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {selectedFrame && (
              <div className="neo-glass bg-[#0f111a]/90 border border-white/10 rounded-3xl p-6 animate-fade-in-up shadow-2xl shadow-cyan-900/10">
                <div className="flex justify-between items-start mb-6">
                  <h2 className="text-xl font-semibold text-white">
                    分镜 #{selectedFrame.frame_number}
                  </h2>
                  <button
                    onClick={() => handleDelete(selectedFrame.id)}
                    className="text-red-200 hover:text-red-100 text-sm font-bold bg-red-500/10 hover:bg-red-500/20 px-3 py-1.5 rounded-lg transition-all"
                  >
                    删除
                  </button>
                </div>

                <div className="grid md:grid-cols-2 gap-8">
                  <div>
                    <div className={`bg-black/30 rounded-xl overflow-hidden border border-white/10 ${
                      previewMode === 'vertical' ? 'aspect-[9/16] max-w-sm mx-auto' : 'aspect-video'
                    }`}>
                      {selectedFrame.image_url ? (
                        <img
                          src={selectedFrame.image_url}
                          alt={`分镜 ${selectedFrame.frame_number}`}
                          className="w-full h-full object-cover"
                        />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center text-white/20 text-6xl">
                          🎬
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="space-y-6">
                    <div>
                      <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
                        场景描述
                      </label>
                      <textarea
                        value={editingDescription}
                        onChange={(e) => setEditingDescription(e.target.value)}
                        rows={5}
                        className="w-full px-4 py-3 bg-[#1a1d2d] border border-white/5 rounded-xl text-white placeholder-slate-600 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition-all resize-none"
                      />
                      <div className="mt-3 flex gap-3">
                        <button
                          type="button"
                          onClick={() => setEditingDescription(selectedFrame.description)}
                          className="px-4 py-2 bg-white/5 border border-white/10 text-slate-200 rounded-xl font-bold hover:bg-white/10 transition-all"
                          disabled={savingDescription}
                        >
                          重置
                        </button>
                        <button
                          type="button"
                          onClick={handleSaveDescription}
                          className="px-4 py-2 bg-gradient-to-r from-cyan-500 to-blue-600 text-white rounded-xl font-bold shadow-lg hover:shadow-cyan-500/25 transition-all disabled:opacity-50"
                          disabled={savingDescription || editingDescription.trim() === selectedFrame.description.trim()}
                        >
                          {savingDescription ? '保存中...' : '保存描述'}
                        </button>
                      </div>
                    </div>

                    <div>
                      <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
                        创建时间
                      </label>
                      <p className="text-slate-300">
                        {new Date(selectedFrame.created_at).toLocaleString('zh-CN')}
                      </p>
                    </div>

                    <div className="bg-blue-500/5 border border-blue-500/10 rounded-xl p-4">
                      <h4 className="font-bold text-cyan-400 mb-2 text-sm uppercase tracking-wide">💡 提示</h4>
                      <ul className="text-sm text-slate-400 space-y-1">
                        <li>• 拖拽分镜卡片可以调整顺序</li>
                        <li>• 点击"保存顺序"确认更改</li>
                        <li>• 竖屏模式优化移动端观看</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

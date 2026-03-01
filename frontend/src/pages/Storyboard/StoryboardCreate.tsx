import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { storyboardApi } from '../../api/storyboard';
import { charactersApi } from '../../api/characters';
import type { Character } from '../../types';
import { ProgressBar } from '../../components/feedback/ProgressBar';
import { useWebSocket } from '../../hooks/useWebSocket';

export function StoryboardCreate() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const projectIdFromQuery = searchParams.get('project_id');
  const storedProjectId = localStorage.getItem('activeProjectId');
  const projectId = projectIdFromQuery || storedProjectId;
  const characterIdParam = searchParams.get('character_id');

  const [characters, setCharacters] = useState<Character[]>([]);
  const [characterId, setCharacterId] = useState(characterIdParam || '');
  const [description, setDescription] = useState('');
  const [style, setStyle] = useState<'anime' | 'realistic'>('anime');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [generating, setGenerating] = useState(false);
  const [progress, setProgress] = useState(0);

  const { messages } = useWebSocket('/feedback');

  useEffect(() => {
    if (!projectIdFromQuery && storedProjectId) {
      navigate(`/storyboard/new?project_id=${storedProjectId}${characterIdParam ? `&character_id=${characterIdParam}` : ''}` , { replace: true });
    }
  }, [characterIdParam, navigate, projectIdFromQuery, storedProjectId]);

  useEffect(() => {
    if (projectId) {
      loadCharacters();
    }
  }, [projectId]);

  useEffect(() => {
    // Handle WebSocket progress updates
    messages.forEach(msg => {
      if (msg.type === 'progress') {
        setProgress(msg.data?.percentage || 0);
      } else if (msg.type === 'success') {
        setGenerating(false);
        navigate(`/storyboard/${projectId}`);
      } else if (msg.type === 'error') {
        setGenerating(false);
        setError(msg.error?.message || '生成失败');
      }
    });
  }, [messages]);

  const loadCharacters = async () => {
    if (!projectId) return;

    try {
      console.log('Loading characters for project:', projectId);
      const data = await charactersApi.getCharacters(projectId);
      console.log('Loaded characters:', data);
      // 不过滤角色，显示所有角色（即使没有参考图）
      setCharacters(data);
    } catch (err: any) {
      console.error('Failed to load characters:', err);
      setError('加载角色列表失败');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!projectId) {
      setError('缺少项目ID');
      return;
    }

    if (!characterId) {
      setError('请选择角色');
      return;
    }

    setError('');
    setLoading(true);
    setGenerating(true);
    setProgress(0);

    // Simulate progress while waiting for backend
    const progressInterval = setInterval(() => {
        setProgress(prev => {
            if (prev >= 90) return prev;
            return prev + 5;
        });
    }, 1000);

    try {
      const storyboard = await storyboardApi.createStoryboard({
        project_id: projectId!,
        character_id: characterId,
        description: description,
        style: style as 'anime' | 'realistic'
      });

      const selectedCharacter = characters.find(c => c.id === characterId);

      // Start image generation
      try {
        await storyboardApi.generateImage(storyboard.id, characterId, style, selectedCharacter?.reference_image_url);
      } catch (genErr: any) {
        console.warn('Image generation failed, but storyboard created:', genErr);
        // 即使图像生成失败，也继续，因为分镜已经创建成功
        setError('分镜已创建，但图像生成失败。请稍后重试。');
        // 不清除 generating 状态，让用户知道还在处理中
        setGenerating(false);
        setProgress(100);
        
        // 延迟跳转到分镜列表
        setTimeout(() => {
          navigate(`/storyboard?project_id=${projectId}`);
        }, 2000);
        return; // 提前返回，不执行后面的成功逻辑
      }
      
      clearInterval(progressInterval);
      setProgress(100);
      
      // Delay navigation slightly to show 100%
      setTimeout(() => {
          setGenerating(false);
          // Navigate back to storyboard list
          navigate(`/storyboard?project_id=${projectId}`);
      }, 500);

      // WebSocket will handle progress updates
    } catch (err: any) {
      clearInterval(progressInterval);
      console.error("Create storyboard failed:", err);
      setError(err.response?.data?.detail || err.message || '创建分镜失败');
      setGenerating(false);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#05050a] relative overflow-hidden text-white flex items-center justify-center">
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-cyan-500/10 rounded-full blur-[100px] opacity-30"></div>
        <div className="absolute bottom-0 right-1/4 w-[500px] h-[500px] bg-blue-600/10 rounded-full blur-[100px] opacity-30"></div>
      </div>

      <div className="relative z-10 container mx-auto px-4 py-8 max-w-3xl">
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold text-white tracking-tight">创建分镜</h1>
          <p className="text-slate-400 mt-2">使用角色一致性模型生成分镜图像</p>
        </div>

        {error && (
          <div className="bg-red-500/20 backdrop-blur-lg border border-red-500/30 text-red-100 px-6 py-4 rounded-2xl mb-6">
            <div className="flex items-center">
              <span className="text-red-300 mr-3">⚠️</span>
              {error}
            </div>
          </div>
        )}

        {generating && (
          <div className="bg-blue-500/10 border border-blue-500/20 text-cyan-100 px-6 py-4 rounded-xl mb-6">
            <h3 className="text-lg font-bold text-cyan-200 mb-4">正在生成分镜图像...</h3>
            <ProgressBar
              percentage={progress}
              status={progress < 30 ? '分析场景描述...' : progress < 70 ? '应用角色特征...' : '渲染图像...'}
              description="生成进度"
            />
            <p className="text-sm text-cyan-200/70 mt-4">
              这可能需要10-30秒，请耐心等待
            </p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="neo-glass bg-[#0f111a]/90 backdrop-blur-xl border border-white/10 rounded-3xl p-8 shadow-2xl shadow-cyan-900/10">
          <div className="mb-6">
            <label htmlFor="character" className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
              选择角色 *
            </label>
            {characters.length === 0 ? (
              <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-xl p-4">
                <p className="text-yellow-200 mb-2">
                  还没有可用的角色，请先添加角色并提取特征
                </p>
                <button
                  type="button"
                  onClick={() => navigate(`/characters/new?project_id=${projectId}`)}
                  className="text-sm text-yellow-300 hover:text-yellow-200 font-bold underline"
                >
                  立即添加角色 →
                </button>
              </div>
            ) : (
              <select
                id="character"
                value={characterId}
                onChange={(e) => setCharacterId(e.target.value)}
                className="w-full px-4 py-3 bg-[#1a1d2d] border border-white/5 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition-all [&>option]:bg-[#1a1d2d] [&>option]:text-white"
                required
                disabled={loading || generating}
              >
                <option value="">请选择角色</option>
                {characters.map((character) => (
                  <option key={character.id} value={character.id}>
                    {character.name}
                  </option>
                ))}
              </select>
            )}
          </div>

          <div className="mb-6">
            <label htmlFor="description" className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
              场景描述 *
            </label>
            <textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="描述这个分镜的场景，例如：主角站在城市街道上，背景是高楼大厦，阳光明媚"
              rows={4}
              className="w-full px-4 py-3 bg-[#1a1d2d] border border-white/5 rounded-xl text-white placeholder-slate-600 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition-all resize-none"
              required
              disabled={loading || generating}
            />
            <p className="text-sm text-slate-500 mt-2">
              详细的描述有助于生成更准确的图像
            </p>
          </div>

          <div className="mb-8">
            <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">
              渲染风格 *
            </label>
            <div className="grid grid-cols-2 gap-4">
              <button
                type="button"
                onClick={() => setStyle('anime')}
                disabled={loading || generating}
                className={`p-4 border rounded-xl transition-all ${
                  style === 'anime'
                    ? 'border-cyan-500/60 bg-cyan-500/10'
                    : 'border-white/10 bg-white/5 hover:bg-white/10 hover:border-white/20'
                }`}
              >
                <div className="text-4xl mb-2">🎨</div>
                <div className="font-medium text-white">动态漫</div>
                <div className="text-sm text-slate-400 mt-1">动画风格，色彩鲜艳</div>
              </button>
              <button
                type="button"
                onClick={() => setStyle('realistic')}
                disabled={loading || generating}
                className={`p-4 border rounded-xl transition-all ${
                  style === 'realistic'
                    ? 'border-cyan-500/60 bg-cyan-500/10'
                    : 'border-white/10 bg-white/5 hover:bg-white/10 hover:border-white/20'
                }`}
              >
                <div className="text-4xl mb-2">📷</div>
                <div className="font-medium text-white">真人短剧</div>
                <div className="text-sm text-slate-400 mt-1">写实风格，接近真人</div>
              </button>
            </div>
          </div>

          <div className="bg-blue-500/5 border border-blue-500/10 rounded-xl p-4 mb-8">
            <h4 className="font-bold text-cyan-400 mb-2 text-sm uppercase tracking-wide">💡 提示</h4>
            <ul className="text-sm text-slate-400 space-y-1">
              <li>• 系统会使用角色的一致性模型生成图像</li>
              <li>• 面部特征相似度 &gt; 90%</li>
              <li>• 服装和发型一致性 &gt; 85%</li>
              <li>• 生成时间约10-30秒</li>
            </ul>
          </div>

          <div className="flex gap-4">
            <button
              type="button"
              onClick={() => navigate(-1)}
              className="flex-1 px-6 py-3 bg-white/5 border border-white/10 text-slate-200 rounded-xl font-bold hover:bg-white/10 transition-all"
              disabled={loading || generating}
            >
              取消
            </button>
            <button
              type="submit"
              disabled={loading || generating || characters.length === 0}
              className="flex-1 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white px-6 py-3 rounded-xl font-bold shadow-lg hover:shadow-cyan-500/25 disabled:opacity-50 disabled:cursor-not-allowed transition-all transform hover:-translate-y-0.5"
            >
              {generating ? '生成中...' : '创建分镜'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

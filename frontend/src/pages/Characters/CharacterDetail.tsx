import { useEffect, useState } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import { charactersApi } from '../../api/characters';
import type { Character } from '../../types';

export function CharacterDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const extracted = searchParams.get('extracted') === 'true';

  const [character, setCharacter] = useState<Character | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [extracting, setExtracting] = useState(false);

  useEffect(() => {
    if (id) {
      loadCharacter();
    }
  }, [id]);

  const loadCharacter = async () => {
    if (!id) return;

    try {
      const data = await charactersApi.getCharacter(id);
      setCharacter(data);
    } catch (err: any) {
      setError('加载角色失败');
    } finally {
      setLoading(false);
    }
  };

  const handleExtractFeatures = async () => {
    if (!id) return;

    setExtracting(true);
    try {
      const result = await charactersApi.extractFeatures(id);
      setCharacter(prev => prev ? { ...prev, consistency_model_url: result.consistency_model_url } : null);
      alert('特征提取成功！');
    } catch (err: any) {
      alert('特征提取失败：' + (err.response?.data?.detail || '未知错误'));
    } finally {
      setExtracting(false);
    }
  };

  const handleDelete = async () => {
    if (!id || !confirm('确定要删除这个角色吗？')) return;

    try {
      await charactersApi.deleteCharacter(id);
      const backProjectId = character?.project_id || localStorage.getItem('activeProjectId');
      navigate(backProjectId ? `/characters?project_id=${backProjectId}` : '/characters');
    } catch (err: any) {
      alert('删除失败：' + (err.response?.data?.detail || '未知错误'));
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#05050a] flex items-center justify-center">
        <div className="w-16 h-16 bg-gradient-to-r from-cyan-500 to-blue-600 rounded-full animate-spin flex items-center justify-center shadow-lg shadow-cyan-500/20">
          <span className="text-white text-2xl">👤</span>
        </div>
      </div>
    );
  }

  if (error || !character) {
    return (
      <div className="min-h-screen bg-[#05050a] flex items-center justify-center text-white">
        <div className="bg-red-500/10 border border-red-500/20 text-red-200 px-6 py-4 rounded-xl">
          {error || '角色不存在'}
        </div>
      </div>
    );
  }

  const canGenerateStoryboard = !!character.consistency_model_url;

  return (
    <div className="min-h-screen bg-[#05050a] relative overflow-hidden text-white flex items-center justify-center py-12">
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-cyan-500/10 rounded-full blur-[100px] opacity-30"></div>
        <div className="absolute bottom-0 right-1/4 w-[500px] h-[500px] bg-blue-600/10 rounded-full blur-[100px] opacity-30"></div>
      </div>

      <div className="relative z-10 container mx-auto px-4 max-w-4xl">
        {extracted && (
          <div className="bg-green-500/10 border border-green-500/20 text-green-200 px-6 py-4 rounded-xl mb-6 flex items-center">
            <span className="text-xl mr-3">✓</span>
            角色创建成功，特征已提取！
          </div>
        )}

        <div className="bg-[#0f111a]/90 backdrop-blur-xl border border-white/10 rounded-3xl overflow-hidden shadow-2xl shadow-cyan-900/10 flex flex-col md:flex-row">
          <div className="md:w-1/2 bg-black/20 relative min-h-[400px]">
            {character.reference_image_url ? (
              <img
                src={character.reference_image_url}
                alt={character.name}
                className="w-full h-full object-cover absolute inset-0"
              />
            ) : (
              <div className="w-full h-full flex items-center justify-center text-white/20 text-8xl">
                👤
              </div>
            )}
            {/* Gradient Overlay */}
            <div className="absolute inset-0 bg-gradient-to-t from-black/70 to-transparent md:bg-gradient-to-r"></div>
          </div>

          <div className="md:w-1/2 p-8 flex flex-col justify-center">
            <div className="mb-8">
              <h1 className="text-4xl font-bold text-white mb-2 tracking-tight">{character.name}</h1>
              <p className="text-slate-400">
                创建于 {new Date(character.created_at).toLocaleDateString('zh-CN')}
              </p>
            </div>

            <div className="mb-8">
              <h3 className="text-lg font-bold text-white mb-3 uppercase tracking-wide">特征提取状态</h3>
              {character.consistency_model_url ? (
                <div className="bg-green-500/10 border border-green-500/20 rounded-xl p-4">
                  <div className="flex items-center text-green-200">
                    <span className="text-2xl mr-3">✓</span>
                    <div>
                      <p className="font-medium">特征已提取</p>
                      <p className="text-sm text-green-300/70">
                        可用于生成一致的分镜图像
                      </p>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-xl p-4">
                  <div className="flex items-center text-yellow-200 mb-3">
                    <span className="text-2xl mr-3">⚠️</span>
                    <div>
                      <p className="font-medium">特征未提取</p>
                      <p className="text-sm text-yellow-200/70">
                        需要提取特征才能使用此角色
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={handleExtractFeatures}
                    disabled={extracting}
                    className="w-full bg-gradient-to-r from-amber-400/20 to-orange-500/20 hover:from-amber-400/30 hover:to-orange-500/30 text-yellow-100 py-2 rounded-lg font-bold border border-yellow-500/20 transition-all"
                  >
                    {extracting ? '提取中...' : '立即提取特征'}
                  </button>
                </div>
              )}
            </div>

            <div className="space-y-3 mt-auto">
              <button
                onClick={() => {
                  if (!canGenerateStoryboard) {
                    alert('请先提取特征，再生成分镜');
                    return;
                  }
                  navigate(`/storyboard/new?project_id=${character.project_id}&character_id=${character.id}`);
                }}
                className={`w-full bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white py-3 rounded-xl font-bold shadow-lg hover:shadow-cyan-500/25 transition-all transform hover:-translate-y-0.5 ${
                  canGenerateStoryboard ? '' : 'opacity-60'
                }`}
              >
                使用此角色生成分镜
              </button>
              <div className="flex gap-3">
                 <button
                  onClick={() => navigate(-1)}
                  className="flex-1 bg-white/5 border border-white/10 text-slate-200 py-3 rounded-xl font-bold hover:bg-white/10 transition-all"
                >
                  返回
                </button>
                <button
                  onClick={handleDelete}
                  className="flex-1 bg-red-500/10 border border-red-500/20 text-red-200 py-3 rounded-xl font-bold hover:bg-red-500/20 transition-all"
                >
                  删除角色
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

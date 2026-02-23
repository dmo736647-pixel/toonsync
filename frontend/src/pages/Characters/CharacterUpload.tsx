import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { charactersApi } from '../../api/characters';

export function CharacterUpload() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const projectIdFromQuery = searchParams.get('project_id');
  const storedProjectId = localStorage.getItem('activeProjectId');
  const projectId = projectIdFromQuery || storedProjectId;

  const [name, setName] = useState('');
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [extractingFeatures, setExtractingFeatures] = useState(false);

  useEffect(() => {
    if (!projectIdFromQuery && storedProjectId) {
      navigate(`/characters/new?project_id=${storedProjectId}`, { replace: true });
    }
  }, [navigate, projectIdFromQuery, storedProjectId]);

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setImageFile(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!imageFile) {
      setError('请选择角色图片');
      return;
    }

    if (!projectId) {
      setError('缺少项目ID');
      return;
    }

    setError('');
    setLoading(true);

    try {
      const character = await charactersApi.createCharacter({
        name,
        project_id: projectId,
        image_file: imageFile,
      });

      // 自动提取特征
      setExtractingFeatures(true);
      try {
        await charactersApi.extractFeatures(character.id);
        navigate(`/characters/${character.id}?extracted=true`);
      } catch (err) {
        // 即使特征提取失败，也跳转到角色详情页
        navigate(`/characters/${character.id}`);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || '创建角色失败');
    } finally {
      setLoading(false);
      setExtractingFeatures(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#05050a] relative overflow-hidden text-white flex items-center justify-center">
      {/* Background Decoration */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-cyan-500/10 rounded-full blur-[100px] opacity-30"></div>
        <div className="absolute bottom-0 right-1/4 w-[500px] h-[500px] bg-blue-600/10 rounded-full blur-[100px] opacity-30"></div>
      </div>

      <div className="relative z-10 container mx-auto px-4 py-8 max-w-2xl">
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold text-white tracking-tight">Add Character</h1>
          <p className="text-slate-400 mt-2">Upload image to extract visual features</p>
        </div>

        {error && (
          <div className="bg-red-500/10 border border-red-500/20 text-red-200 px-6 py-4 rounded-xl mb-6 flex items-center">
            <span className="mr-3">⚠️</span>
            {error}
          </div>
        )}

        {extractingFeatures && (
          <div className="bg-blue-500/10 border border-blue-500/20 text-cyan-200 px-6 py-4 rounded-xl mb-6 flex items-center">
            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-cyan-400 mr-3"></div>
            Extracting character features, please wait...
          </div>
        )}

        <form onSubmit={handleSubmit} className="neo-glass bg-[#0f111a]/90 backdrop-blur-xl border border-white/10 rounded-3xl p-8 shadow-2xl shadow-cyan-900/20">
          <div className="mb-6">
            <label htmlFor="name" className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
              Character Name *
            </label>
            <input
              id="name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Protagonist, Villain"
              className="w-full px-4 py-3 bg-[#1a1d2d] border border-white/5 rounded-xl text-white placeholder-slate-600 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition-all"
              required
              disabled={loading}
            />
          </div>

          <div className="mb-6">
            <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
              Character Image *
            </label>
            <div className="border-2 border-dashed border-white/10 rounded-xl p-6 text-center hover:border-cyan-500/50 hover:bg-[#1a1d2d]/50 transition-all bg-[#1a1d2d]">
              {imagePreview ? (
                <div className="space-y-4">
                  <img
                    src={imagePreview}
                    alt="Preview"
                    className="max-h-64 mx-auto rounded-lg shadow-lg border border-white/10"
                  />
                  <button
                    type="button"
                    onClick={() => {
                      setImageFile(null);
                      setImagePreview('');
                    }}
                    className="text-sm text-red-400 hover:text-red-300 font-medium"
                  >
                    Change Image
                  </button>
                </div>
              ) : (
                <div>
                  <div className="text-slate-600 text-5xl mb-4">📷</div>
                  <label className="cursor-pointer inline-block">
                    <span className="text-cyan-400 hover:text-cyan-300 font-bold transition-colors">
                      Click to upload
                    </span>
                    <input
                      type="file"
                      accept="image/*"
                      onChange={handleImageChange}
                      className="hidden"
                      disabled={loading}
                    />
                  </label>
                  <p className="text-xs text-slate-500 mt-2 uppercase tracking-wide">
                    JPG, PNG • Min 512x512px
                  </p>
                </div>
              )}
            </div>
          </div>

          <div className="bg-blue-500/5 border border-blue-500/10 rounded-xl p-4 mb-8">
            <h4 className="font-bold text-cyan-400 mb-2 text-sm uppercase tracking-wide">💡 Tips</h4>
            <ul className="text-sm text-slate-400 space-y-1">
              <li>• Clear front-facing photos work best</li>
              <li>• System auto-extracts face, clothing, and hair features</li>
              <li>• Features ensure consistent character generation</li>
            </ul>
          </div>

          <div className="flex gap-4">
            <button
              type="button"
              onClick={() => navigate(-1)}
              className="flex-1 px-6 py-3 bg-white/5 border border-white/5 text-slate-300 rounded-xl font-bold hover:bg-white/10 transition-all"
              disabled={loading}
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading || !imageFile}
              className="flex-1 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white px-6 py-3 rounded-xl font-bold shadow-lg hover:shadow-cyan-500/25 disabled:opacity-50 disabled:cursor-not-allowed transition-all transform hover:-translate-y-0.5"
            >
              {loading ? 'Creating...' : 'Create Character'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

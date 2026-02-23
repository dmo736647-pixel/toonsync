import { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { charactersApi } from '../../api/characters';
import type { Character } from '../../types';

export function CharacterList() {
  const [searchParams] = useSearchParams();
  const projectId = searchParams.get('project_id');

  const [characters, setCharacters] = useState<Character[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (projectId) {
      localStorage.setItem('activeProjectId', projectId);
    }
  }, [projectId]);

  useEffect(() => {
    loadCharacters();
  }, [projectId]);

  const loadCharacters = async () => {
    try {
      const data = await charactersApi.getCharacters(projectId || undefined);
      setCharacters(data);
    } catch (err: any) {
      setError('加载角色失败');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('确定要删除这个角色吗？')) return;

    try {
      await charactersApi.deleteCharacter(id);
      setCharacters(characters.filter(c => c.id !== id));
    } catch (err: any) {
      alert('删除失败：' + (err.response?.data?.detail || '未知错误'));
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#05050a] flex items-center justify-center">
        <div className="w-16 h-16 bg-gradient-to-r from-cyan-500 to-blue-600 rounded-full animate-spin flex items-center justify-center shadow-lg shadow-cyan-500/20">
          <span className="text-white text-2xl">👥</span>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#05050a] relative overflow-hidden flex flex-col">
      {/* Background Decoration */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-cyan-500/10 rounded-full blur-[100px] opacity-30"></div>
        <div className="absolute bottom-0 right-1/4 w-[500px] h-[500px] bg-blue-600/10 rounded-full blur-[100px] opacity-30"></div>
      </div>

      <div className="relative z-10 container mx-auto px-6 py-12">
        <div className="flex justify-between items-center mb-12">
          <div>
            <div className="inline-block mb-4 px-3 py-1 rounded-full border border-cyan-500/30 bg-cyan-950/30 backdrop-blur-sm">
                <span className="text-cyan-400 text-xs font-bold uppercase tracking-wider">✨ Characters</span>
            </div>
            <h1 className="text-4xl font-bold text-white mb-2 tracking-tight">Character Library</h1>
            <p className="text-slate-400 text-lg">Manage your characters and consistency models</p>
          </div>
          <Link
            to={`/characters/new${projectId ? `?project_id=${projectId}` : ''}`}
            className="bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white px-8 py-3 rounded-xl font-bold transition-all shadow-lg hover:shadow-cyan-500/25 flex items-center gap-2 group"
          >
            <span className="text-xl group-hover:scale-110 transition-transform">+</span>
            Add Character
          </Link>
        </div>

        {error && (
          <div className="bg-red-500/10 border border-red-500/20 text-red-200 px-6 py-4 rounded-xl mb-8 flex items-center">
            <span className="mr-3">⚠️</span>
            {error}
          </div>
        )}

        {characters.length === 0 ? (
          <div className="text-center py-24">
            <div className="neo-glass bg-[#0f111a]/80 border border-white/5 rounded-3xl p-16 max-w-2xl mx-auto shadow-2xl">
              <div className="text-7xl mb-8 opacity-50">👤</div>
              <h3 className="text-3xl font-bold text-white mb-4">No Characters Yet</h3>
              <p className="text-slate-400 mb-10 text-lg">Add characters to maintain visual consistency across your scenes.</p>
              <Link
                to={`/characters/new${projectId ? `?project_id=${projectId}` : ''}`}
                className="inline-flex items-center justify-center bg-gradient-to-r from-cyan-500 to-blue-600 text-white px-10 py-4 rounded-xl font-bold hover:shadow-lg hover:shadow-cyan-500/25 transition-all transform hover:-translate-y-1"
              >
                Add First Character
              </Link>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8">
            {characters.map((character) => (
              <div
                key={character.id}
                className="group bg-[#0f111a] border border-white/5 rounded-2xl overflow-hidden hover:border-cyan-500/30 transition-all duration-300 hover:shadow-2xl hover:shadow-cyan-900/10 hover:-translate-y-1"
              >
                <div className="aspect-square bg-[#1a1d2d] relative group-hover:opacity-90 transition-opacity">
                  {character.reference_image_url ? (
                    <img
                      src={character.reference_image_url}
                      alt={character.name}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-white/20 text-6xl">
                      👤
                    </div>
                  )}
                  {character.lora_model_id && (
                    <div className="absolute top-3 right-3 bg-green-500/20 backdrop-blur-md text-green-400 px-3 py-1 rounded-full text-xs font-bold border border-green-500/30">
                      ✓ TRAINED
                    </div>
                  )}
                  
                  {/* Overlay Actions */}
                  <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-4 backdrop-blur-sm">
                     <Link
                      to={`/characters/${character.id}`}
                      className="w-12 h-12 flex items-center justify-center bg-white/10 hover:bg-white/20 rounded-full backdrop-blur-md transition-all border border-white/10 text-white"
                      title="View Details"
                    >
                      👁️
                    </Link>
                    <button
                      onClick={() => handleDelete(character.id)}
                      className="w-12 h-12 flex items-center justify-center bg-red-500/20 hover:bg-red-500/30 rounded-full backdrop-blur-md transition-all border border-red-500/30 text-red-200"
                      title="Delete"
                    >
                      🗑️
                    </button>
                  </div>
                </div>

                <div className="p-5">
                  <h3 className="text-lg font-bold text-white mb-1 truncate group-hover:text-cyan-400 transition-colors">
                    {character.name}
                  </h3>
                  <p className="text-xs text-slate-500 mb-3 font-medium uppercase tracking-wide">
                    Created {new Date(character.created_at).toLocaleDateString()}
                  </p>
                  
                  {character.description && (
                    <p className="text-sm text-slate-400 line-clamp-2 h-10 leading-relaxed">
                      {character.description}
                    </p>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

import { useEffect, useState, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { projectsApi } from '../../api/projects';
import type { Project } from '../../types';

// 简单的数据缓存
const projectsCache = {
  data: null as Project[] | null,
  timestamp: 0,
  TTL: 5 * 60 * 1000, // 5 分钟缓存
};

export function ProjectList() {
  const [projects, setProjects] = useState<Project[]>(projectsCache.data || []);
  const [loading, setLoading] = useState(!projectsCache.data);
  const [error, setError] = useState('');

  const loadProjects = useCallback(async () => {
    // 如果缓存有效，不重新加载
    const now = Date.now();
    if (projectsCache.data && now - projectsCache.timestamp < projectsCache.TTL) {
      setLoading(false);
      return;
    }

    try {
      const data = await projectsApi.getProjects();
      setProjects(data);
      projectsCache.data = data;
      projectsCache.timestamp = now;
    } catch (err: any) {
      console.error('Failed to load projects:', err);
      setError('无法加载项目列表，请稍后重试');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadProjects();
  }, [loadProjects]);

  const getStatusText = (status: string) => {
    switch (status) {
      case 'completed': return 'Completed';
      case 'processing': return 'Processing';
      case 'draft': return 'Draft';
      default: return 'Unknown';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-500/20 text-green-300 border border-green-500/30';
      case 'processing': return 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30';
      case 'draft': return 'bg-slate-500/20 text-slate-300 border border-slate-500/30';
      default: return 'bg-slate-500/20 text-slate-300 border border-slate-500/30';
    }
  };

  const getProgress = (status: string) => {
    switch (status) {
      case 'completed': return 100;
      case 'processing': return 50;
      case 'draft': return 10;
      default: return 0;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#05050a] relative overflow-hidden flex items-center justify-center">
        <div className="w-16 h-16 bg-gradient-to-r from-cyan-500 to-blue-600 rounded-full animate-spin flex items-center justify-center shadow-lg shadow-cyan-500/20">
          <span className="text-white text-2xl">🎬</span>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#05050a] relative overflow-hidden flex flex-col">
      {/* Background Decoration */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
         {/* Cyan/Blue glow spots matching Home page */}
        <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-cyan-500/10 rounded-full blur-[100px] opacity-30"></div>
        <div className="absolute bottom-0 right-1/4 w-[500px] h-[500px] bg-blue-600/10 rounded-full blur-[100px] opacity-30"></div>
      </div>

      {/* Main Container */}
      <div className="relative z-10 flex-grow">
        <div className="max-w-7xl mx-auto px-6 py-12">
          
          {/* Header Section */}
          <div className="flex flex-col md:flex-row justify-between items-end mb-12 gap-6">
            <div>
              <div className="inline-block mb-4 px-3 py-1 rounded-full border border-cyan-500/30 bg-cyan-950/30 backdrop-blur-sm">
                <span className="text-cyan-400 text-xs font-bold uppercase tracking-wider">✨ Dashboard</span>
              </div>
              <h1 className="text-4xl md:text-5xl font-bold text-white mb-2 tracking-tight">
                My Projects
              </h1>
              <p className="text-slate-400 text-lg max-w-2xl">
                Manage your creative works and track progress
              </p>
            </div>
            
            <Link
              to="/projects/new"
              className="bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white px-8 py-3 rounded-xl font-bold transition-all shadow-lg hover:shadow-cyan-500/25 flex items-center gap-2 group"
            >
              <span className="text-xl group-hover:scale-110 transition-transform">+</span>
              Create Project
            </Link>
          </div>

          {/* Stats Cards Row */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
            <StatsCard 
              label="Total Projects" 
              value={projects.length} 
              icon="📁" 
              color="from-cyan-500 to-blue-600"
            />
            <StatsCard 
              label="Completed" 
              value={projects.filter(p => p.status === 'completed').length} 
              icon="✅" 
              color="from-green-400 to-emerald-600"
            />
            <StatsCard 
              label="In Progress" 
              value={projects.filter(p => p.status === 'processing').length} 
              icon="⚡" 
              color="from-yellow-400 to-orange-500"
            />
            <StatsCard 
              label="Drafts" 
              value={projects.filter(p => p.status === 'draft').length} 
              icon="📝" 
              color="from-slate-400 to-slate-600"
            />
          </div>

          {error && (
            <div className="bg-red-500/10 border border-red-500/20 text-red-200 px-6 py-4 rounded-xl mb-8 flex items-center">
              <span className="mr-3">⚠️</span>
              {error}
            </div>
          )}

          {projects.length === 0 ? (
            <div className="text-center py-24">
              <div className="neo-glass bg-[#0f111a]/80 border border-white/5 rounded-3xl p-16 max-w-2xl mx-auto shadow-2xl">
                <div className="text-7xl mb-8 opacity-50">🎬</div>
                <h3 className="text-3xl font-bold text-white mb-4">Start Your Story</h3>
                <p className="text-slate-400 mb-10 text-lg">Create your first AI-powered webtoon video today.</p>
                <Link
                  to="/projects/new"
                  className="inline-flex items-center justify-center bg-gradient-to-r from-cyan-500 to-blue-600 text-white px-10 py-4 rounded-xl font-bold hover:shadow-lg hover:shadow-cyan-500/25 transition-all transform hover:-translate-y-1"
                >
                  Create First Project
                </Link>
              </div>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              {projects.map((project) => (
                <div
                  key={project.id}
                  className="group bg-[#0f111a] border border-white/5 rounded-2xl overflow-hidden hover:border-cyan-500/30 transition-all duration-300 hover:shadow-2xl hover:shadow-cyan-900/10 hover:-translate-y-1"
                >
                  {/* Card Image Area */}
                  <div className={`relative h-56 bg-gradient-to-br ${project.gradient || 'from-slate-800 to-slate-900'} group-hover:opacity-90 transition-opacity`}>
                     {/* Overlay Gradient */}
                    <div className="absolute inset-0 bg-gradient-to-t from-[#0f111a] via-transparent to-transparent"></div>
                    
                    {/* Status Badge */}
                    <div className="absolute top-4 right-4">
                      <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wide backdrop-blur-md ${getStatusColor(project.status)}`}>
                        {getStatusText(project.status)}
                      </span>
                    </div>

                    {/* Thumbnail Icon */}
                    <div className="absolute bottom-4 left-6">
                      <div className="text-6xl filter drop-shadow-lg transform group-hover:scale-110 transition-transform duration-300">{project.thumbnail || '🎬'}</div>
                    </div>
                  </div>
                  
                  {/* Card Content */}
                  <div className="p-6">
                    <h3 className="text-xl font-bold text-white mb-2 group-hover:text-cyan-400 transition-colors">{project.title}</h3>
                    <p className="text-slate-400 text-sm mb-6 line-clamp-2 h-10">
                      {project.description || 'No description provided.'}
                    </p>
                    
                    {/* Meta Info */}
                    <div className="flex items-center justify-between mb-6 pb-6 border-b border-white/5">
                      <div className="flex items-center space-x-2 text-slate-500 text-xs font-medium uppercase tracking-wide">
                        <span>🎬 {project.scenes_count || 0} SCENES</span>
                      </div>
                      <div className="flex items-center space-x-2 text-slate-500 text-xs font-medium uppercase tracking-wide">
                        <span>⏱️ {project.duration || '0m'}</span>
                      </div>
                    </div>
                    
                    {/* Progress Bar */}
                    <div className="space-y-2 mb-6">
                      <div className="flex justify-between text-xs text-slate-400 font-medium uppercase tracking-wide">
                        <span>Progress</span>
                        <span className="text-cyan-400">{getProgress(project.status)}%</span>
                      </div>
                      <div className="w-full bg-white/5 rounded-full h-1.5 overflow-hidden">
                        <div 
                          className="bg-gradient-to-r from-cyan-500 to-blue-500 h-full rounded-full transition-all duration-500" 
                          style={{ width: `${getProgress(project.status)}%` }}
                        ></div>
                      </div>
                    </div>
                    
                    {/* Actions */}
                    <div className="flex gap-3">
                      <Link
                        to={`/projects/${project.id}`}
                        className="flex-1 bg-white/5 hover:bg-white/10 text-white py-3 px-4 rounded-xl font-semibold transition-all text-center border border-white/5 hover:border-white/10"
                      >
                        {project.status === 'completed' ? 'Preview' : 'Edit Project'}
                      </Link>
                    </div>
                  </div>
                </div>
              ))}
              
              {/* Create New Project Card (Small) */}
              <Link 
                to="/projects/new" 
                className="group bg-[#0f111a]/50 border-2 border-dashed border-white/10 rounded-2xl flex flex-col items-center justify-center p-8 hover:border-cyan-500/50 hover:bg-cyan-950/10 transition-all cursor-pointer min-h-[400px]"
              >
                <div className="w-20 h-20 rounded-full bg-white/5 flex items-center justify-center mb-6 group-hover:bg-cyan-500/20 group-hover:scale-110 transition-all">
                  <span className="text-4xl text-slate-400 group-hover:text-cyan-400 transition-colors">+</span>
                </div>
                <h3 className="text-xl font-bold text-slate-300 group-hover:text-white transition-colors mb-2">Create New</h3>
                <p className="text-slate-500 text-sm text-center">Start a new creative project</p>
              </Link>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function StatsCard({ label, value, icon, color }: { label: string, value: number, icon: string, color: string }) {
  return (
    <div className="bg-[#0f111a] border border-white/5 rounded-2xl p-6 hover:border-white/10 transition-all">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-slate-400 text-xs font-bold uppercase tracking-wider mb-1">{label}</p>
          <p className="text-3xl font-bold text-white">{value}</p>
        </div>
        <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${color} flex items-center justify-center shadow-lg opacity-80`}>
          <span className="text-xl text-white">{icon}</span>
        </div>
      </div>
    </div>
  );
}

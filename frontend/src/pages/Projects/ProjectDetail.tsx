import { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { projectsApi } from '../../api/projects';
import type { Project } from '../../types';

export function ProjectDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (id) {
      loadProject(id);
    }
  }, [id]);

  useEffect(() => {
    if (project?.id) {
      localStorage.setItem('activeProjectId', project.id);
    }
  }, [project?.id]);

  const loadProject = async (projectId: string) => {
    try {
      const data = await projectsApi.getProject(projectId);
      setProject(data);
    } catch (err: any) {
      console.error('Failed to load project:', err);
      setError('无法加载项目详情');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!project || !window.confirm('确定要删除这个项目吗？此操作不可恢复。')) return;
    
    try {
      await projectsApi.deleteProject(project.id);
      navigate('/projects');
    } catch (err: any) {
      console.error('Failed to delete project:', err);
      alert('删除失败，请重试');
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
        <div className="text-center">
          <h2 className="text-2xl font-bold mb-4">⚠️ Error</h2>
          <p className="mb-6 text-slate-400">{error || 'Project not found'}</p>
          <Link to="/projects" className="bg-white/5 border border-white/10 px-6 py-2 rounded-xl hover:bg-white/10 transition text-white">
            Back to Projects
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#05050a] relative overflow-hidden text-white flex flex-col">
      {/* Background Decoration */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-cyan-500/10 rounded-full blur-[100px] opacity-30"></div>
        <div className="absolute bottom-0 right-1/4 w-[500px] h-[500px] bg-blue-600/10 rounded-full blur-[100px] opacity-30"></div>
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-6 py-12 w-full">
        {/* Header */}
        <div className="flex justify-between items-start mb-16">
          <div>
            <Link to="/projects" className="text-slate-400 hover:text-white mb-4 inline-flex items-center gap-2 transition text-sm font-medium uppercase tracking-wide group">
              <span className="group-hover:-translate-x-1 transition-transform">←</span> Back to List
            </Link>
            <h1 className="text-5xl font-bold text-white mb-4 tracking-tight">
              {project.title}
            </h1>
            <p className="text-slate-400 text-lg max-w-2xl leading-relaxed">{project.description || 'No description provided.'}</p>
          </div>
          <div className="flex gap-4">
             <button 
              onClick={handleDelete}
              className="px-6 py-3 bg-red-500/10 text-red-400 border border-red-500/20 rounded-xl hover:bg-red-500/20 transition font-medium"
            >
              Delete Project
            </button>
            <button className="px-6 py-3 bg-white/5 border border-white/10 text-white rounded-xl hover:bg-white/10 transition font-medium">
              Settings
            </button>
          </div>
        </div>

        {/* Workflow Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {/* 1. Script */}
          <Link to={`/projects/${project.id}/script`} className="group">
            <div className="bg-[#0f111a] border border-white/5 rounded-3xl p-8 h-full hover:border-cyan-500/50 transition-all duration-300 hover:shadow-2xl hover:shadow-cyan-900/20 hover:-translate-y-1 relative overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
              
              <div className="w-16 h-16 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-2xl flex items-center justify-center mb-8 shadow-lg shadow-cyan-500/20 group-hover:scale-110 transition-transform">
                <span className="text-3xl text-white">📝</span>
              </div>
              <h3 className="text-2xl font-bold text-white mb-3">Script</h3>
              <p className="text-slate-400 text-sm leading-relaxed mb-8">
                Write screenplay, dialogues and scene descriptions. AI writing assistance supported.
              </p>
              <div className="mt-auto text-cyan-400 text-sm font-bold uppercase tracking-wide flex items-center gap-2 group-hover:gap-3 transition-all">
                Start Writing <span>→</span>
              </div>
            </div>
          </Link>

          {/* 2. Characters */}
          <Link to={`/characters?project_id=${project.id}`} className="group">
            <div className="bg-[#0f111a] border border-white/5 rounded-3xl p-8 h-full hover:border-purple-500/50 transition-all duration-300 hover:shadow-2xl hover:shadow-purple-900/20 hover:-translate-y-1 relative overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-br from-purple-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
              
              <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-pink-600 rounded-2xl flex items-center justify-center mb-8 shadow-lg shadow-purple-500/20 group-hover:scale-110 transition-transform">
                <span className="text-3xl text-white">👥</span>
              </div>
              <h3 className="text-2xl font-bold text-white mb-3">Characters</h3>
              <p className="text-slate-400 text-sm leading-relaxed mb-8">
                Create and manage character profiles. Maintain consistent visual identity.
              </p>
              <div className="mt-auto text-purple-400 text-sm font-bold uppercase tracking-wide flex items-center gap-2 group-hover:gap-3 transition-all">
                Manage Characters <span>→</span>
              </div>
            </div>
          </Link>

          {/* 3. Storyboard */}
          <Link to={`/storyboard/${project.id}`} className="group">
            <div className="bg-[#0f111a] border border-white/5 rounded-3xl p-8 h-full hover:border-orange-500/50 transition-all duration-300 hover:shadow-2xl hover:shadow-orange-900/20 hover:-translate-y-1 relative overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-br from-orange-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
              
              <div className="w-16 h-16 bg-gradient-to-br from-orange-400 to-red-600 rounded-2xl flex items-center justify-center mb-8 shadow-lg shadow-orange-500/20 group-hover:scale-110 transition-transform">
                <span className="text-3xl text-white">🎬</span>
              </div>
              <h3 className="text-2xl font-bold text-white mb-3">Storyboard</h3>
              <p className="text-slate-400 text-sm leading-relaxed mb-8">
                Generate AI storyboards from script. Plan your shots and camera angles.
              </p>
              <div className="mt-auto text-orange-400 text-sm font-bold uppercase tracking-wide flex items-center gap-2 group-hover:gap-3 transition-all">
                View Storyboard <span>→</span>
              </div>
            </div>
          </Link>

          {/* 4. Export/Publish */}
          <Link to={`/export/${project.id}`} className="group">
            <div className="bg-[#0f111a] border border-white/5 rounded-3xl p-8 h-full hover:border-green-500/50 transition-all duration-300 hover:shadow-2xl hover:shadow-green-900/20 hover:-translate-y-1 relative overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-br from-green-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
              
              <div className="w-16 h-16 bg-gradient-to-br from-green-400 to-emerald-600 rounded-2xl flex items-center justify-center mb-8 shadow-lg shadow-green-500/20 group-hover:scale-110 transition-transform">
                <span className="text-3xl text-white">🚀</span>
              </div>
              <h3 className="text-2xl font-bold text-white mb-3">Export</h3>
              <p className="text-slate-400 text-sm leading-relaxed mb-8">
                Generate final video, export assets, or publish to platforms.
              </p>
              <div className="mt-auto text-green-400 text-sm font-bold uppercase tracking-wide flex items-center gap-2 group-hover:gap-3 transition-all">
                Publish <span>→</span>
              </div>
            </div>
          </Link>
        </div>

        {/* Recent Activity / Status (Placeholder) */}
        <div className="mt-16">
          <h2 className="text-xl font-bold text-white mb-6 uppercase tracking-wider">Recent Activity</h2>
          <div className="bg-[#0f111a] rounded-2xl p-8 text-center border border-white/5">
            <p className="text-slate-500">No recent activity recorded.</p>
          </div>
        </div>
      </div>
    </div>
  );
}

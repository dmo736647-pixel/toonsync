import { Outlet, Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { useI18n } from '../../contexts/I18nContext';
import { useState, useEffect } from 'react';

export function Layout() {
  const { user, logout } = useAuth();
  const { language, setLanguage, t } = useI18n();
  const navigate = useNavigate();
  const location = useLocation();
  const [isLangOpen, setIsLangOpen] = useState(false);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const isActive = (path: string) => location.pathname.startsWith(path);

  const activeProjectId = localStorage.getItem('activeProjectId');

  // Mouse trail effect
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      const cursor = document.createElement('div');
      cursor.className = 'fixed w-1 h-1 bg-cyan-400 rounded-full pointer-events-none z-50';
      cursor.style.left = e.clientX + 'px';
      cursor.style.top = e.clientY + 'px';
      cursor.style.animation = 'cursor-trail 0.5s ease-out forwards';
      document.body.appendChild(cursor);
      
      setTimeout(() => cursor.remove(), 500);
    };

    document.addEventListener('mousemove', handleMouseMove);

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
    };
  }, []);

  const languages = [
    { code: 'en', label: '🇺🇸 EN' },
    { code: 'zh', label: '🇨🇳 中文' },
    { code: 'ja', label: '🇯🇵 日本語' },
    { code: 'ko', label: '🇰🇷 한국어' },
    { code: 'es', label: '🇪🇸 ES' },
    { code: 'fr', label: '🇫🇷 FR' },
    { code: 'de', label: '🇩🇪 DE' },
  ] as const;

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Background is handled by index.css body style */}
      
      {/* Neural Network Nodes (Optional decoration) */}
      <div className="fixed inset-0 pointer-events-none z-0">
         <div className="absolute top-[20%] left-[10%] w-1 h-1 bg-cyan-400 rounded-full opacity-40 animate-pulse"></div>
         <div className="absolute top-[40%] right-[20%] w-1 h-1 bg-purple-400 rounded-full opacity-30 animate-pulse delay-1000"></div>
         <div className="absolute bottom-[30%] left-[30%] w-1 h-1 bg-pink-400 rounded-full opacity-30 animate-pulse delay-2000"></div>
      </div>

      {/* Main Container */}
      <div className="relative z-10">
        {/* Top Navigation */}
        <nav className="neo-glass border-b border-cyan-500/20 sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-6">
            <div className="flex items-center justify-between h-20">
              {/* Left Side: Logo & Navigation */}
              <div className="flex items-center gap-12">
                {/* Logo */}
                <Link to="/" className="group flex items-center gap-4 select-none no-underline">
                    {/* 1. 图标部分：Sync Wave (同步光波) */}
                    <div className="relative flex items-center justify-center w-10 h-10">
                        {/* 动态光晕背景 */}
                        <div className="absolute inset-0 bg-gradient-to-tr from-cyan-500 to-purple-600 rounded-full blur-xl opacity-20 group-hover:opacity-40 transition-all duration-500 animate-pulse"></div>
                        
                        {/* 主图标容器 */}
                        <div className="relative w-full h-full flex items-center justify-center transform group-hover:scale-105 transition-transform duration-300">
                            {/* 抽象流体图标 */}
                            <svg className="w-8 h-8" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M4 12C4 7.58172 7.58172 4 12 4C14.5 4 16.5 5 17.5 6.5C16 6.5 15 7.5 15 9C15 11.5 18 12.5 20 12C20 16.4183 16.4183 20 12 20C9.5 20 7.5 19 6.5 17.5C8 17.5 9 16.5 9 15C9 12.5 6 11.5 4 12Z" 
                                      fill="url(#wave-gradient)" 
                                      stroke="url(#wave-stroke)" strokeWidth="0.5"/>
                                <path d="M7.5 16C7.5 14 9.5 13.5 11 13.5C12.5 13.5 14.5 13 14.5 11" 
                                      stroke="white" strokeOpacity="0.5" strokeWidth="1.5" strokeLinecap="round"/>
                                <defs>
                                    <linearGradient id="wave-gradient" x1="4" y1="20" x2="20" y2="4" gradientUnits="userSpaceOnUse">
                                        <stop stopColor="#06b6d4"/>
                                        <stop offset="0.5" stopColor="#8b5cf6"/>
                                        <stop offset="1" stopColor="#ec4899"/>
                                    </linearGradient>
                                    <linearGradient id="wave-stroke" x1="4" y1="4" x2="20" y2="20" gradientUnits="userSpaceOnUse">
                                        <stop stopColor="white" stopOpacity="0.8"/>
                                        <stop offset="1" stopColor="white" stopOpacity="0.1"/>
                                    </linearGradient>
                                </defs>
                            </svg>
                        </div>
                    </div>

                    {/* 2. 文字部分 */}
                    <div className="flex flex-col">
                        <div className="flex items-center gap-0.5">
                            <span className="text-xl font-semibold tracking-tight text-white font-[Inter]">Toon</span>
                            <span className="text-xl font-bold tracking-tight text-transparent bg-clip-text bg-gradient-to-br from-white via-cyan-200 to-cyan-400">Sync</span>
                            <div className="ml-2 w-1.5 h-1.5 rounded-full bg-gradient-to-r from-cyan-400 to-purple-500 animate-pulse"></div>
                        </div>
                        <span className="text-[10px] font-medium text-slate-500 tracking-[0.15em] uppercase group-hover:text-slate-400 transition-colors pl-0.5">
                            {t('navSubtitle')}
                        </span>
                    </div>
                </Link>

                {/* Primary Navigation - Visible only when logged in */}
                {user && (
                  <div className="hidden md:flex items-center space-x-2">
                      <NavLink to="/projects" icon="📁" label="Projects" active={isActive('/projects')} />
                      <NavLink to={activeProjectId ? `/characters?project_id=${activeProjectId}` : '/characters'} icon="👥" label="Characters" active={isActive('/characters')} />
                      <NavLink to={activeProjectId ? `/storyboard/${activeProjectId}` : '/projects'} icon="🎬" label="Storyboard" active={isActive('/storyboard')} />
                  </div>
                )}
              </div>
              
              {/* Right Side: User Profile or Sign In */}
              <div className="flex items-center space-x-6">
                {/* Language Selector */}
                <div className="relative">
                  <button 
                    onClick={() => setIsLangOpen(!isLangOpen)}
                    className="flex items-center space-x-2 neo-glass px-3 py-1.5 rounded-full hover:bg-white/10 transition-all text-white text-sm font-medium"
                  >
                    <span>{languages.find(l => l.code === language)?.label}</span>
                    <svg className={`w-3 h-3 transition-transform ${isLangOpen ? 'rotate-180' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>
                  
                  {isLangOpen && (
                    <div className="absolute right-0 mt-2 w-40 neo-glass rounded-xl overflow-hidden border border-white/10 shadow-xl flex flex-col z-[100]">
                      {languages.map((lang) => (
                        <button
                          key={lang.code}
                          onClick={() => {
                            setLanguage(lang.code as any);
                            setIsLangOpen(false);
                          }}
                          className={`px-4 py-2 text-left text-sm hover:bg-white/10 transition-colors flex items-center justify-between ${
                            language === lang.code ? 'text-cyan-400 bg-white/5' : 'text-slate-300'
                          }`}
                        >
                          <span>{lang.label}</span>
                          {language === lang.code && <span className="w-1.5 h-1.5 rounded-full bg-cyan-400"></span>}
                        </button>
                      ))}
                    </div>
                  )}
                </div>

                {user ? (
                  <>
                    {/* User Profile Pill */}
                    <div className="flex items-center space-x-3 neo-glass px-4 py-2 rounded-full hover:bg-white/10 transition-all cursor-pointer group">
                        {/* Avatar */}
                        <div className="w-8 h-8 bg-gradient-to-r from-cyan-400 to-purple-500 rounded-full flex items-center justify-center text-white text-xs font-bold shadow-lg">
                            {user?.email?.charAt(0).toUpperCase() || 'C'}
                        </div>
                        
                        {/* Info */}
                        <div className="flex flex-col items-start">
                            <span className="text-white text-sm font-medium leading-none group-hover:text-cyan-300 transition-colors">
                                {user?.user_metadata?.full_name || user?.email?.split('@')[0] || 'Creator'}
                            </span>
                            <div className="flex items-center mt-0.5 space-x-1">
                                <span className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse"></span>
                                <span className="text-[10px] text-cyan-400 uppercase tracking-wider font-bold">
                                    {user?.app_metadata?.subscription_tier || 'FREE'}
                                </span>
                            </div>
                        </div>
                    </div>

                    {/* Sign Out Button */}
                    <button 
                        onClick={handleLogout}
                        className="flex items-center justify-center w-10 h-10 rounded-full neo-glass text-slate-400 hover:text-white hover:bg-red-500/20 hover:border-red-500/30 transition-all"
                        title="Sign Out"
                    >
                        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                        </svg>
                    </button>
                  </>
                ) : (
                  <Link to="/login" className="px-6 py-2 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white rounded-full font-medium transition-all shadow-lg hover:shadow-cyan-500/25">
                    {t('signIn')}
                  </Link>
                )}
              </div>
            </div>
          </div>
        </nav>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-6 py-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

function NavLink({ to, icon, label, active }: { to: string; icon: string; label: string; active: boolean }) {
  return (
    <Link
      to={to}
      className={`px-4 py-2 rounded-xl text-sm font-medium transition-all flex items-center space-x-2 ${
        active 
          ? 'bg-white/10 text-white shadow-lg border border-white/10' 
          : 'text-slate-400 hover:text-white hover:bg-white/5 border border-transparent'
      }`}
    >
      <span>{icon}</span>
      <span>{label}</span>
    </Link>
  );
}

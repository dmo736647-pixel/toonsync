import { useEffect, useMemo, useRef, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { projectsApi } from '../../api/projects';
import { scriptsApi } from '../../api/scripts';
import type { Project, Script } from '../../types';

export function ScriptEditor() {
  const { projectId } = useParams<{ projectId: string }>();
  const [project, setProject] = useState<Project | null>(null);
  const [script, setScript] = useState<Script | null>(null);
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');
  const [saveError, setSaveError] = useState<string | null>(null);

  const textareaRef = useRef<HTMLTextAreaElement | null>(null);
  const saveTimerRef = useRef<number | null>(null);
  const lastSavedContentRef = useRef<string>('');

  useEffect(() => {
    if (projectId) {
      loadData(projectId);
    }
  }, [projectId]);

  const loadData = async (id: string) => {
    try {
      const [projData, scriptData] = await Promise.all([
        projectsApi.getProject(id),
        scriptsApi.getScriptByProjectId(id)
      ]);
      
      setProject(projData);
      
      if (scriptData) {
        setScript(scriptData);
        const initial = String(scriptData.content || '');
        setContent(initial);
        lastSavedContentRef.current = initial;
      } else {
        // Create a new script if none exists
        const newScript = await scriptsApi.createScript(id, '');
        setScript(newScript);
        setContent('');
        lastSavedContentRef.current = '';
      }
    } catch (err) {
      console.error('Failed to load data:', err);
      setMessage('加载失败');
    } finally {
      setLoading(false);
    }
  };

  const saveContent = async (nextContent: string, mode: 'manual' | 'auto') => {
    if (!script) return;
    setSaving(true);
    setSaveError(null);
    setMessage(mode === 'auto' ? '自动保存中…' : '保存中…');
    try {
      await scriptsApi.updateScript(script.id, nextContent);
      lastSavedContentRef.current = nextContent;
      setMessage(mode === 'auto' ? '已自动保存' : '已保存');
      window.setTimeout(() => setMessage(''), 2000);
    } catch (err: any) {
      console.error('Failed to save script:', err);
      setSaveError(err?.response?.data?.detail || err?.message || '保存失败');
      setMessage('保存失败');
    } finally {
      setSaving(false);
    }
  };

  const handleSave = async () => {
    if (!script) return;
    await saveContent(content, 'manual');
  };

  useEffect(() => {
    if (!script) return;
    if (content === lastSavedContentRef.current) return;
    if (saveTimerRef.current) {
      window.clearTimeout(saveTimerRef.current);
    }
    saveTimerRef.current = window.setTimeout(() => {
      void saveContent(content, 'auto');
    }, 1200);
    return () => {
      if (saveTimerRef.current) {
        window.clearTimeout(saveTimerRef.current);
        saveTimerRef.current = null;
      }
    };
  }, [content, script]);

  useEffect(() => {
    const onKeyDown = (e: KeyboardEvent) => {
      const isSave = (e.ctrlKey || e.metaKey) && (e.key === 's' || e.key === 'S');
      if (!isSave) return;
      e.preventDefault();
      void handleSave();
    };
    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, [content, script]);

  const projectTitle = project?.title || project?.name || 'Project';
  const isDirty = content !== lastSavedContentRef.current;

  const scenes = useMemo(() => {
    const lines = content.split(/\r?\n/);
    const items: Array<{ title: string; offset: number }> = [];
    let offset = 0;
    for (const line of lines) {
      const match = line.match(/^\s*(场景\s*\d+[:：]?\s*.*|Scene\s*\d+[:：]?\s*.*)$/i);
      if (match) {
        items.push({ title: match[1].trim(), offset });
      }
      offset += line.length + 1;
    }
    return items;
  }, [content]);

  const jumpToOffset = (offset: number) => {
    const el = textareaRef.current;
    if (!el) return;
    el.focus();
    el.setSelectionRange(offset, offset);
  };

  const insertSceneHeading = () => {
    const el = textareaRef.current;
    const nextNo = scenes.length + 1;
    const heading = `\n场景 ${nextNo}：`;
    if (!el) {
      setContent((prev) => prev + heading);
      return;
    }
    const start = el.selectionStart ?? content.length;
    const end = el.selectionEnd ?? content.length;
    const next = content.slice(0, start) + heading + content.slice(end);
    setContent(next);
    window.setTimeout(() => {
      const cursor = start + heading.length;
      el.focus();
      el.setSelectionRange(cursor, cursor);
    }, 0);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#05050a] flex items-center justify-center text-white">
        <div className="w-16 h-16 bg-gradient-to-r from-cyan-500 to-blue-600 rounded-full animate-spin flex items-center justify-center shadow-lg shadow-cyan-500/20">
          <span className="text-white text-2xl">📝</span>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#05050a] text-white flex flex-col h-screen relative overflow-hidden">
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-cyan-500/10 rounded-full blur-[100px] opacity-30"></div>
        <div className="absolute bottom-0 right-1/4 w-[500px] h-[500px] bg-blue-600/10 rounded-full blur-[100px] opacity-30"></div>
      </div>

      <header className="relative z-10 px-6 py-4 flex justify-between items-center border-b border-white/10 bg-[#0f111a]/70 backdrop-blur-xl">
        <div className="flex items-center gap-4 min-w-0">
          <Link to={`/projects/${projectId}`} className="text-slate-400 hover:text-white transition font-bold">
            ← 返回项目
          </Link>
          <div className="min-w-0">
            <div className="text-xs text-slate-500 font-bold uppercase tracking-wider">Script</div>
            <h1 className="text-lg font-bold truncate">{projectTitle} · 剧本创作</h1>
          </div>
        </div>

        <div className="flex items-center gap-4">
          {(message || saveError) && (
            <div className={`text-sm font-bold ${saveError ? 'text-red-300' : 'text-green-300'}`}>
              {saveError || message}
            </div>
          )}
          <div className={`px-3 py-1 rounded-full border text-xs font-bold uppercase tracking-wider ${
            saveError
              ? 'border-red-500/30 text-red-300 bg-red-500/10'
              : saving
                ? 'border-cyan-500/30 text-cyan-300 bg-cyan-500/10'
                : isDirty
                  ? 'border-yellow-500/30 text-yellow-300 bg-yellow-500/10'
                  : 'border-green-500/30 text-green-300 bg-green-500/10'
          }`}
          >
            {saveError ? 'ERROR' : saving ? 'SAVING' : isDirty ? 'DRAFT' : 'SAVED'}
          </div>
          <button
            onClick={handleSave}
            disabled={saving}
            className="px-6 py-2 rounded-xl font-bold transition-all bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 shadow-lg hover:shadow-cyan-500/25 disabled:opacity-60"
          >
            {saving ? '保存中...' : '保存 (Ctrl+S)'}
          </button>
        </div>
      </header>

      <div className="relative z-10 flex-1 flex overflow-hidden">
        <div className="w-72 border-r border-white/10 bg-[#0f111a]/70 backdrop-blur-xl p-4 hidden md:flex flex-col">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">场景列表</h3>
            <button
              type="button"
              onClick={insertSceneHeading}
              className="text-xs font-bold text-cyan-400 hover:text-cyan-300 transition"
            >
              + 新场景
            </button>
          </div>

          {scenes.length === 0 ? (
            <div className="text-sm text-slate-500">
              还没有检测到场景标题。建议用“场景 1：...”或“Scene 1: ...”作为分段。
            </div>
          ) : (
            <div className="space-y-2 overflow-y-auto pr-1">
              {scenes.map((scene) => (
                <button
                  key={scene.offset}
                  type="button"
                  onClick={() => jumpToOffset(scene.offset)}
                  className="w-full text-left px-3 py-2 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 transition font-bold text-slate-200"
                >
                  <div className="text-sm truncate">{scene.title}</div>
                </button>
              ))}
            </div>
          )}
        </div>

        <div className="flex-1 p-6 overflow-hidden">
          <div className="h-full max-w-5xl mx-auto">
            <div className="h-full neo-glass bg-[#0f111a]/70 border border-white/10 rounded-3xl p-6 shadow-2xl shadow-cyan-900/10">
              <textarea
                ref={textareaRef}
                className="w-full h-full bg-transparent border-none resize-none focus:ring-0 text-base leading-relaxed text-slate-200 placeholder-slate-600"
                placeholder="在此处开始编写您的剧本...\n\n建议用：\n场景 1：开场\n场景 2：咖啡馆"
                value={content}
                onChange={(e) => setContent(e.target.value)}
                spellCheck={false}
              />
            </div>
          </div>
        </div>

        <div className="w-80 border-l border-white/10 bg-[#0f111a]/70 backdrop-blur-xl p-4 hidden lg:block">
          <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4">AI 助手</h3>
          <div className="bg-white/5 border border-white/10 rounded-2xl p-4">
            <p className="text-sm text-slate-200 font-bold mb-2">💡 写作灵感</p>
            <p className="text-xs text-slate-500">试着描述一个发生在雨夜的悬疑场景…</p>
            <button
              type="button"
              className="mt-3 w-full py-2 bg-cyan-500/10 text-cyan-300 text-sm rounded-xl hover:bg-cyan-500/15 transition font-bold border border-cyan-500/20"
            >
              生成建议
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

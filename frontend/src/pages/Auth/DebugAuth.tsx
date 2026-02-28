import { useEffect, useState } from 'react';
import { supabase } from '@/lib/supabase.ts';
import { useAuth } from '../../contexts/AuthContext';

export function DebugAuth() {
  const [sessionInfo, setSessionInfo] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const { user, isAuthenticated } = useAuth();

  useEffect(() => {
    const checkSession = async () => {
      const { data: { session } } = await supabase.auth.getSession();
      setSessionInfo({
        hasSession: !!session,
        user: session?.user?.email,
        userId: session?.user?.id,
        accessToken: session?.access_token ? 'Present' : 'Missing',
        emailConfirmed: session?.user?.email_confirmed_at || 'Not confirmed',
      });
      setLoading(false);
    };

    checkSession();
  }, []);

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <div className="max-w-2xl mx-auto space-y-6">
        <h1 className="text-3xl font-bold text-cyan-400">🔍 认证调试信息</h1>
        
        <div className="bg-gray-800 p-6 rounded-lg space-y-4">
          <h2 className="text-xl font-semibold">当前用户状态</h2>
          <div className="space-y-2">
            <p><strong className="text-cyan-400">isAuthenticated:</strong> {isAuthenticated ? '✅ Yes' : '❌ No'}</p>
            <p><strong className="text-cyan-400">User Email:</strong> {user?.email || 'None'}</p>
            <p><strong className="text-cyan-400">User ID:</strong> {user?.id || 'None'}</p>
          </div>
        </div>

        {loading ? (
          <p className="text-gray-400">正在加载会话信息...</p>
        ) : sessionInfo && (
          <div className="bg-gray-800 p-6 rounded-lg space-y-4">
            <h2 className="text-xl font-semibold">Supabase 会话信息</h2>
            <div className="space-y-2 font-mono text-sm">
              <p><strong className="text-cyan-400">Has Session:</strong> {sessionInfo.hasSession ? '✅ Yes' : '❌ No'}</p>
              <p><strong className="text-cyan-400">User:</strong> {sessionInfo.user || 'None'}</p>
              <p><strong className="text-cyan-400">User ID:</strong> {sessionInfo.userId || 'None'}</p>
              <p><strong className="text-cyan-400">Access Token:</strong> {sessionInfo.accessToken}</p>
              <p><strong className="text-cyan-400">Email Confirmed:</strong> {sessionInfo.emailConfirmed}</p>
            </div>
          </div>
        )}

        <div className="bg-yellow-900/50 border border-yellow-500 p-4 rounded-lg">
          <h3 className="font-semibold text-yellow-400 mb-2">💡 调试说明</h3>
          <ul className="list-disc list-inside space-y-1 text-sm text-yellow-200">
            <li>如果 <code className="bg-gray-700 px-1 rounded">isAuthenticated</code> 是 ❌ No，说明没有登录</li>
            <li>如果 <code className="bg-gray-700 px-1 rounded">Email Confirmed</code> 是 "Not confirmed"，需要验证邮箱</li>
            <li>QQ 邮箱可能收不到验证邮件，建议使用 Gmail、Outlook 或其他国际邮箱</li>
            <li>可以暂时关闭邮箱验证功能进行测试（在 Supabase 后台）</li>
          </ul>
        </div>

        <button
          onClick={() => window.location.reload()}
          className="w-full py-3 bg-cyan-600 hover:bg-cyan-500 rounded-lg font-medium transition-all"
        >
          🔄 刷新页面
        </button>

        <button
          onClick={async () => {
            await supabase.auth.signOut();
            window.location.reload();
          }}
          className="w-full py-3 bg-red-600 hover:bg-red-500 rounded-lg font-medium transition-all"
        >
          🚪 退出登录
        </button>
      </div>
    </div>
  );
}
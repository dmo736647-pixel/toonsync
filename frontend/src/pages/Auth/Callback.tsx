import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { supabase } from '@/lib/supabase.ts';
import { useAuth } from '../../contexts/AuthContext';

export function AuthCallback() {
  const [searchParams] = useSearchParams();
  const [message, setMessage] = useState('正在验证您的账户...');
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  const { refreshAuth } = useAuth();

  useEffect(() => {
    const handleAuthCallback = async () => {
      try {
        const token = searchParams.get('token');
        const type = searchParams.get('type');
        const next = searchParams.get('next');

        if (!token || !type) {
          setError('缺少必要的验证参数');
          return;
        }

        // 刷新认证状态
        await refreshAuth();

        // 根据不同类型的验证进行处理
        switch (type) {
          case 'email':
            setMessage('✅ 邮箱验证成功！正在跳转...');
            // 验证邮箱后自动跳转到主页或指定页面
            setTimeout(() => {
              navigate(next || '/');
            }, 1500);
            break;
          case 'recovery':
            setMessage('✅ 密码已重置！正在跳转到登录页...');
            // 密码恢复后跳转到登录页
            setTimeout(() => {
              navigate('/login');
            }, 1500);
            break;
          case 'signup':
            setMessage('✅ 注册成功！正在跳转...');
            // 完成注册后跳转到主页
            setTimeout(() => {
              navigate('/');
            }, 1500);
            break;
          default:
            setMessage('✅ 验证成功！正在跳转...');
            setTimeout(() => {
              navigate('/');
            }, 1500);
        }
      } catch (err) {
        console.error('Authentication callback error:', err);
        setError('验证过程中出现错误，请重试');
      }
    };

    handleAuthCallback();
  }, [searchParams, navigate, refreshAuth]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 via-cyan-950 to-purple-950 px-4">
      <div className="max-w-md w-full space-y-8 bg-gray-800/50 backdrop-blur-xl p-8 rounded-2xl shadow-2xl border border-cyan-500/20">
        <div className="text-center">
          {error ? (
            <div className="space-y-4">
              <div className="bg-red-900/50 border border-red-500 text-red-200 px-4 py-3 rounded-lg">
                <p className="font-medium">❌ {error}</p>
              </div>
              <button
                onClick={() => navigate('/login')}
                className="w-full px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg font-medium transition-all"
              >
                返回登录页
              </button>
            </div>
          ) : (
            <>
              <div className="relative mx-auto mb-6">
                <div className="animate-spin rounded-full h-16 w-16 border-4 border-cyan-500/30 border-t-cyan-400 mx-auto"></div>
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="w-8 h-8 bg-cyan-400 rounded-full animate-pulse"></div>
                </div>
              </div>
              <p className="text-white text-lg font-medium">{message}</p>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
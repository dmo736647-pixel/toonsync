import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { supabase } from '@/lib/supabase.ts';

export function AuthCallback() {
  const [searchParams] = useSearchParams();
  const [message, setMessage] = useState('正在验证您的账户...');
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const handleAuthCallback = async () => {
      try {
        const token = searchParams.get('token');
        const type = searchParams.get('type');

        if (!token || !type) {
          setError('缺少必要的验证参数');
          return;
        }

        // 根据不同类型的验证进行处理
        switch (type) {
          case 'email':
            setMessage('正在验证您的邮箱...');
            // 验证邮箱后自动跳转到主页
            setTimeout(() => {
              navigate('/');
            }, 2000);
            break;
          case 'recovery':
            setMessage('正在恢复您的账户...');
            // 密码恢复后跳转到登录页
            setTimeout(() => {
              navigate('/login');
            }, 2000);
            break;
          case 'signup':
            setMessage('正在完成注册...');
            // 完成注册后跳转到主页
            setTimeout(() => {
              navigate('/');
            }, 2000);
            break;
          default:
            setMessage('正在处理验证请求...');
            setTimeout(() => {
              navigate('/');
            }, 2000);
        }
      } catch (err) {
        console.error('Authentication callback error:', err);
        setError('验证过程中出现错误，请重试');
      }
    };

    handleAuthCallback();
  }, [searchParams, navigate]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-900 px-4">
      <div className="max-w-md w-full space-y-8 bg-gray-800 p-8 rounded-xl shadow-2xl border border-gray-700">
        <div className="text-center">
          {error ? (
            <div className="bg-red-900/50 border border-red-500 text-red-200 px-4 py-3 rounded">
              {error}
            </div>
          ) : (
            <>
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-500 mx-auto mb-4"></div>
              <p className="text-white">{message}</p>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
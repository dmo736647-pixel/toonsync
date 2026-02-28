import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { useI18n } from '../../contexts/I18nContext';

const translations = {
  en: {
    title: 'Sign in to your account',
    subtitle: 'Or',
    trial: 'start your 14-day free trial',
    email: 'Email address',
    password: 'Password',
    signIn: 'Sign in',
    loading: 'Signing in...',
    forgotPassword: 'Forgot password?',
  },
  zh: {
    title: '登录账户',
    subtitle: '或者',
    trial: '开始 14 天免费试用',
    email: '邮箱地址',
    password: '密码',
    signIn: '登录',
    loading: '登录中...',
    forgotPassword: '忘记密码？',
  },
  ja: {
    title: 'アカウントにログイン',
    subtitle: 'または',
    trial: '14 日間の無料トライアルを開始',
    email: 'メールアドレス',
    password: 'パスワード',
    signIn: 'サインイン',
    loading: 'ログイン中...',
    forgotPassword: 'パスワードをお忘れですか？',
  },
  ko: {
    title: '계정에 로그인',
    subtitle: '또는',
    trial: '14 일 무료 체험 시작',
    email: '이메일 주소',
    password: '비밀번호',
    signIn: '로그인',
    loading: '로그인 중...',
    forgotPassword: '비밀번호를 잊으셨나요?',
  },
  es: {
    title: 'Iniciar sesión en tu cuenta',
    subtitle: 'O',
    trial: 'comienza tu prueba gratuita de 14 días',
    email: 'Correo electrónico',
    password: 'Contraseña',
    signIn: 'Iniciar sesión',
    loading: 'Iniciando sesión...',
    forgotPassword: '¿Olvidaste tu contraseña?',
  },
  fr: {
    title: 'Se connecter à votre compte',
    subtitle: 'Ou',
    trial: 'commencez votre essai gratuit de 14 jours',
    email: 'Adresse e-mail',
    password: 'Mot de passe',
    signIn: 'Se connecter',
    loading: 'Connexion en cours...',
    forgotPassword: 'Mot de passe oublié ?',
  },
  de: {
    title: 'Bei Ihrem Konto anmelden',
    subtitle: 'Oder',
    trial: 'Starten Sie Ihre 14-tägige kostenlose Testversion',
    email: 'E-Mail-Adresse',
    password: 'Passwort',
    signIn: 'Anmelden',
    loading: 'Anmeldung...',
    forgotPassword: 'Passwort vergessen?',
  },
};

type Language = keyof typeof translations;

export function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const { language } = useI18n();
  const navigate = useNavigate();

  const lang: Language = language;
  const t = translations[lang];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      await login(email, password);
      navigate('/');
    } catch (err: any) {
      setError(err.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 via-cyan-950 to-purple-950 px-4 py-12">
      {/* Animated background elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-purple-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-cyan-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-2000"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-80 h-80 bg-pink-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-4000"></div>
      </div>

      <div className="max-w-md w-full space-y-8 bg-gray-800/50 backdrop-blur-xl p-8 rounded-2xl shadow-2xl border border-cyan-500/20 relative z-10">
        <div>
          {/* Logo */}
          <div className="flex justify-center mb-6">
            <div className="w-16 h-16 bg-gradient-to-br from-cyan-400 to-purple-600 rounded-2xl flex items-center justify-center shadow-lg transform hover:scale-105 transition-transform">
              <svg className="w-10 h-10 text-white" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M4 12C4 7.58172 7.58172 4 12 4C14.5 4 16.5 5 17.5 6.5C16 6.5 15 7.5 15 9C15 11.5 18 12.5 20 12C20 16.4183 16.4183 20 12 20C9.5 20 7.5 19 6.5 17.5C8 17.5 9 16.5 9 15C9 12.5 6 11.5 4 12Z" fill="white" fillOpacity="0.9"/>
              </svg>
            </div>
          </div>
          
          <h2 className="mt-6 text-center text-3xl font-extrabold text-white">
            {t.title}
          </h2>
          <p className="mt-2 text-center text-sm text-gray-400">
            {t.subtitle}{' '}
            <Link to="/register" className="font-medium text-cyan-400 hover:text-cyan-300 transition-colors">
              {t.trial}
            </Link>
          </p>
        </div>

        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="bg-red-900/50 border border-red-500/50 text-red-200 px-4 py-3 rounded-xl flex items-center">
              <span className="mr-2">⚠️</span>
              {error}
            </div>
          )}
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                {t.email}
              </label>
              <input
                type="email"
                required
                className="w-full px-4 py-3 bg-gray-700/50 border border-gray-600 rounded-xl placeholder-gray-500 text-white focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition-all"
                placeholder={t.email}
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={loading}
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                {t.password}
              </label>
              <input
                type="password"
                required
                className="w-full px-4 py-3 bg-gray-700/50 border border-gray-600 rounded-xl placeholder-gray-500 text-white focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition-all"
                placeholder={t.password}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={loading}
              />
            </div>
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <input
                type="checkbox"
                id="remember"
                className="h-4 w-4 text-cyan-600 focus:ring-cyan-500 border-gray-600 rounded bg-gray-700"
              />
              <label htmlFor="remember" className="ml-2 block text-sm text-gray-300">
                Remember me
              </label>
            </div>
            <div className="text-sm">
              <a href="#" className="text-cyan-400 hover:text-cyan-300 transition-colors">
                {t.forgotPassword}
              </a>
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={loading}
              className="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-xl text-white bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-cyan-500 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-cyan-500/25 transform hover:scale-105"
            >
              {loading ? (
                <>
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  {t.loading}
                </>
              ) : (
                t.signIn
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
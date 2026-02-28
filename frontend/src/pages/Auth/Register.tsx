import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { supabase } from '@/lib/supabase.ts';
import { useI18n } from '../../contexts/I18nContext';

const translations = {
  en: {
    title: 'Create your account',
    subtitle: 'Already have an account?',
    signIn: 'Sign in',
    fullName: 'Full Name',
    email: 'Email address',
    password: 'Password',
    signUp: 'Sign up',
    successTitle: '🎉 Registration Successful!',
    successMessage: 'We\'ve sent a verification email to',
    successInstruction: 'Please click the verification link in the email to activate your account.',
    successNote: 'After verification, you can log in with your email and password.',
    goToLogin: 'Go to Login Page',
    checkingEmail: 'Checking email...',
  },
  zh: {
    title: '创建账户',
    subtitle: '已有账户？',
    signIn: '登录',
    fullName: '姓名',
    email: '邮箱地址',
    password: '密码',
    signUp: '注册',
    successTitle: '🎉 注册成功！',
    successMessage: '我们已向您的邮箱',
    successInstruction: '请点击邮件中的验证链接完成账户激活。',
    successNote: '验证后，您可以使用注册的邮箱和密码登录。',
    goToLogin: '前往登录页面',
    checkingEmail: '检查邮箱中...',
  },
  ja: {
    title: 'アカウントを作成',
    subtitle: 'すでにアカウントをお持ちですか？',
    signIn: 'サインイン',
    fullName: '氏名',
    email: 'メールアドレス',
    password: 'パスワード',
    signUp: '登録',
    successTitle: '🎉 登録完了！',
    successMessage: '確認メールを送信しました',
    successInstruction: 'メール内の確認リンクをクリックしてアカウントを有効化してください。',
    successNote: '確認後、メールアドレスとパスワードでログインできます。',
    goToLogin: 'ログインページへ',
    checkingEmail: 'メールを確認中...',
  },
  ko: {
    title: '계정 만들기',
    subtitle: '이미 계정이 있으신가요?',
    signIn: '로그인',
    fullName: '이름',
    email: '이메일 주소',
    password: '비밀번호',
    signUp: '등록',
    successTitle: '🎉 등록 성공!',
    successMessage: '인증 이메일을 보냈습니다',
    successInstruction: '이메일의 인증 링크를 클릭하여 계정을 활성화하세요.',
    successNote: '인증 후 이메일과 비밀번호로 로그인할 수 있습니다.',
    goToLogin: '로그인 페이지로',
    checkingEmail: '이메일 확인 중...',
  },
  es: {
    title: 'Crear cuenta',
    subtitle: '¿Ya tienes cuenta?',
    signIn: 'Iniciar sesión',
    fullName: 'Nombre completo',
    email: 'Correo electrónico',
    password: 'Contraseña',
    signUp: 'Registrarse',
    successTitle: '🎉 ¡Registro exitoso!',
    successMessage: 'Hemos enviado un correo de verificación a',
    successInstruction: 'Haz clic en el enlace de verificación del correo para activar tu cuenta.',
    successNote: 'Después de la verificación, puedes iniciar sesión con tu correo y contraseña.',
    goToLogin: 'Ir a inicio de sesión',
    checkingEmail: 'Verificando correo...',
  },
  fr: {
    title: 'Créer un compte',
    subtitle: 'Déjà un compte ?',
    signIn: 'Se connecter',
    fullName: 'Nom complet',
    email: 'Adresse e-mail',
    password: 'Mot de passe',
    signUp: 'S\'inscrire',
    successTitle: '🎉 Inscription réussie !',
    successMessage: 'Nous avons envoyé un e-mail de vérification à',
    successInstruction: 'Cliquez sur le lien de vérification dans l\'e-mail pour activer votre compte.',
    successNote: 'Après vérification, vous pouvez vous connecter avec votre e-mail et mot de passe.',
    goToLogin: 'Aller à la connexion',
    checkingEmail: 'Vérification de l\'e-mail...',
  },
  de: {
    title: 'Konto erstellen',
    subtitle: 'Bereits ein Konto?',
    signIn: 'Anmelden',
    fullName: 'Vollständiger Name',
    email: 'E-Mail-Adresse',
    password: 'Passwort',
    signUp: 'Registrieren',
    successTitle: '🎉 Registrierung erfolgreich!',
    successMessage: 'Wir haben eine Verifizierungs-E-Mail gesendet an',
    successInstruction: 'Klicken Sie auf den Verifizierungslink in der E-Mail, um Ihr Konto zu aktivieren.',
    successNote: 'Nach der Verifizierung können Sie sich mit Ihrer E-Mail und Ihrem Passwort anmelden.',
    goToLogin: 'Zur Anmeldung',
    checkingEmail: 'E-Mail wird überprüft...',
  },
};

type Language = keyof typeof translations;

export function Register() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);
  const { language } = useI18n();

  const lang: Language = language;
  const t = translations[lang];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      const { error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          data: {
            full_name: fullName,
          },
        },
      });
      if (error) throw error;
      setSuccess(true);
    } catch (err: any) {
      setError(err.message || 'Registration failed');
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
            <Link to="/login" className="font-medium text-cyan-400 hover:text-cyan-300 transition-colors">
              {t.signIn}
            </Link>
          </p>
        </div>

        {success ? (
          <div className="mt-8 space-y-6">
            <div className="bg-green-900/50 border border-green-500/50 text-green-200 px-6 py-4 rounded-xl">
              <h3 className="font-bold text-lg mb-3 flex items-center">
                <span className="mr-2">✅</span> {t.successTitle}
              </h3>
              <p className="mb-2">{t.successMessage} <strong className="text-cyan-300">{email}</strong></p>
              <p className="text-sm opacity-90">{t.successInstruction}</p>
            </div>
            <div className="text-center space-y-3">
              <p className="text-gray-400 text-sm">{t.successNote}</p>
              <Link 
                to="/login" 
                className="inline-flex items-center justify-center px-6 py-3 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white rounded-xl font-medium transition-all shadow-lg hover:shadow-cyan-500/25 transform hover:scale-105"
              >
                {t.goToLogin} →
              </Link>
            </div>
          </div>
        ) : (
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
                  {t.fullName}
                </label>
                <input
                  type="text"
                  required
                  className="w-full px-4 py-3 bg-gray-700/50 border border-gray-600 rounded-xl placeholder-gray-500 text-white focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition-all"
                  placeholder={t.fullName}
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  disabled={loading}
                />
              </div>
              
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
                  minLength={6}
                  className="w-full px-4 py-3 bg-gray-700/50 border border-gray-600 rounded-xl placeholder-gray-500 text-white focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition-all"
                  placeholder={t.password}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  disabled={loading}
                />
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
                    {t.checkingEmail}
                  </>
                ) : (
                  t.signUp
                )}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
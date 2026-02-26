import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

const translations: Record<string, Record<string, string>> = {
  en: {
    navSubtitle: 'Storytelling First',
    signIn: 'Sign In',
    heroSubtitle: 'Create Webtoon Videos with Perfect Character Consistency. The only AI tool that combines Story + Character + Multi-language Lip Sync.',
    feature1Title: 'Storytelling First',
    feature1Desc: 'Generate complete story arcs with character development and emotional progression. Not just videos, but meaningful narratives.',
    feature2Title: 'Character Consistency',
    feature2Desc: 'Maintain consistent character appearance across scenes. One character, multiple scenes, perfect consistency every time.',
    feature3Title: 'Perfect Lip Sync',
    feature3Desc: 'Multi-language lip sync support. English, Chinese, Japanese, Korean, Spanish, French, German - all with perfect mouth animation.',
    faqTitle: 'Common Questions',
    faqSubtitle: 'Have other questions? Contact us at',
    faq1Q: 'What is ToonSync and how does it work?',
    faq1A: 'ToonSync is the world\'s first AI webtoon video maker that prioritizes storytelling. It uses advanced AI models to generate consistent characters, coherent story arcs, and perfect lip-sync animation from your text descriptions.',
    faq2Q: 'Is ToonSync really free to use?',
    faq2A: 'Yes, ToonSync offers a generous free tier that allows you to create short webtoon videos with no credit card required. We believe in empowering creators to tell their stories without barriers.',
    faq3Q: 'How do you maintain character consistency?',
    faq3A: 'We use proprietary \'Character Lock\' technology. Once you define a character, our system maintains their facial features, clothing, and style across all generated scenes, regardless of camera angle or pose.',
    faq4Q: 'What languages are supported for lip sync?',
    faq4A: 'We currently support perfect lip synchronization for English, Chinese (Mandarin), Japanese, Korean, Spanish, French, and German, with more languages coming soon.',
    whyDifferentTitle: 'Why We\'re Different',
    otherToolsTitle: '❌ Other AI Video Tools',
    ourToolTitle: '✅ AI Webtoon Maker',
    languageSupportTitle: '🌍 Global Language Support',
    pricingTitle: '💰 Simple Pricing',
    freeTitle: 'Free',
    freePrice: '$0',
    freeFeature1: '• 3 projects',
    freeFeature2: '• 5-minute videos',
    freeFeature3: '• Basic characters',
    freeFeature4: '• English TTS',
    freeButton: 'Get Started',
    proTitle: 'Pro',
    proPrice: '$29',
    proMonth: '/mo',
    proFeature1: '• Unlimited projects',
    proFeature2: '• 30-minute videos',
    proFeature3: '• Advanced characters',
    proFeature4: '• Multi-language TTS',
    proFeature5: '• Character consistency AI',
    proButton: 'Start Pro Trial',
    enterpriseTitle: 'Enterprise',
    enterprisePrice: '$99',
    enterpriseFeature1: '• Team collaboration',
    enterpriseFeature2: '• API access',
    enterpriseFeature3: '• Custom character training',
    enterpriseFeature4: '• Priority support',
    enterpriseFeature5: '• White-label options',
    enterpriseButton: 'Contact Sales',
    ctaTitle: 'Ready to Create Amazing Webtoon Videos?',
    ctaSubtitle: 'Join thousands of creators who are already using AI Webtoon Maker',
    startNow: '🚀 Start Creating Now',
    contactUs: '📧 Contact Us',
    footerText: 'Made with ❤️ for global creators',
    support: 'Support',
    privacy: 'Privacy',
    terms: 'Terms',
  },
  zh: {
    navSubtitle: '故事优先',
    signIn: '登录',
    heroSubtitle: '创建具有完美角色一致性的漫画视频。唯一结合故事+角色+多语言口型同步的AI工具。',
    feature1Title: '故事优先',
    feature1Desc: '生成完整的故事弧线，包含角色发展和情感递进。不仅仅是视频，更是有意义的叙事。',
    feature2Title: '角色一致性',
    feature2Desc: '在场景之间保持一致的角色外观。一个角色，多个场景，每次都完美一致。',
    feature3Title: '完美口型同步',
    feature3Desc: '多语言口型同步支持。英语、中文、日语、韩语、西班牙语、法语、德语 - 全部完美口型动画。',
    faqTitle: '常见问题',
    faqSubtitle: '有其他问题？联系我们：',
    faq1Q: 'ToonSync是什么，它是如何工作的？',
    faq1A: 'ToonSync是世界上第一个优先考虑故事性的AI漫画视频制作器。它使用先进的AI模型从您的文本描述生成一致的角色、连贯的故事弧线和完美的口型同步动画。',
    faq2Q: 'ToonSync真的免费吗？',
    faq2A: '是的，ToonSync提供慷慨的免费层级，让您无需信用卡即可创建短视频。我们相信赋予创作者无障碍讲述故事的能力。',
    faq3Q: '你们如何保持角色一致性？',
    faq3A: '我们使用专有的"角色锁定"技术。一旦您定义了一个角色，我们的系统将在所有生成的场景中保持其面部特征、服装和风格，无论摄像机角度或姿势如何。',
    faq4Q: '口型同步支持哪些语言？',
    faq4A: '我们目前支持英语、中文（普通话）、日语、韩语、西班牙语、法语和德语的完美口型同步，更多语言即将推出。',
    whyDifferentTitle: '为什么我们与众不同',
    otherToolsTitle: '❌ 其他AI视频工具',
    ourToolTitle: '✅ AI漫画制作器',
    languageSupportTitle: '🌍 全球语言支持',
    pricingTitle: '💰 简单定价',
    freeTitle: '免费',
    freePrice: '¥0',
    freeFeature1: '• 3个项目',
    freeFeature2: '• 5分钟视频',
    freeFeature3: '• 基础角色',
    freeFeature4: '• 英语语音',
    freeButton: '开始使用',
    proTitle: '专业版',
    proPrice: '¥199',
    proMonth: '/月',
    proFeature1: '• 无限项目',
    proFeature2: '• 30分钟视频',
    proFeature3: '• 高级角色',
    proFeature4: '• 多语言语音',
    proFeature5: '• 角色一致性AI',
    proButton: '开始专业试用',
    enterpriseTitle: '企业版',
    enterprisePrice: '¥699',
    enterpriseFeature1: '• 团队协作',
    enterpriseFeature2: '• API访问',
    enterpriseFeature3: '• 自定义角色训练',
    enterpriseFeature4: '• 优先支持',
    enterpriseFeature5: '• 白标选项',
    enterpriseButton: '联系销售',
    ctaTitle: '准备好创建精彩的漫画视频了吗？',
    ctaSubtitle: '加入已经在使用AI漫画制作器的数千名创作者',
    startNow: '🚀 立即开始创作',
    contactUs: '📧 联系我们',
    footerText: '用❤️为全球创作者制作',
    support: '支持',
    privacy: '隐私',
    terms: '条款',
  },
  ja: {
    navSubtitle: 'ストーリーテリング・ファースト',
    signIn: 'ログイン',
    heroSubtitle: '完璧なキャラクター一貫性でウェブトゥーン動画を作成。ストーリー+キャラクター+多言語リップシンクを組み合わせた唯一のAIツール。',
    feature1Title: 'ストーリーテリング・ファースト',
    feature1Desc: 'キャラクターの成長と感情の進行を含む完全なストーリーアークを生成。単なる動画ではなく、意味のある物語を。',
    feature2Title: 'キャラクター一貫性',
    feature2Desc: 'シーン間で一貫したキャラクターの外観を維持。1人のキャラクター、複数のシーン、毎回完璧な一貫性。',
    feature3Title: '完璧なリップシンク',
    feature3Desc: '多言語リップシンク対応。英語、中国語、日本語、韓国語、スペイン語、フランス語、ドイツ語 - すべて完璧な口のアニメーション。',
    faqTitle: 'よくある質問',
    faqSubtitle: '他にご質問がありますか？お問い合わせ：',
    faq1Q: 'ToonSyncとは何ですか、どのように機能しますか？',
    faq1A: 'ToonSyncは、ストーリーテリングを優先する世界初のAIウェブトゥーン動画メーカーです。高度なAIモデルを使用して、テキストの説明から一貫したキャラクター、首尾一貫したストーリーアーク、完璧なリップシンクアニメーションを生成します。',
    faq2Q: 'ToonSyncは本当に無料ですか？',
    faq2A: 'はい、ToonSyncは寛大な無料プランを提供しており、クレジットカードなしで短いウェブトゥーン動画を作成できます。クリエイターが障壁なく物語を語れるようにすることを信じています。',
    faq3Q: 'キャラクターの一貫性はどのように維持しますか？',
    faq3A: '独自の「キャラクターロック」技術を使用しています。キャラクターを定義すると、カメラの角度やポーズに関係なく、生成されたすべてのシーンでシステムが顔の特徴、服装、スタイルを維持します。',
    faq4Q: 'リップシンクでサポートされている言語は何ですか？',
    faq4A: '現在、英語、中国語（北京語）、日本語、韓国語、スペイン語、フランス語、ドイツ語の完璧なリップシンクをサポートしており、さらに多くの言語が近日公開予定です。',
    whyDifferentTitle: '私たちが異なる理由',
    otherToolsTitle: '❌ 他のAI動画ツール',
    ourToolTitle: '✅ AIウェブトゥーンメーカー',
    languageSupportTitle: '🌍 グローバル言語サポート',
    pricingTitle: '💰 シンプルな料金プラン',
    freeTitle: '無料',
    freePrice: '$0',
    freeFeature1: '• 3プロジェクト',
    freeFeature2: '• 5分動画',
    freeFeature3: '• 基本キャラクター',
    freeFeature4: '• 英語TTS',
    freeButton: '始める',
    proTitle: 'プロ',
    proPrice: '$29',
    proMonth: '/月',
    proFeature1: '• 無制限プロジェクト',
    proFeature2: '• 30分動画',
    proFeature3: '• 高度なキャラクター',
    proFeature4: '• 多言語TTS',
    proFeature5: '• キャラクター一貫性AI',
    proButton: 'プロトライアル開始',
    enterpriseTitle: 'エンタープライズ',
    enterprisePrice: '$99',
    enterpriseFeature1: '• チームコラボレーション',
    enterpriseFeature2: '• APIアクセス',
    enterpriseFeature3: '• カスタムキャラクタートレーニング',
    enterpriseFeature4: '• 優先サポート',
    enterpriseFeature5: '• ホワイトラベルオプション',
    enterpriseButton: '営業に連絡',
    ctaTitle: '素晴らしいウェブトゥーン動画を作成する準備はできましたか？',
    ctaSubtitle: 'すでにAIウェブトゥーンメーカーを使用している数千人のクリエイターに参加',
    startNow: '🚀 今すぐ作成開始',
    contactUs: '📧 お問い合わせ',
    footerText: '❤️を込めてグローバルクリエイターのために作成',
    support: 'サポート',
    privacy: 'プライバシー',
    terms: '利用規約',
  },
  ko: {
    navSubtitle: '스토리텔링 퍼스트',
    signIn: '로그인',
    heroSubtitle: '완벽한 캐릭터 일관성으로 웹툰 비디오를 만드세요. 스토리 + 캐릭터 + 다국어 립싱크를 결합한 유일한 AI 도구.',
    feature1Title: '스토리텔링 퍼스트',
    feature1Desc: '캐릭터 발전과 감정적 진행이 포함된 완전한 스토리 아크를 생성합니다. 단순한 비디오가 아닌 의미 있는 서사.',
    feature2Title: '캐릭터 일관성',
    feature2Desc: '장면 간에 일관된 캐릭터 외모를 유지합니다. 하나의 캐릭터, 여러 장면, 매번 완벽한 일관성.',
    feature3Title: '완벽한 립싱크',
    feature3Desc: '다국어 립싱크 지원. 영어, 중국어, 일본어, 한국어, 스페인어, 프랑스어, 독일어 - 모두 완벽한 입 모양 애니메이션.',
    faqTitle: '자주 묻는 질문',
    faqSubtitle: '다른 질문이 있으신가요? 문의:',
    faq1Q: 'ToonSync란 무엇이며 어떻게 작동하나요?',
    faq1A: 'ToonSync는 스토리텔링을 우선시하는 세계 최초의 AI 웹툰 비디오 메이커입니다. 고급 AI 모델을 사용하여 텍스트 설명에서 일관된 캐릭터, 일관된 스토리 아크, 완벽한 립싱크 애니메이션을 생성합니다.',
    faq2Q: 'ToonSync는 정말 무료인가요?',
    faq2A: '네, ToonSync는 신용카드 없이 짧은 웹툰 비디오를 만들 수 있는 관대한 무료 플랜을 제공합니다. 크리에이터가 장벽 없이 이야기를 할 수 있도록 힘을 실어주는 것을 믿습니다.',
    faq3Q: '캐릭터 일관성은 어떻게 유지하나요?',
    faq3A: '독자적인 "캐릭터 락" 기술을 사용합니다. 캐릭터를 정의하면, 카메라 각도나 포즈에 관계없이 시스템이 생성된 모든 장면에서 얼굴 특징, 의상, 스타일을 유지합니다.',
    faq4Q: '립싱크에서 지원하는 언어는 무엇인가요?',
    faq4A: '현재 영어, 중국어(만다린), 일본어, 한국어, 스페인어, 프랑스어, 독일어의 완벽한 립싱크를 지원하며, 더 많은 언어가 곧 출시될 예정입니다.',
    whyDifferentTitle: '우리가 다른 이유',
    otherToolsTitle: '❌ 다른 AI 비디오 도구',
    ourToolTitle: '✅ AI 웹툰 메이커',
    languageSupportTitle: '🌍 글로벌 언어 지원',
    pricingTitle: '💰 간단한 가격',
    freeTitle: '무료',
    freePrice: '$0',
    freeFeature1: '• 3개 프로젝트',
    freeFeature2: '• 5분 비디오',
    freeFeature3: '• 기본 캐릭터',
    freeFeature4: '• 영어 TTS',
    freeButton: '시작하기',
    proTitle: '프로',
    proPrice: '$29',
    proMonth: '/월',
    proFeature1: '• 무제한 프로젝트',
    proFeature2: '• 30분 비디오',
    proFeature3: '• 고급 캐릭터',
    proFeature4: '• 다국어 TTS',
    proFeature5: '• 캐릭터 일관성 AI',
    proButton: '프로 체험 시작',
    enterpriseTitle: '엔터프라이즈',
    enterprisePrice: '$99',
    enterpriseFeature1: '• 팀 협업',
    enterpriseFeature2: '• API 액세스',
    enterpriseFeature3: '• 커스텀 캐릭터 훈련',
    enterpriseFeature4: '• 우선 지원',
    enterpriseFeature5: '• 화이트라벨 옵션',
    enterpriseButton: '영업팀 문의',
    ctaTitle: '멋진 웹툰 비디오를 만들 준비가 되셨나요?',
    ctaSubtitle: '이미 AI 웹툰 메이커를 사용하고 있는 수천 명의 크리에이터와 함께하세요',
    startNow: '🚀 지금 만들기 시작',
    contactUs: '📧 문의하기',
    footerText: '❤️를 담아 글로벌 크리에이터를 위해 제작',
    support: '지원',
    privacy: '개인정보',
    terms: '이용약관',
  },
};

const languageFlags: Record<string, { flag: string; name: string }> = {
  en: { flag: '🇺🇸', name: 'EN' },
  zh: { flag: '🇨🇳', name: '中文' },
  ja: { flag: '🇯🇵', name: '日本語' },
  ko: { flag: '🇰🇷', name: '한국어' },
  es: { flag: '🇪🇸', name: 'ES' },
  fr: { flag: '🇫🇷', name: 'FR' },
  de: { flag: '🇩🇪', name: 'DE' },
};

export function LandingPage() {
  const [currentLang, setCurrentLang] = useState('en');
  const [showLangDropdown, setShowLangDropdown] = useState(false);
  const t = translations[currentLang] || translations.en;

  const handleLanguageChange = (lang: string) => {
    setCurrentLang(lang);
    setShowLangDropdown(false);
  };

  useEffect(() => {
    const handleClickOutside = () => setShowLangDropdown(false);
    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, []);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      const cursor = document.createElement('div');
      cursor.className = 'cursor-trail';
      cursor.style.left = e.clientX + 'px';
      cursor.style.top = e.clientY + 'px';
      document.body.appendChild(cursor);
      
      setTimeout(() => cursor.remove(), 500);
    };

    document.addEventListener('mousemove', handleMouseMove);
    return () => document.removeEventListener('mousemove', handleMouseMove);
  }, []);

  return (
    <div className="landing-page min-h-screen relative">
      {/* Neural Network Background */}
      <div className="neural-network">
        <div className="neural-node" style={{ top: '10%', left: '20%', animationDelay: '0s' }} />
        <div className="neural-node" style={{ top: '30%', left: '80%', animationDelay: '1s' }} />
        <div className="neural-node" style={{ top: '60%', left: '15%', animationDelay: '2s' }} />
        <div className="neural-node" style={{ top: '80%', left: '70%', animationDelay: '0.5s' }} />
        <div className="neural-node" style={{ top: '20%', left: '50%', animationDelay: '1.5s' }} />
      </div>

      {/* Main Container */}
      <div className="relative z-10">
        {/* Top Navigation */}
        <nav className="neo-glass border-b border-cyan-500/20">
          <div className="max-w-7xl mx-auto px-6">
            <div className="flex items-center justify-between h-20">
              <div className="flex items-center space-x-8">
                <Link to="/" className="group flex items-center gap-4 select-none no-underline">
                  <div className="relative flex items-center justify-center w-11 h-11">
                    <div className="absolute inset-0 bg-gradient-to-tr from-cyan-500 to-purple-600 rounded-full blur-xl opacity-20 group-hover:opacity-40 transition-all duration-500 animate-pulse" />
                    <div className="relative w-full h-full flex items-center justify-center transform group-hover:scale-105 transition-transform duration-300">
                      <svg className="w-9 h-9" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M4 12C4 7.58172 7.58172 4 12 4C14.5 4 16.5 5 17.5 6.5C16 6.5 15 7.5 15 9C15 11.5 18 12.5 20 12C20 16.4183 16.4183 20 12 20C9.5 20 7.5 19 6.5 17.5C8 17.5 9 16.5 9 15C9 12.5 6 11.5 4 12Z" fill="url(#wave-gradient)" stroke="url(#wave-stroke)" strokeWidth="0.5" />
                        <path d="M7.5 16C7.5 14 9.5 13.5 11 13.5C12.5 13.5 14.5 13 14.5 11" stroke="white" strokeOpacity="0.5" strokeWidth="1.5" strokeLinecap="round" />
                        <defs>
                          <linearGradient id="wave-gradient" x1="4" y1="20" x2="20" y2="4" gradientUnits="userSpaceOnUse">
                            <stop stopColor="#06b6d4" />
                            <stop offset="0.5" stopColor="#8b5cf6" />
                            <stop offset="1" stopColor="#ec4899" />
                          </linearGradient>
                          <linearGradient id="wave-stroke" x1="4" y1="4" x2="20" y2="20" gradientUnits="userSpaceOnUse">
                            <stop stopColor="white" stopOpacity="0.8" />
                            <stop offset="1" stopColor="white" stopOpacity="0.1" />
                          </linearGradient>
                        </defs>
                      </svg>
                    </div>
                  </div>
                  <div className="flex flex-col">
                    <div className="flex items-center gap-0.5">
                      <span className="text-2xl font-semibold tracking-tight text-white font-[Inter]">Toon</span>
                      <span className="text-2xl font-bold tracking-tight text-transparent bg-clip-text bg-gradient-to-br from-white via-cyan-200 to-cyan-400">Sync</span>
                      <div className="ml-2 w-1.5 h-1.5 rounded-full bg-gradient-to-r from-cyan-400 to-purple-500 animate-pulse" />
                    </div>
                    <span className="text-[10px] font-medium text-slate-500 tracking-[0.15em] uppercase group-hover:text-slate-400 transition-colors pl-0.5">{t.navSubtitle}</span>
                  </div>
                </Link>
              </div>

              <div className="flex items-center space-x-6">
                {/* Language Selector */}
                <div className="relative" onClick={(e) => e.stopPropagation()}>
                  <button
                    onClick={() => setShowLangDropdown(!showLangDropdown)}
                    className="flex items-center space-x-3 neo-glass px-4 py-2 rounded-full hover:bg-white/10 transition-all"
                  >
                    <svg className="w-5 h-5 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
                    </svg>
                    <span className="text-white text-sm font-medium">{languageFlags[currentLang].flag} {languageFlags[currentLang].name}</span>
                    <svg className="w-3 h-3 text-white/60" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>
                  {showLangDropdown && (
                    <div className="fixed neo-glass rounded-2xl p-2 w-48 flex flex-col gap-1 border border-white/20 shadow-2xl backdrop-blur-xl bg-black/90" style={{ zIndex: 9999, top: '80px', right: '120px' }}>
                      {Object.entries(languageFlags).map(([lang, { flag, name }]) => (
                        <button
                          key={lang}
                          onClick={() => handleLanguageChange(lang)}
                          className="w-full text-left px-3 py-2 rounded-xl hover:bg-white/10 transition-all text-white text-sm flex items-center space-x-2"
                        >
                          <span className="text-lg">{flag}</span>
                          <span>{name}</span>
                        </button>
                      ))}
                    </div>
                  )}
                </div>

                {/* Sign In Button */}
                <Link to="/login" className="px-6 py-2 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white rounded-full font-medium transition-all shadow-lg hover:shadow-cyan-500/25">
                  {t.signIn}
                </Link>
              </div>
            </div>
          </div>
        </nav>

        {/* Hero Section */}
        <div className="max-w-7xl mx-auto px-6 py-20">
          <div className="text-center space-y-8 mb-16 relative z-10">
            <div className="inline-block mb-6 px-4 py-1.5 rounded-full border border-cyan-500/30 bg-cyan-950/30 backdrop-blur-sm">
              <span className="text-cyan-400 text-sm font-semibold tracking-wide uppercase">✨ Global First AI Webtoon Maker</span>
            </div>

            <h1 className="text-5xl md:text-7xl font-bold text-white mb-6 tracking-tight leading-tight">
              Storytelling <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-purple-500">First</span>
            </h1>
            <p className="text-xl text-slate-300 mb-12 max-w-2xl mx-auto leading-relaxed">{t.heroSubtitle}</p>

            {/* Generator Input Box */}
            <div className="max-w-3xl mx-auto mb-16 relative group">
              <div className="absolute -inset-1 bg-gradient-to-r from-cyan-500 to-purple-600 rounded-2xl blur opacity-30 group-hover:opacity-50 transition duration-500" />
              <div className="relative bg-[#0f111a] border border-cyan-500/30 rounded-2xl p-2 flex flex-col md:flex-row items-center gap-2 shadow-2xl shadow-cyan-900/20">
                <div className="flex-1 w-full relative">
                  <textarea
                    placeholder=""
                    className="w-full bg-transparent text-white text-xl px-6 py-4 focus:outline-none resize-none h-[70px] md:h-[60px] leading-relaxed placeholder-slate-600 whitespace-normal overflow-hidden"
                  />
                </div>
                <div className="flex items-center gap-2 w-full md:w-auto px-2 pb-2 md:pb-0">
                  <button className="p-3 text-slate-400 hover:text-white transition-colors rounded-lg hover:bg-white/5" title="Upload Reference Image">
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                  </button>
                  <Link to="/register" className="w-full md:w-auto bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white px-8 py-3 rounded-xl font-bold text-lg transition-all shadow-lg hover:shadow-cyan-500/25 flex items-center justify-center gap-2 whitespace-nowrap">
                    <span>Generate</span>
                    <span className="text-xs bg-white/20 px-2 py-0.5 rounded uppercase tracking-wider">Free</span>
                  </Link>
                </div>
              </div>
              {/* Quick Tags */}
              <div className="flex flex-wrap justify-center gap-3 mt-4 text-sm text-slate-400">
                <span className="px-3 py-1 rounded-full border border-white/5 bg-white/5 hover:bg-white/10 cursor-pointer transition-colors">🚀 Cyberpunk</span>
                <span className="px-3 py-1 rounded-full border border-white/5 bg-white/5 hover:bg-white/10 cursor-pointer transition-colors">🌸 Anime Romance</span>
                <span className="px-3 py-1 rounded-full border border-white/5 bg-white/5 hover:bg-white/10 cursor-pointer transition-colors">🕵️ Mystery</span>
                <span className="px-3 py-1 rounded-full border border-white/5 bg-white/5 hover:bg-white/10 cursor-pointer transition-colors">🏰 Fantasy</span>
              </div>
            </div>
          </div>

          {/* Inspiration Gallery */}
          <div className="py-12">
            <div className="text-center mb-12">
              <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">Get Inspired</h2>
              <p className="text-slate-400">Discover what's possible with ToonSync</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {[
                { src: 'https://image.pollinations.ai/prompt/cyberpunk%20anime%20city%20neon%20lights%20futuristic%20girl%20high%20quality?width=720&height=1280&nologo=true', category: 'Sci-Fi', title: 'Neon Genesis', color: 'cyan', mt: '' },
                { src: 'https://image.pollinations.ai/prompt/fantasy%20anime%20world%20floating%20islands%20magic%20forest%20elf%20girl?width=720&height=1280&nologo=true', category: 'Fantasy', title: 'Ethereal Dreams', color: 'pink', mt: 'lg:mt-12' },
                { src: 'https://image.pollinations.ai/prompt/anime%20noir%20detective%20rainy%20city%20dark%20atmosphere%20mystery?width=720&height=1280&nologo=true', category: 'Noir', title: 'Shadow City', color: 'purple', mt: '' },
                { src: 'https://image.pollinations.ai/prompt/anime%20action%20battle%20scene%20dynamic%20pose%20effects%20mecha%20warrior?width=720&height=1280&nologo=true', category: 'Action', title: 'Cyber Strike', color: 'yellow', mt: 'lg:mt-12' },
              ].map((item, idx) => (
                <div key={idx} className={`group relative rounded-2xl overflow-hidden aspect-[9/16] cursor-pointer ${item.mt}`}>
                  <img src={item.src} alt={item.title} className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110" />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex flex-col justify-end p-6">
                    <span className={`text-${item.color}-400 text-xs font-bold uppercase tracking-wider mb-2`}>{item.category}</span>
                    <h3 className="text-white font-bold text-lg">{item.title}</h3>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Key Features */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
            <div className="neo-glass rounded-3xl p-8 quantum-card holographic text-center">
              <div className="text-6xl mb-4">🎭</div>
              <h3 className="text-2xl font-bold text-white mb-4">{t.feature1Title}</h3>
              <p className="text-white/70">{t.feature1Desc}</p>
            </div>

            <div className="neo-glass rounded-3xl p-8 quantum-card holographic text-center">
              <div className="text-6xl mb-4">👥</div>
              <h3 className="text-2xl font-bold text-white mb-4">{t.feature2Title}</h3>
              <p className="text-white/70">{t.feature2Desc}</p>
            </div>

            <div className="neo-glass rounded-3xl p-8 quantum-card holographic text-center">
              <div className="text-6xl mb-4">🗣️</div>
              <h3 className="text-2xl font-bold text-white mb-4">{t.feature3Title}</h3>
              <p className="text-white/70">{t.feature3Desc}</p>
            </div>
          </div>

          {/* FAQ Section */}
          <div className="py-12">
            <div className="text-center mb-12">
              <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">{t.faqTitle}</h2>
              <p className="text-slate-400">{t.faqSubtitle} <a href="mailto:support@toonsync.space" className="text-cyan-400 hover:text-cyan-300 underline">support@toonsync.space</a></p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {[
                { q: t.faq1Q, a: t.faq1A },
                { q: t.faq2Q, a: t.faq2A },
                { q: t.faq3Q, a: t.faq3A },
                { q: t.faq4Q, a: t.faq4A },
              ].map((faq, idx) => (
                <div key={idx} className="neo-glass rounded-2xl p-8 hover:bg-white/5 transition-colors border border-white/5">
                  <div className="text-xs font-bold text-cyan-500 mb-4 border border-cyan-500/30 inline-block px-2 py-1 rounded bg-cyan-950/30">0{idx + 1}</div>
                  <h3 className="text-lg font-bold text-white mb-3">{faq.q}</h3>
                  <p className="text-slate-400 leading-relaxed text-sm">{faq.a}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Comparison Section */}
          <div className="neo-glass rounded-3xl p-8 mb-16 holographic">
            <h2 className="text-4xl font-bold text-white text-center mb-8">{t.whyDifferentTitle}</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div>
                <h3 className="text-2xl font-bold text-red-400 mb-4">{t.otherToolsTitle}</h3>
                <ul className="space-y-3 text-white/70">
                  <li>• <strong>Runway</strong>: Great videos, no story coherence</li>
                  <li>• <strong>Civitai</strong>: Only static images, no video</li>
                  <li>• <strong>D-ID</strong>: Real humans only, no anime style</li>
                  <li>• <strong>HeyGen</strong>: Business focus, no creativity</li>
                  <li>• <strong>Synthesia</strong>: Templates only, no customization</li>
                </ul>
              </div>
              <div>
                <h3 className="text-2xl font-bold text-green-400 mb-4">{t.ourToolTitle}</h3>
                <ul className="space-y-3 text-white/70">
                  <li>• <strong>Story Coherence</strong>: Complete narrative arcs</li>
                  <li>• <strong>Character Consistency</strong>: Same character, every scene</li>
                  <li>• <strong>Multi-language Lip Sync</strong>: 7+ languages supported</li>
                  <li>• <strong>Creator Focused</strong>: Built for storytellers</li>
                  <li>• <strong>Anime/Manga Style</strong>: Perfect for webtoons</li>
                </ul>
              </div>
            </div>
          </div>

          {/* Language Support */}
          <div className="neo-glass rounded-3xl p-8 mb-16 holographic">
            <h2 className="text-4xl font-bold text-white text-center mb-8">{t.languageSupportTitle}</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              {[
                { flag: '🇺🇸', name: 'English', desc: 'ElevenLabs Premium' },
                { flag: '🇨🇳', name: 'Chinese', desc: 'Azure Optimized' },
                { flag: '🇯🇵', name: 'Japanese', desc: 'Anime Style' },
                { flag: '🇰🇷', name: 'Korean', desc: 'K-pop Style' },
                { flag: '🇪🇸', name: 'Spanish', desc: 'ElevenLabs' },
                { flag: '🇫🇷', name: 'French', desc: 'ElevenLabs' },
                { flag: '🇩🇪', name: 'German', desc: 'ElevenLabs' },
                { flag: '🌍', name: 'More', desc: 'Coming Soon' },
              ].map((lang, idx) => (
                <div key={idx} className="text-center">
                  <div className="text-4xl mb-2">{lang.flag}</div>
                  <h4 className="text-lg font-bold text-white">{lang.name}</h4>
                  <p className="text-cyan-400 text-sm">{lang.desc}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Pricing Section */}
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-white mb-8">{t.pricingTitle}</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {/* Free */}
              <div className="neo-glass rounded-3xl p-8 quantum-card">
                <h3 className="text-2xl font-bold text-white mb-4">{t.freeTitle}</h3>
                <div className="text-4xl font-bold text-cyan-400 mb-4">{t.freePrice}</div>
                <ul className="space-y-2 text-white/70 mb-6 text-left">
                  <li>{t.freeFeature1}</li>
                  <li>{t.freeFeature2}</li>
                  <li>{t.freeFeature3}</li>
                  <li>{t.freeFeature4}</li>
                </ul>
                <Link to="/register" className="block bg-gradient-to-r from-gray-500 to-gray-600 text-white py-3 rounded-xl font-semibold text-center">
                  {t.freeButton}
                </Link>
              </div>

              {/* Pro */}
              <div className="neo-glass rounded-3xl p-8 quantum-card border-2 border-purple-500">
                <div className="bg-gradient-to-r from-purple-500 to-pink-500 text-white px-4 py-1 rounded-full text-sm font-bold mb-4 inline-block">POPULAR</div>
                <h3 className="text-2xl font-bold text-white mb-4">{t.proTitle}</h3>
                <div className="text-4xl font-bold text-purple-400 mb-4">{t.proPrice}<span className="text-lg">{t.proMonth}</span></div>
                <ul className="space-y-2 text-white/70 mb-6 text-left">
                  <li>{t.proFeature1}</li>
                  <li>{t.proFeature2}</li>
                  <li>{t.proFeature3}</li>
                  <li>{t.proFeature4}</li>
                  <li>{t.proFeature5}</li>
                </ul>
                <Link to="/register" className="block bg-gradient-to-r from-purple-500 to-pink-500 text-white py-3 rounded-xl font-semibold text-center">
                  {t.proButton}
                </Link>
              </div>

              {/* Enterprise */}
              <div className="neo-glass rounded-3xl p-8 quantum-card">
                <h3 className="text-2xl font-bold text-white mb-4">{t.enterpriseTitle}</h3>
                <div className="text-4xl font-bold text-yellow-400 mb-4">{t.enterprisePrice}<span className="text-lg">{t.proMonth}</span></div>
                <ul className="space-y-2 text-white/70 mb-6 text-left">
                  <li>{t.enterpriseFeature1}</li>
                  <li>{t.enterpriseFeature2}</li>
                  <li>{t.enterpriseFeature3}</li>
                  <li>{t.enterpriseFeature4}</li>
                  <li>{t.enterpriseFeature5}</li>
                </ul>
                <a href="mailto:enterprise@toonsync.space" className="block bg-gradient-to-r from-yellow-500 to-orange-500 text-white py-3 rounded-xl font-semibold text-center">
                  {t.enterpriseButton}
                </a>
              </div>
            </div>
          </div>

          {/* CTA Section */}
          <div className="text-center neo-glass rounded-3xl p-12 holographic">
            <h2 className="text-5xl font-bold text-white mb-6">{t.ctaTitle}</h2>
            <p className="text-xl text-white/80 mb-8">{t.ctaSubtitle}</p>
            <div className="flex justify-center space-x-4 flex-wrap gap-4">
              <Link to="/register" className="bg-gradient-to-r from-purple-500 to-pink-500 text-white px-12 py-4 rounded-2xl font-bold text-xl hover:shadow-lg transition-all transform hover:scale-105">
                {t.startNow}
              </Link>
              <a href="mailto:hello@toonsync.space" className="neo-glass text-cyan-400 px-12 py-4 rounded-2xl font-bold text-xl hover:bg-white/10 transition-all">
                {t.contactUs}
              </a>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="neo-glass border-t border-white/20 mt-16">
        <div className="max-w-7xl mx-auto px-6 py-8">
          <div className="text-center">
            <p className="text-white/60">
              {t.footerText} |{' '}
              <a href="mailto:support@toonsync.space" className="text-cyan-400 hover:text-cyan-300">{t.support}</a> |{' '}
              <a href="#" className="text-cyan-400 hover:text-cyan-300">{t.privacy}</a> |{' '}
              <a href="#" className="text-cyan-400 hover:text-cyan-300">{t.terms}</a>
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

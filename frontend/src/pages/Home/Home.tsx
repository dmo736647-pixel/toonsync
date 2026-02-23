import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useI18n } from '../../contexts/I18nContext';

export function Home() {
  const [prompt, setPrompt] = useState('');
  const navigate = useNavigate();
  const { t } = useI18n();

  const handleStartCreate = () => {
    if (prompt.trim()) {
      navigate('/register', { state: { initialPrompt: prompt } });
    } else {
      navigate('/register');
    }
  };

  return (
    <div className="flex flex-col min-h-screen">
      {/* Hero Section */}
      <section className="relative pt-20 pb-32 overflow-hidden">
        <div className="max-w-7xl mx-auto px-6 relative z-10 text-center">
          <div className="inline-block mb-6 px-4 py-1.5 rounded-full border border-cyan-500/30 bg-cyan-950/30 backdrop-blur-sm">
            <span className="text-cyan-400 text-sm font-semibold tracking-wide uppercase">✨ Global First AI Webtoon Maker</span>
          </div>
          
          <h1 className="text-5xl md:text-7xl font-bold text-white mb-6 tracking-tight leading-tight">
            {t('heroTitle')}
          </h1>
          
          <p className="text-xl text-slate-300 mb-12 max-w-2xl mx-auto leading-relaxed">
            {t('heroSubtitle')}
            <br />
            {t('heroDescription')}
          </p>

          {/* Generator Input Box */}
          <div className="max-w-3xl mx-auto mb-16 relative group">
            <div className="absolute -inset-1 bg-gradient-to-r from-cyan-500 to-purple-600 rounded-2xl blur opacity-30 group-hover:opacity-50 transition duration-500"></div>
            <div className="relative bg-[#0f111a] border border-cyan-500/30 rounded-2xl p-2 flex flex-col md:flex-row items-center gap-2 shadow-2xl shadow-cyan-900/20">
              <div className="flex-1 w-full relative">
                <textarea 
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  placeholder=""
                  className="w-full bg-transparent text-white text-xl px-6 py-4 focus:outline-none resize-none h-[70px] md:h-[60px] leading-relaxed placeholder-slate-600 whitespace-normal overflow-hidden"
                />
              </div>
              <div className="flex items-center gap-2 w-full md:w-auto px-2 pb-2 md:pb-0">
                <button className="p-3 text-slate-400 hover:text-white transition-colors rounded-lg hover:bg-white/5" title="Upload Reference Image">
                  <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                </button>
                <button 
                  onClick={handleStartCreate}
                  className="w-full md:w-auto bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white px-8 py-3 rounded-xl font-bold text-lg transition-all shadow-lg hover:shadow-cyan-500/25 flex items-center justify-center gap-2 whitespace-nowrap"
                >
                  <span>Generate</span>
                  <span className="text-xs bg-white/20 px-2 py-0.5 rounded uppercase tracking-wider">Free</span>
                </button>
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
      </section>

      {/* Inspiration Gallery (Masonry Layout) */}
      <section className="py-24 bg-[#0a0a0f]">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">Get Inspired</h2>
            <p className="text-slate-400">Discover what's possible with ToonSync</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* Gallery Item 1 - Sci-Fi */}
            <div className="group relative rounded-2xl overflow-hidden aspect-[9/16] cursor-pointer">
              <img src="https://image.pollinations.ai/prompt/cyberpunk%20anime%20city%20neon%20lights%20futuristic%20girl%20high%20quality?width=720&height=1280&nologo=true" alt="Gallery 1" className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110" />
              <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex flex-col justify-end p-6">
                <span className="text-cyan-400 text-xs font-bold uppercase tracking-wider mb-2">Sci-Fi</span>
                <h3 className="text-white font-bold text-lg">Neon Genesis</h3>
              </div>
            </div>
            
            {/* Gallery Item 2 - Fantasy */}
            <div className="group relative rounded-2xl overflow-hidden aspect-[9/16] cursor-pointer mt-0 lg:mt-12">
              <img src="https://image.pollinations.ai/prompt/fantasy%20anime%20world%20floating%20islands%20magic%20forest%20elf%20girl?width=720&height=1280&nologo=true" alt="Gallery 2" className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110" />
              <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex flex-col justify-end p-6">
                <span className="text-pink-400 text-xs font-bold uppercase tracking-wider mb-2">Fantasy</span>
                <h3 className="text-white font-bold text-lg">Ethereal Dreams</h3>
              </div>
            </div>

            {/* Gallery Item 3 - Noir */}
            <div className="group relative rounded-2xl overflow-hidden aspect-[9/16] cursor-pointer">
              <img src="https://image.pollinations.ai/prompt/anime%20noir%20detective%20rainy%20city%20dark%20atmosphere%20mystery?width=720&height=1280&nologo=true" alt="Gallery 3" className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110" />
              <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex flex-col justify-end p-6">
                <span className="text-purple-400 text-xs font-bold uppercase tracking-wider mb-2">Noir</span>
                <h3 className="text-white font-bold text-lg">Shadow City</h3>
              </div>
            </div>

            {/* Gallery Item 4 - Action */}
            <div className="group relative rounded-2xl overflow-hidden aspect-[9/16] cursor-pointer mt-0 lg:mt-12">
              <img src="https://image.pollinations.ai/prompt/anime%20action%20battle%20scene%20dynamic%20pose%20effects%20mecha%20warrior?width=720&height=1280&nologo=true" alt="Gallery 4" className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110" />
              <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex flex-col justify-end p-6">
                <span className="text-yellow-400 text-xs font-bold uppercase tracking-wider mb-2">Action</span>
                <h3 className="text-white font-bold text-lg">Cyber Strike</h3>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Key Features */}
      <section className="py-12 max-w-7xl mx-auto px-6 w-full">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
            <div className="neo-glass rounded-3xl p-8 text-center border border-white/5 bg-white/5">
                <div className="text-6xl mb-4">🎭</div>
                <h3 className="text-2xl font-bold text-white mb-4">{t('feature1Title')}</h3>
                <p className="text-white/70">{t('feature1Desc')}</p>
            </div>
            
            <div className="neo-glass rounded-3xl p-8 text-center border border-white/5 bg-white/5">
                <div className="text-6xl mb-4">👥</div>
                <h3 className="text-2xl font-bold text-white mb-4">{t('feature2Title')}</h3>
                <p className="text-white/70">{t('feature2Desc')}</p>
            </div>
            
            <div className="neo-glass rounded-3xl p-8 text-center border border-white/5 bg-white/5">
                <div className="text-6xl mb-4">🗣️</div>
                <h3 className="text-2xl font-bold text-white mb-4">{t('feature3Title')}</h3>
                <p className="text-white/70">{t('feature3Desc')}</p>
            </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="py-24 relative overflow-hidden">
        <div className="max-w-4xl mx-auto px-6 relative z-10">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">{t('faqTitle')}</h2>
            <p className="text-slate-400">
              {t('faqSubtitle')} <a href="mailto:support@toonsync.space" className="text-cyan-400 hover:text-cyan-300 underline">support@toonsync.space</a>
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <FAQItem 
              number="01"
              question={t('faq1Q')}
              answer={t('faq1A')}
            />
            <FAQItem 
              number="02"
              question={t('faq2Q')}
              answer={t('faq2A')}
            />
            <FAQItem 
              number="03"
              question={t('faq3Q')}
              answer={t('faq3A')}
            />
            <FAQItem 
              number="04"
              question={t('faq4Q')}
              answer={t('faq4A')}
            />
          </div>
        </div>
      </section>

      {/* Comparison Section */}
      <section className="max-w-7xl mx-auto px-6 mb-24">
        <div className="neo-glass rounded-[2rem] p-12 holographic border border-white/10 bg-gradient-to-b from-slate-900/80 to-slate-900/40 backdrop-blur-xl shadow-2xl">
            <h2 className="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500 text-center mb-16 tracking-tight">
              {t('whyDifferentTitle')}
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
                <div className="bg-white/5 rounded-2xl p-8 border border-white/5 hover:bg-white/10 transition-colors">
                    <h3 className="text-3xl font-bold text-red-400 mb-8 flex items-center gap-3">
                      <span className="text-4xl">❌</span> {t('otherToolsTitle')}
                    </h3>
                    <ul className="space-y-6 text-slate-300 text-lg">
                        <li className="flex items-start gap-3"><span className="text-red-500/50 mt-1">•</span> {t('runway')}</li>
                        <li className="flex items-start gap-3"><span className="text-red-500/50 mt-1">•</span> {t('civitai')}</li>
                        <li className="flex items-start gap-3"><span className="text-red-500/50 mt-1">•</span> {t('did')}</li>
                        <li className="flex items-start gap-3"><span className="text-red-500/50 mt-1">•</span> {t('heyGen')}</li>
                        <li className="flex items-start gap-3"><span className="text-red-500/50 mt-1">•</span> {t('synthesia')}</li>
                    </ul>
                </div>
                <div className="bg-gradient-to-br from-cyan-900/30 to-blue-900/30 rounded-2xl p-8 border border-cyan-500/30 relative overflow-hidden group">
                    <div className="absolute inset-0 bg-cyan-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                    <h3 className="text-3xl font-bold text-green-400 mb-8 flex items-center gap-3 relative z-10">
                      <span className="text-4xl">✅</span> {t('ourToolTitle')}
                    </h3>
                    <ul className="space-y-6 text-white text-lg relative z-10">
                        <li className="flex items-start gap-3"><span className="text-green-400 mt-1">✓</span> {t('storyCoherence')}</li>
                        <li className="flex items-start gap-3"><span className="text-green-400 mt-1">✓</span> {t('characterConsistency')}</li>
                        <li className="flex items-start gap-3"><span className="text-green-400 mt-1">✓</span> {t('multiLangLipSync')}</li>
                        <li className="flex items-start gap-3"><span className="text-green-400 mt-1">✓</span> {t('creatorFocused')}</li>
                        <li className="flex items-start gap-3"><span className="text-green-400 mt-1">✓</span> {t('animeStyle')}</li>
                    </ul>
                </div>
            </div>
        </div>
      </section>

      {/* Language Support */}
      <section className="max-w-7xl mx-auto px-6 mb-24">
        <div className="neo-glass rounded-[2rem] p-12 holographic border border-white/10 bg-gradient-to-b from-blue-950/50 to-slate-900/50">
            <h2 className="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-cyan-400 to-green-400 text-center mb-16 flex items-center justify-center gap-4">
              <span className="text-5xl">🌍</span> {t('languageSupportTitle')}
            </h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                <div className="bg-white/5 rounded-xl p-6 hover:bg-white/10 transition-all hover:-translate-y-1 border border-white/5">
                    <div className="text-xs font-bold text-slate-500 mb-2">US</div>
                    <h4 className="text-2xl font-bold text-white mb-1">{t('englishLabel')}</h4>
                    <p className="text-cyan-400 text-xs font-medium uppercase tracking-wide">{t('englishDesc')}</p>
                </div>
                <div className="bg-white/5 rounded-xl p-6 hover:bg-white/10 transition-all hover:-translate-y-1 border border-white/5">
                    <div className="text-xs font-bold text-slate-500 mb-2">CN</div>
                    <h4 className="text-2xl font-bold text-white mb-1">{t('chineseLabel')}</h4>
                    <p className="text-cyan-400 text-xs font-medium uppercase tracking-wide">{t('chineseDesc')}</p>
                </div>
                <div className="bg-white/5 rounded-xl p-6 hover:bg-white/10 transition-all hover:-translate-y-1 border border-white/5">
                    <div className="text-xs font-bold text-slate-500 mb-2">JP</div>
                    <h4 className="text-2xl font-bold text-white mb-1">{t('japaneseLabel')}</h4>
                    <p className="text-pink-400 text-xs font-medium uppercase tracking-wide">{t('japaneseDesc')}</p>
                </div>
                <div className="bg-white/5 rounded-xl p-6 hover:bg-white/10 transition-all hover:-translate-y-1 border border-white/5">
                    <div className="text-xs font-bold text-slate-500 mb-2">KR</div>
                    <h4 className="text-2xl font-bold text-white mb-1">{t('koreanLabel')}</h4>
                    <p className="text-purple-400 text-xs font-medium uppercase tracking-wide">{t('koreanDesc')}</p>
                </div>
                <div className="bg-white/5 rounded-xl p-6 hover:bg-white/10 transition-all hover:-translate-y-1 border border-white/5">
                    <div className="text-xs font-bold text-slate-500 mb-2">ES</div>
                    <h4 className="text-2xl font-bold text-white mb-1">{t('spanishLabel')}</h4>
                    <p className="text-cyan-400 text-xs font-medium uppercase tracking-wide">{t('spanishDesc')}</p>
                </div>
                <div className="bg-white/5 rounded-xl p-6 hover:bg-white/10 transition-all hover:-translate-y-1 border border-white/5">
                    <div className="text-xs font-bold text-slate-500 mb-2">FR</div>
                    <h4 className="text-2xl font-bold text-white mb-1">{t('frenchLabel')}</h4>
                    <p className="text-cyan-400 text-xs font-medium uppercase tracking-wide">{t('frenchDesc')}</p>
                </div>
                <div className="bg-white/5 rounded-xl p-6 hover:bg-white/10 transition-all hover:-translate-y-1 border border-white/5">
                    <div className="text-xs font-bold text-slate-500 mb-2">DE</div>
                    <h4 className="text-2xl font-bold text-white mb-1">{t('germanLabel')}</h4>
                    <p className="text-cyan-400 text-xs font-medium uppercase tracking-wide">{t('germanDesc')}</p>
                </div>
                <div className="bg-white/5 rounded-xl p-6 hover:bg-white/10 transition-all hover:-translate-y-1 border border-white/5 group cursor-not-allowed">
                    <div className="text-xs font-bold text-slate-500 mb-2">MORE</div>
                    <h4 className="text-2xl font-bold text-slate-400 mb-1 group-hover:text-white transition-colors">{t('moreLabel')}</h4>
                    <p className="text-slate-500 text-xs font-medium uppercase tracking-wide">{t('moreDesc')}</p>
                </div>
            </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section className="max-w-7xl mx-auto px-6 mb-24">
        <div className="text-center mb-16">
            <h2 className="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-yellow-200 via-yellow-400 to-orange-500 mb-8 flex items-center justify-center gap-4">
              <span className="text-5xl filter drop-shadow-lg">💰</span> {t('pricingTitle')}
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 items-stretch">
                {/* Free Plan */}
                <div className="bg-[#1a1d2d] rounded-2xl p-8 border border-white/5 hover:-translate-y-2 transition-transform duration-300 shadow-xl flex flex-col">
                    <h3 className="text-2xl font-bold text-white mb-2">{t('freeTitle')}</h3>
                    <div className="text-5xl font-bold text-cyan-400 mb-8">{t('freePrice')}</div>
                    <ul className="space-y-4 text-slate-300 mb-8 flex-grow text-left">
                        <li className="flex items-center gap-2"><span className="text-cyan-500">•</span> {t('freeFeature1')}</li>
                        <li className="flex items-center gap-2"><span className="text-cyan-500">•</span> {t('freeFeature2')}</li>
                        <li className="flex items-center gap-2"><span className="text-cyan-500">•</span> {t('freeFeature3')}</li>
                        <li className="flex items-center gap-2"><span className="text-cyan-500">•</span> {t('freeFeature4')}</li>
                    </ul>
                    <Link to="/register" className="block w-full bg-slate-700 hover:bg-slate-600 text-white py-4 rounded-xl font-bold transition-colors">
                        {t('freeButton')}
                    </Link>
                </div>
                
                {/* Pro Plan */}
                <div className="bg-[#1a1d2d] rounded-2xl p-8 border-2 border-purple-500 hover:-translate-y-2 transition-transform duration-300 shadow-2xl shadow-purple-900/20 relative flex flex-col transform md:scale-105 z-10">
                    <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-gradient-to-r from-purple-500 to-pink-500 text-white px-6 py-1.5 rounded-full text-sm font-bold shadow-lg whitespace-nowrap">
                        {t('proPopular')}
                    </div>
                    <h3 className="text-2xl font-bold text-white mb-2 mt-2">{t('proTitle')}</h3>
                    <div className="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400 mb-8 flex items-baseline justify-center gap-1">
                        {t('proPrice')}<span className="text-lg text-slate-400 font-normal">{t('proMonth')}</span>
                    </div>
                    <ul className="space-y-4 text-white mb-8 flex-grow text-left">
                        <li className="flex items-center gap-2"><span className="text-purple-400">•</span> {t('proFeature1')}</li>
                        <li className="flex items-center gap-2"><span className="text-purple-400">•</span> {t('proFeature2')}</li>
                        <li className="flex items-center gap-2"><span className="text-purple-400">•</span> {t('proFeature3')}</li>
                        <li className="flex items-center gap-2"><span className="text-purple-400">•</span> {t('proFeature4')}</li>
                        <li className="flex items-center gap-2"><span className="text-purple-400">•</span> {t('proFeature5')}</li>
                    </ul>
                    <Link to="/register" className="block w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white py-4 rounded-xl font-bold transition-all shadow-lg hover:shadow-purple-500/25">
                        {t('proButton')}
                    </Link>
                </div>
                
                {/* Enterprise Plan */}
                <div className="bg-[#1a1d2d] rounded-2xl p-8 border border-white/5 hover:-translate-y-2 transition-transform duration-300 shadow-xl flex flex-col">
                    <h3 className="text-2xl font-bold text-white mb-2">{t('enterpriseTitle')}</h3>
                    <div className="text-5xl font-bold text-orange-400 mb-8 flex items-baseline justify-center gap-1">
                        {t('enterprisePrice')}<span className="text-lg text-slate-400 font-normal">{t('proMonth')}</span>
                    </div>
                    <ul className="space-y-4 text-slate-300 mb-8 flex-grow text-left">
                        <li className="flex items-center gap-2"><span className="text-orange-500">•</span> {t('enterpriseFeature1')}</li>
                        <li className="flex items-center gap-2"><span className="text-orange-500">•</span> {t('enterpriseFeature2')}</li>
                        <li className="flex items-center gap-2"><span className="text-orange-500">•</span> {t('enterpriseFeature3')}</li>
                        <li className="flex items-center gap-2"><span className="text-orange-500">•</span> {t('enterpriseFeature4')}</li>
                        <li className="flex items-center gap-2"><span className="text-orange-500">•</span> {t('enterpriseFeature5')}</li>
                    </ul>
                    <a href="mailto:enterprise@aiwebtoonmaker.com" className="block w-full bg-gradient-to-r from-orange-500 to-yellow-500 hover:from-orange-400 hover:to-yellow-400 text-white py-4 rounded-xl font-bold transition-all shadow-lg hover:shadow-orange-500/25">
                        {t('enterpriseButton')}
                    </a>
                </div>
            </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="max-w-7xl mx-auto px-6 mb-24">
        <div className="text-center neo-glass rounded-[2rem] p-16 holographic border border-white/10 bg-gradient-to-b from-indigo-900/40 to-purple-900/40 backdrop-blur-xl relative overflow-hidden">
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-cyan-500 via-purple-500 to-pink-500"></div>
            <h2 className="text-5xl md:text-6xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-200 via-purple-200 to-pink-200 mb-6 tracking-tight">
                {t('ctaTitle')}
            </h2>
            <p className="text-xl text-slate-300 mb-12 max-w-2xl mx-auto">
                {t('ctaSubtitle')}
            </p>
            <div className="flex flex-col md:flex-row justify-center items-center gap-6">
                <Link to="/register" className="w-full md:w-auto bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white px-12 py-5 rounded-xl font-bold text-xl transition-all shadow-lg hover:shadow-purple-500/30 hover:-translate-y-1">
                    {t('startNow')}
                </Link>
                <a href="mailto:hello@aiwebtoonmaker.com" className="w-full md:w-auto bg-slate-800 hover:bg-slate-700 text-cyan-400 border border-cyan-500/30 px-12 py-5 rounded-xl font-bold text-xl transition-all hover:-translate-y-1">
                    {t('contactUs')}
                </a>
            </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/10 bg-[#05050a] py-12">
        <div className="max-w-7xl mx-auto px-6 text-center text-slate-500 text-sm">
          <p>&copy; 2024 ToonSync. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}

function FAQItem({ number, question, answer }: { number: string; question: string; answer: string }) {
  return (
    <div className="neo-glass rounded-2xl p-8 hover:bg-white/5 transition-colors border border-white/5">
      <div className="text-xs font-bold text-cyan-500 mb-4 border border-cyan-500/30 inline-block px-2 py-1 rounded bg-cyan-950/30">{number}</div>
      <h3 className="text-lg font-bold text-white mb-3">{question}</h3>
      <p className="text-slate-400 leading-relaxed text-sm">{answer}</p>
    </div>
  );
}

# 🎬 ToonSync - AI Webtoon Video Maker

**Storytelling First - Character Consistency - Perfect Lip Sync**

Create amazing webtoon/manga videos with AI-powered character consistency and multi-language lip sync technology.

🌐 **Live Demo**: [toonsync.space](https://toonsync.space) | 📚 **API Docs**: [api.toonsync.space/api/docs](https://api.toonsync.space/api/docs)

## 🌟 Key Features

### 🎭 Storytelling First
- Generate complete story arcs with beginning, development, climax, and ending
- Character development and emotional progression
- Coherent narrative flow across multiple scenes

### 👥 Character Consistency
- Maintain consistent character appearance across different scenes
- Support multi-character interaction scenes
- Natural character emotions and expressions

### 🗣️ Perfect Lip Sync
- Multi-language lip sync support (English, Chinese, Japanese, Korean, Spanish, French, German)
- Natural mouth animation
- Voice emotion matching with lip movements

### 🌍 Global Language Support
- **English**: ElevenLabs TTS (Premium quality)
- **Chinese**: Azure TTS (Optimized for Chinese)
- **Japanese**: Azure TTS (Anime-style voices)
- **Korean**: Azure TTS (K-pop style voices)
- **Spanish/French/German**: ElevenLabs TTS

## 🚀 What Makes Us Different

Unlike other AI video tools that focus only on generation:

- **Runway**: Great video quality, but no story coherence or character consistency
- **Civitai**: Only static images, no video generation
- **D-ID**: Lip sync only for real humans, no anime/manga style
- **HeyGen**: Business-focused, no creative storytelling
- **Synthesia**: Template-based, no character customization

**We are the only tool that combines**: Story Coherence + Character Consistency + Multi-language Lip Sync

## 🎯 Target Users

### Primary Users
- **Independent Creators**: Webtoon/Manga enthusiasts, YouTube creators, TikTok video makers
- **Small Studios**: Animation studios, advertising agencies, educational content creators
- **Enterprise**: Brand marketing teams, training content, product demos

### Secondary Users
- **Chinese Creators**: Leveraging our Chinese lip sync expertise
- **Asian Market**: Japanese and Korean content creators

## 💰 Pricing

```
Free Tier: 
- 3 projects
- 5-minute video length
- Basic character library
- English TTS

Pro Tier ($29/month):
- Unlimited projects
- 30-minute video length
- Advanced character library
- Multi-language TTS
- Character consistency AI

Enterprise ($99/month):
- Team collaboration
- API access
- Custom character training
- Priority support
```

## 🛠️ Technology Stack

### Backend
- **FastAPI**: High-performance Python web framework
- **PostgreSQL**: Robust database with Supabase
- **Redis**: Caching and session management
- **Celery**: Asynchronous task processing

### AI/ML
- **Replicate**: AI model hosting and inference
- **Wav2Lip**: Universal lip sync technology
- **ElevenLabs**: Premium English TTS
- **Azure TTS**: Multi-language voice synthesis
- **Stable Diffusion**: Character image generation

### Frontend
- **React 18**: Modern UI framework
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first styling
- **Vite**: Fast build tool

### Deployment
- **Railway**: Backend hosting
- **Supabase**: Database and storage
- **Cloudflare Pages**: Frontend hosting
- **GitHub Actions**: CI/CD pipeline

## 🚀 Quick Start

### 🚀 快速部署上线

**5 分钟部署你的 ToonSync！**

👉 **[快速部署指南](DEPLOYMENT_QUICKSTART.md)** - 一步步教你部署上线

📖 **[详细部署文档](docs/DEPLOYMENT_GUIDE_SIMPLE.md)** - 完整的部署配置说明

### Prerequisites
- Python 3.10+
- Node.js 18+
- Git

### Local Development

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/ai-webtoon-maker.git
cd ai-webtoon-maker
```

2. **Backend Setup**
```bash
# Install Python dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# Run database migrations
alembic upgrade head

# Start the backend server
python -m uvicorn app.main:app --reload
```

3. **Frontend Setup**
```bash
cd frontend

# Install Node.js dependencies
npm install

# Set up environment variables
cp .env.development.example .env.development
# Edit .env.development with your API URL

# Start the frontend server
npm run dev
```

4. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## 🌐 Deployment

### Cloud Deployment (Recommended)

We provide a complete cloud deployment solution using:
- **GitHub**: Code repository
- **Supabase**: PostgreSQL database and file storage
- **Railway**: Backend API hosting
- **Cloudflare Pages**: Frontend hosting

**Total Cost**: Free tier available, scales with usage

See [DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) for detailed instructions.

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```bash
# Database
DATABASE_URL=postgresql://user:pass@host:port/db

# AI APIs
REPLICATE_API_TOKEN=your_replicate_token
ELEVENLABS_API_KEY=your_elevenlabs_key
OPENAI_API_KEY=your_openai_key

# Storage
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# Security
SECRET_KEY=your_secret_key
```

#### Frontend (.env.development)
```bash
VITE_API_URL=http://localhost:8000
```

## 📚 Documentation

- [API Documentation](docs/API_DOCUMENTATION.md)
- [User Manual](docs/USER_MANUAL.md)
- [Deployment Guide](docs/DEPLOYMENT_GUIDE.md)
- [Operations Manual](docs/OPERATIONS_MANUAL.md)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🌟 Roadmap

### Phase 1: Core Features (Current)
- ✅ Character consistency
- ✅ Multi-language lip sync
- ✅ Story generation
- ✅ Web interface

### Phase 2: Enhancement (Q2 2026)
- 🔄 Mobile app
- 🔄 Advanced character customization
- 🔄 Team collaboration features
- 🔄 API for developers

### Phase 3: Scale (Q3 2026)
- 🔄 Enterprise features
- 🔄 White-label solutions
- 🔄 Advanced analytics
- 🔄 Global CDN

## 📞 Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/yourusername/ai-webtoon-maker/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/ai-webtoon-maker/discussions)
- **Email**: support@aiwebtoonmaker.com

## 🏆 Why Choose AI Webtoon Video Maker?

1. **Unique Value Proposition**: Only tool combining story + character + lip sync
2. **Global Ready**: Multi-language support from day one
3. **Creator Focused**: Built for storytellers, not just video generators
4. **Scalable**: From individual creators to enterprise teams
5. **Open Source**: Transparent, customizable, community-driven

---

**Made with ❤️ for global creators**

*Transform your stories into amazing webtoon videos with AI*
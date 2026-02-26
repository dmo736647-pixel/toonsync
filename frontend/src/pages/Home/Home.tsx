import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export function Home() {
  const [prompt, setPrompt] = useState('');
  const navigate = useNavigate();

  const handleStartCreate = () => {
    if (prompt.trim()) {
      navigate('/register', { state: { initialPrompt: prompt } });
    } else {
      navigate('/register');
    }
  };

  return (
    <div className="flex flex-col min-h-screen">
      <div className="flex-1 flex flex-col items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 px-4">
        <div className="text-center max-w-3xl">
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            AI Webtoon Video Maker
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            Create amazing webtoon/manga videos with AI-powered character consistency and multi-language lip sync technology.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <input
              type="text"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Describe your story idea..."
              className="w-full sm:w-96 px-4 py-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              onClick={handleStartCreate}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
            >
              Start Creating
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

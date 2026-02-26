import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { CheckIcon, CreditCardIcon } from '@heroicons/react/24/outline';

interface PricingPlan {
  name: string;
  price: number;
  features: string[];
  recommended?: boolean;
}

const plans: PricingPlan[] = [
  {
    name: '免费版',
    price: 0,
    features: [
      '3个项目',
      '5分钟视频时长',
      '基础角色库',
      '英文TTS'
    ]
  },
  {
    name: '专业版',
    price: 29,
    features: [
      '无限项目',
      '30分钟视频时长',
      '高级角色库',
      '多语言TTS',
      '角色一致性AI'
    ],
    recommended: true
  },
  {
    name: '企业版',
    price: 99,
    features: [
      '团队协作',
      'API访问',
      '自定义角色训练',
      '优先支持'
    ]
  }
];

export const PaymentPage: React.FC = () => {
  const [selectedPlan, setSelectedPlan] = useState<string>('专业版');
  const [paymentMethod, setPaymentMethod] = useState<string>('paypal');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<boolean>(false);
  const navigate = useNavigate();

  const handlePayment = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/paypal/create-order`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          amount: plans.find(p => p.name === selectedPlan)?.price || 29,
          currency: 'USD',
          subscription_tier: selectedPlan === '专业版' ? 'professional' : 
                          selectedPlan === '企业版' ? 'enterprise' : 'free'
        })
      });

      if (!response.ok) {
        throw new Error('支付创建失败');
      }

      const data = await response.json();
      
      if (data.approval_url) {
        window.location.href = data.approval_url;
      } else {
        throw new Error('支付链接生成失败');
      }
    } catch (err) {
      setError('支付处理失败，请稍后重试');
      console.error('Payment error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleBack = () => {
    navigate('/');
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-3xl font-bold text-gray-900 sm:text-4xl">选择订阅计划</h1>
          <p className="mt-4 text-xl text-gray-500">为您的创意选择最合适的方案</p>
        </div>

        {error && (
          <div className="max-w-3xl mx-auto mb-8 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            {error}
          </div>
        )}

        {success && (
          <div className="max-w-3xl mx-auto mb-8 p-4 bg-green-50 border border-green-200 rounded-lg text-green-700">
            支付成功！正在为您激活订阅...
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {plans.map((plan) => (
            <div 
              key={plan.name}
              className={`relative bg-white rounded-lg p-6 ${plan.recommended ? 'border-2 border-blue-500 shadow-lg' : 'border border-gray-200'}`}
            >
              {plan.recommended && (
                <div className="absolute top-0 right-0 bg-blue-600 text-white text-xs font-bold py-1 px-3 rounded-bl-lg">
                  推荐
                </div>
              )}
              <h2 className="text-xl font-bold mb-2">{plan.name}</h2>
              <div className="text-3xl font-bold text-gray-900 mb-4">
                ¥{plan.price}<span className="text-sm font-normal text-gray-500">/月</span>
              </div>
              <hr className="my-4" />
              <ul className="space-y-3 mb-6">
                {plan.features.map((feature, index) => (
                  <li key={index} className="flex items-start">
                    <CheckIcon className="h-5 w-5 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                    <span className="text-gray-600">{feature}</span>
                  </li>
                ))}
              </ul>
              <button
                onClick={() => setSelectedPlan(plan.name)}
                className={`w-full py-2 px-4 rounded-lg border ${
                  selectedPlan === plan.name 
                    ? 'bg-blue-600 text-white border-blue-600' 
                    : 'bg-white text-gray-700 border-gray-300 hover:border-blue-500'
                }`}
              >
                {selectedPlan === plan.name ? '已选择' : '选择'}
              </button>
            </div>
          ))}
        </div>

        <div className="max-w-3xl mx-auto mt-12">
          <div className="bg-white rounded-lg p-6 border border-gray-200">
            <h3 className="text-lg font-semibold mb-4">支付方式</h3>
            <div className="flex gap-4 mb-6">
              <button
                onClick={() => setPaymentMethod('paypal')}
                className={`flex items-center px-4 py-2 rounded-lg border ${
                  paymentMethod === 'paypal' 
                    ? 'bg-blue-50 border-blue-500' 
                    : 'bg-white border-gray-300'
                }`}
              >
                <span className="text-blue-600 font-semibold">PayPal</span>
              </button>
              <button
                onClick={() => setPaymentMethod('credit-card')}
                className={`flex items-center px-4 py-2 rounded-lg border ${
                  paymentMethod === 'credit-card' 
                    ? 'bg-blue-50 border-blue-500' 
                    : 'bg-white border-gray-300'
                }`}
              >
                <CreditCardIcon className="h-5 w-5 text-blue-600 mr-2" />
                <span>信用卡</span>
              </button>
            </div>

            {paymentMethod === 'credit-card' && (
              <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg mb-4 text-blue-700">
                信用卡支付功能即将上线，敬请期待！
              </div>
            )}

            <div className="flex justify-between items-center mt-8">
              <button 
                onClick={handleBack}
                className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                返回
              </button>
              <button
                onClick={handlePayment}
                disabled={isLoading || paymentMethod !== 'paypal' || selectedPlan === '免费版'}
                className={`px-8 py-2 rounded-lg ${
                  isLoading || paymentMethod !== 'paypal' || selectedPlan === '免费版'
                    ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    : 'bg-blue-600 text-white hover:bg-blue-700'
                }`}
              >
                {isLoading ? '处理中...' : selectedPlan === '免费版' ? '当前方案' : '立即支付'}
              </button>
            </div>
          </div>
        </div>

        <div className="text-center mt-8 text-sm text-gray-500">
          <p>所有订阅均可随时取消。首次订阅可享受7天免费试用。</p>
        </div>
      </div>
    </div>
  );
};

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, Typography, Button, Box, Divider, Radio, RadioGroup, FormControlLabel, Alert, LoadingButton } from '@mui/material';
import { CheckCircle, CreditCard, PayPal } from '@heroicons/react/24/outline';

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
      // 调用PayPal支付API
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
        // 跳转到PayPal支付页面
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
          <Alert severity="error" className="max-w-3xl mx-auto mb-8">
            {error}
          </Alert>
        )}

        {success && (
          <Alert severity="success" className="max-w-3xl mx-auto mb-8">
            支付成功！正在为您激活订阅...
          </Alert>
        )}

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {plans.map((plan) => (
            <Card 
              key={plan.name}
              className={`relative ${plan.recommended ? 'border-2 border-blue-500 shadow-lg' : 'border border-gray-200'}`}
            >
              {plan.recommended && (
                <div className="absolute top-0 right-0 bg-blue-600 text-white text-xs font-bold py-1 px-3 rounded-bl-lg">
                  推荐
                </div>
              )}
              <CardContent className="p-6">
                <Typography variant="h5" component="h2" className="font-bold mb-2">
                  {plan.name}
                </Typography>
                <Typography variant="h3" component="div" className="font-bold text-gray-900 mb-4">
                  ¥{plan.price}<span className="text-sm font-normal text-gray-500">/月</span>
                </Typography>
                <Divider className="my-4" />
                <ul className="space-y-3 mb-6">
                  {plan.features.map((feature, index) => (
                    <li key={index} className="flex items-start">
                      <CheckCircle className="h-5 w-5 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                      <span className="text-gray-600">{feature}</span>
                    </li>
                  ))}
                </ul>
                <RadioGroup
                  row
                  value={selectedPlan === plan.name ? plan.name : ''}
                  onChange={() => setSelectedPlan(plan.name)}
                  className="mb-4"
                >
                  <FormControlLabel
                    value={plan.name}
                    control={<Radio />}
                    label="选择"
                  />
                </RadioGroup>
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="max-w-3xl mx-auto mt-12">
          <Card className="p-6">
            <CardContent>
              <Typography variant="h6" component="h3" className="mb-4">
                支付方式
              </Typography>
              <RadioGroup
                row
                value={paymentMethod}
                onChange={(e) => setPaymentMethod(e.target.value)}
                className="mb-6"
              >
                <FormControlLabel
                  value="paypal"
                  control={<Radio />}
                  label={
                    <div className="flex items-center">
                      <PayPal className="h-5 w-5 text-blue-600 mr-2" />
                      <span>PayPal</span>
                    </div>
                  }
                />
                <FormControlLabel
                  value="credit-card"
                  control={<Radio />}
                  label={
                    <div className="flex items-center">
                      <CreditCard className="h-5 w-5 text-blue-600 mr-2" />
                      <span>信用卡</span>
                    </div>
                  }
                />
              </RadioGroup>

              {paymentMethod === 'credit-card' && (
                <Alert severity="info" className="mb-4">
                  信用卡支付功能即将上线，敬请期待！
                </Alert>
              )}

              <Box className="flex justify-between items-center mt-8">
                <Button 
                  variant="outlined" 
                  onClick={handleBack}
                  className="px-6"
                >
                  返回
                </Button>
                <LoadingButton
                  variant="contained"
                  onClick={handlePayment}
                  loading={isLoading}
                  disabled={paymentMethod !== 'paypal' || selectedPlan === '免费版'}
                  className="bg-blue-600 hover:bg-blue-700 px-8"
                >
                  {selectedPlan === '免费版' ? '当前方案' : '立即支付'}
                </LoadingButton>
              </Box>
            </CardContent>
          </Card>
        </div>

        <div className="text-center mt-8 text-sm text-gray-500">
          <p>所有订阅均可随时取消。首次订阅可享受7天免费试用。</p>
        </div>
      </div>
    </div>
  );
};

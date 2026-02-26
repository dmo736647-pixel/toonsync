import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { CheckCircleIcon, XCircleIcon } from '@heroicons/react/24/outline';

export const PaymentSuccess = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [message, setMessage] = useState<string>('正在处理支付...');

  useEffect(() => {
    const processPayment = async () => {
      const orderId = searchParams.get('orderID');

      if (!orderId) {
        setStatus('error');
        setMessage('支付参数缺失');
        return;
      }

      try {
        const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/paypal/capture-order`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify({
            order_id: orderId
          })
        });

        const data = await response.json();

        if (data.success) {
          setStatus('success');
          setMessage('支付成功！您的订阅已激活');
        } else {
          setStatus('error');
          setMessage(data.message || '支付处理失败');
        }
      } catch (error) {
        setStatus('error');
        setMessage('网络错误，请稍后重试');
        console.error('Payment processing error:', error);
      }
    };

    processPayment();
  }, [searchParams]);

  const handleBackToDashboard = () => {
    navigate('/projects');
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md mx-auto">
        <div className="bg-white rounded-lg p-8 shadow-md">
          <div className="text-center">
            {status === 'loading' ? (
              <>
                <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
                <h2 className="text-xl font-semibold mb-2">处理中</h2>
                <p className="text-gray-600">{message}</p>
              </>
            ) : status === 'success' ? (
              <>
                <CheckCircleIcon className="h-16 w-16 text-green-500 mx-auto mb-4" />
                <h2 className="text-xl font-semibold mb-2 text-green-600">支付成功！</h2>
                <p className="text-gray-600 mb-6">{message}</p>
                <button
                  onClick={handleBackToDashboard}
                  className="bg-blue-600 text-white px-8 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                >
                  返回仪表盘
                </button>
              </>
            ) : (
              <>
                <XCircleIcon className="h-16 w-16 text-red-500 mx-auto mb-4" />
                <h2 className="text-xl font-semibold mb-2 text-red-600">支付失败</h2>
                <p className="text-gray-600 mb-6">{message}</p>
                <div className="flex justify-center gap-4">
                  <button
                    onClick={() => window.history.back()}
                    className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                  >
                    返回重试
                  </button>
                  <button
                    onClick={handleBackToDashboard}
                    className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
                  >
                    返回首页
                  </button>
                </div>
              </>
            )}
          </div>
        </div>

        <div className="mt-8 text-center text-sm text-gray-500">
          <p>如有问题，请联系客服：support@toonsync.space</p>
        </div>
      </div>
    </div>
  );
};

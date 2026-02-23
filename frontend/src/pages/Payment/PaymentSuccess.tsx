import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Card, CardContent, Typography, Button, Box, Alert, CircularProgress } from '@mui/material';
import { CheckCircle, Clock, XCircle } from '@heroicons/react/24/outline';

export const PaymentSuccess: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [message, setMessage] = useState<string>('正在处理支付...');

  useEffect(() => {
    const processPayment = async () => {
      const orderId = searchParams.get('orderID');
      const token = searchParams.get('token');
      const payerId = searchParams.get('PayerID');

      if (!orderId) {
        setStatus('error');
        setMessage('支付参数缺失');
        return;
      }

      try {
        // 调用后端API完成支付
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
  }, [searchParams, navigate]);

  const handleBackToDashboard = () => {
    navigate('/projects');
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md mx-auto">
        <Card className="p-8">
          <CardContent className="text-center">
            {status === 'loading' ? (
              <>
                <CircularProgress className="mx-auto mb-4" />
                <Typography variant="h5" component="h2" className="mb-2">
                  处理中
                </Typography>
                <Typography variant="body1" className="text-gray-600">
                  {message}
                </Typography>
              </>
            ) : status === 'success' ? (
              <>
                <CheckCircle className="h-16 w-16 text-green-500 mx-auto mb-4" />
                <Typography variant="h5" component="h2" className="mb-2 text-green-600 font-bold">
                  支付成功！
                </Typography>
                <Typography variant="body1" className="text-gray-600 mb-6">
                  {message}
                </Typography>
                <Button
                  variant="contained"
                  onClick={handleBackToDashboard}
                  className="bg-blue-600 hover:bg-blue-700 px-8"
                >
                  返回仪表盘
                </Button>
              </>
            ) : (
              <>
                <XCircle className="h-16 w-16 text-red-500 mx-auto mb-4" />
                <Typography variant="h5" component="h2" className="mb-2 text-red-600 font-bold">
                  支付失败
                </Typography>
                <Typography variant="body1" className="text-gray-600 mb-6">
                  {message}
                </Typography>
                <Box className="flex justify-center space-x-4">
                  <Button
                    variant="outlined"
                    onClick={() => window.history.back()}
                  >
                    返回重试
                  </Button>
                  <Button
                    variant="contained"
                    onClick={handleBackToDashboard}
                    className="bg-blue-600 hover:bg-blue-700"
                  >
                    返回首页
                  </Button>
                </Box>
              </>
            )}
          </CardContent>
        </Card>

        <div className="mt-8 text-center text-sm text-gray-500">
          <p>如有问题，请联系客服：support@toonsync.space</p>
        </div>
      </div>
    </div>
  );
};

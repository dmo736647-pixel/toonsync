import { useEffect, useRef, useState, useCallback } from 'react';
import type { WebSocketMessage } from '../types';

const WS_BASE_URL = import.meta.env.VITE_WS_BASE_URL || 'ws://localhost:8000/api/v1/ws';

export function useWebSocket(endpoint: string) {
  const ws = useRef<WebSocket | null>(null);
  const [messages, setMessages] = useState<WebSocketMessage[]>([]);
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      setError('未登录');
      return;
    }

    const wsUrl = `${WS_BASE_URL}${endpoint}?token=${token}`;
    
    try {
      ws.current = new WebSocket(wsUrl);

      ws.current.onopen = () => {
        setConnected(true);
        setError(null);
      };

      ws.current.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data) as WebSocketMessage;
          setMessages((prev) => [...prev, message]);
        } catch (err) {
          console.error('Failed to parse WebSocket message:', err);
        }
      };

      ws.current.onerror = (event) => {
        setError('WebSocket连接错误');
        console.error('WebSocket error:', event);
      };

      ws.current.onclose = () => {
        setConnected(false);
      };
    } catch (err) {
      setError('无法建立WebSocket连接');
      console.error('WebSocket connection error:', err);
    }

    return () => {
      ws.current?.close();
    };
  }, [endpoint]);

  const sendMessage = useCallback((message: any) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected');
    }
  }, []);

  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  return { messages, connected, error, sendMessage, clearMessages };
}

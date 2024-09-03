import React, { useState, useEffect, useRef } from 'react';
import '@chatscope/chat-ui-kit-styles/dist/default/styles.min.css';
import {
  MainContainer,
  ChatContainer,
  MessageList,
  Message,
  MessageInput,
  TypingIndicator
} from '@chatscope/chat-ui-kit-react';

const QaBot = () => {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([]);
  const [typing, setTyping] = useState(false);
  const ws = useRef(null);
  const ongoingStream = useRef(null); // Use useRef for ongoingStream
  const [reconnectAttempts, setReconnectAttempts] = useState(0);
  const maxReconnectAttempts = 5;

  const setupWebSocket = () => {
    if (ws.current) {
      ws.current.close();
    }

    ws.current = new WebSocket('ws://127.0.0.1:8000/ws/chat/');

    if (ws.current) {
      ws.current.onopen = () => {
        console.log('WebSocket connected!');
        setReconnectAttempts(0);
      };
    }

    ws.current.onopen = () => {
      console.log('WebSocket connected!');
      setReconnectAttempts(0);
    };

    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      let sender = data.name;

      if (data.event === 'on_parser_start') {
        ongoingStream.current = { id: data.run_id, content: '' };
        setMessages((prevMessages) => [
          ...prevMessages, 
          { message: '', sender: sender, direction: 'incoming', id: data.run_id }]);
      } else if (data.event === 'on_parser_stream' && ongoingStream.current && data.run_id === ongoingStream.current.id) {
        setMessages((prevMessages) =>
          prevMessages.map((msg) =>
            msg.id === data.run_id ? { ...msg, message: msg.message + data.data.chunk } : msg
          )
        );
      }

      setTyping(false);
    };

    ws.current.onerror = (event) => {
      console.error('WebSocket error observed:', event);
    };

    ws.current.onclose = (event) => {
      console.log(`WebSocket is closed now. Code: ${event.code}, Reason: ${event.reason}`);
      if (event.code !== 1000) {
        handleReconnect();
      }
    };
  };

  const handleReconnect = () => {
    if (reconnectAttempts < maxReconnectAttempts) {
      setReconnectAttempts((prevAttempts) => prevAttempts + 1);
      const timeout = Math.pow(2, reconnectAttempts) * 1000;
      console.log(`Attempting to reconnect in ${timeout / 1000} seconds...`);
      setTimeout(() => {
        setupWebSocket();
      }, timeout);
    } else {
      console.log('Max reconnect attempts reached, not attempting further reconnects.');
    }
  };

  useEffect(() => {
    setupWebSocket();
    return () => {
      if (ws.current && ws.current.readyState === WebSocket.OPEN) {
        ws.current.close();
      }
    };
  }, []);

  const handleSend = (message) => {
    const userMessage = { message: message, sender: 'user', direction: 'outgoing' };
    setMessages((prevMessages) => [...prevMessages, userMessage]);

    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      setTyping(true);
      ws.current.send(JSON.stringify({ message }));
    } else {
      console.error('WebSocket is not connected.');
    }
  };

  return (
    <div className="App">
      <div style={{ position: 'relative', height: '800px', width: '700px' }}>
        <MainContainer>
          <ChatContainer>
            <MessageList typingIndicator={typing ? <TypingIndicator content="ChatGPT is typing..." /> : null}>
              {messages.map((message, i) => (
                <Message key={i} model={{
                  message: message.message,
                  sentTime: "just now",
                  sender: message.sender,
                  direction: message.direction
                }} />
              ))}
            </MessageList>
            <MessageInput placeholder="Type your message here" onSend={handleSend} />
          </ChatContainer>
        </MainContainer>
      </div>
    </div>
  );
};

export default QaBot;

import React, { useEffect, useRef } from 'react';
import { Message } from '../../types/conversation';
import { MessageItem } from './MessageItem';

interface MessageListProps {
  messages: Message[];
  streamingMessage?: string;
  isStreaming?: boolean;
}

export const MessageList: React.FC<MessageListProps> = ({
  messages,
  streamingMessage,
  isStreaming,
}) => {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingMessage]);

  return (
    <div className="flex-1 overflow-y-auto space-y-4 p-4">
      {messages.map((msg) => (
        <MessageItem key={msg.id} message={msg} />
      ))}

      {isStreaming && streamingMessage && (
        <MessageItem
          message={{
            id: 'temp-streaming',
            conversation_id: 'temp',
            sender_type: 'agent',
            content: streamingMessage,
            created_at: new Date().toISOString(),
          }}
          isStreaming={true}
        />
      )}

      <div ref={bottomRef} />
    </div>
  );
};

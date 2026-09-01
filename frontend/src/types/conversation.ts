export interface Attachment {
  id: string;
  file_name: string;
  file_size: number;
  file_type: string;
  file_url: string;
}

export interface Message {
  id: string;
  conversation_id: string;
  sender_type: 'user' | 'agent' | 'system';
  content: string;
  attachments?: Attachment[];
  created_at: string;
}

export interface Conversation {
  id: string;
  title: string;
  agent_id: string;
  owner_id: string;
  visibility: 'private' | 'shared' | 'public';
  public_slug?: string;
  created_at: string;
  updated_at: string;
}

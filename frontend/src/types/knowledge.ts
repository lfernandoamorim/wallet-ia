export interface KBDocument {
  id: string;
  knowledge_base_id: string;
  file_name: string;
  file_size: number;
  file_type: string;
  chunk_count: number;
  status: 'processing' | 'indexed' | 'failed';
  error_message?: string;
  created_at: string;
}

export interface KnowledgeBase {
  id: string;
  name: string;
  description?: string;
  visibility: 'private' | 'shared' | 'public';
  public_slug?: string;
  embedding_model: string;
  document_count?: number;
  created_at: string;
}

export type Bot = {
  id: string;
  slug: string;
  name: string;
  description: string;
  reception_instructions: string;
  office_hours: string;
  location: string;
  phone: string;
  email: string;
  website: string;
};

export type FAQ = {
  id: string;
  question: string;
  answer: string;
};

export type KnowledgeDocument = {
  id: string;
  title: string;
  source_type: string;
  file_name: string;
  current_version: number;
  created_at: string;
};

export type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
  created_at: string;
};

export type ChatSession = {
  id: string;
  visitor_name: string;
  created_at: string;
  messages: ChatMessage[];
};

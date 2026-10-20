export type NoteSummary = {
  id: number;
  noteTitle: string;
  articleTitle: string;
  articleLink: string;
  tags: string[];
  contentExcerpt: string;
  updatedAt: string;
};

export type NoteRecord = NoteSummary & {
  content: string;
  createdAt: string;
};

export type NoteInput = {
  noteTitle: string;
  articleTitle: string;
  articleLink: string;
  tags: string[];
  content: string;
};

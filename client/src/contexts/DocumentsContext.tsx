import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";

export type DocumentItem = {
  id: string;
  documentType: string;
  originalFilename: string;
  mimeType: string;
  fileSize: number;
  createdAt: string;
};

type ApiDocument = {
  id: string;
  document_type: string;
  original_filename: string;
  mime_type: string;
  file_size: number;
  created_at: string;
};

function toDocumentItem(record: ApiDocument): DocumentItem {
  return {
    id: record.id,
    documentType: record.document_type,
    originalFilename: record.original_filename,
    mimeType: record.mime_type,
    fileSize: record.file_size,
    createdAt: record.created_at,
  };
}

type DocumentsContextValue = {
  documents: DocumentItem[];
  uploadDocument: (file: File) => Promise<DocumentItem>;
  deleteDocument: (id: string) => Promise<void>;
  getDownloadUrl: (id: string) => Promise<string>;
};

const DocumentsContext = createContext<DocumentsContextValue | null>(null);

export function DocumentsProvider({ children }: { children: React.ReactNode }) {
  const { status } = useAuth();
  const [documents, setDocuments] = useState<DocumentItem[]>([]);

  const load = useCallback(async () => {
    const response = await apiFetch("/api/documents");
    if (!response.ok) return;
    const data: ApiDocument[] = await response.json();
    setDocuments(data.map(toDocumentItem));
  }, []);

  useEffect(() => {
    if (status === "authenticated") {
      void load();
    } else if (status === "unauthenticated") {
      setDocuments([]);
    }
  }, [status, load]);

  const uploadDocument = useCallback(async (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    const response = await apiFetch("/api/documents", { method: "POST", body: formData });
    if (!response.ok) {
      const body = await response.json().catch(() => null);
      throw new Error(body?.detail || "Unable to upload document");
    }
    const data: ApiDocument = await response.json();
    const document = toDocumentItem(data);
    setDocuments((prev) => [document, ...prev]);
    return document;
  }, []);

  const deleteDocument = useCallback(async (id: string) => {
    const response = await apiFetch(`/api/documents/${id}`, { method: "DELETE" });
    if (!response.ok) throw new Error("Unable to delete document");
    setDocuments((prev) => prev.filter((d) => d.id !== id));
  }, []);

  const getDownloadUrl = useCallback(async (id: string) => {
    const response = await apiFetch(`/api/documents/${id}/download`);
    if (!response.ok) throw new Error("Unable to get download link");
    const data: { url: string } = await response.json();
    return data.url;
  }, []);

  return <DocumentsContext.Provider value={{ documents, uploadDocument, deleteDocument, getDownloadUrl }}>{children}</DocumentsContext.Provider>;
}

export function useDocuments() {
  const value = useContext(DocumentsContext);
  if (!value) throw new Error("useDocuments must be used inside DocumentsProvider");
  return value;
}

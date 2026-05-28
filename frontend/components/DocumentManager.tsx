"use client";

import { useState, useEffect, useRef } from "react";
import { uploadDocument, listDocuments, deleteDocument } from "@/lib/api";

interface Document {
  id: number;
  filename: string;
  file_size: number;
  status: string;
  error_message: string | null;
  created_at: string;
}

export default function DocumentManager({
  kbId,
  onUploadSuccess,
}: {
  kbId: number;
  onUploadSuccess?: () => void;
}) {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (kbId) {
      loadDocuments();
    }
  }, [kbId]);

  async function loadDocuments() {
    try {
      const docs = await listDocuments(kbId);
      setDocuments(docs);
    } catch (e) {
      console.error("Failed to load documents:", e);
    }
  }

  async function handleUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;

    setError("");
    setUploading(true);

    try {
      await uploadDocument(kbId, file);
      await loadDocuments();
      onUploadSuccess?.();
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    } catch (e: any) {
      setError("上传失败，请重试");
    } finally {
      setUploading(false);
    }
  }

  async function handleDelete(docId: number) {
    if (!confirm("确定要删除这个文档吗？")) return;

    try {
      await deleteDocument(docId);
      await loadDocuments();
    } catch (e) {
      setError("删除失败");
    }
  }

  function formatFileSize(bytes: number) {
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
    return (bytes / (1024 * 1024)).toFixed(1) + " MB";
  }

  function getStatusBadge(status: string) {
    const styles: Record<string, string> = {
      uploading: "bg-yellow-100 text-yellow-800",
      parsing: "bg-blue-100 text-blue-800",
      chunking: "bg-blue-100 text-blue-800",
      vectorizing: "bg-blue-100 text-blue-800",
      done: "bg-green-100 text-green-800",
      failed: "bg-red-100 text-red-800",
    };

    const labels: Record<string, string> = {
      uploading: "上传中",
      parsing: "解析中",
      chunking: "切片中",
      vectorizing: "向量化",
      done: "已完成",
      failed: "失败",
    };

    return (
      <span className={`px-2 py-1 rounded-full text-xs ${styles[status] || "bg-gray-100"}`}>
        {labels[status] || status}
      </span>
    );
  }

  return (
    <div className="p-4 border-t">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-medium text-gray-700">文档管理</h3>
        <label className="cursor-pointer bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700">
          {uploading ? "上传中..." : "上传文档"}
          <input
            ref={fileInputRef}
            type="file"
            className="hidden"
            accept=".pdf,.docx,.txt,.md"
            onChange={handleUpload}
            disabled={uploading}
          />
        </label>
      </div>

      {error && (
        <div className="text-red-500 text-sm mb-2">{error}</div>
      )}

      <div className="text-xs text-gray-500 mb-2">
        支持格式：PDF、DOCX、TXT、MD（最大 50MB）
      </div>

      {documents.length === 0 ? (
        <p className="text-sm text-gray-500 text-center py-4">
          暂无文档，请上传文档以使用 RAG 功能
        </p>
      ) : (
        <div className="space-y-2 max-h-60 overflow-y-auto">
          {documents.map((doc) => (
            <div
              key={doc.id}
              className="flex items-center justify-between p-2 bg-gray-50 rounded"
            >
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-800 truncate">
                  {doc.filename}
                </p>
                <p className="text-xs text-gray-500">
                  {formatFileSize(doc.file_size)}
                </p>
                {doc.error_message && (
                  <p className="text-xs text-red-500 mt-1">{doc.error_message}</p>
                )}
              </div>
              <div className="flex items-center gap-2">
                {getStatusBadge(doc.status)}
                <button
                  onClick={() => handleDelete(doc.id)}
                  className="text-red-500 hover:text-red-700 text-sm"
                >
                  删除
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

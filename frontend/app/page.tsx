"use client";

import { useState, useEffect, useRef } from "react";
import { listKnowledgeBases, sendMessage } from "@/lib/api";
import LoginForm from "@/components/LoginForm";
import ChatMessage from "@/components/ChatMessage";
import ChatInput from "@/components/ChatInput";
import KnowledgeBaseSelector from "@/components/KnowledgeBaseSelector";
import DocumentManager from "@/components/DocumentManager";

interface Source {
  filename: string;
  page: number;
  score: number;
}

interface Message {
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
}

interface KB {
  id: number;
  name: string;
  description: string;
}

export default function Home() {
  const [token, setToken] = useState<string | null>(null);
  const [knowledgeBases, setKnowledgeBases] = useState<KB[]>([]);
  const [selectedKB, setSelectedKB] = useState<number | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [chatId, setChatId] = useState<number | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const savedToken = localStorage.getItem("token");
    if (savedToken) {
      setToken(savedToken);
      loadKBs();
    }
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function loadKBs() {
    try {
      const kbs = await listKnowledgeBases();
      setKnowledgeBases(kbs);
      if (kbs.length > 0) setSelectedKB(kbs[0].id);
    } catch (e) {
      console.error("Failed to load KBs:", e);
    }
  }

  function handleLogin(newToken: string) {
    setToken(newToken);
    loadKBs();
  }

  function handleLogout() {
    localStorage.removeItem("token");
    setToken(null);
    setKnowledgeBases([]);
    setSelectedKB(null);
    setMessages([]);
    setChatId(null);
  }

  async function handleSend(message: string) {
    if (!selectedKB) return;

    setMessages((prev) => [...prev, { role: "user", content: message }]);
    setLoading(true);

    try {
      const res = await sendMessage(selectedKB, message, chatId || undefined);
      setChatId(res.chat_id);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: res.answer, sources: res.sources },
      ]);
    } catch (e) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "抱歉，处理请求时出错了。" },
      ]);
    } finally {
      setLoading(false);
    }
  }

  // 未登录显示登录页面
  if (!token) {
    return <LoginForm onLogin={handleLogin} />;
  }

  return (
    <div className="flex h-screen">
      <div className="w-80 bg-gray-50 border-r flex flex-col">
        <div className="p-4 border-b flex items-center justify-between">
          <h1 className="text-lg font-bold text-gray-800">企业知识库 RAG</h1>
          <button
            onClick={handleLogout}
            className="text-sm text-gray-500 hover:text-gray-700"
          >
            退出
          </button>
        </div>

        <KnowledgeBaseSelector
          knowledgeBases={knowledgeBases}
          selectedId={selectedKB}
          onSelect={setSelectedKB}
        />

        {selectedKB && (
          <DocumentManager
            kbId={selectedKB}
            onUploadSuccess={() => {
              // 上传成功后可以刷新某些状态
            }}
          />
        )}

        <div className="flex-1 p-4">
          <p className="text-sm text-gray-500">
            {selectedKB ? "已选择知识库" : "请先选择知识库"}
          </p>
        </div>
      </div>

      <div className="flex-1 flex flex-col">
        <div className="flex-1 overflow-y-auto p-4">
          {messages.length === 0 && (
            <div className="flex items-center justify-center h-full text-gray-400">
              选择知识库后开始提问
            </div>
          )}
          {messages.map((msg, i) => (
            <ChatMessage key={i} message={msg} />
          ))}
          {loading && (
            <div className="flex justify-start mb-4">
              <div className="bg-gray-100 rounded-lg px-4 py-3">
                <span className="animate-pulse">思考中...</span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
        <ChatInput onSend={handleSend} disabled={loading || !selectedKB} />
      </div>
    </div>
  );
}

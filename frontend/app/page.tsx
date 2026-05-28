"use client";

import { useState, useEffect, useRef } from "react";
import { listKnowledgeBases, sendMessage } from "@/lib/api";
import ChatMessage from "@/components/ChatMessage";
import ChatInput from "@/components/ChatInput";
import KnowledgeBaseSelector from "@/components/KnowledgeBaseSelector";

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
  const [knowledgeBases, setKnowledgeBases] = useState<KB[]>([]);
  const [selectedKB, setSelectedKB] = useState<number | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [chatId, setChatId] = useState<number | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      fetch("http://localhost:8000/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: "test@example.com", password: "test123456" }),
      })
        .then((res) => res.json())
        .then((data) => localStorage.setItem("token", data.access_token))
        .then(() => loadKBs());
    } else {
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

  return (
    <div className="flex h-screen">
      <div className="w-64 bg-gray-50 border-r flex flex-col">
        <div className="p-4 border-b">
          <h1 className="text-lg font-bold text-gray-800">企业知识库 RAG</h1>
        </div>
        <KnowledgeBaseSelector
          knowledgeBases={knowledgeBases}
          selectedId={selectedKB}
          onSelect={setSelectedKB}
        />
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

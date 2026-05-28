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

export default function ChatMessage({ message }: { message: Message }) {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`}>
      <div
        className={`max-w-[70%] rounded-lg px-4 py-3 ${
          isUser
            ? "bg-blue-600 text-white"
            : "bg-gray-100 text-gray-900"
        }`}
      >
        <p className="whitespace-pre-wrap">{message.content}</p>
        {message.sources && message.sources.length > 0 && (
          <div className="mt-3 pt-3 border-t border-gray-200">
            <p className="text-xs font-semibold text-gray-500 mb-1">引用来源：</p>
            {message.sources.map((s, i) => (
              <p key={i} className="text-xs text-gray-500">
                {s.filename} (第{s.page}页) - 相关度: {(s.score * 100).toFixed(1)}%
              </p>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

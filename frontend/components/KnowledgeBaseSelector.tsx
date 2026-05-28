"use client";

interface KB {
  id: number;
  name: string;
  description: string;
}

export default function KnowledgeBaseSelector({
  knowledgeBases,
  selectedId,
  onSelect,
}: {
  knowledgeBases: KB[];
  selectedId: number | null;
  onSelect: (id: number) => void;
}) {
  return (
    <div className="p-4 border-b">
      <label className="block text-sm font-medium text-gray-700 mb-2">
        选择知识库
      </label>
      <select
        value={selectedId || ""}
        onChange={(e) => onSelect(Number(e.target.value))}
        className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        <option value="" disabled>
          请选择...
        </option>
        {knowledgeBases.map((kb) => (
          <option key={kb.id} value={kb.id}>
            {kb.name}
          </option>
        ))}
      </select>
    </div>
  );
}

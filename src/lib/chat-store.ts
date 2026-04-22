import { create } from "zustand";

export interface Message {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  agent?: string;
  timestamp: Date;
}

interface ChatStore {
  messages: Message[];
  selectedAgent: string;
  isTyping: boolean;
  addMessage: (message: Message) => void;
  setSelectedAgent: (agent: string) => void;
  setIsTyping: (typing: boolean) => void;
  clearMessages: () => void;
}

export const useChatStore = create<ChatStore>((set) => ({
  messages: [
    {
      id: "welcome",
      role: "system",
      content:
        "Bienvenue dans Luymas AI ! 🚀 Je suis votre orchestrateur multi-agents. Posez-moi une question et je routerai automatiquement vers l'agent le plus qualifié, ou sélectionnez un agent spécifique pour discuter directement.",
      agent: "Luymas",
      timestamp: new Date(),
    },
  ],
  selectedAgent: "auto",
  isTyping: false,
  addMessage: (message) =>
    set((state) => ({ messages: [...state.messages, message] })),
  setSelectedAgent: (agent) => set({ selectedAgent: agent }),
  setIsTyping: (typing) => set({ isTyping: typing }),
  clearMessages: () =>
    set({
      messages: [
        {
          id: "welcome",
          role: "system",
          content:
            "Bienvenue dans Luymas AI ! 🚀 Je suis votre orchestrateur multi-agents. Posez-moi une question et je routerai automatiquement vers l'agent le plus qualifié, ou sélectionnez un agent spécifique pour discuter directement.",
          agent: "Luymas",
          timestamp: new Date(),
        },
      ],
    }),
}));

'use client';

import { useState, useRef, useEffect } from 'react';
import { useChatStore, type Message } from '@/lib/chat-store';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Send, RotateCcw, Bot, User, Sparkles } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const agentConfig: Record<string, { color: string; bg: string; initial: string }> = {
  Victor: { color: 'text-purple-400', bg: 'bg-purple-500', initial: 'V' },
  Aria: { color: 'text-pink-400', bg: 'bg-pink-500', initial: 'A' },
  Kai: { color: 'text-cyan-400', bg: 'bg-cyan-500', initial: 'K' },
  Elena: { color: 'text-emerald-400', bg: 'bg-emerald-500', initial: 'E' },
  Thomas: { color: 'text-amber-400', bg: 'bg-amber-500', initial: 'T' },
  Luymas: { color: 'text-purple-300', bg: 'bg-gradient-to-br from-purple-500 to-pink-500', initial: 'L' },
  system: { color: 'text-purple-300', bg: 'bg-gradient-to-br from-purple-500 to-pink-500', initial: 'L' },
};

function AgentAvatar({ agent }: { agent?: string }) {
  const config = agentConfig[agent || 'system'] || agentConfig.system;
  return (
    <div
      className={`w-8 h-8 rounded-full ${config.bg} flex items-center justify-center text-white font-bold text-xs shrink-0 shadow-lg`}
    >
      {config.initial}
    </div>
  );
}

function TypingIndicator() {
  return (
    <div className="flex items-center gap-2 px-4 py-3">
      <AgentAvatar agent="Luymas" />
      <div className="flex items-center gap-1 rounded-2xl bg-[#1a1a2e] px-4 py-3">
        <div className="typing-dot w-2 h-2 rounded-full bg-purple-400" />
        <div className="typing-dot w-2 h-2 rounded-full bg-pink-400" />
        <div className="typing-dot w-2 h-2 rounded-full bg-purple-400" />
      </div>
    </div>
  );
}

function MessageBubble({ message }: { message: Message }) {
  const isUser = message.role === 'user';
  const isSystem = message.role === 'system';
  const agent = message.agent || 'system';

  if (isUser) {
    return (
      <motion.div
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.3 }}
        className="flex items-start gap-2 justify-end px-4 py-2"
      >
        <div className="max-w-[80%] rounded-2xl rounded-tr-sm bg-gradient-to-r from-purple-500 to-pink-500 px-4 py-3 text-white text-sm shadow-lg shadow-purple-500/20">
          {message.content}
        </div>
        <div className="w-8 h-8 rounded-full bg-[#1a1a2e] border border-purple-500/30 flex items-center justify-center shrink-0">
          <User className="w-4 h-4 text-purple-400" />
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.3 }}
      className="flex items-start gap-2 px-4 py-2"
    >
      <AgentAvatar agent={agent} />
      <div className="max-w-[80%]">
        {!isSystem && (
          <span className={`text-xs font-semibold ${agentConfig[agent]?.color || 'text-purple-300'} mb-1 block`}>
            {agent}
          </span>
        )}
        <div
          className={`rounded-2xl rounded-tl-sm px-4 py-3 text-sm shadow-lg ${
            isSystem
              ? 'bg-gradient-to-r from-purple-500/10 to-pink-500/10 border border-purple-500/20 text-purple-200'
              : 'bg-[#1a1a2e] text-gray-200 border border-purple-500/10'
          }`}
        >
          {message.content}
        </div>
        <span className="text-[10px] text-muted-foreground mt-1 block">
          {new Date(message.timestamp).toLocaleTimeString('fr-FR', {
            hour: '2-digit',
            minute: '2-digit',
          })}
        </span>
      </div>
    </motion.div>
  );
}

export function ChatPanel() {
  const { messages, selectedAgent, isTyping, addMessage, setSelectedAgent, setIsTyping, clearMessages } =
    useChatStore();
  const [input, setInput] = useState('');
  const scrollRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isTyping]);

  const handleSend = async () => {
    if (!input.trim() || isTyping) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date(),
    };

    addMessage(userMessage);
    setInput('');
    setIsTyping(true);

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userMessage.content,
          agent: selectedAgent,
          history: messages.filter((m) => m.role !== 'system'),
        }),
      });

      if (!res.ok) throw new Error('API error');

      const data = await res.json();
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.response || 'Désolé, je n\'ai pas pu traiter votre demande.',
        agent: data.agent || (selectedAgent === 'auto' ? 'Victor' : selectedAgent),
        timestamp: new Date(),
      };
      addMessage(assistantMessage);
    } catch {
      // Fallback: generate a mock response
      const agent = selectedAgent === 'auto' ? 'Victor' : selectedAgent;
      const fallbackResponses: Record<string, string> = {
        Victor: "En tant qu'architecte, je vais structurer une solution robuste pour votre demande. Laissez-moi analyser les exigences et proposer un plan d'architecture adapté. 🏗️",
        Aria: "Je vois le potentiel d'une belle interface utilisateur ici ! Laissez-moi imaginer un design intuitif et élégant qui enchantéra vos utilisateurs. 🎨",
        Kai: "Code time ! 🧑‍💻 Je vais implémenter cette fonctionnalité avec les meilleures pratiques. Clean code, tests, et documentation inclus.",
        Elena: "Qualité avant tout ! 🔍 Je vais mettre en place des tests rigoureux pour garantir la fiabilité de cette fonctionnalité.",
        Thomas: "Côté infrastructure, je prépare le déploiement avec CI/CD, monitoring et scaling automatique. 🚀",
      };
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: fallbackResponses[agent] || "Je traite votre demande... L'orchestrateur va router vers le meilleur agent disponible. ⚡",
        agent,
        timestamp: new Date(),
      };
      addMessage(assistantMessage);
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Chat messages */}
      <ScrollArea className="flex-1 px-2 py-4" ref={scrollRef}>
        <div className="max-w-3xl mx-auto space-y-2">
          <AnimatePresence>
            {messages.map((msg) => (
              <MessageBubble key={msg.id} message={msg} />
            ))}
          </AnimatePresence>
          {isTyping && <TypingIndicator />}
        </div>
      </ScrollArea>

      {/* Input area */}
      <div className="border-t border-purple-500/20 bg-[#0f0f1a]/90 backdrop-blur-xl p-4">
        <div className="max-w-3xl mx-auto space-y-3">
          {/* Agent selector row */}
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <Bot className="w-3.5 h-3.5" />
              <span>Agent:</span>
            </div>
            <Select value={selectedAgent} onValueChange={setSelectedAgent}>
              <SelectTrigger className="w-[140px] h-8 text-xs bg-[#1a1a2e] border-purple-500/20">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="bg-[#1e1e30] border-purple-500/20">
                <SelectItem value="auto" className="text-xs">
                  <span className="flex items-center gap-2">
                    <Sparkles className="w-3 h-3 text-purple-400" />
                    Auto (Orchestrateur)
                  </span>
                </SelectItem>
                <SelectItem value="Victor" className="text-xs">
                  <span className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-purple-500" />
                    Victor (Architecte)
                  </span>
                </SelectItem>
                <SelectItem value="Aria" className="text-xs">
                  <span className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-pink-500" />
                    Aria (Designer)
                  </span>
                </SelectItem>
                <SelectItem value="Kai" className="text-xs">
                  <span className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-cyan-500" />
                    Kai (Développeur)
                  </span>
                </SelectItem>
                <SelectItem value="Elena" className="text-xs">
                  <span className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-emerald-500" />
                    Elena (QA)
                  </span>
                </SelectItem>
                <SelectItem value="Thomas" className="text-xs">
                  <span className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-amber-500" />
                    Thomas (DevOps)
                  </span>
                </SelectItem>
              </SelectContent>
            </Select>
            <Button
              variant="ghost"
              size="sm"
              onClick={clearMessages}
              className="text-xs text-muted-foreground hover:text-pink-400 hover:bg-pink-500/10 ml-auto"
            >
              <RotateCcw className="w-3.5 h-3.5 mr-1" />
              Reset
            </Button>
          </div>

          {/* Input row */}
          <div className="flex items-end gap-2">
            <Textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Écrivez votre message..."
              className="min-h-[44px] max-h-[120px] resize-none bg-[#1a1a2e] border-purple-500/20 focus:border-purple-500/40 focus:ring-purple-500/20 text-sm"
              rows={1}
            />
            <Button
              onClick={handleSend}
              disabled={!input.trim() || isTyping}
              className="h-11 w-11 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white shadow-lg shadow-purple-500/25 shrink-0"
              size="icon"
            >
              <Send className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}

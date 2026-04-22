'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  FolderOpen,
  Folder,
  FileText,
  FileCode2,
  FileJson,
  ChevronRight,
  ChevronDown,
  Rocket,
  Circle,
  Terminal as TerminalIcon,
} from 'lucide-react';
import { motion } from 'framer-motion';

interface FileItem {
  name: string;
  type: 'file' | 'folder';
  icon: typeof FileText;
  color?: string;
  children?: FileItem[];
}

const fileTree: FileItem[] = [
  {
    name: 'src',
    type: 'folder',
    icon: Folder,
    children: [
      {
        name: 'components',
        type: 'folder',
        icon: Folder,
        children: [
          { name: 'Home.tsx', type: 'file', icon: FileCode2, color: '#06b6d4' },
          { name: 'Header.tsx', type: 'file', icon: FileCode2, color: '#06b6d4' },
          { name: 'Footer.tsx', type: 'file', icon: FileCode2, color: '#06b6d4' },
        ],
      },
      {
        name: 'app',
        type: 'folder',
        icon: Folder,
        children: [
          { name: 'layout.tsx', type: 'file', icon: FileCode2, color: '#06b6d4' },
          { name: 'page.tsx', type: 'file', icon: FileCode2, color: '#06b6d4' },
        ],
      },
      { name: 'index.ts', type: 'file', icon: FileCode2, color: '#06b6d4' },
    ],
  },
  { name: 'package.json', type: 'file', icon: FileJson, color: '#f59e0b' },
  { name: 'tsconfig.json', type: 'file', icon: FileJson, color: '#f59e0b' },
  { name: 'README.md', type: 'file', icon: FileText, color: '#64748b' },
];

const agents = [
  { name: 'Kai', role: 'Developer', status: 'online' as const, color: '#06b6d4' },
  { name: 'Anya', role: 'Designer', status: 'online' as const, color: '#ec4899' },
  { name: 'Leo', role: 'Architect', status: 'busy' as const, color: '#f59e0b' },
  { name: 'Mira', role: 'Tester', status: 'offline' as const, color: '#64748b' },
];

const codeLines = [
  { num: 1, content: '<span style="color:#c678dd">import</span> <span style="color:#e5c07b">React</span> <span style="color:#c678dd">from</span> <span style="color:#98c379">\'react\'</span>;' },
  { num: 2, content: '<span style="color:#c678dd">import</span> { <span style="color:#e5c07b">Button</span> } <span style="color:#c678dd">from</span> <span style="color:#98c379">\'@/components/ui/button\'</span>;' },
  { num: 3, content: '' },
  { num: 4, content: '<span style="color:#c678dd">interface</span> <span style="color:#e5c07b">HomeProps</span> {' },
  { num: 5, content: '  <span style="color:#e06c75">title</span>: <span style="color:#e5c07b">string</span>;' },
  { num: 6, content: '  <span style="color:#e06c75">description</span>?: <span style="color:#e5c07b">string</span>;' },
  { num: 7, content: '}' },
  { num: 8, content: '' },
  { num: 9, content: '<span style="color:#c678dd">export default function</span> <span style="color:#61afef">Home</span>({ <span style="color:#e06c75">title</span>, <span style="color:#e06c75">description</span> }: <span style="color:#e5c07b">HomeProps</span>) {' },
  { num: 10, content: '  <span style="color:#c678dd">return</span> (' },
  { num: 11, content: '    &lt;<span style="color:#e06c75">div</span> <span style="color:#d19a66">className</span>=<span style="color:#98c379">"flex flex-col min-h-screen"</span>&gt;' },
  { num: 12, content: '      &lt;<span style="color:#e5c07b">Header</span> /&gt;' },
  { num: 13, content: '      &lt;<span style="color:#e06c75">main</span> <span style="color:#d19a66">className</span>=<span style="color:#98c379">"flex-1"</span>&gt;' },
  { num: 14, content: '        &lt;<span style="color:#e06c75">h1</span>&gt;{<span style="color:#e06c75">title</span>}&lt;/<span style="color:#e06c75">h1</span>&gt;' },
  { num: 15, content: '        {<span style="color:#e06c75">description</span> &amp;&amp; &lt;<span style="color:#e06c75">p</span>&gt;{<span style="color:#e06c75">description</span>}&lt;/<span style="color:#e06c75">p</span>&gt;}' },
  { num: 16, content: '      &lt;/<span style="color:#e06c75">main</span>&gt;' },
  { num: 17, content: '    &lt;/<span style="color:#e06c75">div</span>&gt;' },
  { num: 18, content: '  );' },
  { num: 19, content: '}' },
];

function FileTreeNode({ item, depth = 0 }: { item: FileItem; depth?: number }) {
  const [expanded, setExpanded] = useState(depth < 2);
  const Icon = item.icon;

  if (item.type === 'folder') {
    return (
      <div>
        <button
          onClick={() => setExpanded(!expanded)}
          className="w-full flex items-center gap-1.5 px-2 py-1 text-sm hover:bg-white/5 rounded transition-colors"
          style={{ paddingLeft: `${depth * 12 + 8}px` }}
        >
          {expanded ? (
            <ChevronDown className="w-3 h-3 text-slate-500 shrink-0" />
          ) : (
            <ChevronRight className="w-3 h-3 text-slate-500 shrink-0" />
          )}
          <Icon className={`w-3.5 h-3.5 shrink-0 ${expanded ? 'text-blue-400' : 'text-slate-500'}`} />
          <span className={`${expanded ? 'text-slate-300' : 'text-slate-500'}`}>{item.name}</span>
        </button>
        {expanded && item.children && (
          <div>
            {item.children.map((child) => (
              <FileTreeNode key={child.name} item={child} depth={depth + 1} />
            ))}
          </div>
        )}
      </div>
    );
  }

  return (
    <div
      className="flex items-center gap-1.5 px-2 py-1 text-sm hover:bg-white/5 rounded transition-colors cursor-pointer"
      style={{ paddingLeft: `${depth * 12 + 20}px` }}
    >
      <Icon className="w-3.5 h-3.5 shrink-0" style={{ color: item.color || '#64748b' }} />
      <span className="text-slate-400">{item.name}</span>
    </div>
  );
}

export function DevEnvironment() {
  return (
    <div className="flex flex-1 overflow-hidden">
      {/* Left panel - File Explorer */}
      <aside className="hidden lg:flex flex-col w-[200px] bg-[#060e1f] border-r border-blue-500/10 shrink-0">
        <div className="px-3 py-3 border-b border-blue-500/10">
          <div className="flex items-center gap-2">
            <FolderOpen className="w-3.5 h-3.5 text-blue-400" />
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Explorer</span>
          </div>
        </div>
        <div className="flex-1 overflow-y-auto py-2">
          {fileTree.map((item) => (
            <FileTreeNode key={item.name} item={item} />
          ))}
        </div>
      </aside>

      {/* Center panel - Code Editor */}
      <main className="flex-1 flex flex-col min-w-0 bg-[#050a18]">
        {/* Tab bar */}
        <div className="flex items-center border-b border-blue-500/10 bg-[#060e1f]">
          <div className="flex items-center gap-0">
            <div className="flex items-center gap-2 px-4 py-2 bg-[#050a18] border-r border-blue-500/10">
              <FileCode2 className="w-3.5 h-3.5 text-cyan-400" />
              <span className="text-xs text-white font-medium">Home.tsx</span>
              <button className="ml-2 text-slate-600 hover:text-slate-400 text-xs">×</button>
            </div>
            <div className="flex items-center gap-2 px-4 py-2 border-r border-blue-500/10 opacity-60">
              <FileCode2 className="w-3.5 h-3.5 text-cyan-400" />
              <span className="text-xs text-slate-400">Header.tsx</span>
              <button className="ml-2 text-slate-600 hover:text-slate-400 text-xs">×</button>
            </div>
          </div>
        </div>

        {/* Code content */}
        <div className="flex-1 overflow-auto p-4 font-mono text-sm">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.3 }}
          >
            {codeLines.map((line) => (
              <div key={line.num} className="flex hover:bg-white/[0.02]">
                <span className="w-10 text-right pr-4 text-slate-600 select-none shrink-0 text-xs leading-6">
                  {line.num}
                </span>
                <span
                  className="text-xs leading-6"
                  dangerouslySetInnerHTML={{ __html: line.content || '&nbsp;' }}
                />
              </div>
            ))}
            <div className="flex">
              <span className="w-10 text-right pr-4 text-slate-600 select-none shrink-0 text-xs leading-6">20</span>
              <span className="cursor-blink text-blue-400 text-xs leading-6">▊</span>
            </div>
          </motion.div>
        </div>
      </main>

      {/* Right panel - Agent Orchestrator + Terminal */}
      <aside className="hidden md:flex flex-col w-[350px] bg-[#060e1f] border-l border-blue-500/10 shrink-0">
        {/* Agent Orchestrator */}
        <div className="flex-1 flex flex-col overflow-hidden">
          <div className="px-4 py-3 border-b border-blue-500/10 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Rocket className="w-3.5 h-3.5 text-blue-400" />
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Agent Orchestrator</span>
            </div>
            <Button
              size="sm"
              className="h-7 text-xs bg-blue-500 hover:bg-blue-600 text-white gap-1 px-3"
            >
              <Rocket className="w-3 h-3" />
              Deploy
            </Button>
          </div>

          {/* Agent list */}
          <div className="flex-1 overflow-y-auto p-3 space-y-2">
            {agents.map((agent, i) => (
              <motion.div
                key={agent.name}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.1 }}
                className="flex items-center gap-3 p-3 bg-[#0a1628] rounded-lg border border-blue-500/10 hover:border-blue-500/20 transition-colors"
              >
                <div
                  className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold text-white shrink-0"
                  style={{ backgroundColor: agent.color + '30' }}
                >
                  <span style={{ color: agent.color }}>{agent.name[0]}</span>
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium text-white">{agent.name}</div>
                  <div className="text-xs text-slate-500">{agent.role}</div>
                </div>
                <div className="flex items-center gap-1.5">
                  <Circle
                    className={`w-2 h-2 fill-current ${
                      agent.status === 'online'
                        ? 'text-emerald-400'
                        : agent.status === 'busy'
                        ? 'text-yellow-400'
                        : 'text-slate-600'
                    }`}
                  />
                  <span
                    className={`text-xs ${
                      agent.status === 'online'
                        ? 'text-emerald-400'
                        : agent.status === 'busy'
                        ? 'text-yellow-400'
                        : 'text-slate-600'
                    }`}
                  >
                    {agent.status === 'online' ? 'Online' : agent.status === 'busy' ? 'Busy' : 'Offline'}
                  </span>
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Terminal */}
        <div className="h-[200px] border-t border-blue-500/10 flex flex-col">
          <div className="px-4 py-2 border-b border-blue-500/10 flex items-center gap-2">
            <TerminalIcon className="w-3.5 h-3.5 text-emerald-400" />
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Terminal</span>
          </div>
          <div className="flex-1 overflow-auto p-3 font-mono text-xs leading-5 bg-[#030712]">
            <div className="text-emerald-400">$ npm run build</div>
            <div className="text-slate-400">Compiling...</div>
            <div className="text-emerald-400">✓ Build successful!</div>
            <div className="text-slate-500">  42 modules transformed</div>
            <div className="text-slate-500">  output: dist/index.js (12.4kb)</div>
            <div className="text-emerald-400">$ <span className="cursor-blink">▊</span></div>
          </div>
        </div>
      </aside>
    </div>
  );
}

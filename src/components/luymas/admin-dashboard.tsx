'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  LayoutDashboard,
  Search,
  Monitor,
  Mail,
  Settings,
  ExternalLink,
  Play,
  Send,
} from 'lucide-react';
import { motion } from 'framer-motion';

const sidebarNav = [
  { icon: LayoutDashboard, label: 'Dashboard', active: true },
  { icon: Search, label: 'Scans' },
  { icon: Monitor, label: 'Demos' },
  { icon: Mail, label: 'Emails' },
  { icon: Settings, label: 'Settings' },
];

const metrics = [
  { label: 'Total Scanned', value: '12,450', change: '+12%', color: '#3b82f6' },
  { label: 'Demos Generated', value: '875', change: '+8%', color: '#8b5cf6' },
  { label: 'Emails Sent', value: '3,200', change: '+15%', color: '#06b6d4' },
  { label: 'Conversion Rate', value: '7.0%', change: '+2.3%', color: '#10b981' },
];

const prospects = [
  { name: 'Boulangerie Dubois', sector: 'Boulangerie', location: 'Lyon', status: 'Active' },
  { name: 'TechSolutions', sector: 'IT', location: 'Paris', status: 'Active' },
  { name: 'Café du Commerce', sector: 'Restaurant', location: 'Marseille', status: 'Pending' },
  { name: 'AutoExpress', sector: 'Automobile', location: 'Toulouse', status: 'Active' },
  { name: 'StyleChic', sector: 'Mode', location: 'Bordeaux', status: 'Inactive' },
  { name: 'GreenGarden', sector: 'Paysagisme', location: 'Nantes', status: 'Active' },
];

export function AdminDashboard() {
  const [activeNav, setActiveNav] = useState('Dashboard');
  const [command, setCommand] = useState('');

  return (
    <div className="flex flex-1 overflow-hidden">
      {/* Sidebar */}
      <aside className="hidden md:flex flex-col w-[200px] bg-[#060e1f] border-r border-blue-500/10 shrink-0">
        {/* Mini logo */}
        <div className="flex items-center gap-2 px-4 h-16 border-b border-blue-500/10">
          <div className="w-7 h-7 rounded-md bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center">
            <span className="text-white font-bold text-xs">L</span>
          </div>
          <span className="text-sm font-semibold text-white">Luymas AI</span>
        </div>

        {/* Nav items */}
        <nav className="flex-1 py-4 px-2 space-y-1">
          {sidebarNav.map((item) => {
            const Icon = item.icon;
            const isActive = activeNav === item.label;
            return (
              <button
                key={item.label}
                onClick={() => setActiveNav(item.label)}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all duration-200 ${
                  isActive
                    ? 'bg-blue-500/15 text-blue-400 shadow-sm shadow-blue-500/10'
                    : 'text-slate-500 hover:text-slate-300 hover:bg-white/5'
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-blue-400' : ''}`} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Sidebar footer */}
        <div className="px-4 py-3 border-t border-blue-500/10">
          <p className="text-[10px] text-slate-600">v2.0.0 - 2026</p>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-y-auto bg-[#050a18]">
        <div className="p-4 sm:p-6 space-y-6">
          {/* Page title */}
          <div>
            <h2 className="text-xl font-bold text-white">Dashboard</h2>
            <p className="text-sm text-slate-500 mt-1">Vue d&apos;ensemble de vos opérations</p>
          </div>

          {/* Metric cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {metrics.map((metric, i) => (
              <motion.div
                key={metric.label}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.1 }}
                className="bg-[#0a1628] rounded-lg border-t-2 p-4 glow-border"
                style={{ borderTopColor: metric.color }}
              >
                <p className="text-xs text-slate-500 uppercase tracking-wider">{metric.label}</p>
                <div className="flex items-baseline gap-2 mt-2">
                  <span className="text-2xl font-bold text-white">{metric.value}</span>
                  <span className="text-xs font-medium text-emerald-400">{metric.change}</span>
                </div>
              </motion.div>
            ))}
          </div>

          {/* Prospects table */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="bg-[#0a1628] rounded-lg glow-border overflow-hidden"
          >
            <div className="px-4 py-3 border-b border-blue-500/10 flex items-center justify-between">
              <h3 className="text-sm font-semibold text-white">Local Prospects</h3>
              <Badge variant="outline" className="border-blue-500/20 text-slate-400 text-xs">
                {prospects.length} résultats
              </Badge>
            </div>

            {/* Desktop table */}
            <div className="hidden sm:block overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-blue-500/10">
                    <th className="text-left text-xs text-slate-500 font-medium px-4 py-3">Company Name</th>
                    <th className="text-left text-xs text-slate-500 font-medium px-4 py-3">Sector</th>
                    <th className="text-left text-xs text-slate-500 font-medium px-4 py-3">Location</th>
                    <th className="text-left text-xs text-slate-500 font-medium px-4 py-3">Website Status</th>
                    <th className="text-left text-xs text-slate-500 font-medium px-4 py-3">Action</th>
                  </tr>
                </thead>
                <tbody>
                  {prospects.map((p) => (
                    <tr key={p.name} className="border-b border-blue-500/5 hover:bg-white/[0.02] transition-colors">
                      <td className="px-4 py-3 text-sm text-white font-medium">{p.name}</td>
                      <td className="px-4 py-3 text-sm text-slate-400">{p.sector}</td>
                      <td className="px-4 py-3 text-sm text-slate-400">{p.location}</td>
                      <td className="px-4 py-3">
                        <Badge
                          variant="outline"
                          className={`text-xs ${
                            p.status === 'Active'
                              ? 'border-emerald-500/30 text-emerald-400 bg-emerald-500/10'
                              : p.status === 'Pending'
                              ? 'border-yellow-500/30 text-yellow-400 bg-yellow-500/10'
                              : 'border-slate-500/30 text-slate-400 bg-slate-500/10'
                          }`}
                        >
                          {p.status}
                        </Badge>
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-2">
                          <Button
                            size="sm"
                            variant="outline"
                            className="h-7 text-xs border-blue-500/20 text-blue-400 hover:bg-blue-500/10 hover:text-blue-300 bg-transparent gap-1 px-2"
                          >
                            <Play className="w-3 h-3" />
                            Demo
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            className="h-7 text-xs border-purple-500/20 text-purple-400 hover:bg-purple-500/10 hover:text-purple-300 bg-transparent gap-1 px-2"
                          >
                            <Send className="w-3 h-3" />
                            Email
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Mobile cards */}
            <div className="sm:hidden space-y-3 p-4">
              {prospects.map((p) => (
                <div key={p.name} className="bg-[#0f1d36] rounded-lg p-3 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-white">{p.name}</span>
                    <Badge
                      variant="outline"
                      className={`text-xs ${
                        p.status === 'Active'
                          ? 'border-emerald-500/30 text-emerald-400 bg-emerald-500/10'
                          : p.status === 'Pending'
                          ? 'border-yellow-500/30 text-yellow-400 bg-yellow-500/10'
                          : 'border-slate-500/30 text-slate-400 bg-slate-500/10'
                      }`}
                    >
                      {p.status}
                    </Badge>
                  </div>
                  <div className="flex items-center gap-3 text-xs text-slate-400">
                    <span>{p.sector}</span>
                    <span>•</span>
                    <span>{p.location}</span>
                  </div>
                  <div className="flex items-center gap-2 pt-1">
                    <Button
                      size="sm"
                      variant="outline"
                      className="h-7 text-xs border-blue-500/20 text-blue-400 hover:bg-blue-500/10 bg-transparent gap-1 px-2"
                    >
                      <Play className="w-3 h-3" />
                      Demo
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      className="h-7 text-xs border-purple-500/20 text-purple-400 hover:bg-purple-500/10 bg-transparent gap-1 px-2"
                    >
                      <Send className="w-3 h-3" />
                      Email
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>

          {/* Command input */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
          >
            <div className="relative">
              <Input
                value={command}
                onChange={(e) => setCommand(e.target.value)}
                placeholder="/admin scan [city] [sector]"
                className="w-full h-11 bg-[#0a1628] border-blue-500/30 text-white placeholder:text-slate-600 glow-border focus-visible:ring-blue-500/50 font-mono text-sm"
              />
              <ExternalLink className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-600" />
            </div>
          </motion.div>
        </div>
      </main>
    </div>
  );
}

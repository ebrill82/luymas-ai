'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { motion } from 'framer-motion';
import {
  Lock,
  Building2,
  Mail,
  TrendingUp,
  Search,
  Play,
  Eye,
  Send,
  Globe,
  BarChart3,
  Users,
  Target,
  Loader2,
} from 'lucide-react';

interface Company {
  nom: string;
  secteur: string;
  score: number;
  statut: 'Prospect' | 'Contacté' | 'En négociation' | 'Client';
  region: string;
}

const sampleCompanies: Company[] = [
  { nom: 'AfroTech Solutions', secteur: 'Tech', score: 92, statut: 'Client', region: 'Afrique' },
  { nom: 'Sahara Digital', secteur: 'Fintech', score: 87, statut: 'En négociation', region: 'Afrique' },
  { nom: 'Kigali Innovate', secteur: 'SaaS', score: 81, statut: 'Contacté', region: 'Afrique' },
  { nom: 'LagosPay', secteur: 'Fintech', score: 78, statut: 'Prospect', region: 'Afrique' },
  { nom: 'ParisTech AI', secteur: 'IA', score: 95, statut: 'Client', region: 'Europe' },
  { nom: 'BerlinDev GmbH', secteur: 'DevTools', score: 89, statut: 'En négociation', region: 'Europe' },
  { nom: 'NileCode', secteur: 'Tech', score: 75, statut: 'Prospect', region: 'Afrique' },
  { nom: 'CapeAI Labs', secteur: 'IA', score: 83, statut: 'Contacté', region: 'Afrique' },
];

const statutColors: Record<string, string> = {
  Prospect: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
  'Contacté': 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30',
  'En négociation': 'bg-amber-500/20 text-amber-400 border-amber-500/30',
  Client: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
};

function StatCardMini({
  title,
  value,
  icon,
  gradient,
}: {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  gradient: string;
}) {
  return (
    <Card className="bg-[#1e1e30]/80 border-0 overflow-hidden">
      <div className={`h-1 w-full bg-gradient-to-r ${gradient}`} />
      <CardContent className="p-4 flex items-center gap-3">
        <div className={`w-9 h-9 rounded-lg bg-gradient-to-br ${gradient} flex items-center justify-center text-white shadow-lg`}>
          {icon}
        </div>
        <div>
          <p className="text-lg font-bold text-white">{value}</p>
          <p className="text-[11px] text-muted-foreground">{title}</p>
        </div>
      </CardContent>
    </Card>
  );
}

export function AdminPanel() {
  const [authenticated, setAuthenticated] = useState(false);
  const [password, setPassword] = useState('');
  const [passwordError, setPasswordError] = useState('');
  const [selectedRegion, setSelectedRegion] = useState('Afrique');
  const [isScanning, setIsScanning] = useState(false);
  const [companies, setCompanies] = useState<Company[]>(sampleCompanies);

  const handleLogin = () => {
    if (password === 'luymas2024') {
      setAuthenticated(true);
      setPasswordError('');
    } else {
      setPasswordError('Mot de passe incorrect');
    }
  };

  const handleScan = () => {
    setIsScanning(true);
    setTimeout(() => {
      // Add some "new" companies based on region
      const newCompanies: Company[] = [
        ...sampleCompanies.filter((c) => c.region === selectedRegion),
        {
          nom: `NovaTech ${selectedRegion}`,
          secteur: 'Tech',
          score: Math.floor(Math.random() * 30) + 70,
          statut: 'Prospect',
          region: selectedRegion,
        },
        {
          nom: `DigitalFlow ${selectedRegion}`,
          secteur: 'SaaS',
          score: Math.floor(Math.random() * 30) + 65,
          statut: 'Prospect',
          region: selectedRegion,
        },
      ];
      setCompanies(newCompanies);
      setIsScanning(false);
    }, 2500);
  };

  // Auth gate
  if (!authenticated) {
    return (
      <div className="flex items-center justify-center min-h-[60vh] p-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.4 }}
          className="w-full max-w-sm"
        >
          <Card className="bg-[#1e1e30]/80 border-0 overflow-hidden">
            <div className="h-1 w-full bg-gradient-to-r from-purple-500 to-pink-500" />
            <CardContent className="p-6 space-y-6">
              <div className="text-center space-y-2">
                <div className="w-16 h-16 mx-auto rounded-2xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center shadow-lg shadow-purple-500/25">
                  <Lock className="w-8 h-8 text-white" />
                </div>
                <h2 className="text-lg font-bold gradient-text">Admin Dashboard</h2>
                <p className="text-xs text-muted-foreground">
                  Accès réservé aux administrateurs
                </p>
              </div>

              <div className="space-y-3">
                <Input
                  type="password"
                  placeholder="Mot de passe..."
                  value={password}
                  onChange={(e) => {
                    setPassword(e.target.value);
                    setPasswordError('');
                  }}
                  onKeyDown={(e) => e.key === 'Enter' && handleLogin()}
                  className="bg-[#1a1a2e] border-purple-500/20 focus:border-purple-500/40"
                />
                {passwordError && (
                  <p className="text-xs text-red-400">{passwordError}</p>
                )}
                <Button
                  onClick={handleLogin}
                  className="w-full bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white shadow-lg shadow-purple-500/25"
                >
                  <Lock className="w-4 h-4 mr-2" />
                  Connexion
                </Button>
                <p className="text-[10px] text-center text-muted-foreground">
                  Demo: luymas2024
                </p>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="p-4 max-w-5xl mx-auto space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
      >
        <h2 className="text-xl font-bold gradient-text">Dashboard Admin</h2>
        <p className="text-sm text-muted-foreground mt-1">
          Gestion commerciale et prospection
        </p>
      </motion.div>

      {/* Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
          <StatCardMini
            title="Scannées"
            value="1,247"
            icon={<Building2 className="w-4 h-4" />}
            gradient="from-purple-500 to-pink-500"
          />
        </motion.div>
        <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}>
          <StatCardMini
            title="Démos Générées"
            value="89"
            icon={<BarChart3 className="w-4 h-4" />}
            gradient="from-cyan-500 to-cyan-600"
          />
        </motion.div>
        <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <StatCardMini
            title="Emails Envoyés"
            value="342"
            icon={<Mail className="w-4 h-4" />}
            gradient="from-amber-500 to-amber-600"
          />
        </motion.div>
        <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }}>
          <StatCardMini
            title="Taux Conversion"
            value="24.8%"
            icon={<TrendingUp className="w-4 h-4" />}
            gradient="from-emerald-500 to-emerald-600"
          />
        </motion.div>
      </div>

      {/* Region Scanner */}
      <motion.div
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <Card className="bg-[#1e1e30]/80 border-0 overflow-hidden">
          <div className="h-1 w-full bg-gradient-to-r from-purple-500 to-pink-500" />
          <CardHeader className="pb-2 pt-4 px-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Search className="w-4 h-4 text-purple-400" />
                <CardTitle className="text-sm font-semibold text-white">
                  Scanner Régional
                </CardTitle>
              </div>
            </div>
          </CardHeader>
          <CardContent className="px-4 pb-4">
            <div className="flex items-center gap-3 flex-wrap">
              <Select value={selectedRegion} onValueChange={setSelectedRegion}>
                <SelectTrigger className="w-[160px] h-9 text-xs bg-[#1a1a2e] border-purple-500/20">
                  <Globe className="w-3.5 h-3.5 mr-1 text-muted-foreground" />
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-[#1e1e30] border-purple-500/20">
                  <SelectItem value="Afrique" className="text-xs">🌍 Afrique</SelectItem>
                  <SelectItem value="Europe" className="text-xs">🌍 Europe</SelectItem>
                  <SelectItem value="Amérique" className="text-xs">🌎 Amérique</SelectItem>
                  <SelectItem value="Asie" className="text-xs">🌏 Asie</SelectItem>
                </SelectContent>
              </Select>

              <Button
                onClick={handleScan}
                disabled={isScanning}
                className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white shadow-lg shadow-purple-500/25 h-9 text-xs"
              >
                {isScanning ? (
                  <>
                    <Loader2 className="w-3.5 h-3.5 mr-1 animate-spin" />
                    Scan en cours...
                  </>
                ) : (
                  <>
                    <Play className="w-3.5 h-3.5 mr-1" />
                    Lancer le Scan
                  </>
                )}
              </Button>

              <div className="flex items-center gap-2 ml-auto">
                <Users className="w-3.5 h-3.5 text-muted-foreground" />
                <span className="text-xs text-muted-foreground">
                  {companies.length} entreprises
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Companies table */}
      <motion.div
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
      >
        <Card className="bg-[#1e1e30]/80 border-0 overflow-hidden">
          <div className="h-1 w-full bg-gradient-to-r from-purple-500 to-pink-500" />
          <CardHeader className="pb-2 pt-4 px-4">
            <CardTitle className="text-sm font-semibold text-white flex items-center gap-2">
              <Building2 className="w-4 h-4 text-purple-400" />
              Entreprises Détectées
            </CardTitle>
          </CardHeader>
          <CardContent className="px-4 pb-4">
            {/* Desktop table */}
            <div className="hidden sm:block overflow-x-auto">
              <table className="w-full text-xs">
                <thead>
                  <tr className="border-b border-purple-500/10">
                    <th className="text-left py-2 px-3 text-muted-foreground font-medium">Nom</th>
                    <th className="text-left py-2 px-3 text-muted-foreground font-medium">Secteur</th>
                    <th className="text-left py-2 px-3 text-muted-foreground font-medium">Score</th>
                    <th className="text-left py-2 px-3 text-muted-foreground font-medium">Statut</th>
                    <th className="text-right py-2 px-3 text-muted-foreground font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {companies.map((company, i) => (
                    <motion.tr
                      key={i}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: i * 0.05 }}
                      className="border-b border-purple-500/5 hover:bg-purple-500/5 transition-colors"
                    >
                      <td className="py-2.5 px-3 font-medium text-white">{company.nom}</td>
                      <td className="py-2.5 px-3 text-gray-400">{company.secteur}</td>
                      <td className="py-2.5 px-3">
                        <div className="flex items-center gap-2">
                          <div className="w-16 h-1.5 rounded-full bg-[#1a1a2e] overflow-hidden">
                            <div
                              className={`h-full rounded-full ${
                                company.score >= 85
                                  ? 'bg-emerald-500'
                                  : company.score >= 70
                                  ? 'bg-amber-500'
                                  : 'bg-gray-500'
                              }`}
                              style={{ width: `${company.score}%` }}
                            />
                          </div>
                          <span className="text-gray-300">{company.score}</span>
                        </div>
                      </td>
                      <td className="py-2.5 px-3">
                        <Badge
                          variant="outline"
                          className={`text-[10px] ${statutColors[company.statut]}`}
                        >
                          {company.statut}
                        </Badge>
                      </td>
                      <td className="py-2.5 px-3 text-right">
                        <div className="flex items-center justify-end gap-1">
                          <Button variant="ghost" size="icon" className="h-7 w-7 text-muted-foreground hover:text-purple-400 hover:bg-purple-500/10">
                            <Eye className="w-3.5 h-3.5" />
                          </Button>
                          <Button variant="ghost" size="icon" className="h-7 w-7 text-muted-foreground hover:text-pink-400 hover:bg-pink-500/10">
                            <Send className="w-3.5 h-3.5" />
                          </Button>
                        </div>
                      </td>
                    </motion.tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Mobile cards */}
            <div className="sm:hidden space-y-2 max-h-96 overflow-y-auto">
              {companies.map((company, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.05 }}
                  className="p-3 rounded-lg bg-[#1a1a2e] border border-purple-500/10 space-y-2"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-medium text-white text-sm">{company.nom}</span>
                    <Badge
                      variant="outline"
                      className={`text-[10px] ${statutColors[company.statut]}`}
                    >
                      {company.statut}
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between text-xs text-muted-foreground">
                    <span>{company.secteur}</span>
                    <span className="flex items-center gap-1">
                      <Target className="w-3 h-3" />
                      Score: {company.score}
                    </span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Button variant="ghost" size="sm" className="h-7 text-[10px] text-muted-foreground hover:text-purple-400">
                      <Eye className="w-3 h-3 mr-1" /> Voir
                    </Button>
                    <Button variant="ghost" size="sm" className="h-7 text-[10px] text-muted-foreground hover:text-pink-400">
                      <Send className="w-3 h-3 mr-1" /> Contacter
                    </Button>
                  </div>
                </motion.div>
              ))}
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}

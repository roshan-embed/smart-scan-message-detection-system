import React, { useState, useEffect } from 'react';
import { Shield, ShieldAlert, AlertCircle, FileText, CheckCircle, Activity, Globe, MessageSquare, PlayCircle, Heart } from 'lucide-react';
import RiskGauge from './components/RiskGauge';
import HighlightedText from './components/HighlightedText';
import ThreatRadar from './components/ThreatRadar';
import { motion, AnimatePresence } from 'framer-motion';

// Base API URL
const API_BASE = '/api';

function App() {
  const [text, setText] = useState('');
  const [channel, setChannel] = useState('SMS');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState(null);
  const [scenarios, setScenarios] = useState([]);
  const [activeTab, setActiveTab] = useState('analyze'); 

  useEffect(() => {
    fetch(`${API_BASE}/scenarios`)
      .then(res => res.json())
      .then(data => setScenarios(data))
      .catch(err => console.error("Failed to load scenarios:", err));
  }, []);

  const handleAnalyze = async (e) => {
    e?.preventDefault();
    if (!text.trim()) return;

    setIsAnalyzing(true);
    try {
      const res = await fetch(`${API_BASE}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, channel })
      });
      const data = await res.json();
      setResult(data);
    } catch (err) {
      console.error(err);
      alert("Error connecting to backend API.");
    } finally {
      setIsAnalyzing(false);
    }
  };

  const loadScenario = (scenario) => {
    setText(scenario.message);
    setChannel(scenario.channel);
    setActiveTab('analyze');
    setResult(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-slate-900 dark:to-slate-950 text-gray-900 dark:text-gray-100 font-sans selection:bg-blue-500/30 flex flex-col">
      {/* Navbar - Glassmorphism */}
      <nav className="sticky top-0 z-50 backdrop-blur-xl bg-white/70 dark:bg-slate-900/70 border-b border-gray-200/50 dark:border-slate-800/50 supports-[backdrop-filter]:bg-white/60 transition-all">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-20 items-center">
            <motion.div 
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="flex items-center gap-4"
            >
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white shadow-lg shadow-blue-500/30">
                <Shield className="w-7 h-7" />
              </div>
              <div>
                <h1 className="text-2xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-indigo-600 dark:from-blue-400 dark:to-indigo-400">
                  Smart Scam Detector
                </h1>
                <p className="text-xs text-gray-500 dark:text-gray-400 font-semibold tracking-widest uppercase">AI Threat Intelligence</p>
              </div>
            </motion.div>
            <motion.div 
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="flex gap-2 p-1.5 bg-gray-100/50 dark:bg-slate-800/50 rounded-lg backdrop-blur-sm border border-gray-200/50 dark:border-slate-700/50"
            >
              <button 
                onClick={() => setActiveTab('analyze')} 
                className={`px-5 py-2.5 rounded-md text-sm font-semibold transition-all duration-300 ${activeTab === 'analyze' ? 'bg-white dark:bg-slate-700 text-blue-600 dark:text-blue-400 shadow-sm' : 'text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white hover:bg-white/50 dark:hover:bg-slate-700/50'}`}
              >
                Inspector
              </button>
              <button 
                onClick={() => setActiveTab('scenarios')} 
                className={`px-5 py-2.5 rounded-md text-sm font-semibold transition-all duration-300 ${activeTab === 'scenarios' ? 'bg-white dark:bg-slate-700 text-blue-600 dark:text-blue-400 shadow-sm' : 'text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white hover:bg-white/50 dark:hover:bg-slate-700/50'}`}
              >
                Threat Library
              </button>
            </motion.div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 flex-1 w-full flex flex-col">
        <AnimatePresence mode="wait">
          {activeTab === 'analyze' && (
            <motion.div 
              key="analyze"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.4, ease: "easeOut" }}
              className="grid grid-cols-1 lg:grid-cols-12 gap-8 flex-1"
            >
              {/* Input Section */}
              <div className="lg:col-span-5 flex flex-col gap-6">
                <div className="bg-white/80 dark:bg-slate-800/80 backdrop-blur-md rounded-3xl shadow-xl shadow-gray-200/50 dark:shadow-none border border-gray-100 dark:border-slate-700 overflow-hidden transition-all duration-300 hover:border-blue-500/30">
                  <div className="p-5 border-b border-gray-100 dark:border-slate-700 bg-gradient-to-r from-gray-50/50 to-transparent dark:from-slate-800/50">
                    <h2 className="text-lg font-bold flex items-center gap-2">
                      <MessageSquare className="w-5 h-5 text-blue-500" /> Message Input
                    </h2>
                  </div>
                  <form onSubmit={handleAnalyze} className="p-6">
                    <div className="mb-5">
                      <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Channel / Source</label>
                      <select 
                        value={channel} 
                        onChange={(e) => setChannel(e.target.value)}
                        className="w-full bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-700 rounded-xl p-3 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all shadow-sm"
                      >
                        <option value="SMS">SMS / Text Message</option>
                        <option value="Email">Email</option>
                        <option value="WhatsApp">WhatsApp / Telegram</option>
                        <option value="Social Media">Social Media DM</option>
                      </select>
                    </div>
                    <div className="mb-6">
                      <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Message Content</label>
                      <textarea
                        value={text}
                        onChange={(e) => setText(e.target.value)}
                        placeholder="Paste the suspicious message here to begin analysis..."
                        className="w-full h-48 bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-700 rounded-xl p-4 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all resize-none shadow-sm placeholder:text-gray-400 dark:placeholder:text-gray-600"
                      ></textarea>
                    </div>
                    <button 
                      type="submit" 
                      disabled={isAnalyzing || !text.trim()}
                      className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-bold py-3.5 px-4 rounded-xl shadow-lg shadow-blue-500/30 hover:shadow-blue-500/50 transition-all duration-300 disabled:opacity-50 disabled:hover:shadow-blue-500/30 flex justify-center items-center gap-2 hover:-translate-y-0.5 active:translate-y-0"
                    >
                      {isAnalyzing ? (
                        <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                      ) : (
                        <><Activity className="w-5 h-5" /> Analyze Threat</>
                      )}
                    </button>
                  </form>
                </div>
              </div>

              {/* Results Section */}
              <div className="lg:col-span-7 flex flex-col gap-6 h-full">
                <AnimatePresence mode="wait">
                  {!result && !isAnalyzing && (
                    <motion.div 
                      key="empty"
                      initial={{ opacity: 0, scale: 0.95 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0, scale: 0.95 }}
                      className="h-full min-h-[400px] flex flex-col items-center justify-center border-2 border-dashed border-gray-300 dark:border-slate-700 rounded-3xl text-gray-400 p-8 text-center bg-white/40 dark:bg-slate-800/20 backdrop-blur-sm"
                    >
                      <div className="w-20 h-20 bg-gray-100 dark:bg-slate-800 rounded-full flex items-center justify-center mb-6 shadow-inner">
                        <ShieldAlert className="w-10 h-10 text-gray-400 dark:text-gray-500" />
                      </div>
                      <h3 className="text-2xl font-bold mb-3 text-gray-700 dark:text-gray-200 tracking-tight">System Ready for Scan</h3>
                      <p className="max-w-md text-gray-500 dark:text-gray-400 leading-relaxed text-sm">
                        Our AI engine is standing by. Paste a suspicious message on the left or load a test scenario from the Threat Library.
                      </p>
                    </motion.div>
                  )}

                  {result && (
                    <motion.div 
                      key="results"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="grid grid-cols-1 md:grid-cols-2 gap-6"
                    >
                      <RiskGauge score={result.risk_score} />
                      <ThreatRadar factors={result.factors} />
                      
                      <div className="md:col-span-2 bg-white/80 dark:bg-slate-800/80 backdrop-blur-md rounded-3xl shadow-lg border border-gray-100 dark:border-slate-700 overflow-hidden">
                        <div className="p-5 border-b border-gray-100 dark:border-slate-700 bg-indigo-50/50 dark:bg-indigo-900/10">
                          <h2 className="text-lg font-bold flex items-center gap-2">
                            <FileText className="w-5 h-5 text-indigo-500" /> Highlighted Analysis
                          </h2>
                        </div>
                        <div className="p-6">
                          <HighlightedText text={text} highlights={result.highlights} />
                        </div>
                      </div>

                      {result.urls && result.urls.length > 0 && (
                        <div className="md:col-span-2 bg-white/80 dark:bg-slate-800/80 backdrop-blur-md rounded-3xl shadow-lg border border-gray-100 dark:border-slate-700 overflow-hidden">
                          <div className="p-5 border-b border-gray-100 dark:border-slate-700 bg-teal-50/50 dark:bg-teal-900/10">
                            <h2 className="text-lg font-bold flex items-center gap-2">
                              <Globe className="w-5 h-5 text-teal-500" /> Extracted Links
                            </h2>
                          </div>
                          <div className="p-6">
                            <div className="flex flex-col gap-3">
                              {result.urls.map((urlInfo, idx) => (
                                <div key={idx} className="flex flex-col sm:flex-row sm:items-center justify-between p-4 rounded-xl bg-gray-50 dark:bg-slate-900 border border-gray-200 dark:border-slate-700 gap-4 hover:border-teal-500/30 transition-colors">
                                  <div className="break-all font-mono text-sm text-teal-600 dark:text-teal-400 font-medium">
                                    {urlInfo.url}
                                  </div>
                                  <div className="flex items-center gap-2">
                                    <span className="text-xs font-bold px-3 py-1.5 bg-red-100 text-red-700 rounded-full shrink-0 shadow-sm">
                                      Risk: {urlInfo.risk_score}%
                                    </span>
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                        </div>
                      )}

                      <div className="md:col-span-2 bg-white/80 dark:bg-slate-800/80 backdrop-blur-md rounded-3xl shadow-lg border border-gray-100 dark:border-slate-700 overflow-hidden">
                        <div className="p-5 border-b border-gray-100 dark:border-slate-700 bg-emerald-50/50 dark:bg-emerald-900/10">
                          <h2 className="text-lg font-bold flex items-center gap-2">
                            <CheckCircle className="w-5 h-5 text-emerald-500" /> Action Plan
                          </h2>
                        </div>
                        <div className="p-6">
                          <ul className="space-y-4">
                            {result.recommendations.map((rec, idx) => (
                              <li key={idx} className="flex items-start gap-4 text-sm bg-gray-50 dark:bg-slate-900/50 p-4 rounded-xl border border-gray-100 dark:border-slate-800">
                                <div className="mt-0.5 shrink-0 w-6 h-6 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center text-xs font-bold shadow-sm">{idx + 1}</div>
                                <span className="text-gray-700 dark:text-gray-300 leading-relaxed font-medium">{rec}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </motion.div>
          )}

          {activeTab === 'scenarios' && (
            <motion.div 
              key="scenarios"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.4 }}
              className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6"
            >
              {scenarios.map((s, index) => (
                <motion.div 
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                  key={s.id} 
                  className="bg-white/80 dark:bg-slate-800/80 backdrop-blur-md rounded-3xl shadow-lg border border-gray-100 dark:border-slate-700 overflow-hidden flex flex-col hover:shadow-xl hover:border-blue-500/30 transition-all duration-300 cursor-pointer group transform hover:-translate-y-1"
                  onClick={() => loadScenario(s)}
                >
                  <div className="p-6 flex-1">
                    <div className="flex justify-between items-start mb-4">
                      <span className="text-xs font-bold px-3 py-1 rounded-full bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 uppercase tracking-wider">
                        {s.channel}
                      </span>
                      <span className={`text-xs font-bold px-3 py-1 rounded-full ${s.category.includes('Legitimate') ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400' : 'bg-rose-100 text-rose-700 dark:bg-rose-900/30 dark:text-rose-400'} uppercase tracking-wider`}>
                        {s.category}
                      </span>
                    </div>
                    <h3 className="text-xl font-bold mb-3 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors tracking-tight">{s.title}</h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400 line-clamp-3 leading-relaxed italic">"{s.message}"</p>
                  </div>
                  <div className="p-5 border-t border-gray-100 dark:border-slate-700 bg-gray-50/50 dark:bg-slate-900/50 flex justify-between items-center group-hover:bg-blue-50/50 dark:group-hover:bg-blue-900/10 transition-colors">
                    <span className="text-sm font-bold text-blue-600 dark:text-blue-400">Run Scenario</span>
                    <PlayCircle className="w-6 h-6 text-blue-600 dark:text-blue-400 group-hover:translate-x-1 group-hover:scale-110 transition-all" />
                  </div>
                </motion.div>
              ))}
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {/* Footer / Copyright Section */}
      <footer className="w-full bg-white/50 dark:bg-slate-900/50 backdrop-blur-md border-t border-gray-200/50 dark:border-slate-800/50 py-8 mt-auto z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row justify-between items-center gap-4">
          <div className="flex items-center gap-2 text-gray-500 dark:text-gray-400 text-sm font-medium">
            <Shield className="w-4 h-4 text-blue-500" />
            <span>&copy; {new Date().getFullYear()} Smart Scam Detector. All rights reserved.</span>
          </div>
          <div className="flex items-center gap-1.5 text-sm text-gray-500 dark:text-gray-400 font-medium">
            Designed & Developed by Roshan
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;

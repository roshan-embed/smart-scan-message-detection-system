import React, { useState, useEffect } from 'react';
import { Shield, ShieldAlert, AlertCircle, FileText, CheckCircle, Activity, Globe, MessageSquare, PlayCircle } from 'lucide-react';
import RiskGauge from './components/RiskGauge';
import HighlightedText from './components/HighlightedText';
import ThreatRadar from './components/ThreatRadar';

// Base API URL
const API_BASE = 'http://localhost:8000/api';

function App() {
  const [text, setText] = useState('');
  const [channel, setChannel] = useState('SMS');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState(null);
  const [scenarios, setScenarios] = useState([]);
  const [activeTab, setActiveTab] = useState('analyze'); // analyze, scenarios, quiz

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
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100 font-sans selection:bg-blue-500/30">
      {/* Navbar */}
      <nav className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-blue-600 flex items-center justify-center text-white">
                <Shield className="w-6 h-6" />
              </div>
              <div>
                <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-indigo-600 dark:from-blue-400 dark:to-indigo-400">
                  Smart Scam Detector
                </h1>
                <p className="text-xs text-gray-500 font-medium tracking-wide uppercase">AI Threat Intelligence</p>
              </div>
            </div>
            <div className="flex gap-2">
              <button onClick={() => setActiveTab('analyze')} className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${activeTab === 'analyze' ? 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white' : 'text-gray-500 hover:text-gray-900 dark:hover:text-white'}`}>
                Inspector
              </button>
              <button onClick={() => setActiveTab('scenarios')} className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${activeTab === 'scenarios' ? 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white' : 'text-gray-500 hover:text-gray-900 dark:hover:text-white'}`}>
                Threat Library
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {activeTab === 'analyze' && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
            {/* Input Section */}
            <div className="lg:col-span-5 flex flex-col gap-6">
              <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden">
                <div className="p-4 border-b border-gray-100 dark:border-gray-700 bg-gray-50/50 dark:bg-gray-800/50 flex justify-between items-center">
                  <h2 className="text-lg font-semibold flex items-center gap-2">
                    <MessageSquare className="w-5 h-5 text-blue-500" /> Message Input
                  </h2>
                </div>
                <form onSubmit={handleAnalyze} className="p-4">
                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Channel / Source</label>
                    <select 
                      value={channel} 
                      onChange={(e) => setChannel(e.target.value)}
                      className="w-full bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg p-2.5 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
                    >
                      <option value="SMS">SMS / Text Message</option>
                      <option value="Email">Email</option>
                      <option value="WhatsApp">WhatsApp / Telegram</option>
                      <option value="Social Media">Social Media DM</option>
                    </select>
                  </div>
                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Message Content</label>
                    <textarea
                      value={text}
                      onChange={(e) => setText(e.target.value)}
                      placeholder="Paste the suspicious message here..."
                      className="w-full h-48 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg p-4 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all resize-none"
                    ></textarea>
                  </div>
                  <button 
                    type="submit" 
                    disabled={isAnalyzing || !text.trim()}
                    className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-4 rounded-xl shadow-md shadow-blue-500/20 transition-all disabled:opacity-50 flex justify-center items-center gap-2"
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
            <div className="lg:col-span-7 flex flex-col gap-6">
              {!result && !isAnalyzing && (
                <div className="h-full min-h-[400px] flex flex-col items-center justify-center border-2 border-dashed border-gray-200 dark:border-gray-700 rounded-2xl text-gray-400 p-8 text-center bg-white/50 dark:bg-gray-800/50">
                  <ShieldAlert className="w-16 h-16 mb-4 text-gray-300 dark:text-gray-600" />
                  <h3 className="text-xl font-semibold mb-2 text-gray-600 dark:text-gray-300">Ready for Scan</h3>
                  <p className="max-w-md">Paste a message on the left or select a scenario from the Threat Library to begin analysis.</p>
                </div>
              )}

              {result && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
                  <RiskGauge score={result.risk_score} />
                  <ThreatRadar factors={result.factors} />
                  
                  <div className="md:col-span-2 bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden">
                    <div className="p-4 border-b border-gray-100 dark:border-gray-700 bg-gray-50/50 dark:bg-gray-800/50">
                      <h2 className="text-lg font-semibold flex items-center gap-2">
                        <FileText className="w-5 h-5 text-indigo-500" /> Highlighted Analysis
                      </h2>
                    </div>
                    <div className="p-4">
                      <HighlightedText text={text} highlights={result.highlights} />
                    </div>
                  </div>

                  {result.urls && result.urls.length > 0 && (
                    <div className="md:col-span-2 bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden">
                      <div className="p-4 border-b border-gray-100 dark:border-gray-700 bg-gray-50/50 dark:bg-gray-800/50">
                        <h2 className="text-lg font-semibold flex items-center gap-2">
                          <Globe className="w-5 h-5 text-teal-500" /> Extracted Links
                        </h2>
                      </div>
                      <div className="p-4">
                        <div className="flex flex-col gap-3">
                          {result.urls.map((urlInfo, idx) => (
                            <div key={idx} className="flex flex-col sm:flex-row sm:items-center justify-between p-3 rounded-lg bg-gray-50 dark:bg-gray-900 border border-gray-100 dark:border-gray-700 gap-4">
                              <div className="break-all font-mono text-sm text-blue-600 dark:text-blue-400">
                                {urlInfo.url}
                              </div>
                              <div className="flex items-center gap-2">
                                <span className="text-xs font-semibold px-2 py-1 bg-red-100 text-red-700 rounded-full shrink-0">
                                  Risk: {urlInfo.risk_score}%
                                </span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  )}

                  <div className="md:col-span-2 bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden">
                    <div className="p-4 border-b border-gray-100 dark:border-gray-700 bg-gray-50/50 dark:bg-gray-800/50">
                      <h2 className="text-lg font-semibold flex items-center gap-2">
                        <CheckCircle className="w-5 h-5 text-emerald-500" /> Action Plan
                      </h2>
                    </div>
                    <div className="p-4">
                      <ul className="space-y-3">
                        {result.recommendations.map((rec, idx) => (
                          <li key={idx} className="flex items-start gap-3 text-sm">
                            <div className="mt-0.5 shrink-0 w-5 h-5 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center text-xs font-bold">{idx + 1}</div>
                            <span className="text-gray-700 dark:text-gray-300 leading-relaxed">{rec}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'scenarios' && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 animate-in fade-in duration-300">
            {scenarios.map(s => (
              <div key={s.id} className="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden flex flex-col hover:shadow-md transition-shadow cursor-pointer group" onClick={() => loadScenario(s)}>
                <div className="p-5 flex-1">
                  <div className="flex justify-between items-start mb-3">
                    <span className="text-xs font-bold px-2 py-1 rounded bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 uppercase tracking-wide">
                      {s.channel}
                    </span>
                    <span className={`text-xs font-bold px-2 py-1 rounded ${s.category.includes('Legitimate') ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'} uppercase tracking-wide`}>
                      {s.category}
                    </span>
                  </div>
                  <h3 className="text-lg font-bold mb-2 group-hover:text-blue-600 transition-colors">{s.title}</h3>
                  <p className="text-sm text-gray-500 dark:text-gray-400 line-clamp-3">"{s.message}"</p>
                </div>
                <div className="p-4 border-t border-gray-100 dark:border-gray-700 bg-gray-50/50 dark:bg-gray-800/50 flex justify-between items-center">
                  <span className="text-sm font-medium text-blue-600">Test Scenario</span>
                  <PlayCircle className="w-5 h-5 text-blue-600 group-hover:translate-x-1 transition-transform" />
                </div>
              </div>
            ))}
          </div>
        )}

      </main>
    </div>
  );
}

export default App;

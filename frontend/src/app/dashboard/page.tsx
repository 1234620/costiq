'use client';

import { useEffect, useState, useCallback } from 'react';
import Navbar from '@/components/Navbar';
import FindingCard from '@/components/FindingCard';
import AgentFeed from '@/components/AgentFeed';
import { api, Finding, AgentActivity, createWebSocket } from '@/lib/api';

export default function Dashboard() {
  const [findings, setFindings] = useState<Finding[]>([]);
  const [activity, setActivity] = useState<AgentActivity[]>([]);
  const [stats, setStats] = useState({ identified: 0, approved: 0, executed: 0 });
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisComplete, setAnalysisComplete] = useState(false);

  // Load existing data
  const loadData = useCallback(async () => {
    try {
      const [findingsRes, activityRes, statsRes] = await Promise.all([
        api.getFindings(),
        api.getActivity(),
        api.getStats(),
      ]);
      setFindings(findingsRes.findings || []);
      setActivity(activityRes.activity || []);
      setStats({
        identified: statsRes.total_identified || 0,
        approved: statsRes.total_approved || 0,
        executed: statsRes.total_executed || 0,
      });
      if ((findingsRes.findings || []).length > 0) {
        setAnalysisComplete(true);
      }
    } catch {
      // API not available yet — that's OK
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // WebSocket for real-time updates
  useEffect(() => {
    const ws = createWebSocket('global');
    if (!ws) return;

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'finding') {
          // Refresh findings
          loadData();
        } else if (data.type === 'agent_activity') {
          setActivity((prev) => [
            { ...data.payload, timestamp: new Date().toISOString() },
            ...prev,
          ].slice(0, 50));
        } else if (data.type === 'approval_decision') {
          loadData();
        }
      } catch {
        // ignore
      }
    };

    return () => ws.close();
  }, [loadData]);

  const triggerAnalysis = async () => {
    setIsAnalyzing(true);
    try {
      await api.triggerAnalysis(['demo']);
      
      // Poll for results
      const pollInterval = setInterval(async () => {
        await loadData();
      }, 1000);

      // Stop polling after 15 seconds
      setTimeout(() => {
        clearInterval(pollInterval);
        setIsAnalyzing(false);
        setAnalysisComplete(true);
        loadData();
      }, 15000);
    } catch {
      setIsAnalyzing(false);
    }
  };

  const formatDollar = (n: number) => {
    if (n >= 1_000_000) return `$${(n / 1_000_000).toFixed(1)}M`;
    if (n >= 1_000) return `$${(n / 1_000).toFixed(0)}K`;
    return `$${n.toFixed(0)}`;
  };

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-primary)' }}>
      <Navbar />

      <div className="page">
        {/* Page Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px' }}>
          <div>
            <span className="label-accent">Command Center</span>
            <h1 className="heading-1" style={{ marginTop: '8px' }}>Dashboard</h1>
          </div>
          <button
            className="btn-primary"
            onClick={triggerAnalysis}
            disabled={isAnalyzing}
            style={{
              opacity: isAnalyzing ? 0.7 : 1,
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
            }}
          >
            {isAnalyzing && <span className="spinner" />}
            {isAnalyzing ? 'Agents Working...' : '🚀 Run Analysis'}
          </button>
        </div>

        {/* Savings Counter Cards */}
        <div className="grid-3" style={{ marginBottom: '32px' }}>
          {[
            { label: 'Savings Identified', value: stats.identified, color: 'var(--accent)', icon: '🔍' },
            { label: 'Savings Approved', value: stats.approved, color: 'var(--agent-finops)', icon: '✅' },
            { label: 'Savings Executed', value: stats.executed, color: 'var(--agent-resource)', icon: '⚡' },
          ].map((item) => (
            <div key={item.label} className="card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span className="label">{item.label}</span>
                <span style={{ fontSize: '24px' }}>{item.icon}</span>
              </div>
              <div className="metric-value" style={{ color: item.color }}>
                {formatDollar(item.value)}
              </div>
            </div>
          ))}
        </div>

        {/* Main Content Grid */}
        <div className="grid-2-sidebar">
          {/* Findings Feed */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <span className="label-accent">
                💡 Cost Findings ({findings.length})
              </span>
            </div>

            {findings.length === 0 ? (
              <div className="card" style={{ textAlign: 'center', padding: '60px 40px' }}>
                <div style={{ fontSize: '48px', marginBottom: '16px' }}>🔎</div>
                <h3 className="heading-3" style={{ marginBottom: '12px' }}>No findings yet</h3>
                <p className="body-sm" style={{ maxWidth: '400px', margin: '0 auto 24px' }}>
                  Click &quot;Run Analysis&quot; to unleash all 4 agents on your enterprise data.
                  They&apos;ll find cost leakage with full financial math.
                </p>
                <button className="btn-primary" onClick={triggerAnalysis} disabled={isAnalyzing}>
                  {isAnalyzing ? 'Analyzing...' : '🚀 Run Demo Analysis'}
                </button>
              </div>
            ) : (
              findings.map((finding, i) => (
                <FindingCard key={finding.id} finding={finding} index={i} />
              ))
            )}
          </div>

          {/* Agent Activity Sidebar */}
          <div
            className="card"
            style={{
              maxHeight: 'calc(100vh - 180px)',
              overflowY: 'auto',
              position: 'sticky',
              top: '96px',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <span className="label-accent">🤖 Live Agent Activity</span>
              {isAnalyzing && <span className="spinner" />}
            </div>
            <AgentFeed activity={activity} />
          </div>
        </div>
      </div>
    </div>
  );
}

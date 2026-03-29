'use client';

import { useEffect, useState } from 'react';
import Navbar from '@/components/Navbar';
import { api, Stats, Finding } from '@/lib/api';
import { Coins, Zap, Cloud, BarChart2, Calculator } from 'lucide-react';

const agentMeta: Record<string, { label: string; icon: React.ReactNode; color: string }> = {
  spend: { label: 'Spend Intelligence', icon: <Coins size={28} />, color: 'var(--agent-spend)' },
  sla: { label: 'SLA Prevention', icon: <Zap size={28} />, color: 'var(--agent-sla)' },
  resource: { label: 'Resource Optimization', icon: <Cloud size={28} />, color: 'var(--agent-resource)' },
  finops: { label: 'Financial Operations', icon: <BarChart2 size={28} />, color: 'var(--agent-finops)' },
};

export default function ImpactPage() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [findings, setFindings] = useState<Finding[]>([]);

  useEffect(() => {
    const load = async () => {
      try {
        const [statsRes, findingsRes] = await Promise.all([api.getStats(), api.getFindings()]);
        setStats(statsRes);
        setFindings(findingsRes.findings || []);
      } catch {
        // API not running
      }
    };
    load();
  }, []);

  const formatDollar = (n: number) => {
    if (n >= 1_000_000) return `$${(n / 1_000_000).toFixed(1)}M`;
    if (n >= 1_000) return `$${(n / 1_000).toFixed(0)}K`;
    return `$${n.toFixed(0)}`;
  };

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-primary)' }}>
      <Navbar />
      <div className="page">
        <div style={{ marginBottom: '48px', textAlign: 'center' }}>
          <span className="label-accent">The Bottom Line</span>
          <h1 className="heading-1" style={{ marginTop: '8px' }}>Impact Board</h1>
          <p className="body" style={{ marginTop: '8px' }}>
            Every dollar tracked. Every formula auditable.
          </p>
        </div>

        {stats ? (
          <>
            {/* Big Number */}
            <div className="reveal-up" style={{ textAlign: 'center', marginBottom: '64px' }}>
              <div style={{ fontSize: 'clamp(48px, 8vw, 100px)', fontWeight: 900, color: 'var(--accent)', lineHeight: 1 }}>
                {formatDollar(stats.total_identified)}
              </div>
              <div className="label" style={{ marginTop: '12px', fontSize: '12px' }}>
                Total Savings Identified
              </div>
            </div>

            {/* Status Breakdown */}
            <div className="grid-3 reveal-up" style={{ marginBottom: '48px', animationDelay: '0.1s' }}>
              {[
                { label: 'Identified', value: stats.total_identified, color: 'var(--accent)' },
                { label: 'Approved', value: stats.total_approved, color: 'var(--agent-finops)' },
                { label: 'Executed', value: stats.total_executed, color: 'var(--agent-resource)' },
              ].map((item) => (
                <div key={item.label} className="card" style={{ textAlign: 'center' }}>
                  <div className="label">{item.label}</div>
                  <div className="metric-value" style={{ color: item.color }}>
                    {formatDollar(item.value)}
                  </div>
                </div>
              ))}
            </div>

            {/* Agent Breakdown */}
            <div className="reveal-up" style={{ animationDelay: '0.2s', marginBottom: '48px' }}>
              <span className="label-accent" style={{ marginBottom: '20px', display: 'block' }}>
                Savings by Agent
              </span>
              <div className="grid-3" style={{ gridTemplateColumns: 'repeat(4, 1fr)' }}>
                {Object.entries(stats.by_agent).map(([agent, data]) => {
                  const meta = agentMeta[agent] || { label: agent, icon: <div />, color: 'var(--accent)' };
                  const pct = stats.total_identified > 0
                    ? ((data.savings / stats.total_identified) * 100).toFixed(0)
                    : '0';
                  return (
                    <div key={agent} className="card">
                      <div style={{ marginBottom: '8px', color: meta.color }}>{meta.icon}</div>
                      <div className="label" style={{ marginBottom: '4px' }}>{meta.label}</div>
                      <div style={{ fontSize: '28px', fontWeight: 900, color: meta.color }}>
                        {formatDollar(data.savings)}
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '12px' }}>
                        <span className="label">{data.count} findings</span>
                        <span style={{ fontSize: '12px', fontWeight: 700, color: meta.color }}>
                          {pct}%
                        </span>
                      </div>
                      {/* Contribution bar */}
                      <div className="confidence-bar" style={{ marginTop: '4px' }}>
                        <div className="confidence-fill" style={{ width: `${pct}%`, background: meta.color }} />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Individual FIS Details */}
            <div className="reveal-up" style={{ animationDelay: '0.3s' }}>
              <span className="label-accent" style={{ marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Calculator size={14} /> Financial Impact Statements
              </span>
              {findings.slice(0, 10).map((finding, i) => {
                const meta = agentMeta[finding.agent_type] || { color: 'var(--accent)' };
                return (
                  <div key={finding.id} className="card" style={{ marginBottom: '12px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <div>
                        <span className="label" style={{ color: meta.color }}>
                          {finding.agent_type} · {finding.finding_type}
                        </span>
                        <h3 className="heading-3" style={{ marginTop: '4px' }}>{finding.title}</h3>
                      </div>
                      <div style={{ textAlign: 'right' }}>
                        <div style={{ fontSize: '24px', fontWeight: 900, color: meta.color }}>
                          {formatDollar(finding.fis.projected_savings)}
                        </div>
                        <div className="label">
                          {(finding.fis.confidence_score * 100).toFixed(0)}% confidence
                        </div>
                      </div>
                    </div>
                    <div className="fis-formula" style={{ marginTop: '12px', fontSize: '12px' }}>
                      {finding.fis.formula}
                    </div>
                  </div>
                );
              })}
            </div>
          </>
        ) : (
          <div className="card" style={{ textAlign: 'center', padding: '80px' }}>
            <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '16px', color: 'var(--text-muted)' }}>
              <BarChart2 size={48} />
            </div>
            <h3 className="heading-3" style={{ marginBottom: '12px' }}>No data yet</h3>
            <p className="body-sm">Run an analysis from the Dashboard to see your impact board.</p>
          </div>
        )}
      </div>
    </div>
  );
}

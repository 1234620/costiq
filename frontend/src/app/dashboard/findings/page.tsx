'use client';

import { useEffect, useState } from 'react';
import Navbar from '@/components/Navbar';
import FindingCard from '@/components/FindingCard';
import { api, Finding } from '@/lib/api';

export default function FindingsPage() {
  const [findings, setFindings] = useState<Finding[]>([]);
  const [filter, setFilter] = useState<string>('all');
  const [totalSavings, setTotalSavings] = useState(0);

  useEffect(() => {
    const load = async () => {
      try {
        const res = await api.getFindings();
        setFindings(res.findings || []);
        setTotalSavings(res.total_savings || 0);
      } catch {
        // API not available
      }
    };
    load();
  }, []);

  const filtered = filter === 'all'
    ? findings
    : findings.filter((f) => f.agent_type === filter);

  const agentTabs = [
    { key: 'all', label: 'All', icon: '🌐' },
    { key: 'spend', label: 'Spend', icon: '💰' },
    { key: 'sla', label: 'SLA', icon: '⚡' },
    { key: 'resource', label: 'Resource', icon: '☁️' },
    { key: 'finops', label: 'FinOps', icon: '📊' },
  ];

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-primary)' }}>
      <Navbar />
      <div className="page">
        <div style={{ marginBottom: '32px' }}>
          <span className="label-accent">All Discoveries</span>
          <h1 className="heading-1" style={{ marginTop: '8px' }}>
            Findings
          </h1>
          <p className="body" style={{ marginTop: '8px' }}>
            {findings.length} findings · ${totalSavings.toLocaleString()} total savings identified
          </p>
        </div>

        {/* Filter Tabs */}
        <div style={{ display: 'flex', gap: '12px', marginBottom: '32px', flexWrap: 'wrap' }}>
          {agentTabs.map((tab) => (
            <button
              key={tab.key}
              onClick={() => setFilter(tab.key)}
              style={{
                padding: '10px 20px',
                borderRadius: 'var(--radius-full)',
                background: filter === tab.key ? 'var(--accent)' : 'var(--bg-secondary)',
                color: filter === tab.key ? 'var(--bg-primary)' : 'var(--text-secondary)',
                fontWeight: 800,
                fontSize: '11px',
                letterSpacing: '0.15em',
                textTransform: 'uppercase' as const,
                border: `1px solid ${filter === tab.key ? 'var(--accent)' : 'var(--border)'}`,
                cursor: 'pointer',
                transition: 'all 0.3s',
              }}
            >
              {tab.icon} {tab.label} ({tab.key === 'all' ? findings.length : findings.filter(f => f.agent_type === tab.key).length})
            </button>
          ))}
        </div>

        {/* Findings List */}
        {filtered.map((finding, i) => (
          <FindingCard key={finding.id} finding={finding} index={i} />
        ))}

        {filtered.length === 0 && (
          <div className="card" style={{ textAlign: 'center', padding: '60px' }}>
            <p className="body-sm">No findings found. Run an analysis first!</p>
          </div>
        )}
      </div>
    </div>
  );
}

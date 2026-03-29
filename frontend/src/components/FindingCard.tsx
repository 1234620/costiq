'use client';

import { Finding } from '@/lib/api';
import { useState } from 'react';
import FISPanel from './FISPanel';
import { Coins, Zap, Cloud, BarChart2 } from 'lucide-react';

const agentColors: Record<string, string> = {
  spend: 'var(--agent-spend)',
  sla: 'var(--agent-sla)',
  resource: 'var(--agent-resource)',
  finops: 'var(--agent-finops)',
};

const agentLabels: Record<string, React.ReactNode> = {
  spend: <span style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}><Coins size={14} /> Spend Intelligence</span>,
  sla: <span style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}><Zap size={14} /> SLA Prevention</span>,
  resource: <span style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}><Cloud size={14} /> Resource Optimization</span>,
  finops: <span style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}><BarChart2 size={14} /> Financial Operations</span>,
};

export default function FindingCard({ finding, index = 0 }: { finding: Finding; index?: number }) {
  const [expanded, setExpanded] = useState(false);
  const color = agentColors[finding.agent_type] || 'var(--accent)';

  return (
    <div
      className="card"
      onClick={() => setExpanded(!expanded)}
      style={{
        marginBottom: '16px',
        cursor: 'pointer',
        borderLeft: `3px solid ${color}`,
        animation: `reveal-up 0.6s var(--ease-luxury) both`,
        animationDelay: `${index * 0.1}s`,
      }}
    >
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div style={{ flex: 1 }}>
          <div style={{ display: 'flex', gap: '12px', alignItems: 'center', marginBottom: '8px' }}>
            <span className="label-accent" style={{ color }}>
              {agentLabels[finding.agent_type] || finding.agent_type}
            </span>
            <span className={`badge badge-severity-${finding.severity}`}>
              {finding.severity}
            </span>
          </div>
          <h3 className="heading-3" style={{ marginBottom: '8px' }}>
            {finding.title}
          </h3>
          <p className="body-sm" style={{ maxWidth: '600px' }}>
            {finding.description}
          </p>
        </div>

        {/* Savings badge */}
        <div style={{ textAlign: 'right', minWidth: '130px', paddingLeft: '24px' }}>
          <div style={{ fontSize: '32px', fontWeight: 900, color, lineHeight: 1 }}>
            ${finding.fis.projected_savings >= 1000
              ? `${(finding.fis.projected_savings / 1000).toFixed(0)}K`
              : finding.fis.projected_savings.toFixed(0)}
          </div>
          <div className="label" style={{ marginTop: '4px' }}>
            Savings
          </div>
        </div>
      </div>

      {/* Confidence bar */}
      <div style={{ marginTop: '20px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
          <span className="label">Confidence</span>
          <span style={{ fontSize: '12px', fontWeight: 700, color }}>
            {(finding.fis.confidence_score * 100).toFixed(0)}%
          </span>
        </div>
        <div className="confidence-bar">
          <div
            className="confidence-fill"
            style={{
              width: `${finding.fis.confidence_score * 100}%`,
              background: color,
            }}
          />
        </div>
      </div>

      {/* Expanded FIS */}
      {expanded && (
        <div style={{ marginTop: '20px' }}>
          <FISPanel fis={finding.fis} color={color} />
          {finding.action_description && (
            <div
              style={{
                marginTop: '16px',
                padding: '16px',
                background: 'var(--bg-tertiary)',
                borderRadius: 'var(--radius-md)',
                borderLeft: `3px solid ${color}`,
              }}
            >
              <span className="label" style={{ marginBottom: '8px', display: 'block' }}>
                Proposed Action
              </span>
              <p className="mono" style={{ color: 'var(--text-primary)' }}>
                {finding.action_description}
              </p>
            </div>
          )}
        </div>
      )}

      {/* Status + Action */}
      <div style={{ marginTop: '16px', display: 'flex', gap: '12px', alignItems: 'center' }}>
        <span className={`badge badge-${finding.status}`}>{finding.status}</span>
        {finding.status === 'open' && (
          <a
            href={`/dashboard/approvals`}
            className="btn-primary"
            style={{ fontSize: '10px', padding: '6px 16px' }}
            onClick={(e) => e.stopPropagation()}
          >
            Review & Approve →
          </a>
        )}
        <span className="label" style={{ marginLeft: 'auto' }}>
          {expanded ? '▲ Collapse' : '▼ Show Math'}
        </span>
      </div>
    </div>
  );
}

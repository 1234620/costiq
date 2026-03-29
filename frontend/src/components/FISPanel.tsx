'use client';

import { FIS } from '@/lib/api';
import { Calculator } from 'lucide-react';

interface FISPanelProps {
  fis: FIS;
  color?: string;
}

export default function FISPanel({ fis, color = 'var(--accent)' }: FISPanelProps) {
  const rows = [
    { label: 'Baseline Cost', value: `$${fis.baseline_cost.toLocaleString('en-US', { minimumFractionDigits: 0 })}`, highlight: false },
    { label: 'Intervention Cost', value: `$${fis.intervention_cost.toLocaleString('en-US', { minimumFractionDigits: 0 })}`, highlight: false },
    { label: 'Projected Savings', value: `$${fis.projected_savings.toLocaleString('en-US', { minimumFractionDigits: 0 })}`, highlight: true },
    { label: 'Annualized Savings', value: `$${fis.annualized_savings.toLocaleString('en-US', { minimumFractionDigits: 0 })}`, highlight: true },
    { label: 'Confidence Score', value: `${(fis.confidence_score * 100).toFixed(0)}%`, highlight: false },
    { label: 'Payback Period', value: fis.payback_period, highlight: false },
  ];

  return (
    <div className="fis-panel">
      <div className="label-accent" style={{ marginBottom: '16px', color, display: 'flex', alignItems: 'center', gap: '8px' }}>
        <Calculator size={14} /> Financial Impact Statement
      </div>

      {/* Key metrics */}
      {rows.map((row) => (
        <div className="fis-row" key={row.label}>
          <span className="body-sm">{row.label}</span>
          <span
            style={{
              fontWeight: row.highlight ? 900 : 600,
              fontSize: row.highlight ? '18px' : '14px',
              color: row.highlight ? color : 'var(--text-primary)',
            }}
          >
            {row.value}
          </span>
        </div>
      ))}

      {/* Formula */}
      <div style={{ marginTop: '16px' }}>
        <span className="label" style={{ marginBottom: '8px', display: 'block' }}>
          Formula
        </span>
        <div className="fis-formula">{fis.formula}</div>
      </div>

      {/* Audit trail */}
      {fis.audit_trail && fis.audit_trail.length > 0 && (
        <div style={{ marginTop: '16px' }}>
          <span className="label" style={{ marginBottom: '8px', display: 'block' }}>
            Audit Trail
          </span>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
            {fis.audit_trail.map((source, i) => (
              <span
                key={i}
                style={{
                  display: 'inline-block',
                  padding: '4px 12px',
                  background: 'var(--bg-tertiary)',
                  borderRadius: 'var(--radius-full)',
                  fontSize: '11px',
                  fontWeight: 600,
                  color: 'var(--text-secondary)',
                  fontFamily: "'SF Mono', 'Fira Code', monospace",
                }}
              >
                {source}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

'use client';

import { AgentActivity } from '@/lib/api';

const agentColors: Record<string, string> = {
  spend: 'var(--agent-spend)',
  sla: 'var(--agent-sla)',
  resource: 'var(--agent-resource)',
  finops: 'var(--agent-finops)',
  supervisor: 'var(--accent)',
};

const statusIcons: Record<string, string> = {
  running: '⚡',
  completed: '✅',
  error: '❌',
  executing: '🔄',
};

export default function AgentFeed({ activity }: { activity: AgentActivity[] }) {
  if (activity.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '40px 0' }}>
        <div style={{ fontSize: '40px', marginBottom: '12px' }}>🤖</div>
        <p className="body-sm">No agent activity yet.</p>
        <p className="label" style={{ marginTop: '8px' }}>
          Trigger an analysis to see agents in action
        </p>
      </div>
    );
  }

  return (
    <div>
      {activity.map((item, i) => {
        const color = agentColors[item.agent] || 'var(--text-muted)';
        const icon = statusIcons[item.status] || '📌';

        return (
          <div
            key={i}
            className="activity-item"
            style={{ animationDelay: `${i * 0.05}s` }}
          >
            <div
              className={`activity-dot ${item.status === 'running' ? 'running' : ''}`}
              style={{ background: color }}
            />
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ display: 'flex', gap: '8px', alignItems: 'center', marginBottom: '4px' }}>
                <span
                  style={{
                    fontSize: '10px',
                    fontWeight: 900,
                    letterSpacing: '0.2em',
                    textTransform: 'uppercase' as const,
                    color,
                  }}
                >
                  {item.agent}
                </span>
                <span style={{ fontSize: '12px' }}>{icon}</span>
              </div>
              <p style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '2px' }}>
                {item.action}
              </p>
              <p style={{ fontSize: '12px', color: 'var(--text-secondary)', lineHeight: 1.4 }}>
                {item.detail}
              </p>
              {item.timestamp && (
                <span className="label" style={{ fontSize: '9px', marginTop: '4px', display: 'block' }}>
                  {new Date(item.timestamp).toLocaleTimeString()}
                </span>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}

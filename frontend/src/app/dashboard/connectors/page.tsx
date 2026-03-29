'use client';

import { useEffect, useState } from 'react';
import Navbar from '@/components/Navbar';
import { api } from '@/lib/api';

interface Connector {
  id: string;
  name: string;
  type: string;
  icon: string;
  status: string;
  description: string;
}

export default function ConnectorsPage() {
  const [connectors, setConnectors] = useState<Connector[]>([]);
  const [connecting, setConnecting] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      try {
        const res = await api.getConnectors();
        setConnectors(res.connectors || []);
      } catch {
        // Default connectors when API is not available
        setConnectors([
          { id: 'sap', name: 'SAP ERP', type: 'erp', icon: '🏢', status: 'available', description: 'Procurement, finance, and HR data' },
          { id: 'salesforce', name: 'Salesforce', type: 'crm', icon: '☁️', status: 'available', description: 'Customer and revenue data' },
          { id: 'aws', name: 'AWS Cost Explorer', type: 'cloud', icon: '🔶', status: 'available', description: 'Cloud infrastructure costs and usage' },
          { id: 'jira', name: 'JIRA', type: 'project', icon: '📋', status: 'available', description: 'Project tracking and SLA metrics' },
          { id: 'quickbooks', name: 'QuickBooks', type: 'finance', icon: '📊', status: 'available', description: 'Financial transactions and reporting' },
          { id: 'csv', name: 'CSV Upload', type: 'file', icon: '📄', status: 'available', description: 'Universal data import via CSV' },
        ]);
      }
    };
    load();
  }, []);

  const handleConnect = async (id: string) => {
    setConnecting(id);
    try {
      await api.connectConnector(id);
      setConnectors((prev) =>
        prev.map((c) => (c.id === id ? { ...c, status: 'connected' } : c))
      );
    } catch {
      // Show connected anyway for demo
      setConnectors((prev) =>
        prev.map((c) => (c.id === id ? { ...c, status: 'connected' } : c))
      );
    }
    setTimeout(() => setConnecting(null), 500);
  };

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-primary)' }}>
      <Navbar />
      <div className="page">
        <div style={{ marginBottom: '32px' }}>
          <span className="label-accent">Data Sources</span>
          <h1 className="heading-1" style={{ marginTop: '8px' }}>Connectors</h1>
          <p className="body" style={{ marginTop: '8px' }}>
            Connect your enterprise systems for real-time cost analysis.
            Demo mode uses synthetic data with embedded anomalies.
          </p>
        </div>

        <div className="connector-grid">
          {connectors.map((connector, i) => (
            <div
              key={connector.id}
              className="connector-card reveal-up"
              style={{ animationDelay: `${i * 0.1}s` }}
            >
              <div className="connector-icon">{connector.icon}</div>
              <h3 className="heading-3" style={{ marginBottom: '8px' }}>
                {connector.name}
              </h3>
              <p className="body-sm" style={{ marginBottom: '16px' }}>
                {connector.description}
              </p>

              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div className={`connector-status ${connector.status}`}>
                  <span className="dot" />
                  <span style={{ color: connector.status === 'connected' ? 'var(--agent-finops)' : 'var(--text-muted)' }}>
                    {connector.status === 'connected' ? 'Connected' : 'Available'}
                  </span>
                </div>

                {connector.status !== 'connected' ? (
                  <button
                    className="btn-primary"
                    style={{ fontSize: '10px', padding: '8px 16px' }}
                    onClick={() => handleConnect(connector.id)}
                    disabled={connecting === connector.id}
                  >
                    {connecting === connector.id ? (
                      <span className="spinner" style={{ width: '14px', height: '14px' }} />
                    ) : (
                      'Connect'
                    )}
                  </button>
                ) : (
                  <span style={{
                    fontSize: '10px',
                    fontWeight: 800,
                    letterSpacing: '0.15em',
                    textTransform: 'uppercase' as const,
                    color: 'var(--agent-finops)',
                  }}>
                    ✓ Active
                  </span>
                )}
              </div>

              {connector.status === 'connected' && (
                <div style={{
                  marginTop: '12px',
                  padding: '8px 12px',
                  background: 'rgba(16, 185, 129, 0.08)',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: '11px',
                  color: 'var(--agent-finops)',
                  fontWeight: 600,
                }}>
                  📡 Demo mode — synthetic data with embedded anomalies
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

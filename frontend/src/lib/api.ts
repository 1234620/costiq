/**
 * CostIQ API Client — Communicates with the FastAPI backend.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface FIS {
  baseline_cost: number;
  intervention_cost: number;
  projected_savings: number;
  annualized_savings: number;
  confidence_score: number;
  formula: string;
  payback_period: string;
  audit_trail: string[];
  baseline_period: string;
  currency: string;
  notes: string | null;
}

export interface Finding {
  id: string;
  run_id: string;
  agent_type: 'spend' | 'sla' | 'resource' | 'finops';
  finding_type: string;
  title: string;
  description: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  fis: FIS;
  action_description: string;
  status: 'open' | 'approved' | 'rejected' | 'executed';
  created_at: string;
}

export interface ApprovalItem {
  approval_id: string;
  finding_id: string;
  tier: string;
  required_approvers: string[];
  decision: string;
  created_at: string;
  finding: {
    title: string;
    agent_type: string;
    savings: number;
    severity: string;
  } | null;
}

export interface AgentActivity {
  agent: string;
  action: string;
  detail: string;
  status: string;
  timestamp: string;
}

export interface Stats {
  total_findings: number;
  total_identified: number;
  total_approved: number;
  total_executed: number;
  by_agent: Record<string, { count: number; savings: number }>;
  by_severity: Record<string, number>;
}

class CostIQAPI {
  private base: string;

  constructor(baseUrl: string = API_BASE) {
    this.base = baseUrl;
  }

  private async fetch<T>(path: string, options?: RequestInit): Promise<T> {
    const res = await fetch(`${this.base}${path}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });
    return res.json();
  }

  // Analysis
  async triggerAnalysis(dataSources: string[] = ['demo']) {
    return this.fetch<{ task_id: string; status: string }>('/api/v1/analyze', {
      method: 'POST',
      body: JSON.stringify({ data_sources: dataSources }),
    });
  }

  async getAnalysisStatus(runId: string) {
    return this.fetch(`/api/v1/analyze/${runId}`);
  }

  // Findings
  async getFindings() {
    return this.fetch<{ findings: Finding[]; total: number; total_savings: number }>('/api/v1/findings');
  }

  async getFinding(id: string) {
    return this.fetch<Finding & { approvals: any[] }>(`/api/v1/findings/${id}`);
  }

  // Approvals
  async getApprovals() {
    return this.fetch<{ approvals: ApprovalItem[]; total_pending: number }>('/api/v1/approvals');
  }

  async respondToApproval(approvalId: string, decision: string, notes: string = '') {
    return this.fetch(`/api/v1/approvals/${approvalId}/respond`, {
      method: 'POST',
      body: JSON.stringify({ decision, notes, approver_id: 'demo_user' }),
    });
  }

  // Stats
  async getStats() {
    return this.fetch<Stats>('/api/v1/stats');
  }

  // Activity
  async getActivity(limit: number = 50) {
    return this.fetch<{ activity: AgentActivity[] }>(`/api/v1/activity?limit=${limit}`);
  }

  // Connectors
  async getConnectors() {
    return this.fetch<{ connectors: any[] }>('/api/v1/connectors');
  }

  async connectConnector(id: string) {
    return this.fetch(`/api/v1/connectors/${id}/connect`, { method: 'POST' });
  }

  // Health
  async health() {
    return this.fetch<{ status: string }>('/api/v1/health');
  }
}

export const api = new CostIQAPI();

// WebSocket connection
export function createWebSocket(channel: string = 'global'): WebSocket | null {
  const wsBase = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000';
  try {
    return new WebSocket(`${wsBase}/ws/${channel}`);
  } catch {
    console.warn('WebSocket connection failed');
    return null;
  }
}

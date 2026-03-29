'use client';

import { useEffect, useState } from 'react';
import Navbar from '@/components/Navbar';
import FISPanel from '@/components/FISPanel';
import { api, ApprovalItem, Finding } from '@/lib/api';

export default function ApprovalsPage() {
  const [approvals, setApprovals] = useState<ApprovalItem[]>([]);
  const [selectedApproval, setSelectedApproval] = useState<ApprovalItem | null>(null);
  const [selectedFinding, setSelectedFinding] = useState<(Finding & { approvals: any[] }) | null>(null);
  const [step, setStep] = useState(0);
  const [processing, setProcessing] = useState(false);

  useEffect(() => {
    const load = async () => {
      try {
        const res = await api.getApprovals();
        setApprovals(res.approvals || []);
      } catch {
        // API not available
      }
    };
    load();
  }, []);

  const openApproval = async (approval: ApprovalItem) => {
    setSelectedApproval(approval);
    setStep(0);
    try {
      const finding = await api.getFinding(approval.finding_id);
      setSelectedFinding(finding);
    } catch {
      // ignore
    }
  };

  const handleDecision = async (decision: 'approve' | 'reject') => {
    if (!selectedApproval) return;
    setProcessing(true);
    try {
      await api.respondToApproval(selectedApproval.approval_id, decision);
      // Refresh
      const res = await api.getApprovals();
      setApprovals(res.approvals || []);
      setSelectedApproval(null);
      setSelectedFinding(null);
      setStep(0);
    } catch {
      // ignore
    }
    setProcessing(false);
  };

  const steps = ['Finding Summary', 'Financial Impact Statement', 'Review & Approve'];

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-primary)' }}>
      <Navbar />
      <div className="page">
        <div style={{ marginBottom: '32px' }}>
          <span className="label-accent">Enterprise Approval Workflow</span>
          <h1 className="heading-1" style={{ marginTop: '8px' }}>Approvals</h1>
          <p className="body" style={{ marginTop: '8px' }}>
            {approvals.length} pending approvals
          </p>
        </div>

        {/* Approval Steps Modal */}
        {selectedApproval && selectedFinding ? (
          <div className="card" style={{ maxWidth: '800px', margin: '0 auto' }}>
            {/* Stepper */}
            <div className="stepper">
              {steps.map((s, i) => (
                <div key={s} style={{ display: 'contents' }}>
                  <div
                    className={`step-indicator ${i === step ? 'active' : i < step ? 'completed' : ''}`}
                    onClick={() => setStep(i)}
                    style={{ cursor: 'pointer' }}
                  >
                    {i < step ? '✓' : i + 1}
                  </div>
                  {i < steps.length - 1 && (
                    <div className={`step-line ${i < step ? 'completed' : ''}`} />
                  )}
                </div>
              ))}
            </div>

            <div style={{ marginBottom: '8px' }}>
              <span className="label">{steps[step]}</span>
            </div>

            {/* Step Content */}
            {step === 0 && (
              <div className="fade-in">
                <div className="glass-accent" style={{ borderRadius: 'var(--radius-lg)', padding: '20px', marginBottom: '20px' }}>
                  <span className="label-accent">
                    {selectedFinding.agent_type} Agent · {selectedFinding.finding_type}
                  </span>
                  <h3 className="heading-3" style={{ marginTop: '8px' }}>{selectedFinding.title}</h3>
                </div>
                <p className="body" style={{ lineHeight: 1.7 }}>{selectedFinding.description}</p>
                <div style={{ marginTop: '20px', display: 'flex', gap: '12px' }}>
                  <span className={`badge badge-severity-${selectedFinding.severity}`}>
                    {selectedFinding.severity}
                  </span>
                  <span className="badge badge-open">
                    Tier: {selectedApproval.tier}
                  </span>
                </div>
              </div>
            )}

            {step === 1 && (
              <div className="fade-in">
                <FISPanel fis={selectedFinding.fis} />
              </div>
            )}

            {step === 2 && (
              <div className="fade-in">
                <h3 className="heading-3" style={{ marginBottom: '16px' }}>
                  The agent will execute:
                </h3>
                <div style={{
                  background: 'var(--bg-tertiary)',
                  borderRadius: 'var(--radius-md)',
                  padding: '20px',
                  borderLeft: '3px solid var(--accent)',
                  marginBottom: '24px',
                }}>
                  <p className="mono" style={{ color: 'var(--text-primary)', lineHeight: 1.6 }}>
                    {selectedFinding.action_description}
                  </p>
                </div>

                <div style={{
                  background: 'rgba(228, 164, 189, 0.06)',
                  borderRadius: 'var(--radius-lg)',
                  padding: '20px',
                  marginBottom: '24px',
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                    <span className="label">Projected Savings</span>
                    <span style={{ fontSize: '24px', fontWeight: 900, color: 'var(--accent)' }}>
                      ${selectedFinding.fis.projected_savings.toLocaleString()}
                    </span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span className="label">Confidence</span>
                    <span style={{ fontSize: '16px', fontWeight: 700, color: 'var(--text-primary)' }}>
                      {(selectedFinding.fis.confidence_score * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>

                <div style={{ display: 'flex', gap: '16px' }}>
                  <button
                    className="btn-primary"
                    onClick={() => handleDecision('approve')}
                    disabled={processing}
                    style={{ flex: 1 }}
                  >
                    {processing ? 'Executing...' : '✅ Approve & Execute'}
                  </button>
                  <button
                    className="btn-secondary"
                    onClick={() => handleDecision('reject')}
                    disabled={processing}
                    style={{ flex: 1 }}
                  >
                    ❌ Reject
                  </button>
                </div>
              </div>
            )}

            {/* Navigation */}
            <div style={{ marginTop: '24px', display: 'flex', justifyContent: 'space-between' }}>
              <button
                className="btn-ghost"
                onClick={() => step > 0 ? setStep(step - 1) : (setSelectedApproval(null), setSelectedFinding(null))}
              >
                ← {step > 0 ? 'Back' : 'Cancel'}
              </button>
              {step < 2 && (
                <button className="btn-primary" onClick={() => setStep(step + 1)}>
                  Continue →
                </button>
              )}
            </div>
          </div>
        ) : (
          /* Approvals List */
          <div>
            {approvals.length === 0 ? (
              <div className="card" style={{ textAlign: 'center', padding: '60px' }}>
                <div style={{ fontSize: '48px', marginBottom: '16px' }}>✅</div>
                <h3 className="heading-3" style={{ marginBottom: '12px' }}>No pending approvals</h3>
                <p className="body-sm">
                  All clear! Run an analysis to generate findings that need approval.
                </p>
              </div>
            ) : (
              approvals.map((approval, i) => (
                <div
                  key={approval.approval_id}
                  className="card reveal-up"
                  style={{
                    marginBottom: '16px',
                    cursor: 'pointer',
                    animationDelay: `${i * 0.1}s`,
                  }}
                  onClick={() => openApproval(approval)}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <div>
                      <span className="label-accent">
                        {approval.finding?.agent_type || 'unknown'} Agent
                      </span>
                      <h3 className="heading-3" style={{ marginTop: '8px' }}>
                        {approval.finding?.title || 'Unknown finding'}
                      </h3>
                      <div style={{ marginTop: '8px', display: 'flex', gap: '12px' }}>
                        <span className="badge badge-open">Tier: {approval.tier}</span>
                        <span className={`badge badge-severity-${approval.finding?.severity || 'medium'}`}>
                          {approval.finding?.severity || 'medium'}
                        </span>
                      </div>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <div style={{ fontSize: '28px', fontWeight: 900, color: 'var(--accent)' }}>
                        ${((approval.finding?.savings || 0) / 1000).toFixed(0)}K
                      </div>
                      <div className="label">Projected Savings</div>
                    </div>
                  </div>
                  <div style={{ marginTop: '16px', textAlign: 'right' }}>
                    <span className="btn-primary" style={{ fontSize: '10px', padding: '8px 20px' }}>
                      Review & Decide →
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        )}
      </div>
    </div>
  );
}

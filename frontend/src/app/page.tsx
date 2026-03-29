'use client';

import Link from 'next/link';
import Navbar from '@/components/Navbar';

export default function LandingPage() {
  return (
    <main style={{ position: 'relative', minHeight: '100vh', overflow: 'hidden', background: 'var(--bg-primary)' }}>
      {/* Fluid Background */}
      <div className="fluid-bg">
        <div className="fluid-orb fluid-orb-1" />
        <div className="fluid-orb fluid-orb-2" />
        <div className="fluid-orb fluid-orb-3" />
      </div>

      <Navbar />

      {/* Hero */}
      <div
        style={{
          position: 'relative',
          zIndex: 10,
          display: 'flex',
          alignItems: 'center',
          minHeight: '100vh',
          padding: '120px 48px 48px',
        }}
      >
        <div style={{ maxWidth: '65%' }}>
          {/* Tagline */}
          <div className="reveal-up" style={{ marginBottom: '16px' }}>
            <span className="label-accent">
              AI Cost Intelligence · Enterprise Grade
            </span>
          </div>

          {/* Headline */}
          <div className="reveal-up" style={{ animationDelay: '0.1s' }}>
            <h1 className="heading-hero" style={{ marginBottom: '24px' }}>
              STOP{' '}
              <em style={{ color: 'var(--accent)', fontStyle: 'italic', fontWeight: 400 }}>
                leaking
              </em>
              <br />
              MONEY.
            </h1>
          </div>

          {/* Subtitle */}
          <div className="reveal-up" style={{ animationDelay: '0.2s' }}>
            <p className="body-lg" style={{ maxWidth: '520px', marginBottom: '48px' }}>
              Four autonomous AI agents that don&apos;t just find cost leakage —
              they plug it. With board-ready math on every dollar saved.
            </p>
          </div>

          {/* CTAs */}
          <div className="reveal-up" style={{ animationDelay: '0.3s', display: 'flex', gap: '24px', alignItems: 'center' }}>
            <Link href="/dashboard" className="btn-primary">
              See It In Action
            </Link>
            <Link
              href="/dashboard/impact"
              style={{
                fontWeight: 700,
                fontSize: '14px',
                letterSpacing: '0.1em',
                textTransform: 'uppercase' as const,
                color: 'var(--text-primary)',
                borderBottom: '2px solid var(--accent)',
                paddingBottom: '4px',
              }}
            >
              Read the Math →
            </Link>
          </div>

          {/* Stats ticker */}
          <div
            className="reveal-up"
            style={{ animationDelay: '0.5s', marginTop: '80px', display: 'flex', gap: '64px' }}
          >
            {[
              { value: '$2.4M', label: 'Avg savings identified' },
              { value: '73%', label: 'Actions auto-approved' },
              { value: '< 4min', label: 'From detection to action' },
            ].map((stat) => (
              <div key={stat.label}>
                <div style={{ fontSize: '36px', fontWeight: 900, color: 'var(--accent)' }}>
                  {stat.value}
                </div>
                <div className="label" style={{ marginTop: '4px' }}>
                  {stat.label}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Floating Badge */}
        <div
          style={{
            position: 'absolute',
            right: '10%',
            top: '50%',
            transform: 'translateY(-50%)',
            width: '160px',
            height: '160px',
            borderRadius: '50%',
            background: 'var(--accent)',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            animation: 'bounce-slow 4s ease-in-out infinite',
            boxShadow: '0 0 60px rgba(228, 164, 189, 0.3)',
          }}
        >
          <span style={{ fontSize: '40px', fontStyle: 'italic', fontWeight: 400, color: '#080808', lineHeight: 1 }}>
            04
          </span>
          <span
            style={{
              fontSize: '8px',
              fontWeight: 900,
              letterSpacing: '0.2em',
              textTransform: 'uppercase' as const,
              color: '#080808',
              marginTop: '4px',
            }}
          >
            Agents
          </span>
        </div>
      </div>

      {/* Features Section */}
      <section
        style={{
          position: 'relative',
          zIndex: 10,
          padding: '100px 48px',
          borderTop: '1px solid var(--border)',
        }}
      >
        <div className="reveal-up" style={{ textAlign: 'center', marginBottom: '64px' }}>
          <span className="label-accent">How It Works</span>
          <h2 className="heading-1" style={{ marginTop: '16px' }}>
            Four Agents.{' '}
            <em style={{ color: 'var(--accent)', fontWeight: 400, fontStyle: 'italic' }}>
              One Mission.
            </em>
          </h2>
        </div>

        <div className="grid-3" style={{ maxWidth: '1200px', margin: '0 auto' }}>
          {[
            {
              icon: '💰',
              title: 'Spend Intelligence',
              color: 'var(--agent-spend)',
              desc: 'Detects duplicate invoices, rate creep, vendor overcharges. Every finding includes exact formulas and contract references.',
            },
            {
              icon: '⚡',
              title: 'SLA Prevention',
              color: 'var(--agent-sla)',
              desc: 'Predicts SLA breaches using probabilistic models. Calculates expected loss and intervention ROI before taking action.',
            },
            {
              icon: '☁️',
              title: 'Resource Optimization',
              color: 'var(--agent-resource)',
              desc: 'Identifies overprovisioned cloud instances, unused SaaS licenses, and Reserved Instance savings opportunities.',
            },
            {
              icon: '📊',
              title: 'Financial Operations',
              color: 'var(--agent-finops)',
              desc: 'Variance decomposition (volume/rate/mix), transaction reconciliation, and accrual management.',
            },
            {
              icon: '🔐',
              title: 'Approval Workflows',
              color: 'var(--accent)',
              desc: '4-tier approval routing: auto → manager → director → C-suite. Every action requires human sign-off above threshold.',
            },
            {
              icon: '📐',
              title: 'The Math',
              color: 'var(--accent)',
              desc: 'Every finding produces a Financial Impact Statement with baseline, formula, confidence score, and full audit trail.',
            },
          ].map((feature, i) => (
            <div
              key={feature.title}
              className="card reveal-up"
              style={{ animationDelay: `${i * 0.1}s` }}
            >
              <div style={{ fontSize: '36px', marginBottom: '16px' }}>{feature.icon}</div>
              <h3 className="heading-3" style={{ marginBottom: '12px', color: feature.color }}>
                {feature.title}
              </h3>
              <p className="body-sm">{feature.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA Section */}
      <section
        style={{
          position: 'relative',
          zIndex: 10,
          padding: '100px 48px',
          textAlign: 'center',
          borderTop: '1px solid var(--border)',
        }}
      >
        <div className="reveal-up">
          <h2 className="heading-1" style={{ marginBottom: '24px' }}>
            Ready to stop{' '}
            <em style={{ color: 'var(--accent)', fontWeight: 400, fontStyle: 'italic' }}>
              leaking
            </em>{' '}
            money?
          </h2>
          <p className="body-lg" style={{ maxWidth: '500px', margin: '0 auto 40px' }}>
            Other tools show dashboards. CostIQ shows math and takes action.
          </p>
          <Link href="/dashboard" className="btn-primary" style={{ fontSize: '14px', padding: '16px 40px' }}>
            Launch CostIQ →
          </Link>
        </div>
      </section>
    </main>
  );
}

'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

const navLinks = [
  { href: '/dashboard', label: 'Dashboard' },
  { href: '/dashboard/findings', label: 'Findings' },
  { href: '/dashboard/approvals', label: 'Approvals' },
  { href: '/dashboard/connectors', label: 'Connectors' },
  { href: '/dashboard/impact', label: 'Impact' },
];

export default function Navbar() {
  const pathname = usePathname();

  return (
    <nav className="nav">
      <Link href="/" className="nav-logo">
        COST<span>IQ</span>
      </Link>

      <div className="nav-links">
        {navLinks.map((link) => (
          <Link
            key={link.href}
            href={link.href}
            className={`nav-link ${pathname === link.href ? 'active' : ''}`}
          >
            {link.label}
          </Link>
        ))}
      </div>

      <Link href="/dashboard" className="btn-primary" style={{ fontSize: '10px', padding: '10px 22px' }}>
        Launch Platform
      </Link>
    </nav>
  );
}

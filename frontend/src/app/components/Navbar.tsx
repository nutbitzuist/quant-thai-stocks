'use client';

import Link from 'next/link';

// Dynamic import for Clerk components
let useAuth: any = () => ({ isSignedIn: false, isLoaded: true });
let UserButton: any = () => null;

// Try to import Clerk if available
try {
  const clerk = require('@clerk/nextjs');
  if (process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY) {
    useAuth = clerk.useAuth;
    UserButton = clerk.UserButton;
  }
} catch {
  // Clerk not available, use defaults
}

export default function Navbar() {
  let isSignedIn = false;
  let isLoaded = true;

  // Only use Clerk hooks if configured
  if (process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY) {
    try {
      const auth = useAuth();
      isSignedIn = auth.isSignedIn;
      isLoaded = auth.isLoaded;
    } catch {
      // Clerk context not available
    }
  }

  return (
    <nav style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      zIndex: 1000,
      background: 'var(--card)',
      borderBottom: '3px solid var(--border)',
      padding: '1rem 2rem',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
    }}>
      {/* Logo */}
      <Link href="/" style={{ textDecoration: 'none' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{
            width: '40px',
            height: '40px',
            background: 'var(--primary)',
            border: '3px solid var(--border)',
            boxShadow: '3px 3px 0 var(--border)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontWeight: '900',
            fontSize: '1.25rem',
            color: 'var(--primary-foreground)',
          }}>
            Q
          </div>
          <span style={{
            fontWeight: '800',
            fontSize: '1.25rem',
            color: 'var(--foreground)',
            letterSpacing: '-0.02em',
          }}>
            QuantStack
          </span>
        </div>
      </Link>

      {/* Navigation Links */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '2rem' }}>
        <Link href="#features" style={{
          textDecoration: 'none',
          color: 'var(--foreground)',
          fontWeight: '600',
          fontSize: '0.9rem',
        }}>
          Features
        </Link>
        <Link href="#models" style={{
          textDecoration: 'none',
          color: 'var(--foreground)',
          fontWeight: '600',
          fontSize: '0.9rem',
        }}>
          Models
        </Link>
        <Link href="#pricing" style={{
          textDecoration: 'none',
          color: 'var(--foreground)',
          fontWeight: '600',
          fontSize: '0.9rem',
        }}>
          Pricing
        </Link>
      </div>

      {/* Auth Buttons */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        {!isLoaded ? (
          <div style={{ width: '120px' }} />
        ) : isSignedIn ? (
          <>
            <Link href="/dashboard" style={{
              textDecoration: 'none',
              padding: '0.625rem 1.25rem',
              background: 'var(--card)',
              color: 'var(--foreground)',
              border: '3px solid var(--border)',
              boxShadow: '3px 3px 0 var(--border)',
              fontWeight: '700',
              fontSize: '0.9rem',
              cursor: 'pointer',
              transition: 'transform 0.1s ease, box-shadow 0.1s ease',
            }}>
              Dashboard
            </Link>
            {process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY && (
              <UserButton
                afterSignOutUrl="/"
                appearance={{
                  elements: {
                    avatarBox: {
                      width: '40px',
                      height: '40px',
                      border: '3px solid var(--border)',
                      boxShadow: '3px 3px 0 var(--border)',
                    }
                  }
                }}
              />
            )}
          </>
        ) : (
          <>
            <Link href="/sign-in" style={{
              textDecoration: 'none',
              color: 'var(--foreground)',
              fontWeight: '600',
              fontSize: '0.9rem',
            }}>
              Sign In
            </Link>
            <Link href="/sign-up" style={{
              textDecoration: 'none',
              padding: '0.625rem 1.5rem',
              background: 'var(--primary)',
              color: 'var(--primary-foreground)',
              border: '3px solid var(--border)',
              boxShadow: '4px 4px 0 var(--border)',
              fontWeight: '700',
              fontSize: '0.9rem',
              cursor: 'pointer',
              transition: 'transform 0.1s ease, box-shadow 0.1s ease',
            }}>
              Get Started Free
            </Link>
          </>
        )}
      </div>
    </nav>
  );
}


'use client';

import React, { useState } from 'react';
import { useAuth, useUser } from '@clerk/nextjs';
import { API_URL } from '@/types/dashboard';

interface UpgradeButtonProps {
    priceId: string;
    className?: string;
    children?: React.ReactNode;
}

export function UpgradeButton({ priceId, className = "", children }: UpgradeButtonProps) {
    const { getToken } = useAuth();
    const { user } = useUser();
    const [loading, setLoading] = useState(false);

    const handleUpgrade = async () => {
        if (!user) {
            // Redirect to login if not authenticated
            window.location.href = '/sign-in';
            return;
        }

        try {
            setLoading(true);
            const token = await getToken();

            const res = await fetch(`${API_URL}/api/billing/checkout`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                    'X-User-ID': user.id
                },
                body: JSON.stringify({
                    price_id: priceId,
                    user_email: user.primaryEmailAddress?.emailAddress,
                    success_url: `${window.location.origin}/dashboard?success=true`,
                    cancel_url: `${window.location.origin}/pricing?canceled=true`
                })
            });

            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.detail || 'Failed to create checkout');
            }

            const data = await res.json();
            if (data.url) {
                window.location.href = data.url;
            }
        } catch (error) {
            console.error('Upgrade failed:', error);
            alert('Failed to start upgrade. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <button
            onClick={handleUpgrade}
            disabled={loading}
            className={`px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded transition-colors disabled:opacity-50 ${className}`}
        >
            {loading ? 'Redirecting...' : (children || 'Upgrade to Pro')}
        </button>
    );
}

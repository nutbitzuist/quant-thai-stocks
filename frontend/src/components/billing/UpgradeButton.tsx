
'use client';

import React, { useState } from 'react';
import { useAuth } from '@clerk/nextjs';
import { API_URL } from '@/types/dashboard';

interface UpgradeButtonProps {
    variantId: string;
    className?: string;
    children?: React.ReactNode;
}

export function UpgradeButton({ variantId, className = "", children }: UpgradeButtonProps) {
    const { getToken, user } = useAuth();
    const [loading, setLoading] = useState(false);

    const handleUpgrade = async () => {
        if (!user) return;

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
                    variant_id: variantId,
                    user_email: user.primaryEmailAddress?.emailAddress,
                    user_name: user.fullName
                })
            });

            if (!res.ok) throw new Error('Failed to create checkout');

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
            {loading ? 'Process...' : (children || 'Upgrade to Pro')}
        </button>
    );
}

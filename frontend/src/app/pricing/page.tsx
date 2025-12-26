
import React from 'react';
import { UpgradeButton } from '@/components/billing/UpgradeButton';

// Replace with your actual LemonSqueezy Variant IDs
const PRO_VARIANT_ID = "123456";

export default function PricingPage() {
    return (
        <div className="min-h-screen bg-gray-900 text-white py-20 px-4">
            <div className="max-w-5xl mx-auto text-center">
                <h1 className="text-4xl font-bold mb-4">Simple, Transparent Pricing</h1>
                <p className="text-xl text-gray-400 mb-12">Unlock the full power of quantitative analysis.</p>

                <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
                    {/* Free Plan */}
                    <div className="bg-gray-800 p-8 rounded-2xl border border-gray-700 flex flex-col">
                        <h3 className="text-2xl font-semibold mb-2">Basic</h3>
                        <div className="text-4xl font-bold mb-6">$0</div>
                        <ul className="text-left space-y-4 mb-8 flex-grow">
                            <li className="flex items-center">✓ 5 Scans per day</li>
                            <li className="flex items-center">✓ Standard Models</li>
                            <li className="flex items-center">✓ Daily updates</li>
                        </ul>
                        <button className="w-full py-3 rounded-lg bg-gray-700 text-gray-300 cursor-not-allowed">
                            Current Plan
                        </button>
                    </div>

                    {/* Pro Plan */}
                    <div className="bg-gray-800 p-8 rounded-2xl border-2 border-blue-500 relative flex flex-col">
                        <div className="absolute top-0 right-0 bg-blue-500 text-xs font-bold px-3 py-1 rounded-bl-lg rounded-tr-lg">
                            POPULAR
                        </div>
                        <h3 className="text-2xl font-semibold mb-2">Pro Analyst</h3>
                        <div className="text-4xl font-bold mb-6">$29<span className="text-lg text-gray-400 font-normal">/mo</span></div>
                        <ul className="text-left space-y-4 mb-8 flex-grow">
                            <li className="flex items-center">✓ Unlimited Scans</li>
                            <li className="flex items-center">✓ Advanced ML Models</li>
                            <li className="flex items-center">✓ Real-time Analysis</li>
                            <li className="flex items-center">✓ API Access</li>
                        </ul>
                        <UpgradeButton
                            variantId={PRO_VARIANT_ID}
                            className="w-full py-3 rounded-lg bg-blue-600 hover:bg-blue-700 font-semibold"
                        >
                            Upgrade Now
                        </UpgradeButton>
                    </div>
                </div>
            </div>
        </div>
    );
}

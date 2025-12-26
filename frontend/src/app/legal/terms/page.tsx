
import React from 'react';

export default function TermsPage() {
    return (
        <div className="container mx-auto py-12 px-4 max-w-4xl">
            <h1 className="text-3xl font-bold mb-8">Terms of Service</h1>
            <div className="prose dark:prose-invert">
                <p className="mb-4">Last updated: {new Date().toLocaleDateString()}</p>

                <h2 className="text-xl font-semibold mt-6 mb-4">1. Acceptance of Terms</h2>
                <p>By accessing or using our services, you agree to be bound by these Terms of Service.</p>

                <h2 className="text-xl font-semibold mt-6 mb-4">2. Description of Service</h2>
                <p>Quant Thai Stocks provides financial analysis tools and data. We do not provide financial advice. All investment decisions are your own responsibility.</p>

                <h2 className="text-xl font-semibold mt-6 mb-4">3. User Accounts</h2>
                <p>You are responsible for safeguarding the password that you use to access the service and for any activities or actions under your password.</p>

                <h2 className="text-xl font-semibold mt-6 mb-4">4. Payment Terms</h2>
                <p>Services are billed in advance on a subscription basis. You may cancel your subscription at any time.</p>

                <h2 className="text-xl font-semibold mt-6 mb-4">5. Limitation of Liability</h2>
                <p>In no event shall Quant Thai Stocks be liable for any indirect, incidental, special, consequential or punitive damages.</p>
            </div>
        </div>
    );
}

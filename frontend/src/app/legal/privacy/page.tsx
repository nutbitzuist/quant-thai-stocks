
import React from 'react';

export default function PrivacyPage() {
    return (
        <div className="container mx-auto py-12 px-4 max-w-4xl">
            <h1 className="text-3xl font-bold mb-8">Privacy Policy</h1>
            <div className="prose dark:prose-invert">
                <p className="mb-4">Last updated: {new Date().toLocaleDateString()}</p>

                <h2 className="text-xl font-semibold mt-6 mb-4">1. Information We Collect</h2>
                <p>We collect information you provide directly to us, such as when you create an account, subscribe to our services, or communicate with us. This may include your name, email address, and payment information.</p>

                <h2 className="text-xl font-semibold mt-6 mb-4">2. How We Use Your Information</h2>
                <p>We use the information we collect to provide, maintain, and improve our services, process transactions, and communicate with you.</p>

                <h2 className="text-xl font-semibold mt-6 mb-4">3. Data Security</h2>
                <p>We implement appropriate technical and organizational measures to protect your personal data against unauthorized access, alteration, disclosure, or destruction.</p>

                <h2 className="text-xl font-semibold mt-6 mb-4">4. Contact Us</h2>
                <p>If you have any questions about this Privacy Policy, please contact us at support@quantthaistocks.com.</p>
            </div>
        </div>
    );
}


import React from 'react';

export default function ContactPage() {
    return (
        <div className="min-h-screen bg-gray-900 text-white py-20 px-4">
            <div className="max-w-2xl mx-auto">
                <h1 className="text-3xl font-bold mb-8">Contact Support</h1>

                <div className="bg-gray-800 p-8 rounded-2xl border border-gray-700">
                    <p className="text-gray-300 mb-6">
                        Have questions about your subscription, a bug report, or feature request?
                        We're here to help.
                    </p>

                    <div className="space-y-6">
                        <div>
                            <h3 className="text-lg font-semibold mb-2">Email Support</h3>
                            <a
                                href="mailto:support@quantthaistocks.com"
                                className="text-blue-400 hover:text-blue-300 text-xl"
                            >
                                support@quantthaistocks.com
                            </a>
                            <p className="text-sm text-gray-500 mt-1">Typical response time: 24-48 hours</p>
                        </div>

                        <div className="border-t border-gray-700 pt-6">
                            <h3 className="text-lg font-semibold mb-2">General Inquiries</h3>
                            <p className="text-gray-400">
                                For partnerships or enterprise access, please mention "Enterprise" in your subject line.
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

import { SignIn } from "@clerk/nextjs";

export default function SignInPage() {
    return (
        <div style={{
            minHeight: '100vh',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: 'var(--background)',
            padding: '2rem',
        }}>
            <div style={{
                background: 'var(--card)',
                padding: '2rem',
                border: '3px solid var(--border)',
                boxShadow: '6px 6px 0 var(--border)',
            }}>
                <SignIn
                    appearance={{
                        elements: {
                            rootBox: {
                                boxShadow: 'none',
                            },
                            card: {
                                border: 'none',
                                boxShadow: 'none',
                                background: 'transparent',
                            },
                            headerTitle: {
                                fontWeight: '800',
                                fontFamily: 'var(--font-sans)',
                            },
                            headerSubtitle: {
                                fontFamily: 'var(--font-sans)',
                            },
                            formButtonPrimary: {
                                background: 'var(--primary)',
                                border: '3px solid var(--border)',
                                boxShadow: '4px 4px 0 var(--border)',
                                borderRadius: '0',
                                fontWeight: '700',
                                textTransform: 'none',
                                transition: 'transform 0.1s ease, box-shadow 0.1s ease',
                            },
                            formFieldInput: {
                                border: '3px solid var(--border)',
                                borderRadius: '0',
                                boxShadow: '3px 3px 0 var(--border)',
                            },
                            footerActionLink: {
                                color: 'var(--primary)',
                                fontWeight: '600',
                            },
                            identityPreviewEditButton: {
                                color: 'var(--primary)',
                            },
                        },
                    }}
                />
            </div>
        </div>
    );
}

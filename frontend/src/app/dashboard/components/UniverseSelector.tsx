'use client';

import { useState, useEffect } from 'react';
import { Universe, CustomUniverse } from '@/types/dashboard';
import { S, getMarketIcon } from '../styles';

interface UniverseSelectorProps {
    current: string;
    universes: Universe[];
    customUniverses: CustomUniverse[];
    onChange: (id: string) => void;
    sidebarCollapsed: boolean;
}

export function UniverseSelector({
    current,
    universes,
    customUniverses,
    onChange,
    sidebarCollapsed
}: UniverseSelectorProps) {
    const [isOpen, setIsOpen] = useState(false);
    const selected = universes.find(u => u.id === current) ||
        customUniverses.find(u => u.id === current) ||
        universes[0];

    useEffect(() => {
        const close = () => setIsOpen(false);
        if (isOpen) window.addEventListener('click', close);
        return () => window.removeEventListener('click', close);
    }, [isOpen]);

    if (sidebarCollapsed) {
        return (
            <div
                style={{ textAlign: 'center', cursor: 'pointer' }}
                onClick={() => setIsOpen(!isOpen)}
                title={`Universe: ${selected?.name}`}
            >
                <span style={{ fontSize: '1.2rem' }}>{getMarketIcon(selected?.market || '')}</span>
            </div>
        );
    }

    return (
        <div style={{ position: 'relative' }} onClick={e => e.stopPropagation()}>
            <button
                onClick={() => setIsOpen(!isOpen)}
                style={{
                    ...S.select,
                    width: '100%',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    cursor: 'pointer',
                    textAlign: 'left'
                }}
            >
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', overflow: 'hidden' }}>
                    <span style={{ fontSize: '1.2rem' }}>{getMarketIcon(selected?.market || '')}</span>
                    <div style={{ display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
                        <span style={{ fontWeight: '600', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                            {selected?.name || 'Select Universe'}
                        </span>
                        <span style={{ fontSize: '10px', color: 'var(--muted-foreground)' }}>
                            {selected?.count || 0} companies
                        </span>
                    </div>
                </div>
                <span style={{ fontSize: '0.7rem', color: 'var(--muted-foreground)' }}>▼</span>
            </button>

            {isOpen && (
                <div style={{
                    position: 'absolute',
                    top: '100%',
                    left: 0,
                    width: '300px',
                    maxHeight: '400px',
                    overflowY: 'auto',
                    background: 'var(--card)',
                    color: 'var(--card-foreground)',
                    border: '3px solid var(--border)',
                    borderRadius: '0',
                    boxShadow: '4px 4px 0 var(--border)',
                    marginTop: '5px',
                    zIndex: 50,
                    padding: '8px',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '4px'
                }}>
                    <div style={{ padding: '8px 12px', fontSize: '0.75rem', fontWeight: 'bold', color: 'var(--muted-foreground)', textTransform: 'uppercase' }}>
                        Built-in Universes
                    </div>
                    {universes.map(u => (
                        <UniverseItem
                            key={u.id}
                            universe={u}
                            isSelected={u.id === current}
                            onClick={() => { onChange(u.id); setIsOpen(false); }}
                        />
                    ))}

                    {customUniverses.length > 0 && (
                        <>
                            <div style={{ padding: '8px 12px', fontSize: '0.75rem', fontWeight: 'bold', color: 'var(--muted-foreground)', textTransform: 'uppercase', marginTop: '8px' }}>
                                Custom Universes
                            </div>
                            {customUniverses.map(u => (
                                <UniverseItem
                                    key={u.id}
                                    universe={{ ...u, market: 'Custom' }}
                                    isSelected={u.id === current}
                                    onClick={() => { onChange(u.id); setIsOpen(false); }}
                                />
                            ))}
                        </>
                    )}
                </div>
            )}
        </div>
    );
}

interface UniverseItemProps {
    universe: { id: string; name: string; market: string; count?: number };
    isSelected: boolean;
    onClick: () => void;
}

function UniverseItem({ universe, isSelected, onClick }: UniverseItemProps) {
    return (
        <div
            onClick={onClick}
            style={{
                padding: '10px',
                borderRadius: 'var(--radius)',
                cursor: 'pointer',
                background: isSelected ? 'var(--muted)' : 'transparent',
                display: 'flex',
                alignItems: 'center',
                gap: '10px',
                transition: 'background 0.2s',
                border: isSelected ? '1px solid var(--primary)' : '1px solid transparent'
            }}
            onMouseEnter={e => e.currentTarget.style.background = 'var(--muted)'}
            onMouseLeave={e => e.currentTarget.style.background = isSelected ? 'var(--muted)' : 'transparent'}
        >
            <div style={{ fontSize: '1.5rem' }}>{getMarketIcon(universe.market)}</div>
            <div style={{ flex: 1 }}>
                <div style={{ fontWeight: '600', fontSize: '0.9rem' }}>{universe.name}</div>
                <div style={{ fontSize: '0.8rem', color: 'var(--muted-foreground)' }}>
                    <span style={{ color: 'var(--primary)', fontWeight: 'bold' }}>{universe.count || 0}</span> companies
                </div>
            </div>
            {isSelected && <div style={{ marginLeft: 'auto', color: 'var(--primary)' }}>✓</div>}
        </div>
    );
}

export default UniverseSelector;

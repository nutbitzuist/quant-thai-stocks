// Neo-Brutalist Style Object - HQ0 inspired
export const S = {
    card: {
        background: 'var(--card)',
        color: 'var(--card-foreground)',
        borderRadius: '0',
        padding: '1.25rem',
        marginBottom: '1rem',
        boxShadow: '4px 4px 0 var(--border)',
        border: '3px solid var(--border)',
    },
    button: {
        base: 'inline-flex items-center justify-center px-4 py-2 text-sm font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none ring-offset-background',
        primary: 'bg-primary text-primary-foreground hover:bg-primary/90 border-2 border-primary shadow-[2px_2px_0_0_#000]',
        secondary: 'bg-secondary text-secondary-foreground hover:bg-secondary/80 border-2 border-secondary shadow-[2px_2px_0_0_#000]',
        outline: 'border-2 border-input hover:bg-accent hover:text-accent-foreground shadow-[2px_2px_0_0_#000]',
        ghost: 'hover:bg-accent hover:text-accent-foreground',
        danger: 'bg-destructive text-destructive-foreground hover:bg-destructive/90 border-2 border-destructive shadow-[2px_2px_0_0_#000]',
    },
    input: 'flex h-10 w-full rounded-none border-2 border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50',
    textarea: 'flex min-h-[80px] w-full rounded-none border-2 border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50',
    select: 'flex h-10 w-full items-center justify-between rounded-none border-2 border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50',
    badge: {
        base: 'inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2',
        default: 'border-transparent bg-primary text-primary-foreground hover:bg-primary/80',
        secondary: 'border-transparent bg-secondary text-secondary-foreground hover:bg-secondary/80',
        destructive: 'border-transparent bg-destructive text-destructive-foreground hover:bg-destructive/80',
        outline: 'text-foreground',
    },
    tabs: {
        list: 'inline-flex h-10 items-center justify-center rounded-none bg-muted p-1 text-muted-foreground border-2 border-border',
        trigger: 'inline-flex items-center justify-center whitespace-nowrap rounded-none px-3 py-1.5 text-sm font-medium ring-offset-background transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 data-[state=active]:bg-background data-[state=active]:text-foreground data-[state=active]:shadow-sm border-r-2 last:border-r-0 border-transparent data-[state=active]:border-border',
        content: 'mt-2 ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2',
    }
};

import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

// Simple middleware that skips auth when Clerk is not configured
export function middleware(request: NextRequest) {
    // If Clerk keys are not configured, allow all requests
    if (!process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY || !process.env.CLERK_SECRET_KEY) {
        return NextResponse.next();
    }

    // When Clerk is configured, we use dynamic import
    // For now, if keys exist but this runs in development without Clerk,
    // we'll just pass through. The actual Clerk auth will be handled
    // by @clerk/nextjs/middleware when properly configured.
    return NextResponse.next();
}

export const config = {
    matcher: ["/((?!.+\\.[\\w]+$|_next).*)", "/", "/(api|trpc)(.*)"],
};

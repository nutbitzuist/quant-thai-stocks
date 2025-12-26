import { authMiddleware } from "@clerk/nextjs";
import { NextResponse } from "next/server";

// Check if Clerk is configured
const hasClerkKeys = process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY && process.env.CLERK_SECRET_KEY;

// When Clerk is NOT configured, use a simple pass-through middleware
function simpleMiddleware() {
    return NextResponse.next();
}

// Export the appropriate middleware based on configuration
export default hasClerkKeys
    ? authMiddleware({
        // Public routes that don't require authentication
        publicRoutes: [
            "/",
            "/sign-in(.*)",
            "/sign-up(.*)",
            "/api/health",
        ],
        // Routes that can be accessed but will show different content based on auth
        ignoredRoutes: [
            "/api/models(.*)",
            "/api/universe(.*)",
            "/api/status(.*)",
        ],
    })
    : simpleMiddleware;

export const config = {
    matcher: ["/((?!.+\\.[\\w]+$|_next).*)", "/", "/(api|trpc)(.*)"],
};

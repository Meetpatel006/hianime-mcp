# Aniwatch Implementation Details

This document provides a deep dive into the implementation details of the Aniwatch ecosystem, including code examples and technical explanations of how various features are implemented.

## Table of Contents
- [Core Package Implementation](#core-package-implementation)
  - [Scraper Class Structure](#scraper-class-structure)
  - [HTML Parsing with Cheerio](#html-parsing-with-cheerio)
  - [Type System Implementation](#type-system-implementation)
  - [Error Handling](#error-handling)
  - [Video Source Extraction](#video-source-extraction)
- [API Implementation](#api-implementation)
  - [Server Setup](#server-setup)
  - [Route Definitions](#route-definitions)
  - [Caching Mechanism](#caching-mechanism)
  - [Rate Limiting Implementation](#rate-limiting-implementation)
  - [Error Handling Middleware](#error-handling-middleware)
- [Testing Strategy](#testing-strategy)
- [Common Implementation Patterns](#common-implementation-patterns)
- [Performance Optimizations](#performance-optimizations)

## Core Package Implementation

### Scraper Class Structure

The core of the aniwatch package is the `Scraper` class in `src/hianime/hianime.ts`, which provides a clean API for all scraping operations. Below is a simplified version of how the class is structured:

```typescript
// src/hianime/hianime.ts
class Scraper {
    /**
     * Get detailed information about an anime
     * @param {string} animeId - unique anime id
     * @throws {HiAnimeError}
     */
    async getInfo(animeId: string) {
        return getAnimeAboutInfo(animeId);
    }
    
    /**
     * Get anime by category
     * @param {string} category - anime category
     * @param {number} page - page number, defaults to 1
     * @throws {HiAnimeError}
     */
    async getCategory(category: AnimeCategories, page: number = 1) {
        return getAnimeCategory(category, page);
    }
    
    // Additional methods for other scraping operations...
}
```

Each method in the Scraper class delegates to a specialized scraper function, following the Single Responsibility Principle. This design allows for better code organization and testability.

### HTML Parsing with Cheerio

The package uses Cheerio for HTML parsing, which provides a jQuery-like API for server-side HTML manipulation. Here's an example of how HTML is parsed to extract anime information:

```typescript
// Example from a scraper implementation
async function getAnimeAboutInfo(animeId: string): Promise<AnimeInfo> {
    try {
        const url = `${BASE_URL}/anime/${animeId}`;
        const { data } = await client.get<string>(url);
        
        const $ = cheerio.load(data);
        
        // Extract basic info
        const title = $('.anime-info h1').text().trim();
        const japaneseTitle = $('.anime-info .japanese').text().trim();
        const poster = $('.anime-poster img').attr('src') || null;
        
        // Extract detailed info
        const description = $('.anime-description p').text().trim();
        const type = $('.anime-info .type a').text().trim();
        
        // ... extract additional fields
        
        return {
            id: animeId,
            name: title,
            jname: japaneseTitle,
            poster,
            description,
            type,
            // ... other fields
        };
    } catch (error) {
        // Error handling
        throw new HiAnimeError(
            `Failed to get anime info for ${animeId}`,
            error instanceof Error ? error : new Error(String(error))
        );
    }
}
```

### Type System Implementation

TypeScript is used extensively to define the structure of data. Here's an example of how anime types are defined:

```typescript
// src/hianime/types/anime.ts
export type Anime = {
    id: string | null;
    name: string | null;
    jname: string | null;
    poster: string | null;
    duration: string | null;
    type: string | null;
    rating: string | null;
    episodes: {
        sub: number | null;
        dub: number | null;
    };
};

export type AnimeGeneralAboutInfo = Pick<Anime, CommonAnimeProps> &
    Pick<SpotlightAnime, "description"> & {
    japaneseTitle: string | null;
    type: string | null;
    episodes: number | null;
    status: string | null;
    year: number | null;
    season: string | null;
    studios: string[] | null;
    genres: Array<{
        id: string | null;
        name: string | null;
    }> | null;
    producers: Array<{
        id: string | null;
        name: string | null;
    }> | null;
    externalLinks: Array<{
        site: string | null;
        url: string | null;
    }> | null;
    otherInfo: Array<string>;
};

// Additional type definitions...
```

### Error Handling

The package implements a custom error system to provide meaningful error messages and maintain context:

```typescript
// src/hianime/error.ts
export class HiAnimeError extends Error {
    public readonly originalError?: Error;

    constructor(message: string, originalError?: Error) {
        super(message);
        this.name = 'HiAnimeError';
        this.originalError = originalError;
        
        // Preserve stack trace
        if (Error.captureStackTrace) {
            Error.captureStackTrace(this, HiAnimeError);
        }
    }
    
    /**
     * Get the full error chain as a string
     */
    public getFullErrorMessage(): string {
        if (!this.originalError) return this.message;
        
        if (this.originalError instanceof HiAnimeError) {
            return `${this.message} -> ${this.originalError.getFullErrorMessage()}`;
        }
        
        return `${this.message} -> ${this.originalError.message}`;
    }
}
```

### Video Source Extraction

The package includes specialized extractors for different video hosting providers. Here's a simplified example of how video sources are extracted:

```typescript
// src/extractors/megacloud.ts
export async function extractMegacloudSources(
    serverUrl: string,
    options: ExtractorOptions = {}
): Promise<VideoSource[]> {
    try {
        const { data } = await client.get<string>(serverUrl);
        
        // Extract key information from the page
        const videoKey = extractKey(data);
        const encryptedData = extractEncryptedData(data);
        
        // Decrypt the video source data
        const decryptedData = decrypt(encryptedData, videoKey);
        const sourceData = JSON.parse(decryptedData);
        
        // Format the sources
        return sourceData.sources.map(source => ({
            url: source.file,
            quality: parseQuality(source.label),
            isM3U8: source.file.includes('.m3u8')
        }));
    } catch (error) {
        throw new ExtractorError(
            `Failed to extract MegaCloud sources: ${error instanceof Error ? error.message : String(error)}`
        );
    }
}

// Helper functions for extraction and decryption
function extractKey(html: string): string {
    // Implementation of key extraction
}

function extractEncryptedData(html: string): string {
    // Implementation of encrypted data extraction
}

function decrypt(data: string, key: string): string {
    // Implementation of decryption algorithm
}
```

## API Implementation

### Server Setup

The API server is built with Hono.js, setting up middleware, routes, and error handling:

```typescript
// src/server.ts
import { Hono } from "hono";
import { serve } from "@hono/node-server";
import { serveStatic } from "@hono/node-server/serve-static";

import { corsConfig } from "./config/cors.js";
import { ratelimit } from "./config/ratelimit.js";
import { errorHandler } from "./config/errorHandler.js";
import { hianimeRouter } from "./routes/hianime.js";
import { logging } from "./middleware/logging.js";
import { cacheControl } from "./middleware/cache.js";

const BASE_PATH = "/api/v2" as const;
const app = new Hono();

// Apply middleware
app.use(logging);
app.use(corsConfig);
app.use(cacheControl);

// Apply rate limiting if configured
const isPersonalDeployment = Boolean(process.env.ANIWATCH_API_HOSTNAME);
if (isPersonalDeployment) {
    app.use(ratelimit);
}

// Serve static files
app.use("/", serveStatic({ root: "public" }));

// Health check endpoint
app.get("/health", (c) => c.text("daijoubu", { status: 200 }));

// API routes
app.route(BASE_PATH + "/hianime", hianimeRouter);

// Error handling
app.notFound(errorHandler.notFound);
app.onError(errorHandler.serverError);

// Start server
const PORT = process.env.PORT || 3000;
serve({ fetch: app.fetch, port: Number(PORT) }, (info) => {
    console.log(`Server running at http://localhost:${info.port}`);
});
```

### Route Definitions

The API routes are defined in separate files, mapping HTTP endpoints to the core package functionality:

```typescript
// src/routes/hianime.ts
import { Hono } from "hono";
import { HiAnime } from "aniwatch";
import { cache } from "../config/cache.js";

const hianime = new HiAnime.Scraper();
const hianimeRouter = new Hono();

// GET /api/v2/hianime/home
hianimeRouter.get("/home", async (c) => {
    const cacheConfig = c.get("CACHE_CONFIG");
    
    const data = await cache.getOrSet(
        hianime.getHomePage,
        cacheConfig.key,
        cacheConfig.duration
    );
    
    return c.json({ status: 200, data }, { status: 200 });
});

// GET /api/v2/hianime/info/:animeId
hianimeRouter.get("/info/:animeId", async (c) => {
    const cacheConfig = c.get("CACHE_CONFIG");
    const animeId = decodeURIComponent(c.req.param("animeId").trim());
    
    const data = await cache.getOrSet(
        async () => hianime.getInfo(animeId),
        cacheConfig.key,
        cacheConfig.duration
    );
    
    return c.json({ status: 200, data }, { status: 200 });
});

// Additional routes...
```

### Caching Mechanism

The API implements a caching mechanism to improve performance and reduce load on the target website:

```typescript
// src/config/cache.ts
type CacheItem<T> = {
    data: T;
    expiry: number;
};

class Cache {
    private cache: Map<string, CacheItem<any>> = new Map();
    
    /**
     * Get item from cache or set it if not found
     */
    async getOrSet<T>(
        fn: () => Promise<T>,
        key: string,
        duration: number = 60 * 60 // 1 hour default
    ): Promise<T> {
        const now = Date.now();
        const cached = this.cache.get(key);
        
        // Return from cache if valid
        if (cached && cached.expiry > now) {
            return cached.data;
        }
        
        // Otherwise, call the function and cache the result
        const data = await fn();
        
        this.cache.set(key, {
            data,
            expiry: now + (duration * 1000)
        });
        
        return data;
    }
    
    /**
     * Clear expired cache items
     */
    clearExpired(): void {
        const now = Date.now();
        for (const [key, item] of this.cache.entries()) {
            if (item.expiry <= now) {
                this.cache.delete(key);
            }
        }
    }
    
    /**
     * Clear all cache
     */
    clear(): void {
        this.cache.clear();
    }
}

export const cache = new Cache();
```

### Rate Limiting Implementation

The API implements rate limiting to prevent abuse:

```typescript
// src/config/ratelimit.ts
import { createMiddleware } from "hono/factory";

type RateLimitStorage = Map<string, { count: number; resetTime: number }>;

const storage: RateLimitStorage = new Map();

const LIMIT = 100; // requests
const WINDOW = 60 * 60 * 1000; // 1 hour in ms

export const ratelimit = createMiddleware(async (c, next) => {
    const ip = c.req.header("x-forwarded-for") || "unknown";
    const now = Date.now();
    
    let data = storage.get(ip);
    
    // Reset if window expired
    if (!data || data.resetTime < now) {
        data = { count: 0, resetTime: now + WINDOW };
    }
    
    // Increment count
    data.count++;
    storage.set(ip, data);
    
    // Set headers
    c.header("X-RateLimit-Limit", String(LIMIT));
    c.header("X-RateLimit-Remaining", String(Math.max(0, LIMIT - data.count)));
    c.header("X-RateLimit-Reset", String(Math.ceil(data.resetTime / 1000)));
    
    // Check if rate limit exceeded
    if (data.count > LIMIT) {
        return c.json(
            {
                status: 429,
                error: "Too Many Requests",
                message: "Rate limit exceeded, please try again later"
            },
            { status: 429 }
        );
    }
    
    await next();
});
```

### Error Handling Middleware

The API implements consistent error handling:

```typescript
// src/config/errorHandler.ts
import { Context } from "hono";
import { HiAnime } from "aniwatch";

export const errorHandler = {
    notFound: (c: Context) => {
        return c.json(
            {
                status: 404,
                error: "Not Found",
                message: "The requested resource was not found"
            },
            { status: 404 }
        );
    },
    
    serverError: (err: Error, c: Context) => {
        console.error(err);
        
        // Handle different types of errors
        if (err instanceof HiAnime.HiAnimeError) {
            return c.json(
                {
                    status: 500,
                    error: "Internal Server Error",
                    message: err.message
                },
                { status: 500 }
            );
        }
        
        return c.json(
            {
                status: 500,
                error: "Internal Server Error",
                message: "An unexpected error occurred"
            },
            { status: 500 }
        );
    }
};
```

## Testing Strategy

Both projects include comprehensive testing suites using Vitest:

```typescript
// __tests__/hianime/animeAboutInfo.test.ts
import { describe, it, expect } from "vitest";
import { HiAnime } from "../../src/index";

describe("Anime About Info", () => {
    const hianime = new HiAnime.Scraper();
    
    it("should get anime info for valid ID", async () => {
        const animeId = "steinsgate-3";
        const result = await hianime.getInfo(animeId);
        
        expect(result).toBeDefined();
        expect(result.id).toEqual(animeId);
        expect(result.name).toBeDefined();
        expect(result.description).toBeDefined();
        // Additional assertions...
    });
    
    it("should throw for invalid anime ID", async () => {
        const animeId = "non-existent-anime-123456789";
        
        await expect(async () => {
            await hianime.getInfo(animeId);
        }).rejects.toThrow(HiAnime.HiAnimeError);
    });
});
```

## Common Implementation Patterns

### Method Chaining for Scrapers

The scrapers often use a method chaining pattern for readability:

```typescript
function extractAnimeInfo($: CheerioAPI, selector: string): AnimeInfo {
    return {
        id: extractId($.find(`${selector} .anime-title`).attr("href")),
        name: $.find(`${selector} .anime-title`).text().trim(),
        poster: $.find(`${selector} .anime-poster img`).attr("src") || null,
        // Additional extractions...
    };
}
```

### Retry Logic for Resilience

The HTTP client implements retry logic to handle transient failures:

```typescript
async function fetchWithRetry<T>(url: string, options: RequestOptions = {}): Promise<AxiosResponse<T>> {
    const { retries = 3, delay = 1000 } = options;
    
    let lastError: Error | null = null;
    
    for (let attempt = 0; attempt < retries; attempt++) {
        try {
            return await axios.get<T>(url, options);
        } catch (error) {
            lastError = error instanceof Error ? error : new Error(String(error));
            
            // Don't retry for certain errors
            if (error.response?.status === 404) {
                throw lastError;
            }
            
            // Wait before next attempt
            await new Promise(resolve => setTimeout(resolve, delay));
        }
    }
    
    throw lastError || new Error(`Failed to fetch ${url} after ${retries} attempts`);
}
```

### Resource Cleanup

Both projects implement proper resource cleanup:

```typescript
// Graceful shutdown in server.ts
function gracefulShutdown() {
    console.log("Shutting down gracefully...");
    
    // Clear any scheduled tasks
    clearInterval(cacheCleanupInterval);
    
    // Close server connections
    server.close(() => {
        console.log("Server closed");
        process.exit(0);
    });
    
    // Force close after timeout
    setTimeout(() => {
        console.error("Forced shutdown due to timeout");
        process.exit(1);
    }, 10000);
}

process.on("SIGTERM", gracefulShutdown);
process.on("SIGINT", gracefulShutdown);
```

## Performance Optimizations

### Parallel Processing

For operations that require multiple independent requests, the code uses Promise.all for parallel processing:

```typescript
async function getMultipleAnimeInfo(animeIds: string[]): Promise<AnimeInfo[]> {
    return Promise.all(animeIds.map(id => getAnimeAboutInfo(id)));
}
```

### Partial Response Loading

For large responses, the API implements partial loading:

```typescript
// When fetching episode lists
function getAnimeEpisodes(animeId: string, page: number = 1): Promise<EpisodesPagination> {
    // Implementation with pagination
}
```

### Lazy Evaluation

Some heavy operations use lazy evaluation techniques:

```typescript
// Only extract video sources when explicitly requested
async function getAnimeEpisodeSources(episodeId: string, server: string = Servers.MEGACLOUD): Promise<VideoSources> {
    // Only fetch when requested
}
```

This document provides a comprehensive overview of the implementation details of the Aniwatch ecosystem, showcasing the various techniques and patterns used to create a robust, performant, and maintainable codebase.

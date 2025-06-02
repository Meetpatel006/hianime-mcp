# Aniwatch Project Analysis

## Overview
The Aniwatch project consists of two main components:
1. **aniwatch** - A TypeScript npm package that provides scrapers for anime information from hianimez.to
2. **aniwatch-api** - A RESTful API server that exposes the aniwatch package functionality via HTTP endpoints

Both projects work together to provide comprehensive anime data scraping and serving capabilities, with the core functionality implemented in the base package and the API project providing a web interface to that functionality.

## Aniwatch Package

### Purpose
- A TypeScript package for scraping anime information from hianimez.to
- Provides programmatic access to anime data for developers
- Can be integrated into other projects

### Key Features
1. **Anime Information Retrieval**:
   - Get detailed information about specific anime by ID
   - Access metadata like titles, descriptions, ratings, etc.

2. **Content Discovery**:
   - Homepage content (trending, popular, spotlight anime)
   - A-Z listing with various sorting options
   - Genre and producer-based filtering

3. **Search Capabilities**:
   - Full search functionality
   - Search suggestions/autocomplete

4. **Episode Information**:
   - Episode listings
   - Server information
   - Episode streaming sources

5. **Schedule Information**:
   - Estimated release schedules
   - Next episode air dates

### Structure
- **src/index.ts**: Main export file
- **src/hianime/**: Core functionality
  - **hianime.ts**: Main Scraper class with all methods
  - **error.ts**: Custom error handling
  - **scrapers/**: Individual scrapers for different types of content
  - **types/**: TypeScript type definitions for all data structures
- **src/config/**: Configuration for clients, errors, logging
- **src/extractors/**: Specialized extractors for video sources
- **src/utils/**: Helper functions and constants

### Notable APIs
- `getHomePage`: Get featured and trending anime on the homepage
- `getAZList`: Get alphabetical listings of anime
- `getQtipInfo`: Quick information popup data
- `getAnimeAboutInfo`: Detailed anime information
- `getAnimeSearchResults`: Search functionality
- `getAnimeSearchSuggestion`: Auto-complete suggestions
- `getProducerAnimes`: Filter by production company
- `getGenreAnime`: Filter by genre
- `getAnimeCategory`: Filter by category
- `getEstimatedSchedule`: Get release schedule information
- `getNextEpisodeSchedule`: Get next episode release dates
- `getAnimeEpisodes`: Get episode listings
- `getEpisodeServers`: Get server options for episodes
- `getAnimeEpisodeSources`: Get streaming sources for episodes

## Aniwatch-API

### Purpose
- RESTful API server exposing the aniwatch package functionality
- Makes anime data accessible via HTTP for web applications
- Provides caching and rate limiting

### Key Features
1. **REST API Interface**:
   - Converts aniwatch package functions into HTTP endpoints
   - JSON responses for easy integration

2. **Performance Optimizations**:
   - Caching system to reduce scraper load
   - Rate limiting for API protection

3. **Deployment Options**:
   - Docker support
   - Vercel and Render deployment configurations

4. **Error Handling**:
   - Consistent error responses
   - Graceful failure modes

### Structure
- **src/server.ts**: Main server setup
- **src/routes/**: API route definitions
  - **hianime.ts**: Routes for all anime endpoints
- **src/config/**: Server configuration
  - **cache.ts**: Caching mechanisms
  - **cors.ts**: CORS handling
  - **ratelimit.ts**: Rate limiting
  - **env.ts**: Environment variables
- **src/middleware/**: Request processing
  - **logging.ts**: Request logging
  - **cache.ts**: Cache control

### API Endpoints
All endpoints are under `/api/v2/hianime/`:
- `/home`: Homepage data
- `/azlist/{sortOption}`: A-Z listings
- `/qtip/{animeId}`: Quick info tooltips
- `/info/{animeId}`: Detailed anime info
- `/search`: Search functionality
- `/search/suggest`: Search suggestions
- `/producer/{producerId}`: Producer-specific anime
- `/genre/{genreId}`: Genre-specific anime
- `/category/{categoryId}`: Category-specific anime
- `/schedule/estimated`: Estimated schedules
- `/schedule/next`: Next episode schedules
- `/episodes/{animeId}`: Episode listings
- `/episode-servers/{episodeId}`: Server options
- `/episode-srcs`: Episode streaming sources

## Technical Implementation

### Technologies Used
- **TypeScript**: For type safety and modern JavaScript features
- **Node.js**: Runtime environment
- **Hono**: Lightweight web framework for API routes
- **Cheerio**: For HTML parsing and scraping
- **Docker**: For containerization and deployment

### Design Patterns
1. **Scraper Pattern**: Each content type has dedicated scraper functions
2. **Caching Strategy**: In-memory caching for performance
3. **Middleware Architecture**: For request processing and response handling
4. **Type-Driven Development**: Extensive TypeScript types

### Testing
- Comprehensive test suites for both projects
- Unit tests for individual scrapers
- Integration tests for API endpoints

## Integration with MCP-Demo
The MCP-Demo project appears to provide a Model Context Protocol server that could potentially interact with the aniwatch system, possibly providing an AI interface to the anime data.

## Development and Deployment

### Local Development
- Package manager support for npm, yarn, and pnpm
- Test-driven development workflow

### Deployment Options
- Docker containerization
- Vercel serverless deployment
- Render deployment support

## Note on Usage
Both projects are unofficial packages/APIs for hianimez.to and have no official affiliation. They are intended as demonstrations of web scraping and API development techniques.

The projects emphasize that the content they provide belongs to their respective owners, and the code simply demonstrates how to build systems that scrape websites and utilize their content.

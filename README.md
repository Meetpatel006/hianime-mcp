# Aniwatch MCP Demo

This project demonstrates the integration of the Aniwatch anime data system with the Model Context Protocol (MCP) to create an AI assistant that can provide anime information and recommendations.

## Project Overview

The Aniwatch MCP Demo combines several components:

1. **Aniwatch Package**: A TypeScript library for scraping anime information from hianimez.to
2. **Aniwatch API**: A RESTful API server that exposes the Aniwatch functionality via HTTP endpoints
3. **MCP Server**: A Python-based server using FastMCP that connects AI assistants to the Aniwatch ecosystem

This integration allows AI assistants to search for anime, retrieve episode information, get streaming links, and more through a conversational interface.

## Documentation

The project includes several comprehensive documentation files:

- [**Aniwatch Technical Architecture**](./aniwatch-technical.md): Detailed technical architecture of the Aniwatch ecosystem
- [**Aniwatch Implementation Details**](./aniwatch-implementation.md): Code-focused documentation with implementation examples
- [**Aniwatch Deployment Guide**](./aniwatch-deployment.md): Comprehensive deployment instructions
- [**Aniwatch MCP Integration Guide**](./aniwatch-mcp-integration.md): Guide for integrating with Model Context Protocol

## Project Structure

```
├── aniwatch/                  # Core package for anime data scraping
├── aniwatch-api/              # RESTful API for exposing anime data
├── scrapers/                  # Python scrapers for anime data
│   ├── __init__.py
│   └── episodes_scraper.py    # Episodes scraper implementation
├── main.py                    # MCP server implementation
├── aniwatch-technical.md      # Technical architecture documentation
├── aniwatch-implementation.md # Implementation details
├── aniwatch-deployment.md     # Deployment instructions
└── aniwatch-mcp-integration.md # MCP integration guide
```

## Getting Started

### Prerequisites

- Node.js v18+ for the Aniwatch API
- Python 3.11+ for the MCP server
- pnpm (recommended) or npm for Node.js package management

### Setup Instructions

1. **Start the Aniwatch API server**:

   ```bash
   cd aniwatch-api
   npm install
   npm run dev
   ```

2. **Install Python dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the MCP server**:

   ```bash
   python main.py
   ```

4. **Connect with an MCP client** like Claude Desktop or Continue for VS Code.

## Key Features

- **Anime Search**: Search for anime by title or keywords
- **Detailed Information**: Get comprehensive details about anime shows
- **Episode Listings**: Access episode information
- **Streaming Sources**: Get streaming sources for episodes
- **MCP Integration**: Connect AI assistants to anime data through resources and tools

## MCP Tools and Resources

The MCP server exposes the following tools:

- **search_anime**: Search for anime by name or keywords
- **get_anime_info**: Get detailed information about an anime
- **get_anime_episodes**: Get episode listings for an anime
- **get_streaming_sources**: Get streaming sources for episodes

And the following resources:

- **anime://{anime_id}**: Access anime information directly
- **episode://{anime_id}/{episode_number}**: Access episode information

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Aniwatch](https://github.com/ghoshRitesh12/aniwatch) - The core package for anime data
- [Aniwatch API](https://github.com/ghoshRitesh12/aniwatch-api) - The RESTful API server
- [Model Context Protocol](https://modelcontextprotocol.io/) - Protocol for AI tools and resources

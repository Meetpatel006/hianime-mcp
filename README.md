# 🎌 Hianime-MCP: AI-Powered Anime Data Service

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://python.org)
[![MCP](https://img.shields.io/badge/MCP-1.9.1-green.svg)](https://modelcontextprotocol.io)
[![FastMCP](https://img.shields.io/badge/FastMCP-Latest-purple.svg)](https://github.com/modelcontextprotocol/python-sdk)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/Meetpatel006/hianime-mcp)

> **Transform your AI assistant into an anime expert!** 🤖✨

Get real-time anime information, episode sources, and detailed character data through a simple, AI-friendly interface. Perfect for Claude Desktop, Continue IDE, and any MCP-compatible application.

## ✨ What Makes This Special?

🚀 **Instant Setup** - Works out-of-the-box with Claude Desktop and other MCP clients  
🔄 **Real-Time Data** - Always up-to-date anime information from live sources  
🎯 **AI-Optimized** - Designed specifically for natural language interactions  
⚡ **Lightning Fast** - Async architecture with intelligent caching  
🛡️ **Reliable** - Built-in error handling and fallback mechanisms

## 🚀 Quick Start

### 1. Install & Run
```bash
# Clone and setup
git clone https://github.com/Meetpatel006/hianime-mcp.git
cd hianime-mcp
pip install -r requirements.txt

# Start the server
python main.py
```

### 2. Connect to Claude Desktop
Add this to your Claude Desktop MCP configuration:
```json
{
  "mcpServers": {
    "hianime": {
      "command": "python",
      "args": ["/path/to/hianime-mcp/main.py"]
    }
  }
}
```

### 3. Start Asking!
Now you can ask Claude things like:
- *"What are the trending anime right now?"*
- *"Tell me about Attack on Titan"*
- *"Find streaming sources for Demon Slayer episode 5"*

## 🎯 What You Can Do

### 🏠 Homepage & Discovery
- **Trending Anime** - Get what's hot right now
- **Spotlight Features** - Featured anime with detailed info
- **Genre Browsing** - Explore by categories

### 📺 Anime Details
- **Complete Profiles** - Ratings, episodes, characters, voice actors
- **Character Information** - Detailed character data and relationships
- **Recommendations** - Similar anime suggestions

### 🎬 Episode Streaming
- **Multi-Server Sources** - VidStreaming, VidCloud, MegaCloud, StreamSB, StreamTape
- **Quality Options** - Multiple resolution choices
- **Subtitle Support** - Sub, dub, and raw versions
- **Auto-Decryption** - Handles protected streaming sources automatically

## 🛠️ Built With

**Core Stack:**
- 🐍 **Python 3.12+** - Modern async/await support
- ⚡ **FastMCP** - High-performance MCP server framework  
- 🌐 **CloudScraper** - Advanced web scraping with anti-bot protection
- 🔍 **BeautifulSoup4** - HTML parsing and data extraction

**Why These Choices:**
- **Async-First** - Handle multiple requests efficiently
- **Type-Safe** - Comprehensive type hints for reliability
- **Anti-Detection** - CloudScraper bypasses common blocking mechanisms
- **MCP Native** - Built specifically for AI assistant integration

## 📁 Project Structure

```
hianime-mcp/
├── src/                          # Source code
│   ├── management/               # Logging and debugging infrastructure
│   │   ├── _init_.py
│   │   └── logger.py            # Centralized logging with rotation
│   ├── models/                   # Data models and type definitions
│   │   ├── _init_.py
│   │   ├── anime.py             # Anime-related models
│   │   ├── character.py         # Character and voice actor models
│   │   ├── client.py            # HTTP client configuration
│   │   ├── episode.py           # Episode and server models
│   │   └── media.py             # Media and homepage models
│   ├── scrapers/                 # Core scraping functionality
│   │   ├── _init_.py
│   │   ├── homePages.py         # Homepage data extraction
│   │   ├── animeAboutInfo.py    # Detailed anime information
│   │   ├── animeEpisodeSrcs.py  # Episode source extraction
│   │   ├── animeEpisodeServers.py # Server discovery and mapping
│   │   └── extractor/           # Streaming service extractors
│   │       ├── megacloud.py     # MegaCloud decryption
│   │       ├── rapidcloud.py    # RapidCloud extraction
│   │       ├── streamsb.py      # StreamSB handling
│   │       └── streamtape.py    # StreamTape processing
│   └── utils/                    # Utility functions and configuration
│       ├── _init_.py
│       ├── config.py            # Application configuration
│       ├── constants.py         # URL constants and mappings
│       ├── extractors.py        # HTML extraction utilities
│       └── cleanup_logs.py      # Log maintenance utilities
├── tests/                        # Test suites
│   ├── _init_.py
│   ├── run_tests.py             # Test runner
│   ├── test_anime_scraper.py    # Core scraper tests
│   ├── test_episode_sources.py  # Episode source tests
│   ├── test_home_scraper.py     # Homepage scraper tests
│   └── [additional test files]
├── docs/                         # Documentation
│   ├── PRODUCT_MANAGEMENT.md    # Product strategy and roadmap
│   ├── mcp.md                   # MCP integration guide
│   ├── Testing.md               # Testing documentation
│   └── [additional docs]
├── examples/                     # Usage examples
│   └── client_example.py        # Client SDK examples
├── logs/                         # Application logs
├── main.py                       # MCP server entry point
├── requirements.txt              # Python dependencies
├── pyproject.toml               # Project configuration
└── README.md                     # This file!
```

## 🔧 Advanced Setup

### Development Mode
```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
python tests/run_tests.py

# Format code
black src/ tests/
```

### Requirements
- Python 3.12+
- Internet connection for scraping

## 🎮 Available Commands

When connected to your AI assistant, you can use these natural language commands:

### 🏠 Homepage & Trending
- *"What anime is trending right now?"*
- *"Show me the homepage spotlight anime"*
- *"What are the popular anime genres?"*

### 📺 Anime Information  
- *"Tell me about [anime name]"*
- *"Get details for anime ID: spy-x-family"*
- *"What characters are in Attack on Titan?"*

### 🎬 Episode Streaming
- *"Find streaming sources for [anime] episode [number]"*
- *"Get episode servers for demon-slayer?ep=12345"*
- *"Show me dub sources for this episode"*

### 🔧 Technical Tools (for developers)

| Tool | Purpose | Parameters |
|------|---------|------------|
| `get_home_page` | Homepage data | None |
| `get_trending_anime` | Trending list | None |
| `get_anime_about_info` | Anime details | `anime_id` |
| `get_anime_episode_sources` | Streaming sources | `episode_id`, `category` |
| `get_episode_servers` | Available servers | `episode_id` |

**Supported Servers:** VidStreaming, RapidCloud, MegaCloud, StreamSB, StreamTape

## 💻 Usage Examples

### For AI Assistants (Recommended)
Just ask naturally! Once connected to Claude Desktop or another MCP client:

> **You:** "What anime is trending right now?"  
> **Claude:** *Shows current trending anime with details*

> **You:** "Tell me about Demon Slayer"  
> **Claude:** *Provides comprehensive anime information*

> **You:** "Find streaming sources for Attack on Titan episode 1"  
> **Claude:** *Lists available streaming servers and sources*

### For Developers

**Basic Python Usage:**
```python
from main import get_home_page, get_anime_about_info

# Get trending anime
homepage = await get_home_page()
print(f"Found {len(homepage['spotlightAnimes'])} spotlight anime")

# Get anime details  
anime_info = await get_anime_about_info(anime_id="attack-on-titan")
print(f"Rating: {anime_info['data']['anime']['info']['stats']['rating']}")
```

**Claude Desktop Config:**
```json
{
  "mcpServers": {
    "hianime": {
      "command": "python",
      "args": ["/path/to/hianime-mcp/main.py"]
    }
  }
}
```

## 🧪 Testing

```bash
# Run all tests
python tests/run_tests.py

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html
```

**Test Coverage:**
- ✅ Unit tests for all scrapers
- ✅ Integration tests for MCP tools  
- ✅ Performance and load testing

## 🏗️ Architecture Overview

**Clean & Simple Design:**
- 🏠 **Scrapers** - Extract data from anime websites
- 📊 **Models** - Type-safe data structures  
- 🔧 **Utils** - Helper functions and configuration
- 🎯 **MCP Tools** - AI assistant integration layer

**Key Features:**
- **Async-First** - Concurrent processing for speed
- **Error Recovery** - Graceful fallbacks when servers fail
- **Smart Caching** - Reduces redundant requests
- **Type Safety** - Full Python type hints

## 🎯 Roadmap

### ✅ Current Features
- Homepage and trending anime data
- Detailed anime information with characters
- Multi-server episode source extraction
- MCP integration for AI assistants

### 🔄 Coming Soon
- **Performance improvements** - Faster response times
- **More streaming servers** - Additional source support  
- **Enhanced error handling** - Better reliability
- **Caching system** - Reduced load times

### 📋 Future Plans
- Manga integration
- Advanced search capabilities
- Multi-language support
- Web dashboard for monitoring

## 🔒 Security & Privacy

**Privacy First:**
- 🚫 No personal data collection or storage
- 🔒 Only processes public anime information
- ⚡ Built-in rate limiting to prevent abuse
- 🛡️ Input validation and sanitization

**Compliance:**
- Respectful scraping with appropriate delays
- Adheres to website terms of service
- Links to publicly available content only

## 🤝 Contributing

**Want to help make this better?** We'd love your contributions!

### Quick Start
```bash
# Fork and clone
git clone https://github.com/Meetpatel006/hianime-mcp.git
cd hianime-mcp

# Setup development environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e ".[dev]"

# Run tests
python tests/run_tests.py
```

### What We Need
- 🐛 **Bug fixes** - Help us squash issues
- ⚡ **Performance improvements** - Make it faster
- 🎯 **New features** - Add streaming servers, improve data extraction
- 📚 **Documentation** - Better examples and guides
- 🧪 **Tests** - Improve coverage and reliability

### Guidelines
- Follow PEP 8 style (use `black` for formatting)
- Add type hints to new functions
- Include tests for new features
- Update documentation as needed

**Questions?** Open an issue or start a discussion!

## 📚 Documentation

- **[MCP Tools Reference](docs/mcp.md)** - Complete tool documentation
- **[Testing Guide](docs/Testing.md)** - How to run and write tests
- **[Examples](examples/)** - Usage examples and integrations

## 📞 Support

- 🐛 **Issues**: [GitHub Issues](https://github.com/Meetpatel006/hianime-mcp/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/Meetpatel006/hianime-mcp/discussions)
- 📖 **Docs**: Check the `/docs` folder

---

**Built with ❤️ for the anime and AI communities**

*Making anime knowledge accessible to AI assistants everywhere!* 🎌🤖

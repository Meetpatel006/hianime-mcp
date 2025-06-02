# Anime Scraper MCP Server

A microservice that provides anime information through an MCP (Message Control Protocol) interface.

## Features

- Homepage scraping with spotlight and trending anime
- Detailed anime information including:
  - Basic info (name, description, rating)
  - Episodes (sub/dub counts)
  - Characters and voice actors
  - Promotional videos
  - Related and recommended anime
- Genre listings
- Error handling and logging

## Project Structure

```
src/
├── management/     # Logging and debugging tools
├── models/        # Data models
├── scrapers/      # Core scraping functionality
└── utils/         # Utility functions and configuration

tests/            # Test files
```

## Setup

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Server

To start the MCP server:
```bash
python main.py
```

The server provides the following endpoints:
- `get_home_page`: Get homepage information
- `get_anime_about_info`: Get detailed anime information

## Testing with Client

To test the functionality:
```bash
# In one terminal, start the server
python main.py

# In another terminal, run the test client
python test_client.py
```

The test client will:
1. Fetch homepage information
2. Display spotlight and trending anime
3. Get detailed information about an anime
4. Test error handling

## Development

- Models are in `src/models/`
- Scraping logic is in `src/scrapers/`
- Configuration in `src/utils/config.py`
- Logging setup in `src/management/logger.py`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

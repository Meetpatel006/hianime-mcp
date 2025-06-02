# Testing Guide

This guide explains how to test the Anime MCP Server and Client implementation.

## Prerequisites

- Python 3.9 or higher
- Required dependencies installed (`pip install -r requirements.txt`)

## Running the Server

1. Start the MCP server:
```bash
python main.py
```

The server provides the following endpoints:
- `get_home_page`: Get homepage data including spotlight and trending anime
- `get_anime_about_info`: Get detailed information about a specific anime

## Testing with the Interactive Client

1. Start the server as described above
2. In a new terminal, run the interactive client example:
```bash
python examples/client_example.py
```

The interactive client provides the following features:
1. View Homepage Data
   - Show all information
   - Filter spotlight animes
   - Filter trending animes
   - View available genres

2. Get Detailed Anime Information
   - Search by anime ID
   - Configurable display options
   - View recommendations
   - Show/hide various information sections

3. Save Data
   - Export homepage data to JSON
   - Configurable file naming

## Using the Client Library

You can also use the client library programmatically:

```python
from src.client import AnimeClient

async def example():
    async with AnimeClient() as client:
        await client.initialize()
        
        # Get homepage data
        home_data = await client.get_home_page()
        
        # Get specific anime details
        anime_data = await client.get_anime_details("spy-x-family")

        if anime_data["success"]:
            print(f"Found anime: {anime_data['data']['anime']['info']['name']}")
```

## Error Handling

The client includes built-in error handling for:
- Connection issues
- Invalid anime IDs
- Server errors
- Data parsing errors

All errors are properly logged and include descriptive messages for debugging.

## Development Testing

When developing new features:
1. Run the server in debug mode
2. Use the interactive client to validate changes
3. Check the logs in `logs/` directory for debugging information

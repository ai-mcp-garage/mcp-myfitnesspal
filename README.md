# MyFitnessPal MCP Server

A FastMCP server that retrieves your MyFitnessPal nutrition data through the Model Context Protocol.

## Quick Start

### Local Development

1. **Prerequisites**: Python 3.12+, uv, MyFitnessPal account
2. **Install dependencies**: `uv sync`
3. **Log into MyFitnessPal** in your browser (Chrome, Firefox, Safari, or Edge)
4. **Test the server**: `uv run python test_client.py`

### Deployment (Server/Docker)

For environments without a browser:

1. **Export cookies** from your local browser:
   ```bash
   uv run python export_cookies.py
   ```

2. **Deploy** with the generated `.env` file - no browser needed!

See **[Deployment Guide](docs/DEPLOYMENT.md)** for Docker, systemd, and cloud deployment options.

## Features

- Daily nutrition summary (calories, macros, water)
- Detailed meal-by-meal breakdown
- Exercise tracking (cardio + strength)
- Macro & micronutrient analysis
- Water intake monitoring
- Date range summaries with trends

## Configuration

Add to your MCP client config (e.g., `.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "myfitnesspal": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "--directory", "/path/to/mfp-mcp", "python", "main.py"]
    }
  }
}
```

## Documentation

- **[Full Documentation](docs/README.md)** - Complete setup and usage guide
- **[Deployment Guide](docs/DEPLOYMENT.md)** - Docker, server, and cloud deployment
- **[Quick Start Guide](docs/USAGE.md)** - Fast setup instructions
- **[Project Summary](docs/PROJECT_SUMMARY.md)** - Architecture and design decisions
- **[Implementation Notes](docs/IMPLEMENTATION_NOTES.md)** - Technical details

## How It Works

Uses the `python-myfitnesspal` library (GitHub version) which:
- Extracts cookies from your browser automatically
- Scrapes MyFitnessPal website for data
- No credentials stored in files
- Works with Chrome, Firefox, Safari, and Edge

### Cookie Authentication

**Browser-based (default)**:
- Automatically extracts cookies from your local browser
- Works out of the box if you're logged into MyFitnessPal

**Environment variable (for Docker/servers)**:
- Set `MFP_COOKIES` environment variable with exported cookies
- Use `export_cookies.py` utility to extract cookies beforehand:
  ```bash
  uv run python export_cookies.py
  ```
- Perfect for environments without browser access (Docker containers, remote servers, etc.)
- Cookies expire after ~30 days, re-export when needed

## Project Structure

```
mfp-mcp/
├── docs/              # All documentation
├── myfitnesspal/      # External library (GitHub)
├── main.py            # FastMCP server
├── api_client.py      # Client wrapper
├── utils.py           # Helper functions
├── test_client.py     # Test script
└── pyproject.toml     # Dependencies
```

## Requirements

- Python 3.12+
- uv package manager
- Active MyFitnessPal session in browser
- fastmcp 2.12+
- lxml, browser-cookie3, measurement

## License

For personal use and educational purposes. Respect MyFitnessPal's Terms of Service.

## Credits

- **python-myfitnesspal**: https://github.com/coddingtonbear/python-myfitnesspal
- **FastMCP**: https://github.com/jlowin/fastmcp


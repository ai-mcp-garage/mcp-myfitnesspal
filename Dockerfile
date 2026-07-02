# MyFitnessPal MCP Server
# 
# NOTE: This MCP uses browser cookie authentication by default.
# For Docker deployment, you'll need to mount your browser's cookie database
# or use an alternative authentication method.
#
# Build: docker build -t mcp-myfitnesspal .
# Run: docker run -it --rm -v ~/.config/google-chrome:/root/.config/google-chrome:ro mcp-myfitnesspal

FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml README.md ./
COPY src/ ./src/

# Install the package
RUN pip install --no-cache-dir -e .

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash mcp
USER mcp

# Expose default port (for HTTP transport if needed)
EXPOSE 8000

# Default command runs the MCP server with stdio transport
ENTRYPOINT ["python", "-m", "mfp_mcp.server"]

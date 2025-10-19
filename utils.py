from fastmcp.tools.tool import ToolResult
from mcp.types import TextContent


def text_response(text: str) -> ToolResult:
    """Return raw text as a ToolResult without JSON wrapping overhead."""
    return ToolResult(
        content=[TextContent(type="text", text=text)],
        structured_content=None  # Explicitly disable structured content
    )

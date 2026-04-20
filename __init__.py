"""
NotebookLM MCP Skill — Acesso programático ao Google NotebookLM
Integração com Antigravity, Claude Code, Gemini e CLI
"""

from .skill import (
    NotebookLMClient,
    setup_authentication,
    setup_mcp_for_tool,
    diagnose_system,
    example_create_and_query,
    example_research_and_podcast,
)

__version__ = "1.2.0"
__author__ = "Antigravity Skills"
__all__ = [
    "NotebookLMClient",
    "setup_authentication",
    "setup_mcp_for_tool",
    "diagnose_system",
    "example_create_and_query",
    "example_research_and_podcast",
]

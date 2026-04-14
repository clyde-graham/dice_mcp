"""
dice_server.py — RPG Dice Roller MCP Server
Provides dice rolling tools to Claude via the Model Context Protocol.
Uses the d20 library for notation parsing and rolling.

Tools exposed:
  - roll(notation)        — roll any standard dice expression
  - roll_history()        — view the last N rolls this session
  - clear_history()       — clear the roll history
"""

import d20
from mcp.server.fastmcp import FastMCP
from datetime import datetime

# ── Server instance ────────────────────────────────────────────────────────────
# FastMCP is the high-level wrapper that handles all MCP protocol boilerplate.
# The string here is the server name Claude will see.
mcp = FastMCP("RPG Dice Roller")

# ── Session roll history ───────────────────────────────────────────────────────
# Simple in-memory log. Resets when the server restarts.
# Each entry: {"notation": str, "result": str, "total": int, "timestamp": str}
_roll_history: list[dict] = []
HISTORY_LIMIT = 50  # maximum rolls to keep


# ── Tools ──────────────────────────────────────────────────────────────────────

@mcp.tool()
def roll(notation: str) -> str:
    """
    Roll dice using standard RPG notation.

    Supports a wide range of expressions, for example:
      d20          — single d20
      1d20+5       — d20 with modifier
      3d6          — three six-sided dice, summed
      4d6kh3       — roll 4d6, keep highest 3 (classic D&D ability score)
      2d20kh1      — roll with advantage (keep highest)
      2d20kl1      — roll with disadvantage (keep lowest)
      1d6e6        — exploding die (reroll and add on a 6)
      2d6ro<3      — reroll 1s and 2s once
      3d6 [fire]   — annotated roll (e.g. damage type)
      2d6+1d4+3    — mixed dice expression

    Returns a full breakdown of the roll including individual dice values and total.
    """
    notation = notation.strip()
    if not notation:
        return "Error: no dice notation provided."

    try:
        result = d20.roll(notation)
    except d20.errors.RollSyntaxError as e:
        return f"Syntax error in notation '{notation}': {e}"
    except d20.errors.RollValueError as e:
        return f"Value error in notation '{notation}': {e}"
    except Exception as e:
        return f"Unexpected error rolling '{notation}': {e}"

    # Format the output. d20's str() already produces a nice Markdown breakdown,
    # e.g. "4d6kh3 (4, 4, **6**, ~~3~~) = `14`"
    result_str = str(result)

    # Append to history
    _roll_history.append({
        "notation": notation,
        "result": result_str,
        "total": int(result.total),
        "timestamp": datetime.now().strftime("%H:%M:%S"),
    })
    # Trim to limit
    if len(_roll_history) > HISTORY_LIMIT:
        _roll_history.pop(0)

    return result_str


@mcp.tool()
def roll_history(count: int = 10) -> str:
    """
    Return the last N rolls from this session.

    Args:
        count: How many recent rolls to show (default 10, max 50).

    Returns a formatted list of recent rolls with timestamps and totals.
    """
    if not _roll_history:
        return "No rolls yet this session."

    count = max(1, min(count, HISTORY_LIMIT))
    recent = _roll_history[-count:]

    lines = [f"Last {len(recent)} roll(s) this session:\n"]
    for i, entry in enumerate(reversed(recent), 1):
        lines.append(
            f"{i}. [{entry['timestamp']}] `{entry['notation']}` → {entry['result']}"
        )

    return "\n".join(lines)


@mcp.tool()
def clear_history() -> str:
    """
    Clear the roll history for this session.
    """
    count = len(_roll_history)
    _roll_history.clear()
    return f"Cleared {count} roll(s) from history."


# ── Entry point ────────────────────────────────────────────────────────────────

def main():
    """Entry point for pyproject.toml [project.scripts]."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    # stdio transport is correct for a local Claude Desktop MCP server.
    # Claude Desktop launches this script as a subprocess and communicates
    # via stdin/stdout.
    main()

# dice-mcp — RPG Dice Roller MCP Server

An [MCP](https://modelcontextprotocol.io) server that provides RPG dice rolling tools to Claude Desktop. Uses the [`d20`](https://d20.readthedocs.io) library for notation parsing.

## Tools

| Tool | Description |
|------|-------------|
| `roll(notation)` | Roll any standard dice expression (e.g. `4d6kh3`, `2d20kl1`) |
| `roll_history(count)` | View the last N rolls this session (default 10) |
| `clear_history()` | Clear the session roll history |

See the [d20 notation reference](https://d20.readthedocs.io) for full expression syntax.

## Requirements

- Python 3.10+
- [`uv`](https://docs.astral.sh/uv/getting-started/installation/) package manager

## Setup

### 1. Install uv (if not already installed)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Clone and install dependencies

```bash
git clone https://github.com/YOUR_USERNAME/dice-mcp.git
cd dice-mcp
uv sync
```

### 3. Verify the install

```bash
uv run python check_env.py
```

### 4. Configure Claude Desktop

Edit your Claude Desktop config file:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

Add the following under `"mcpServers"`:

```json
{
  "mcpServers": {
    "dice-roller": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/absolute/path/to/dice-mcp",
        "python",
        "dice_server.py"
      ]
    }
  }
}
```

Replace `/absolute/path/to/dice-mcp` with the actual path where you cloned the repo.

### 5. Restart Claude Desktop

The dice roller tools (`roll`, `roll_history`, `clear_history`) will appear in Claude's tool list when connected.

## Session Notes

Roll history is in-memory only and resets when the MCP server restarts (i.e., when Claude Desktop is quit or the server is cycled).

## Troubleshooting

**Hammer icon doesn't appear after restart:**
Check the Claude Desktop logs:
```bash
cat ~/Library/Logs/Claude/mcp-server-dice-roller.log
```

**`ModuleNotFoundError: No module named 'd20'`:**
Make sure your Claude Desktop config's `command`/`args` match the `uv run --directory` pattern shown above — the server must be launched through `uv run` so it resolves the project's own environment, not your system Python.

**Roll history resets:**
Expected — history is in-memory and resets when Claude Desktop restarts the server process.

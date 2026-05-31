"""Package initialization files."""

from pathlib import Path

# Create __init__.py files for all packages
packages = [
    "src",
    "src/api",
    "src/api/middleware",
    "src/bot",
    "src/bot/telegram",
    "src/bot/whatsapp",
    "src/ai",
    "src/ai/agents",
    "src/ai/tools",
    "src/memory",
    "src/database",
    "src/workflows",
    "src/security",
    "src/monitoring",
]

for package in packages:
    init_file = Path(__file__).parent / package / "__init__.py"
    if not init_file.exists():
        init_file.parent.mkdir(parents=True, exist_ok=True)
        init_file.write_text("")

"""
Memory CLI Commands

Commands for memory operations.
"""
import argparse
from sros.memory import MemoryRouter, ShortTermMemory, LongTermMemory, CodexMemory


def register_commands(parser: argparse.ArgumentParser):
    """Register memory subcommands."""
    subparsers = parser.add_subparsers(dest="action", help="Memory actions")
    
    # Read command
    read_parser = subparsers.add_parser("read", help="Read from memory")
    read_parser.add_argument("--layer", default="short", help="Memory layer (short, long, codex)")
    read_parser.add_argument("--query", help="Search query")
    read_parser.add_argument("--key", help="Specific key")
    
    # Write command
    write_parser = subparsers.add_parser("write", help="Write to memory")
    write_parser.add_argument("content", help="Content to write")
    write_parser.add_argument("--layer", default="short", help="Memory layer")
    write_parser.add_argument("--key", help="Optional key")
    
    # Stats command
    subparsers.add_parser("stats", help="Get memory statistics")


def execute(args: argparse.Namespace) -> dict:
    """Execute memory command."""
    if args.action == "read":
        return read_memory(args.layer, args.query, args.key)
    elif args.action == "write":
        return write_memory(args.content, args.layer, args.key)
    elif args.action == "stats":
        return get_memory_stats()
    else:
        return {"error": "Unknown memory action"}


def read_memory(layer: str, query: str = None, key: str = None) -> dict:
    """Read from memory."""
    try:
        router = MemoryRouter()
        router.initialize_layers(
            short_term=ShortTermMemory(),
            long_term=LongTermMemory(),
            codex=CodexMemory()
        )
        
        results = router.read(query=query, layer=layer, key=key)
        
        return {
            "status": "success",
            "layer": layer,
            "count": len(results),
            "results": results
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def write_memory(content: str, layer: str, key: str = None) -> dict:
    """Write to memory."""
    try:
        router = MemoryRouter()
        router.initialize_layers(
            short_term=ShortTermMemory(),
            long_term=LongTermMemory(),
            codex=CodexMemory()
        )
        
        router.write(content, layer=layer, key=key)
        
        return {
            "status": "success",
            "layer": layer,
            "message": "Content written to memory"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def get_memory_stats() -> dict:
    """Get memory statistics."""
    try:
        router = MemoryRouter()
        router.initialize_layers(
            short_term=ShortTermMemory(),
            long_term=LongTermMemory(),
            codex=CodexMemory()
        )
        
        stats = router.get_stats()
        
        return {
            "status": "success",
            "stats": stats
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

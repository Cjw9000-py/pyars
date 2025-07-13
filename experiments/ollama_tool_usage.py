"""Demonstrate requesting a tool call via Ollama's raw generation API.

The script sends a request asking the model to call a tool named ``hello`` and
prints the raw response returned by the server. Tool calls are not currently
honored by the raw generation endpoint, so this is useful to inspect how the
model attempts to respond regardless.
"""

from __future__ import annotations

import json

import ollama


TOOL_SPEC = [
    {
        "type": "function",
        "function": {
            "name": "hello",
            "description": "Print a friendly greeting",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "Text to include in the greeting",
                    }
                },
                "required": ["message"],
            },
        },
    }
]


def run_experiment() -> None:
    """Send the generation request and dump the raw response."""
    response = ollama.generate(
        model="llama3",
        prompt="Use the hello tool to greet the world.",
        tools=TOOL_SPEC,
        tool_choice={"type": "function", "function": {"name": "hello"}},
        stream=False,
        raw=True,
    )
    print(json.dumps(response, indent=2))


if __name__ == "__main__":
    run_experiment()

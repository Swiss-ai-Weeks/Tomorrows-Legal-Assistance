#!/usr/bin/env python3
"""Generate PNG diagram of the Swiss Legal Analysis Agent workflow."""

import base64
import os
import random
import re
import sys
import time
from pathlib import Path
from typing import Literal

import requests

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from backend.agent.graph_with_tools import create_legal_agent


def draw_mermaid_png(
    mermaid_syntax: str,
    output_file_path: str | None = None,
    background_color: str | None = "white",
    file_type: Literal["jpeg", "png", "webp"] | None = "png",
    max_retries: int = 1,
    retry_delay: float = 1.0,
    proxies: dict = {"http": "http://localhost:8887", "https": "http://localhost:8887"},
) -> bytes:
    """Renders Mermaid graph using the Mermaid.INK API."""

    # Use Mermaid API to render the image
    mermaid_syntax_encoded = base64.b64encode(mermaid_syntax.encode("utf8")).decode(
        "ascii"
    )

    # Check if the background color is a hexadecimal color code using regex
    if background_color is not None:
        hex_color_pattern = re.compile(r"^#(?:[0-9a-fA-F]{3}){1,2}$")
        if not hex_color_pattern.match(background_color):
            background_color = f"!{background_color}"

    image_url = (
        f"https://mermaid.ink/img/{mermaid_syntax_encoded}"
        f"?type={file_type}&bgColor={background_color}"
    )

    error_msg_suffix = (
        "To resolve this issue:\n"
        "1. Check your internet connection and try again\n"
        "2. Try with higher retry settings: "
        "`draw_mermaid_png(..., max_retries=5, retry_delay=2.0)`"
    )

    for attempt in range(max_retries + 1):
        try:
            response = requests.get(
                image_url, proxies=proxies, verify=False, timeout=10
            )
            if response.status_code == requests.codes.ok:
                img_bytes = response.content
                if output_file_path is not None:
                    Path(output_file_path).write_bytes(response.content)

                return img_bytes

            # If we get a server error (5xx), retry
            if 500 <= response.status_code < 600 and attempt < max_retries:
                # Exponential backoff with jitter
                sleep_time = retry_delay * (2**attempt) * (0.5 + 0.5 * random.random())  # noqa: S311 not used for crypto
                time.sleep(sleep_time)
                continue

            # For other status codes, fail immediately
            msg = (
                "Failed to reach https://mermaid.ink/ API while trying to render "
                f"your graph. Status code: {response.status_code}.\n\n"
            ) + error_msg_suffix
            raise ValueError(msg)

        except (requests.RequestException, requests.Timeout) as e:
            if attempt < max_retries:
                # Exponential backoff with jitter
                sleep_time = retry_delay * (2**attempt) * (0.5 + 0.5 * random.random())  # noqa: S311 not used for crypto
                time.sleep(sleep_time)
            else:
                msg = (
                    "Failed to reach https://mermaid.ink/ API while trying to render "
                    f"your graph after {max_retries} retries. "
                ) + error_msg_suffix
                raise ValueError(msg) from e

    # This should not be reached, but just in case
    msg = (
        "Failed to reach https://mermaid.ink/ API while trying to render "
        f"your graph after {max_retries} retries. "
    ) + error_msg_suffix
    raise ValueError(msg)

def generate_workflow_png():
    """Generate and save the legal agent workflow graph as a PNG file."""
    
    # Load API key from environment
    api_key = os.getenv("APERTUS_API_KEY")
    
    if not api_key:
        print("⚠️  APERTUS_API_KEY not found in environment")
        print("💡 Loading from .env file...")
        
        # Try to load from .env file (look in project root)
        env_path = os.path.join(project_root, ".env")
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                for line in f:
                    if line.startswith('APERTUS_API_KEY='):
                        api_key = line.split('=', 1)[1].strip().strip('"\'')
                        break
    
    if not api_key:
        print("❌ No API key found. Please set APERTUS_API_KEY in environment or .env file")
        return None
        
    print(f"🔑 Using API key: {api_key[:8]}...")
    
    try:
        print("🤖 Creating legal agent...")
        agent = create_legal_agent(api_key=api_key)
        
        print("📊 Generating workflow diagram...")
        
        # Get Mermaid syntax from the graph
        mermaid_syntax = agent.get_graph().draw_mermaid()
        print("✓ Generated Mermaid syntax")
        
        # First save the Mermaid syntax for reference
        mermaid_file = "swiss_legal_agent_workflow.mmd"
        with open(mermaid_file, 'w', encoding='utf-8') as f:
            f.write(mermaid_syntax)
        print(f"📄 Mermaid syntax saved: {mermaid_file}")
        
        # Generate PNG using custom function without proxies
        filename = "swiss_legal_agent_workflow.png"
        print(f"🖼️  Rendering PNG: {filename}")
        
        png_data = draw_mermaid_png(
            mermaid_syntax=mermaid_syntax,
            output_file_path=filename,
            background_color="white",
            file_type="png",
            max_retries=5,
            retry_delay=2.0,
            proxies={}  # No proxies
        )
        
        # File is already saved by draw_mermaid_png function
        full_path = os.path.abspath(filename)
        print("✅ Graph PNG saved successfully!")
        print(f"📁 PNG File: {filename}")
        print(f"� Mermaid File: {mermaid_file}")
        print(f"� Full path: {full_path}")
        print(f"📏 PNG size: {len(png_data)} bytes")
        
        return full_path
        
    except Exception as e:
        print(f"❌ Failed to generate PNG: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure graphviz is installed: uv add graphviz")
        print("2. Install system graphviz: sudo apt-get install graphviz")
        print("3. Check API key is valid")
        return None

if __name__ == "__main__":
    print("🇨🇭 Swiss Legal Analysis Agent - PNG Generator")
    print("=" * 50)
    generate_workflow_png()
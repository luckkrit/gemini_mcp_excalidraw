"""
gemini_to_excalidraw.py
-----------------------
Sends a text description to Gemini → Excalidraw elements JSON →
add_elements via excalidraw-mcp → clean diagram in browser canvas.

Requirements:
    pip install google-genai mcp python-dotenv

Usage:
    python gemini_to_excalidraw.py
    python gemini_to_excalidraw.py --prompt "Draw a 3-tier web architecture"
    python gemini_to_excalidraw.py --prompt "Draw a 3-tier web architecture" --output arch.excalidraw
"""
import asyncio
import argparse
import json
import math
import os
import random
import re
import sys
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from excalidraw_rules import get_system_prompt, detect_diagram_type
from sanitize_elements import sanitize_elements, fix_elements

# ─────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE")
GEMINI_MODEL   = os.getenv("GEMINI_MODEL", "YOUR_GEMINI_MODEL_HERE")




# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────
def dump_result(label: str, result) -> None:
    print(f"\n  ┌─ {label} ───────────────────────────────────")
    if not result.content:
        print("  │  (empty)")
    for i, block in enumerate(result.content):
        kind = getattr(block, "type", type(block).__name__)
        text = getattr(block, "text", repr(block))
        print(f"  │  [{i}] type={kind}")
        print(f"  │      {text[:600]}")
    print(f"  │  isError={getattr(result, 'isError', False)}")
    print(f"  └────────────────────────────────────────────\n")


# ─────────────────────────────────────────────
# Step 1: Gemini → Excalidraw elements JSON
# ─────────────────────────────────────────────
def generate_elements(user_prompt: str, system_prompt: str) -> list:
    client = genai.Client(api_key=GEMINI_API_KEY)
    print(f"[1/2] Sending to Gemini ({GEMINI_MODEL})...")
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
        ),
    )
    raw = response.text.strip()
    # Strip accidental markdown fences
    raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.MULTILINE)
    raw = re.sub(r"```\s*$",          "", raw, flags=re.MULTILINE)
    raw = raw.strip()

    print(f"\n── Raw Gemini output (first 500 chars) ─────\n{raw[:500]}\n────────────────────────────────────────────\n")

    elements = json.loads(raw)   # raises if Gemini returned bad JSON
    print(f"      ✔ Parsed {len(elements)} raw elements from Gemini")

    

    return elements




# ─────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt",  "-p", type=str, default=None)
    parser.add_argument("--session", "-s", type=str, default="gemini-diagram")
    parser.add_argument("--output",  "-o", type=str, default=None)
    args = parser.parse_args()

    if GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
        sys.exit("❌  Set GEMINI_API_KEY environment variable.")

    user_prompt = args.prompt or input("📝 Enter diagram description: ").strip()
    if not user_prompt:
        sys.exit("❌  No prompt provided.")


    
    diagram_type = detect_diagram_type(user_prompt)   # or pass explicitly
    system_prompt = get_system_prompt(diagram_type)

    # Step 1 — Gemini
    elements = generate_elements(user_prompt,system_prompt)
    
    print(f"[2/2] Santize elements")
    # Step 2 — Sanitize
    elements = sanitize_elements(elements)
    
    elements = fix_elements(elements) 

    excalidraw_file = {
            "type": "excalidraw",
            "version": 2,
            "source": "https://fastapi-gemini-app.com",
            "elements": elements,
            "appState": {"viewBackgroundColor": "#ffffff"},
            "files": {}
        }
    
    with open("arch.excalidraw", "w") as f:
        json.dump(excalidraw_file, f, ensure_ascii=False)
   


if __name__ == "__main__":
    main()
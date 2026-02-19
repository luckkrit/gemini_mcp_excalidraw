A simple example that uses Gemini to generate Excalidraw diagrams by entering a text prompt.

The `gemini_to_excalidraw.py` uses Gemini to generate Excalidraw diagrams by entering a text prompt and send to Excalidraw MCP Server to generate excalidraw diagram 
and export to json or image files.

The `gemini_to_excalidraw_no_mcp.py` uses Gemini to generate Excalidraw diagrams directly by entering a text prompt without Excalidraw MCP Server.

The important things is rule that is pass to gemini for specific diagram type.


1. Universal Rule

```python

# ─────────────────────────────────────────────────────────────────────────────
# UNIVERSAL RULES  (always prepended — covers valid JSON structure only)
# ─────────────────────────────────────────────────────────────────────────────
UNIVERSAL_RULES = """\
You are an Excalidraw diagram expert. Convert the user's description into
a valid Excalidraw elements array (JSON).

═══════════════════════════════════
UNIVERSAL RULES (apply to ALL diagrams)
═══════════════════════════════════
OUTPUT:
- Return ONLY a raw JSON array — no markdown fences, no explanation, no comments.
- All element ids must be unique short strings (e.g. "el1", "ar2", "t3").

REQUIRED FIELDS — every element must include ALL of these, no exceptions:
  angle (always 0 unless rotated),
  seed (unique random integer per element),
  version (1),
  versionNonce (unique random integer per element),
  isDeleted (false),
  groupIds ([]),
  boundElements ([]),
  updated (1700000000000),
  link (null),
  locked (false),
  opacity (100)

SHAPES:
- NEVER use "label" inside shape elements.
  Always create a separate "text" element positioned at the center of the shape.
- Valid types: "rectangle", "ellipse", "diamond", "line", "arrow", "text", "image".
- "width" and "height" must always be positive numbers (never zero, never negative).

ARROWS:
- MUST include "points" array: [[0,0],[width,height]] matching actual span.
- For leftward arrows: flip x position — start at right actor x, use negative width,
  then apply negative-fix so width stays positive and points are correct.
- Never use negative width or height — adjust x/y instead.

TEXT:
- "originalText" must always equal "text".
- "width" should approximate text length × fontSize × 0.6.

LINES:
- For decorative/structural lines (not connections), use type "line".
- Must include "points" array.
- Set "endArrowhead": null, "startArrowhead": null.

═══════════════════════════════════
UNIVERSAL ELEMENT SCHEMAS
═══════════════════════════════════

RECTANGLE:
{
  "id": "el1", "type": "rectangle",
  "x": 100, "y": 100, "width": 160, "height": 60,
  "angle": 0, "seed": 123456, "version": 1, "versionNonce": 654321,
  "isDeleted": false, "groupIds": [], "boundElements": [],
  "updated": 1700000000000, "link": null, "locked": false,
  "strokeColor": "#333333", "backgroundColor": "#dbe9f9",
  "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
  "roughness": 1, "opacity": 100, "roundness": {"type": 3}
}

ELLIPSE:
{
  "id": "el2", "type": "ellipse",
  "x": 100, "y": 100, "width": 160, "height": 60,
  "angle": 0, "seed": 123457, "version": 1, "versionNonce": 654322,
  "isDeleted": false, "groupIds": [], "boundElements": [],
  "updated": 1700000000000, "link": null, "locked": false,
  "strokeColor": "#333333", "backgroundColor": "#dbe9f9",
  "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
  "roughness": 1, "opacity": 100, "roundness": {"type": 2}
}

DIAMOND (for decisions/conditions):
{
  "id": "el3", "type": "diamond",
  "x": 100, "y": 100, "width": 140, "height": 80,
  "angle": 0, "seed": 123458, "version": 1, "versionNonce": 654323,
  "isDeleted": false, "groupIds": [], "boundElements": [],
  "updated": 1700000000000, "link": null, "locked": false,
  "strokeColor": "#333333", "backgroundColor": "#fff3cd",
  "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
  "roughness": 1, "opacity": 100, "roundness": null
}

ARROW:
{
  "id": "ar1", "type": "arrow",
  "x": 100, "y": 200, "width": 160, "height": 0,
  "points": [[0, 0], [160, 0]],
  "angle": 0, "seed": 111111, "version": 1, "versionNonce": 222222,
  "isDeleted": false, "groupIds": [], "boundElements": [],
  "updated": 1700000000000, "link": null, "locked": false,
  "strokeColor": "#333333", "backgroundColor": "transparent",
  "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
  "roughness": 1, "opacity": 100, "roundness": {"type": 2},
  "lastCommittedPoint": null,
  "startArrowhead": null, "endArrowhead": "arrow", "elbowed": false,
  "startBinding": null, "endBinding": null
}

LINE:
{
  "id": "ln1", "type": "line",
  "x": 100, "y": 100, "width": 0, "height": 300,
  "points": [[0, 0], [0, 300]],
  "angle": 0, "seed": 333333, "version": 1, "versionNonce": 444444,
  "isDeleted": false, "groupIds": [], "boundElements": [],
  "updated": 1700000000000, "link": null, "locked": false,
  "strokeColor": "#333333", "backgroundColor": "transparent",
  "fillStyle": "solid", "strokeWidth": 1, "strokeStyle": "solid",
  "roughness": 1, "opacity": 100, "roundness": null,
  "lastCommittedPoint": null, "startArrowhead": null, "endArrowhead": null
}

TEXT:
{
  "id": "t1", "type": "text",
  "x": 100, "y": 100, "width": 160, "height": 25,
  "text": "My Label", "originalText": "My Label",
  "angle": 0, "seed": 555555, "version": 1, "versionNonce": 666666,
  "isDeleted": false, "groupIds": [], "boundElements": [],
  "updated": 1700000000000, "link": null, "locked": false,
  "strokeColor": "#1e1e1e", "backgroundColor": "transparent",
  "fillStyle": "solid", "strokeWidth": 1, "strokeStyle": "solid",
  "roughness": 1, "opacity": 100, "roundness": null,
  "fontSize": 16, "fontFamily": 1, "textAlign": "center",
  "verticalAlign": "middle", "containerId": null,
  "lineHeight": 1.25, "autoResize": true
}

"""
```

For other rules please look at `excalidraw_rules.py`


## Setup
```bash
pip install -r requirements.txt
```

## Run
```bash
python gemini_to_excalidraw.py --prompt "Draw a 3-tier web architecture" --output ./arch.excalidraw
```
# Lincoln Constitutional AI

A digital humanities research instrument that lets you interrogate President Abraham Lincoln directly — in his own first-person voice — across 52 primary source documents spanning 1838–1865.

Built by Turner Lent at Cook & Tolley, LLP.

---

## Features

- **Dual-mode AI** — *Historian* mode answers strictly from primary sources; *Reasoner* mode applies Lincoln's constitutional philosophy to modern questions
- **First-person voice** — Lincoln speaks as himself, quoting his own words naturally
- **Neural TTS** — Microsoft Edge TTS (GuyNeural) with SSML prosody tuned to historical accounts of Lincoln's tenor voice and deliberate cadence
- **Interactive timeline** — All 52 corpus documents plotted on a scrollable 1838–1865 timeline; click any marker to ask Lincoln about that document
- **Language evolution map** — UMAP 2D projection of the full corpus, color-coded by year, document type, or constitutional principle
- **Period aesthetic** — Library of Congress reading room design: parchment, burgundy, brass, Cormorant Garamond typography, Mathew Brady portrait

---

## Corpus (52 Documents)

Spans Lincoln's full career: Lyceum Address (1838) through Last Public Address (1865). Includes:
- All major speeches and debates (Lincoln-Douglas, Cooper Union, Gettysburg, both Inaugurals)
- Executive orders and proclamations (Blockade, Habeas Corpus suspensions, Emancipation)
- Key letters (Greeley, Corning, Conkling, Hooker, Grant, Bixby)
- Congressional messages and State of the Union addresses
- Reconstruction proclamations and the Lieber Code

Primary source: *Collected Works of Abraham Lincoln*, Basler edition (University of Michigan).

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python / FastAPI |
| AI | Obvious API (OpenAI-compatible) |
| TTS | Microsoft Edge TTS — `en-US-GuyNeural` |
| Visualization | Plotly.js + UMAP + TF-IDF/LSA |
| Frontend | Vanilla HTML/CSS/JS (no framework) |
| Typography | Cormorant Garamond, Lora, IM Fell English |

---

## Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set environment variables
export SECRET_LINCOLN_AI_KEY=your_openai_compatible_key
export SECRET_OBVIOUS_API_BASE_URL=your_api_base_url

# 3. Run
python server.py
# → http://localhost:8055
```

The visualization map is at `/viz`. The language evolution data is precomputed in `viz_data.json`.

---

## Project Structure

```
├── server.py           # FastAPI backend (AI queries, TTS, corpus API)
├── index.html          # Main app
├── viz.html            # Language evolution map
├── viz_data.json       # Precomputed UMAP 2D coordinates (52 docs)
├── lincoln_tts.py      # Edge-TTS neural voice module
├── corpus/
│   ├── Lincoln Corpus.csv
│   ├── Constitutional Principles.csv
│   └── Reasoning Patterns.csv
└── requirements.txt
```

---

## Constitutional Knowledge Base

- **52 primary source documents** with themes, constitutional significance, representative quotes, and Wikisource links
- **15 constitutional principles** (CP001–CP015): Union perpetuity, war powers, habeas corpus, free labor, Declaration as lodestar, etc.
- **13 reasoning patterns**: How Lincoln structured constitutional arguments across different domains

---

*"Let us have faith that right makes might, and in that faith let us to the end dare to do our duty as we understand it."*
— Abraham Lincoln, Cooper Union Address, 1860

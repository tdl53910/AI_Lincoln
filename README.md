# Lincoln Constitutional AI

A digital humanities research instrument for computational constitutional history. This system enables direct interrogation of Abraham Lincoln's political and constitutional thought through primary source documents spanning his entire public career (1838–1865).

**Live Site**: [https://0qfzch9rk9-8055.hosted.obvious.ai](https://0qfzch9rk9-8055.hosted.obvious.ai)

---

## 🔍 Overview

The Lincoln Constitutional AI project applies computational methods—semantic embedding, dimensionality reduction, and large language models—to the study of presidential rhetoric and constitutional interpretation. It provides scholars, students, and researchers with two complementary modes of inquiry:

| Mode | Function |
|------|----------|
| **Historian** | Answers factual questions strictly from Lincoln's documented writings, speeches, and official acts. Responses quote primary sources directly and include citations. |
| **Reasoner** | Applies Lincoln's constitutional principles and reasoning patterns to modern questions of governance, federalism, and executive power. Explicitly distinguishes between historical positions and their contemporary application. |

---

## ✨ Features

### Dual-Mode Architecture
- **Historian Mode**: Strict primary-source grounding with verbatim quotations and document citations
- **Reasoner Mode**: Applies Lincoln's constitutional principles and reasoning patterns to contemporary questions

### First-Person Voice
Lincoln speaks as himself, quoting his own words naturally—not as a chatbot impersonation, but as a scholarly reconstruction grounded in the documentary record.

### Neural Text-to-Speech
Microsoft Edge TTS (en-US-GuyNeural) with SSML prosody tuned to historical accounts of Lincoln's voice:
- Tenor range (higher pitch than expected for a tall man)
- Deliberate, measured cadence
- Kentucky-Indiana frontier rhythm with rising emphasis at key rhetorical moments

### Interactive Visualizations
- **Timeline Explorer**: Documents plotted chronologically (1838–1865); click any marker to ask Lincoln about that document
- **Language Evolution Map**: UMAP 2D projection of the corpus, color-coded by year, document type, or constitutional principle
- **Semantic Drift Analysis**: Visualizes how Lincoln's constitutional language evolved across his career

### Period-Aesthetic Interface
Library of Congress reading room design: parchment textures, burgundy and brass accents, Cormorant Garamond typography, and Mathew Brady's iconic portrait.

---

## 📚 Corpus

The knowledge base comprises primary source documents from the *Collected Works of Abraham Lincoln* (Basler edition, University of Michigan), carefully selected to represent the full arc of Lincoln's constitutional thought.

### Document Types
- Speeches (Lyceum Address, Gettysburg Address, Cooper Union)
- Debates (Lincoln-Douglas Debates)
- Letters (Greeley, Corning, Conkling, Hodges, Bixby)
- Executive Orders & Proclamations (Blockade Proclamation, Habeas Corpus Suspensions, Emancipation Proclamation)
- Messages to Congress (Annual Messages, Special Session Message)
- Inaugural Addresses (First, Second)
- Fragments & Memoranda

### Chronological Scope
- **Earliest**: Lyceum Address (January 27, 1838)
- **Latest**: Last Public Address (April 11, 1865)
- **Coverage**: Full span of Lincoln's public life

### Key Themes
- Union perpetuity and secession
- Executive power in wartime
- Habeas corpus and civil liberties
- Emancipation and the Thirteenth Amendment
- Declaration of Independence as constitutional lodestar
- Free labor ideology and economic liberty
- Reconstruction and reconciliation

---

## 🧠 Methodology

### Semantic Embedding Pipeline
Documents are embedded using `all-MiniLM-L6-v2`, creating vector representations that capture semantic content independent of specific word choice.

### Dimensionality Reduction
UMAP (Uniform Manifold Approximation and Projection) projects the high-dimensional semantic space into 2D for visualization, preserving both local and global structure.

### Constitutional Principle Extraction
Constitutional principles were inductively derived from close reading of the corpus, each with:
- Textual basis in specific documents
- Scholarly corroboration (Fehrenbacher, Foner, Guelzo, Jaffa, Zarefsky)
- Applicability to modern constitutional questions

### Reasoning Pattern Analysis
Recurring argumentative structures were identified across Lincoln's rhetorical repertoire, including:
- Means-ends constitutional reasoning
- Historical precedent invocation
- Founders' intent arguments
- Slippery slope construction
- Moral-constitutional synthesis

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Backend** | Python / FastAPI | API server, request routing, corpus access |
| **AI/LLM** | Obvious API (OpenAI-compatible) | Constitutional reasoning and response generation |
| **Embeddings** | sentence-transformers/all-MiniLM-L6-v2 | Document vectorization for semantic visualization |
| **TTS** | Microsoft Edge TTS (en-US-GuyNeural) | Neural voice synthesis with historical prosody |
| **Visualization** | Plotly.js + UMAP | Interactive language evolution map |
| **Frontend** | Vanilla HTML/CSS/JavaScript | No framework—lightweight, self-contained |
| **Typography** | Cormorant Garamond, Lora, IM Fell English | Period-appropriate aesthetic |
| **Deployment** | Obvious Hosting | Live demo hosting |

---

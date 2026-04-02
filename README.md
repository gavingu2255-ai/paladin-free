# Paladin-AI-free

`paladin-free` is the open-source surface of the Paladin architecture — a minimal, modular, and structurally transparent framework designed for experimentation, extension, and public-facing development. This repository intentionally exposes only the free-tier, non-sovereign layers of the broader system.

---

## Vision

`paladin-free` is built around four principles:

- **Minimalism** — no unnecessary dependencies or heavy runtime assumptions  
- **Composability** — modules can be rearranged, extended, or embedded  
- **Transparency** — structure is favored over cleverness or opacity  
- **Safety** — no closed-world engines, no subjectivity simulation, no high‑risk logic  

The goal is to provide a clean, understandable foundation without exposing sovereign or private runtime layers.

---

## Case Study: Layer-by-Layer Testing  
This section demonstrates how each Paladin-Free layer can be tested independently.  
**STP is included here for completeness, but it is used ONLY in LLM chat mode and is NOT included in the agentic version.**

---

### STP Layer — Structural Topology Protocol (LLM‑Only)  
**Test Prompt**  
```
Code: Keep a neutral stance and avoid emotional mirroring.
```

**Expected Behavior**  
- Stabilizes tone and stance  
- Prevents polarity, bias, or emotional drift  
- Ensures consistent LLM behavior across long conversations  

**Why It Matters**  
- Lightweight stance-stabilization layer  
- Designed specifically for LLM chat systems  
- **Not included in the agentic version** (agentic mode requires full autonomy and no stance override)

---

### 1. SLP Layer — Structural Language Parser  
**Test Prompt**  
```
Code: Describe a red ball on a wooden table.
```

**Expected Behavior**  
- Extracts objects: `ball`, `table`  
- Extracts attributes: `red`, `wooden`  
- Extracts relations: `on(top_of)`  

**Why It Matters**  
- Fully deterministic  
- No model dependency  
- Converts natural language into a structural graph  
- Foundation for all higher‑level reasoning  

---

### 2. WLM Layer — World Model Interpreter  
**Test Prompt**  
```
Code: Where is the cat relative to the chair?
```

**Expected Behavior**  
- Identifies entities: `cat`, `chair`  
- Infers spatial relations (e.g., `left_of`, `near`, `behind`)  
- Produces a structured world‑state  

**Why It Matters**  
- Builds a world, not just an answer  
- Deterministic relational inference  
- Enables persistent reasoning across turns  

---

### 3. Knowledge Layer — Declarative Knowledge Retrieval  
**Test Prompt**  
```
Code: Why does the sun shine?
```

**Expected Behavior**  
- Retrieves concise factual knowledge  
- No hallucination  
- No unnecessary elaboration  

**Why It Matters**  
- Knowledge is modular and auditable  
- Can be replaced with your own knowledge base  
- Ensures factual stability across the system  

---

### 4. Persona Layer — Tone & Style Filter  
**Test Prompt**  
```
Code: Explain this in a friendly tone.
```

**Expected Behavior**  
- Content stays the same  
- Tone shifts to “friendly”  
- No structural distortion  

**Why It Matters**  
- Persona is a post‑processing layer  
- Does not contaminate logic or reasoning  
- Fully replaceable and controllable  

---

### 5. Metacognition Layer — Reasoning Transparency  
**Test Prompt**  
```
Code: Explain your reasoning step by step.
```

**Expected Behavior**  
- Outputs a structured reasoning trace  
- Does not reveal internal prompts  
- Does not leak system instructions  

**Why It Matters**  
- Transparent reasoning without chain‑of‑thought leakage  
- Auditable and compressible  
- Safe for production environments  

---

### 6. Behavior Layer — Action Selection  
**Test Prompt**  
```
Code: What should I do next?
```

**Expected Behavior**  
- Provides structured next‑step options  
- No prescriptive decisions  
- No unsafe or overreaching suggestions  

**Why It Matters**  
- Suggestion‑level, not decision‑level  
- Fully controllable  
- Ideal for agentic or semi‑agentic systems  

---

### 7. WGP Layer — World Generation Pipeline  
**Test Prompt**  
```
Code: Generate a tiny imaginary world.
```

**Expected Behavior**  
- Produces a structured mini‑world  
- Includes objects, relations, and rules  
- Suitable for simulation or agent environments  

**Why It Matters**  
- Not storytelling — world‑building  
- Deterministic structural generation  
- Extensible to games, agents, or simulations  

---

### Shadow Memory — Structural Memory  
**Test Prompt**  
```
Code: A cat sits on a mat.
```
Then:
```
Code: Where is the cat?
```

**Expected Behavior**  
- Stores world‑state  
- Answers from structural memory, not chat history  

**Why It Matters**  
- Memory is world‑based, not text‑based  
- Enables persistent reasoning  
- Avoids hallucinated recall  

---

### Full Memory — Conversation Log  
**Test Prompt**  
```
Code: Hello.
```
Then:
```
Code: What did I just say?
```

**Expected Behavior**  
- Returns the last user message  
- Does not mix with structural memory  

**Why It Matters**  
- Clean separation of “world memory” and “chat memory”  
- Ideal for debugging and UI layers  

---

### Surface Realizer — Final Output Layer  
**Test Prompt**  
```
Code: Explain gravity.
```

**Expected Behavior**  
- Converts structured content into natural language  
- Does not add new information  
- Does not modify structure  

**Why It Matters**  
- Predictable and controllable output  
- Style can be swapped without touching logic  
- Ensures clean separation between structure and appearance  

---

### Full Pipeline Test — All Layers Combined  
**Test Prompt**  
```
Code: In a friendly tone, explain how a bird flies, then generate a tiny imaginary world where the bird lives.
```

**Expected Behavior**  
- SLP → WLM → Knowledge → Persona → Behavior → WGP → Realizer  
- Produces a complete structured world + readable output  

**Why It Matters**  
- Demonstrates the entire Paladin pipeline  
- Shows deterministic structure → appearance flow  
- Proves Paladin‑Free is a real runtime, not a wrapper  

---
## Repository Structure

The project is organized into clear, purpose-driven layers:

```
paladin-free/
├── backend/
│   ├── main.py
│   ├── personal_profile/
│   ├── runtime/
│   ├── shadow/
│   └── __pycache__/
├── frontend/
│   ├── index.html
│   ├── app.js
│   ├── lights.js
│   └── style.css
├── shared/
│   └── dimension_rules.json
├── personal_profile/
├── paladin-free/
├── venv/
├── .gitignore
├── .gitattributes
├── Case study.txt
└── tree.txt
```



---

## Backend Overview

The backend contains several modular subsystems:

- **runtime/** — core operational modules  
  - behavior  
  - file intelligence  
  - knowledge  
  - metacognition  
  - persona  
  - slp / stp / wgp / wlm  
  - workflow  
  - world simulation  
  - llm client, orchestrator, utils, types  

- **shadow/** — structural adapters and surface realizer  
  - chat wrapper  
  - structural memory  
  - full memory  
  - orchestrator  
  - slp → wlm adapter  

- **personal_profile/** — profile data and structural memory JSON  

Each module is isolated and extendable, allowing developers to integrate or replace components without modifying core invariants.

---

## Frontend Overview

The frontend is intentionally lightweight:

- `index.html` — base UI  
- `app.js` — interaction logic  
- `lights.js` — visual effects  
- `style.css` — styling  

It serves as a simple interface layer for interacting with backend logic.

---

## Getting Started

### 1. Clone the repository

git clone git clone git clone https://github.com/gavingu2255-ai/paladin-free.git

cd paladin-free

Code

### 2. Explore the backend

- Begin with `backend/main.py`  
- Review modules inside `backend/runtime/` and `backend/shadow/`  
- Follow the structure rather than treating the system as a black box  

### 3. Extend or integrate

- Add new runtime modules  
- Create adapters or bridges  
- Build additional frontend interfaces  
- Keep sovereign or private logic in separate repositories  

---

## Design Principles

- **Structure over behavior** — the architecture is the primary artifact  
- **Explicit boundaries** — public vs private, free vs sovereign  
- **Append‑only evolution** — prefer adding layers over mutating invariants  
- **Readable over clever** — clarity is prioritized over abstraction  

---

## License

This repository currently does not include a finalized license file.  
You may later add:

- MIT  
- Apache 2.0  
- or a custom Paladin License  

Until a license is added, treat the code as **all rights reserved**.

---

## Contributing

Contributions are welcome, especially in areas such as:

- structural clarity  
- modularity and extension points  
- documentation  
- safe public-layer patterns  

---

## Roadmap

Potential future additions include:

- clearer module boundaries and diagrams  
- example integrations  
- optional higher-level utilities  
- documentation of structural patterns and anti-patterns  

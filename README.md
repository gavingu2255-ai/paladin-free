# paladin-free

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

## Repository Structure

The project is organized into clear, purpose-driven layers:

'''
    paladin-free/
    │
    ├── backend/
    │   ├── main.py
    │   ├── personal_profile/
    │   ├── runtime/
    │   ├── shadow/
    │   └── __pycache__/
    │
    ├── frontend/
    │   ├── index.html
    │   ├── app.js
    │   ├── lights.js
    │   └── style.css
    │
    ├── shared/
    │   └── dimension_rules.json
    │
    ├── personal_profile/
    │
    ├── paladin-free/
    │
    ├── venv/
    │
    ├── .gitignore
    ├── .gitattributes
    ├── Case study.txt
    └── tree.txt
'''

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

git clone https://github.com/<your-username>/paladin-free.git
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

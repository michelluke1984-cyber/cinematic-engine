# 🎬 Cinematic Engine V17.2 — Enterprise AI Orchestration Platform

<div align="center">

![Version](https://img.shields.io/badge/version-V17.2-f5a623?style=flat-square)
![Python](https://img.shields.io/badge/python-3.10%2B-3776ab?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-00ff88?style=flat-square)
![GPU](https://img.shields.io/badge/GPU-CUDA%20T4%2B-76b900?style=flat-square)
![Status](https://img.shields.io/badge/status-production%20ready-00d4ff?style=flat-square)

**A professional control system and real-time dashboard for cinematic AI image generation.**  
Orchestrates FLUX · SDXL · ControlNet · FaceID · LoRA with 26 managed tasks,  
distributed workers, AI Copilot, version control, and live WebSocket integration.

[Open Dashboard](cinematic_engine_v17_2_final.html) · [Colab Quickstart](cev17_colab.ipynb) · [Landing Page](cev17_landing.html)

</div>

---

## Table of Contents

- [What Is This?](#what-is-this)
- [Project Structure](#project-structure)
- [Quick Start — Google Colab](#quick-start--google-colab-5-minutes)
- [Quick Start — Local GPU](#quick-start--local-gpu)
- [Dashboard Reference](#dashboard-reference)
- [WebSocket Bridge API](#websocket-bridge-api)
- [Plugin System](#plugin-system)
- [AI Copilot Commands](#ai-copilot-commands)
- [Execution Modes](#execution-modes)
- [Version History](#version-history)
- [Troubleshooting](#troubleshooting)
- [Architecture](#architecture)

---

## What Is This?

Cinematic Engine is a **two-part system**:

| Component | File | Description |
|-----------|------|-------------|
| **Dashboard** | `cinematic_engine_v17_2_final.html` | Browser UI — runs anywhere, zero dependencies |
| **Engine** | `cinematic_engine_v16_pro.py` | Python AI engine — runs on GPU (Colab / local) |
| **Bridge** | `cev17_backend.py` | WebSocket server — connects Dashboard ↔ Engine |
| **Notebook** | `cev17_colab.ipynb` | One-click Colab setup |

The Dashboard works **standalone in simulation mode** without the Engine.  
Connect the Bridge to get **real GPU metrics, real task execution, and live image generation**.

---

## Project Structure

```
cinematic-engine/
│
├── cinematic_engine_v17_2_final.html   ← Dashboard (open in browser)
├── cinematic_engine_v16_pro.py         ← AI Engine (run on GPU)
├── cev17_backend.py                    ← WebSocket Bridge (connects both)
├── cev17_colab.ipynb                   ← Google Colab notebook
├── cev17_landing.html                  ← Product landing page
│
├── README.md                           ← This file
├── DEPLOYMENT.md                       ← Detailed deployment guide
├── PLUGIN_SPEC.md                      ← Plugin development reference
├── CHANGELOG.md                        ← Version history
│
└── v16_cinematic_storyboard/           ← Generated output directory
    ├── scene_001.png
    ├── scene_001.json
    └── storyboard_YYYYMMDD.zip
```

---

## Quick Start — Google Colab (5 minutes)

**Requirements:** Google account, T4 GPU (free tier works)

### Step 1 — Open the Colab Notebook

1. Upload `cev17_colab.ipynb` to [colab.research.google.com](https://colab.research.google.com)
2. `Runtime → Change runtime type → T4 GPU → Save`

### Step 2 — Upload Required Files

In the Colab file panel (📁 left sidebar), upload:
- `cinematic_engine_v16_pro.py`
- `cev17_backend.py`

### Step 3 — Run Cell 1: Setup

```python
# Installs all packages + downloads model weights
# Takes 3–5 minutes on first run, cached afterwards
▶ Run Cell 1
```

Expected output:
```
✓ GPU: Tesla T4 | VRAM: 15.0 GB
✓ Recommended: FLUX SCHNELL
  Installing diffusers… ✓
  Installing GFPGAN… ✓
  ...
══════════════════════════════════════════
  ✓ SETUP COMPLETE — ready to run Cell 2
══════════════════════════════════════════
```

### Step 4 — Run Cell 2: Load Engine

```python
▶ Run Cell 2
```

Expected output:
```
[ENGINE] Initialising CinematicEngineV16…
[ENGINE] ✓ Ready — models not loaded yet
```

### Step 5 — Run Cell 3: Start Bridge

```python
# In Cell 3, keep USE_NGROK = False for local access
▶ Run Cell 3
```

Expected output:
```
════════════════════════════════════════════════════════════
  CINEMATIC ENGINE V17 BRIDGE — STARTING
  WebSocket: ws://0.0.0.0:7860
  Engine:    CONNECTED ✓
  GPU:       CUDA ✓
════════════════════════════════════════════════════════════
  Open the V17.2 Dashboard HTML and click 'WS: OFF' to connect
════════════════════════════════════════════════════════════
```

### Step 6 — Open the Dashboard

Open `cinematic_engine_v17_2_final.html` in your browser.  
Click **`WS: OFF`** in the header → it turns **`WS: LIVE ✓`** (green).

The Dashboard immediately shows real GPU metrics and all tasks become executable.

---

## Quick Start — Local GPU

**Requirements:** Python 3.10+, CUDA GPU (8GB+ VRAM recommended), CUDA 11.8+

```bash
# 1. Clone / download the project
git clone https://github.com/your-repo/cinematic-engine
cd cinematic-engine

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate          # Linux/Mac
# venv\Scripts\activate           # Windows

# 3. Install PyTorch (match your CUDA version)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# 4. Install all dependencies
pip install -r requirements.txt

# 5. Run the engine
python cinematic_engine_v16_pro.py &

# 6. Run the bridge (in a second terminal)
python cev17_backend.py

# 7. Open the dashboard
# Open cinematic_engine_v17_2_final.html in your browser
# Click WS: OFF → WS: LIVE ✓
```

### requirements.txt

```
diffusers>=0.27.0
transformers>=4.38.0
accelerate>=0.27.0
xformers>=0.0.24
triton>=2.2.0
einops>=0.7.0
gfpgan>=1.3.8
realesrgan>=0.3.0
tqdm>=4.66.0
sentencepiece>=0.1.99
nltk>=3.8.0
controlnet-aux>=0.0.7
open-clip-torch>=2.24.0
gradio>=4.0.0
bitsandbytes>=0.41.0
Pillow>=10.0.0
insightface>=0.7.3
onnxruntime-gpu>=1.17.0
websockets>=12.0
pyngrok>=7.0.0
numpy>=1.24.0
```

---

## Dashboard Reference

The Dashboard has **3 panels** and **14 views**:

### Left Sidebar (always visible)

| Section | Content |
|---------|---------|
| ⚡ Real-Time Metrics | GEN TIME · MODEL LOAD · VRAM FREE · QUEUE DEPTH · THROUGHPUT · WORKERS |
| 🖥 Worker Nodes | 3 workers (2 Local + 1 Remote) with load bars and status dots |
| 📊 Progress Ring | Overall project completion % with gradient SVG ring |
| 🗂 Navigation | 9 view links with live counters |

### Center Area — 14 Views

| View | Access | Description |
|------|--------|-------------|
| ⚙ Task Control | Default | 26 tasks in 6 groups — RUN / RETRY / RESET per task |
| 🎼 Orchestrator | Sidebar | Execution levels, strategy selector, custom workflows |
| 📋 Task Queue | Sidebar | Live queue with worker assignments and timestamps |
| 🕐 Versions | Sidebar | Snapshots list, rollback, free diff picker |
| 🧩 Plugins | Sidebar | Load plugin.json, manage installed plugins |
| 👥 Sessions | Sidebar | Multi-session with rename, progress bars, isolation |
| 🤖 Auto-Optimize | Sidebar | VRAM/PERF/SPEED/CACHE recommendations with APPLY buttons |
| 🧠 Log Intelligence | Sidebar | AI-classified error patterns with fix suggestions |
| 🐛 Debug Monitor | Sidebar | Error counts, live log stream, export |
| 🕸 Workflow Builder | Header | Drag-and-drop canvas, auto-layout, PNG export |
| 📊 Monitor | Header | 4 real-time charts + smart alerts |
| 🏗 Enterprise | Header | K8s cluster, Docker config, live deployment health |
| 🔐 Security | Header | JWT auth, token rotation, security checklist |
| 🧩 Marketplace | Header | 6 plugins — install/remove with search |

### Right Panel — 4 Tabs

| Tab | Content |
|-----|---------|
| LOGS | Live log stream — all levels (INFO/OK/WARN/ERROR/DEBUG/WS/AI/ORCH) |
| COPILOT | AI chat — Arabic + English commands with multi-step plans |
| METRICS | `/metrics` JSON endpoint + timing history + auto-poll |
| QUEUE | Live task queue with worker assignments |

---

## Task Groups & Dependencies

```
SETUP ──────────────────────────────────────────────────────────
  setup_gpu [HIGH]     → no deps
  install_pkgs [HIGH]  → setup_gpu
  download_mdl [HIGH]  → install_pkgs
  nltk_data [MED]      → install_pkgs

ENGINE ─────────────────────────────────────────────────────────
  cuda_opt [HIGH]      → setup_gpu
  smart_cache [MED]    → cuda_opt
  vram_mgr [HIGH]      → cuda_opt
  logger_init [MED]    → cuda_opt

PIPELINES ──────────────────────────────────────────────────────
  load_flux_s [HIGH]   → vram_mgr, download_mdl   (7GB VRAM)
  load_flux_d [LOW]    → vram_mgr, download_mdl   (13GB VRAM)
  load_sdxl [MED]      → vram_mgr, download_mdl   (5.5GB VRAM)
  load_cn [LOW]        → load_sdxl                (3GB VRAM)
  load_gfpgan [MED]    → download_mdl
  load_esrgan [MED]    → download_mdl

IDENTITY ───────────────────────────────────────────────────────
  faceid_ext [MED]     → load_sdxl, download_mdl
  ip_adapter [MED]     → load_sdxl
  lora_mgr [MED]       → load_sdxl

PHYSICS ────────────────────────────────────────────────────────
  llm_load [MED]       → install_pkgs, vram_mgr   (8GB VRAM)
  neural_phys [MED]    → llm_load, smart_cache
  prompt_bld [MED]     → neural_phys

GENERATION ─────────────────────────────────────────────────────
  gen_config [HIGH]    → load_flux_s
  scene_chain [MED]    → gen_config, prompt_bld
  hires_fix [LOW]      → load_sdxl, vram_mgr      (4GB VRAM)
  run_generate [HIGH]  → scene_chain, hires_fix, gen_config

POST ───────────────────────────────────────────────────────────
  postproc [MED]       → run_generate, load_gfpgan, load_esrgan
  zip_export [MED]     → postproc
```

**Minimum path for FLUX SCHNELL generation (7 tasks):**
```
setup_gpu → install_pkgs → cuda_opt + vram_mgr + download_mdl
→ load_flux_s → gen_config → scene_chain → run_generate
```

---

## WebSocket Bridge API

The bridge listens on `ws://localhost:7860/ws` (configurable in `BridgeConfig`).

### Messages: Dashboard → Bridge

```json
{ "type": "exec_task", "task_id": "load_flux_s", "params": {} }
{ "type": "exec_task", "task_id": "run_generate",
  "params": {
    "scenes": ["A detective in rain-soaked alley"],
    "camera": "Low Angle",
    "lighting": "Neon Cyberpunk",
    "style": "Cinematic",
    "cfg": 8.5,
    "steps": 35
  }
}
{ "type": "get_metrics" }
{ "type": "flush_vram" }
{ "type": "get_session" }
{ "type": "ping" }
```

### Messages: Bridge → Dashboard

```json
{ "type": "task_update", "task_id": "load_flux_s", "state": "running" }
{ "type": "task_update", "task_id": "load_flux_s", "state": "complete",
  "data": { "model": "flux_schnell" } }
{ "type": "metrics", "data": {
    "gpu": "Tesla T4",
    "vram_total_gb": 15.0,
    "vram_used_gb": 7.2,
    "vram_free_gb": 7.8,
    "gen_time_ms": 3200,
    "active_model": "flux_schnell",
    "scenes_generated": 4,
    "throughput": 1.2
  }
}
{ "type": "log", "level": "ok", "message": "[GEN] Scene 1/4 done in 3200ms ✓" }
{ "type": "gen_result", "data": { "results": [...], "total": 4 } }
{ "type": "pong" }
```

### Python Integration Example

```python
# Attach bridge to a running engine instance
from cev17_backend import run_bridge

engine = CinematicEngineV16()
run_bridge(engine=engine, use_ngrok=False)
```

### Changing the WebSocket Port

In `cev17_backend.py`:
```python
class BridgeConfig:
    PORT = 8080   # change from default 7860
```

In `cinematic_engine_v17_2_final.html` (line ~1149):
```javascript
const WS_URL = 'ws://localhost:8080/ws';
```

---

## Plugin System

Plugins extend the Dashboard without modifying any core file.

### Plugin File Format (`plugin.json`)

```json
{
  "name": "My Custom Pipeline",
  "version": "1.0.0",
  "author": "Your Name",
  "tasks": [
    {
      "id": "my_task_001",
      "name": "Custom Processing Step",
      "desc": "Applies custom post-processing to generated images",
      "icon": "🔥",
      "g": "CUSTOM",
      "deps": ["postproc"],
      "pri": "medium",
      "est": 3000
    }
  ]
}
```

### Loading a Plugin

1. Open Dashboard → Sidebar → 🧩 Plugins
2. Drop `plugin.json` onto the drop zone, or click to browse
3. Tasks appear immediately in Task Control view under their group
4. Tasks are fully integrated into the dependency graph

### Removing a Plugin

Click the ✕ button next to the plugin name.  
**V17.2:** Tasks are fully removed from `TASK_DEFS`, `taskStates`, and all sessions.

### Field Reference

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | ✓ | Unique task identifier (alphanumeric + underscore) |
| `name` | string | ✓ | Display name in Dashboard |
| `desc` | string | ✓ | Technical description shown under name |
| `icon` | string | ✓ | Emoji icon for the task card |
| `g` | string | ✓ | Group label (creates new section if new) |
| `deps` | array | ✓ | Array of task IDs that must complete first |
| `pri` | string | ✓ | `"high"` / `"medium"` / `"low"` |
| `est` | number | ✓ | Estimated execution time in milliseconds |

---

## AI Copilot Commands

The Copilot panel and Command Bar accept natural language in Arabic and English.

### Command Bar (⌘ Input at top of Dashboard)

| Command | Arabic | Action |
|---------|--------|--------|
| `run all` / `نفذ الكل` | ✓ | Starts Production Mode |
| `reset` / `إعادة` | ✓ | Resets all tasks to idle |
| `parallel` / `موازي` | ✓ | Switches to Parallel execution mode |
| `sequential` / `متسلسل` | ✓ | Switches to Sequential mode |
| `dry run` / `محاكاة` | ✓ | Toggles Simulation Mode |
| `snapshot` / `نسخة` | ✓ | Saves a manual version snapshot |
| `high priority` / `أولوية عالية` | ✓ | Runs all HIGH priority tasks immediately |
| `vram` / `ذاكرة` | ✓ | Runs low-VRAM pipeline only |
| `fast` / `سريع` | ✓ | Runs core engine tasks only |
| `status` / `حالة` | ✓ | Shows progress toast |
| `export` / `تصدير` | ✓ | Opens export modal |
| Any other text | — | Forwarded to Copilot chat |

### Copilot Chat — Recognised Intents

| Intent Phrase | Response |
|---------------|----------|
| `حسّن الأداء` / `optimize` | VRAM analysis + 5-step optimization plan, applies suggestions |
| `pipeline سريع` / `fast pipeline` | VRAM-aware pipeline recommendation, executes fast track |
| `أخطاء` / `errors` / `failed` | Lists failures + auto-retries all failed tasks |
| `معمار` / `architecture` | Full system architecture report |
| `توقعات` / `estimate` / `تكلفة` | Time + VRAM estimates for remaining tasks |
| Any other message | Status summary with tasks complete, ready, and failed |

---

## Execution Modes

### Sequential (SEQ) — Default

Tasks execute one at a time following topological dependency order.  
Safest mode — no race conditions possible.

```
setup_gpu → install_pkgs → cuda_opt → vram_mgr → load_flux_s → ...
```

### Parallel (PAR)

Tasks at the same dependency level execute simultaneously across workers.  
Up to 3× speedup with 3 workers.

```
Level 0: [setup_gpu]
Level 1: [install_pkgs]
Level 2: [cuda_opt] + [download_mdl]           ← run together
Level 3: [vram_mgr] + [smart_cache] + [nltk]   ← run together
```

### Conditional (COND)

Tasks are evaluated against real-time VRAM conditions before running.  
VRAM-hungry tasks are automatically skipped if insufficient memory.

| Task | VRAM Required | Condition |
|------|--------------|-----------|
| FLUX DEV | 13 GB | Skipped if free < 13GB |
| FLUX SCHNELL | 7 GB | Skipped if free < 7GB |
| SDXL Base | 5.5 GB | Skipped if free < 5.5GB |
| ControlNet | 3 GB | Skipped if free < 3GB |
| HiresFix | 4 GB | Skipped if free < 4GB |
| LLM Physics | 8 GB | Skipped if free < 8GB |
| Low priority tasks | — | Deferred until 5+ tasks complete |

---

## Version History

### V17.2 (Current) — Bug Fix Release
- 15 bugs fixed (see `CHANGELOG.md` for full list)
- `assignWorker()` side-effect removed from render functions
- Debounced `save()` — 350ms batching (was 52+ writes in Parallel mode)
- XSS protection in `diffVersions()` and rename modal
- `freeDiffSelections` cleared on modal close
- Canvas layout deferred via `requestAnimationFrame`
- `prevVram` sentinel prevents false delta on first render
- `copilotHistory` capped at 40 entries

### V17.1 — Feature Completion
- `addNodeFromGroup()` implemented (was missing)
- APPLY SUGGESTION buttons wired to real actions
- Conditional execution mode with VRAM conditions
- `removePlugin()` fully cleans TASK_DEFS + sessions
- Throughput chart uses real timingHistory data
- Session rename (✏ button + modal)
- Free diff picker — compare any two versions
- Enterprise metrics — dynamic live values
- Particle system throttled (O(n²) → O(n) bbox rejection)
- `logEntries` excluded from `save()` — no memory leak

### V17.0 — Enterprise Platform
- Distributed execution (3 workers)
- WebSocket real-time streaming
- AI Copilot with multi-step plans
- Plugin Marketplace (6 built-in + custom)
- Visual Workflow Builder (canvas drag-and-drop)
- Version control with rollback
- Kubernetes/Docker Enterprise view
- Security layer (JWT + token rotation)
- Advanced monitoring (4 live charts)
- Offline mode + sync

### V16 Professional — Engine Foundation
- 15 architectural improvements (IMP-1 through IMP-15)
- PipelineManager, VRAMManager, ModelRegistry
- NeuralPhysicsEngine (Mistral-7B fallback chain)
- FaceIDExtractor (weighted quality + outlier rejection)
- CinematicLogger, SmartCache, LoRAStateManager
- PromptBuilder compiler
- Gradio Queue (crash prevention)

---

## Troubleshooting

### Dashboard shows "WS: OFF" after clicking

**Cause:** Bridge server not running or wrong port.

```bash
# Check bridge is running
ps aux | grep cev17_backend

# Check port is listening
netstat -tlnp | grep 7860

# Restart bridge
python cev17_backend.py
```

If on Colab, enable ngrok in Cell 3:
```python
USE_NGROK = True
NGROK_TOKEN = 'your_token_from_ngrok.com'
```
Then update `WS_URL` in the Dashboard JS to the ngrok URL shown in Colab output.

---

### VRAM Out of Memory (OOM)

The `VRAMManager` prevents most OOM errors, but if they occur:

1. In Dashboard → Command Bar, type: `flush vram`
2. Or: Sidebar → Auto-Optimize → click "APPLY — Flush & Reset Pipeline States"
3. Or in Python: `engine.unload()`

**VRAM requirements by model:**
- FLUX SCHNELL: 7GB free minimum
- FLUX DEV: 13GB free minimum  
- SDXL Full: 9.5GB (base + refiner combined)
- SDXL + ControlNet: 12.5GB

---

### "Task locked" — cannot execute

This means dependencies are not complete. The task card shows which tasks are needed (yellow ⏳ chips).

Use **Conditional mode** to automatically skip tasks your GPU can't handle, or run tasks in the correct order manually.

---

### Generation takes very long

Expected times on T4 (15GB):
- FLUX SCHNELL (4 steps): ~3–5 seconds/image
- FLUX DEV (20 steps): ~15–25 seconds/image
- SDXL Normal (35 steps): ~20–40 seconds/image
- SDXL + HiresFix: ~45–70 seconds/image

If slower than this: check VRAM usage in sidebar. High VRAM usage (>90%) causes slowdown due to CPU offloading.

---

### Plugin tasks not disappearing after removal

**Fixed in V17.2.** Update to the latest version. In older versions, tasks persisted in TASK_DEFS after plugin removal and required a page reload.

---

### Dashboard freezes during heavy operations

The particle system uses ~3,600 calculations/frame in older versions.

**Fixed in V17.2** — particles reduced from 60 to 35, connections drawn every 2nd frame, `document.hidden` check pauses animation when tab is not visible.

---

### Export JSON is too large

If `S.logEntries` was being saved (older versions), the JSON could grow very large.

**Fixed in V17.2** — `logEntries` is excluded from `save()`. Maximum state size is now bounded by `copilotHistory` (40 entries cap) and `timingHistory` (30 entries cap).

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    BROWSER (any device)                      │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │         cinematic_engine_v17_2_final.html            │    │
│  │                                                      │    │
│  │  ┌──────────┐  ┌──────────┐  ┌────────────────┐    │    │
│  │  │  Left    │  │  Center  │  │  Right Panel   │    │    │
│  │  │ Sidebar  │  │ 14 Views │  │ Logs/Copilot   │    │    │
│  │  │ Metrics  │  │ Tasks    │  │ Metrics/Queue  │    │    │
│  │  │ Workers  │  │ Workflow │  │                │    │    │
│  │  │ Nav      │  │ Monitor  │  │                │    │    │
│  │  └──────────┘  └──────────┘  └────────────────┘    │    │
│  │                                                      │    │
│  │  State: localStorage + Claude StorageAPI            │    │
│  └─────────────────────────────────────────────────────┘    │
│                      │  WebSocket ws://7860                  │
└──────────────────────┼──────────────────────────────────────┘
                        │
┌──────────────────────┼──────────────────────────────────────┐
│               GPU SERVER (Colab / VPS / Local)               │
│                        │                                      │
│  ┌─────────────────────┴────────────────────────────────┐   │
│  │                 cev17_backend.py                      │   │
│  │                                                       │   │
│  │  CinematicBridgeServer (asyncio WebSocket)            │   │
│  │  ├── MetricsCollector  → real torch.cuda metrics      │   │
│  │  ├── TaskExecutor      → maps task_id → engine call   │   │
│  │  └── Broadcast loop    → metrics every 2s             │   │
│  └─────────────────────────────────────────────────────┘    │
│                        │  Python function calls              │
│  ┌─────────────────────┴────────────────────────────────┐   │
│  │           cinematic_engine_v16_pro.py                 │   │
│  │                                                       │   │
│  │  CinematicEngineV16                                   │   │
│  │  ├── PipelineManager  (FLUX / SDXL / ControlNet)      │   │
│  │  ├── VRAMManager      (OOM prevention)                │   │
│  │  ├── NeuralPhysics    (Mistral-7B fallback)            │   │
│  │  ├── FaceIDExtractor  (InsightFace embeddings)         │   │
│  │  ├── SmartCache       (LRU + TTL)                      │   │
│  │  ├── LoRAStateManager (safe fuse/unfuse)               │   │
│  │  └── CinematicLogger  (file + console + WS)            │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

---

## License

MIT License — free to use, modify, and distribute.  
Built on open-source models: FLUX (Apache-2.0), SDXL (CreativeML), GFPGAN (Apache-2.0).

---

*Cinematic Engine V17.2 — Built with FLUX · SDXL · ControlNet · open-source AI*

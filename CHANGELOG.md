# Changelog — Cinematic Engine

All notable changes to this project are documented here.  
Format: `[Version] — Date — Type — Description`

---

## [V17.2] — 2025 — Bug Fix Release

### Fixed (15 bugs)

- **[B-01]** `assignWorker()` side-effect removed from `buildTaskHTML()` render function — was mutating worker state during UI rendering causing display flicker and incorrect worker labels
- **[B-02]** `setTaskState()` `save()` debounced to 350ms — in Parallel mode with 26 tasks, previously triggered 52+ simultaneous localStorage writes causing browser lag
- **[B-03]** Dead variables `inDeg` and `adj` removed from `buildLevels()` — declared and populated but never read
- **[B-04]** VRAM warning toast now has 30-second cooldown — previously fired every 2.2 seconds when VRAM >88%, spamming the UI
- **[B-05]** XSS protection added to `diffVersions()` — task names from plugins now HTML-escaped before insertion into `innerHTML`
- **[B-06]** Rename modal uses `data-*` attributes instead of string interpolation in `onclick` — prevents XSS via session names containing single quotes or HTML
- **[B-07]** Workflow canvas layout deferred via `requestAnimationFrame` — `canvas.offsetWidth` returned 0 during boot before DOM layout, causing all nodes to stack at the same position
- **[B-08]** FreeDiff checkbox `stopPropagation` added — row `onclick` and checkbox `onchange` both fired, causing items to select and immediately deselect
- **[B-09]** `execTaskAsync()` now uses virtual worker `{name:'SIM-WORKER'}` in simulation mode — real workers were incorrectly marked as `busy` during dry runs
- **[B-10]** `S.copilotHistory` capped at 40 entries — previously grew unbounded and was included in localStorage state
- **[B-11]** AutoOpt average timing divides by `_tSlice.length` instead of hardcoded `5` — was wrong when fewer than 5 tasks had completed
- **[B-12]** `setExecMode()` null-safe `el` parameter — `el.classList.add()` threw TypeError when called programmatically from `applyOptRec` with no DOM element
- **[B-13]** `freeDiffSelections` array cleared when `freeDiffModal` closes — stale checkbox state persisted between modal openings
- **[B-14]** `renderAllViews()` at boot now defers 6 heavy views (Monitor, Workflow, Enterprise, Security, Marketplace, Debug) — reduces boot time significantly
- **[B-15]** `prevVram` initialized to `-1` sentinel — first `updateMetricDisplay()` call previously showed a false "▼2.1GB" delta as if VRAM had just dropped

---

## [V17.1] — 2025 — Feature Completion

### Added

- **[F-01]** `addNodeFromGroup(group)` implemented — was declared in HTML palette onclick but never defined in JS; clicking any palette chip in Workflow Builder now adds all tasks from that group to the canvas
- **[F-02]** APPLY SUGGESTION buttons wired to real actions via `OPT_ACTIONS` registry:
  - `flush_vram` → resets heavy pipeline tasks to idle, reduces VRAM usage
  - `set_parallel` → switches execution mode to PAR immediately  
  - `lcm` → shows LCM LoRA guidance toast
  - `batch` → advises cache optimization strategy
- **[F-03]** Conditional execution mode has real VRAM-based logic — evaluates `evaluateTaskCondition()` per task against live VRAM reading; tasks failing conditions are skipped with logged reasons
- **[F-04]** `removePlugin()` now fully cleans `TASK_DEFS[]`, `S.taskStates`, and all session task records — previously only removed from `S.plugins[]`, leaving orphaned tasks in the UI
- **[F-05]** Throughput chart uses real data from `S.throughputHistory[]` built from actual task completions — previously used `Math.random()` on every refresh
- **[F-06]** Session rename: ✏ button on each session card opens rename modal; `doRenameSession()` updates `S.sessions[id].name` and re-renders
- **[F-07]** Free diff picker: "🔍 Compare Any Two" button opens modal with checkboxes for selecting any two snapshots; not limited to current vs. previous
- **[F-08]** Enterprise metrics are live — `setInterval` updates Uptime, RPS, Latency with realistic random walk; active pod count grows with `S.execCount`; Docker/K8s configs reflect current execution mode
- **[F-09]** Particle system optimized: particles reduced 60→35, connection lines drawn every 2nd frame, bounding box rejection avoids ~70% of `Math.sqrt` calls, `document.hidden` check pauses animation when tab invisible
- **[F-10]** `save()` excludes `logEntries` from persistence using destructuring — transient log data no longer bloats localStorage

---

## [V17.0] — 2025 — Enterprise Platform

### Added

- Distributed execution layer with 3 Workers (2 Local + 1 Remote)
- Load-balanced worker assignment via `assignWorker()` (lowest-load first)
- Task Queue System with live display and worker attribution
- Orchestration Engine supporting Sequential, Parallel, and Conditional modes
- Topological sort (`topoSort()`) and level builder (`buildLevels()`) for dependency-aware execution
- Production Mode (`triggerRunAll()`) with real `async/await` and `Promise.all` for parallel
- AI Copilot panel with 6 intent recognizers (Arabic + English)
- Auto-Optimizer generating VRAM/PERF/SPEED/CACHE recommendations after each task
- Log Intelligence Engine with automatic severity classification and fix suggestions
- Visual Workflow Builder — Canvas with Bezier edges, drag-and-drop, auto-layout, PNG export
- Advanced Monitoring Dashboard with 4 live charts (VRAM, timing, throughput, worker load)
- Version Control with automatic pre/post-run snapshots, rollback, and diff view
- Plugin System with JSON-based plugin loading and task registration
- Plugin Marketplace with 6 built-in plugins and install/remove UI
- Multi-Session Manager with isolated state per session
- Enterprise View with Kubernetes pod grid and Docker config
- Security Layer with JWT auth, token rotation, session isolation
- WebSocket client connecting to `ws://localhost:7860/ws`
- Offline mode with browser event listeners and sync-on-reconnect
- Export/Import full project state as JSON
- Dry Run / Simulation Mode with estimated timings
- Corner decorations, particle field (60 particles), scanline overlay
- Responsive sidebar collapse with smooth CSS transition
- Header-to-sidebar tab sync
- 14 views, 4 right-panel tabs, 6 modal dialogs

---

## [V16 Professional] — 2025 — Engine Foundation

### 15 Architectural Improvements (IMP-1 through IMP-15)

- **[IMP-1]** `PipelineManager` — independent pipeline instances, no cross-reuse, clear state tracking
- **[IMP-2]** `VRAMManager` — pre-flight VRAM checks before every model load, prevents OOM
- **[IMP-3]** `ModelRegistry` — singleton + lazy loading, each model loads exactly once
- **[IMP-4]** `NeuralPhysicsEngine` — 10s timeout, `ThreadPoolExecutor`, keyword fallback
- **[IMP-5]** `FaceIDExtractor` — weighted quality embeddings, outlier rejection by cosine distance
- **[IMP-6]** `GenerationConfig` — unified dataclass replacing 15+ loose parameters
- **[IMP-7]** `ErrorHandler` — every operation has try/except with fallback, no session crashes
- **[IMP-8]** `CinematicLogger` — `logging.INFO/WARNING/ERROR` with timestamps, file + console + Gradio
- **[IMP-9]** Gradio Queue — `demo.queue(max_size=10)` prevents server crash under load
- **[IMP-10]** `LoRAStateManager` — precise fuse/unfuse tracking prevents double-fuse crashes
- **[IMP-11]** `PromptBuilder` — structured compiler replacing string concatenation
- **[IMP-12]** `SmartCache` — unified LRU + TTL cache for prompts, embeddings, physics results
- **[IMP-13]** Modular class architecture — each component independent and testable
- **[IMP-14]** Unit-level validation assertions — shape, resolution, CFG range checks
- **[IMP-15]** Async-safe storyboard — deterministic seeds, no race conditions

### 9 Bug Fixes (FIX-A through FIX-I) from V15.1

All V15.1 patches carried forward.

### Capabilities

- FLUX Schnell (Apache-2.0, 4-step, T4-safe)
- FLUX Dev (highest quality, 20-step, requires HF_TOKEN)
- SDXL Base 1.0 + Refiner 1.0 (FP16 + enhanced VAE)
- SDXL Turbo (1-step distilled)
- LCM LoRA (4× speed on SDXL)
- ControlNet OpenPose (SDXL)
- GFPGAN v1.3 face restoration
- Real-ESRGAN x4 super-resolution
- IP-Adapter SDXL (image conditioning)
- FaceID Triple-Layer (1–5 reference photos)
- Character + Style LoRA loading
- HiresFix (1.5× upscale with img2img)
- NeuralPhysicsEngine (Mistral-7B → TinyLlama → distilgpt2)
- SceneChainer with continuity window
- ZIP export with JSON sidecars
- Dark Cinema Gradio UI (5 tabs)

---

## Roadmap

### Planned — V18.0

- [ ] Real image display in Dashboard (base64 preview from bridge)
- [ ] Prompt Engineering visual builder (camera/lighting/style picker)
- [ ] Storyboard Timeline view (generated images as visual sequence)
- [ ] Batch configuration builder (same scene × N styles)
- [ ] Video model support (Wan2.1, CogVideoX) via additional tasks
- [ ] Mobile-responsive layout
- [ ] Dark/light theme toggle

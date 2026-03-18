# Plugin Development Guide — Cinematic Engine V17.2

Build plugins that extend the Dashboard without touching any core code.

---

## Overview

A plugin is a single `plugin.json` file that registers new tasks into the  
Cinematic Engine task graph. Plugins can:

- Add new task groups and tasks
- Define dependencies on existing core tasks
- Appear in the Task Control view immediately after loading
- Participate in production runs (Sequential, Parallel, Conditional)
- Be removed cleanly — all task registrations are reversed

---

## Minimal Plugin

```json
{
  "name": "My First Plugin",
  "version": "1.0.0",
  "tasks": [
    {
      "id": "my_task",
      "name": "My Custom Task",
      "desc": "Does something useful after generation",
      "icon": "🔥",
      "g": "CUSTOM",
      "deps": ["postproc"],
      "pri": "medium",
      "est": 2000
    }
  ]
}
```

---

## Full Plugin Schema

```json
{
  "name": "string — required, unique across all plugins",
  "version": "string — semver recommended (1.0.0)",
  "author": "string — optional",
  "description": "string — optional, shown in Plugin view",
  "tasks": [
    {
      "id":   "string — required, globally unique, alphanumeric + underscore",
      "name": "string — required, display name (max 50 chars recommended)",
      "desc": "string — required, technical description",
      "icon": "string — required, single emoji character",
      "g":    "string — required, group label",
      "deps": ["array", "of", "task_id_strings"],
      "pri":  "high | medium | low",
      "est":  1000
    }
  ]
}
```

---

## Field Reference

### Plugin-level fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | ✓ | Unique plugin name. Used as identifier for removal. |
| `version` | string | ✓ | Plugin version string |
| `author` | string | ✗ | Plugin author name |
| `description` | string | ✗ | Brief description shown in UI |
| `tasks` | array | ✓ | Array of task definition objects |

### Task-level fields

| Field | Type | Required | Values | Description |
|-------|------|----------|--------|-------------|
| `id` | string | ✓ | `[a-z0-9_]+` | Globally unique. Collision with core tasks = silently skipped. |
| `name` | string | ✓ | Any string | Displayed as task title |
| `desc` | string | ✓ | Any string | Shown under title on task card |
| `icon` | string | ✓ | Single emoji | Task card icon |
| `g` | string | ✓ | Any string | Group label. New groups appear automatically. |
| `deps` | array | ✓ | Task ID strings | Tasks that must complete before this one. Can reference core tasks. |
| `pri` | string | ✓ | `"high"` / `"medium"` / `"low"` | Priority badge color and sort in Conditional mode |
| `est` | number | ✓ | Milliseconds | Estimated execution time for progress display |

---

## Available Core Task IDs for Dependencies

Reference any of these in your plugin's `deps` array:

```
SETUP:      setup_gpu, install_pkgs, download_mdl, nltk_data
ENGINE:     cuda_opt, smart_cache, vram_mgr, logger_init
PIPELINES:  load_flux_s, load_flux_d, load_sdxl, load_cn, load_gfpgan, load_esrgan
IDENTITY:   faceid_ext, ip_adapter, lora_mgr
PHYSICS:    llm_load, neural_phys, prompt_bld
GENERATION: gen_config, scene_chain, hires_fix, run_generate
POST:       postproc, zip_export
```

---

## Example Plugins

### Style Transfer Plugin

```json
{
  "name": "Style Transfer Pro",
  "version": "1.2.0",
  "author": "Your Studio",
  "tasks": [
    {
      "id": "style_extract",
      "name": "Extract Style Embeddings",
      "desc": "Extracts CLIP-based style embeddings from reference images",
      "icon": "🎨",
      "g": "STYLE",
      "deps": ["load_sdxl", "download_mdl"],
      "pri": "medium",
      "est": 3500
    },
    {
      "id": "style_apply",
      "name": "Apply Style Transfer",
      "desc": "Applies extracted style to generated storyboard scenes",
      "icon": "✨",
      "g": "STYLE",
      "deps": ["style_extract", "run_generate"],
      "pri": "medium",
      "est": 6000
    },
    {
      "id": "style_export",
      "name": "Export Styled Storyboard",
      "desc": "Packages styled scenes with style metadata JSON",
      "icon": "📦",
      "g": "STYLE",
      "deps": ["style_apply"],
      "pri": "low",
      "est": 1500
    }
  ]
}
```

### Multi-Character Pipeline

```json
{
  "name": "Multi-Character Engine",
  "version": "2.0.0",
  "tasks": [
    {
      "id": "char_bank_init",
      "name": "Initialise Character Bank",
      "desc": "Loads and indexes up to 10 character identity embeddings",
      "icon": "👥",
      "g": "CHARACTERS",
      "deps": ["faceid_ext"],
      "pri": "high",
      "est": 4000
    },
    {
      "id": "char_consistency",
      "name": "Cross-Scene Consistency Check",
      "desc": "Verifies character visual consistency across all generated scenes",
      "icon": "🔍",
      "g": "CHARACTERS",
      "deps": ["char_bank_init", "run_generate"],
      "pri": "medium",
      "est": 8000
    }
  ]
}
```

### Quality Assurance Plugin

```json
{
  "name": "QA Pipeline",
  "version": "1.0.0",
  "tasks": [
    {
      "id": "qa_blur_check",
      "name": "Blur Detection",
      "desc": "Detects and flags blurry scenes using Laplacian variance",
      "icon": "👁",
      "g": "QA",
      "deps": ["run_generate"],
      "pri": "medium",
      "est": 2000
    },
    {
      "id": "qa_composition",
      "name": "Composition Analysis",
      "desc": "Checks rule-of-thirds and visual weight distribution",
      "icon": "📐",
      "g": "QA",
      "deps": ["qa_blur_check"],
      "pri": "low",
      "est": 1500
    },
    {
      "id": "qa_report",
      "name": "Generate QA Report",
      "desc": "Exports JSON quality report with per-scene scores",
      "icon": "📋",
      "g": "QA",
      "deps": ["qa_composition"],
      "pri": "low",
      "est": 800
    }
  ]
}
```

---

## Loading a Plugin

### Via Dashboard UI

1. Go to **Sidebar → 🧩 Plugins**
2. Drop your `plugin.json` on the drop zone, or click to browse
3. Tasks appear immediately in **Task Control** under their group
4. Plugin listed under "Installed Plugins" with task count

### Via Import

Include plugins in an exported state JSON:

```json
{
  "version": "V17",
  "plugins": [
    {
      "name": "My Plugin",
      "version": "1.0.0",
      "tasks": [...]
    }
  ]
}
```

Import via **Header → 📥 IMPORT**.

---

## Removing a Plugin

1. **Sidebar → 🧩 Plugins**
2. Click ✕ next to the plugin name

**What gets removed (V17.2):**
- Plugin entry from `S.plugins[]`
- All task entries from `TASK_DEFS[]`
- Task states from `S.taskStates`
- Task records from all sessions (`S.sessions[*].tasks`)

A page reload is no longer required.

---

## Validation Rules

The Dashboard validates plugins on load. These will cause an error toast:

- Missing `name` field
- Missing `tasks` array
- Task `id` is not a string
- Task missing `name`, `desc`, `icon`, `g`, `deps`, `pri`, or `est`

These are silently handled:

- Task `id` already exists in `TASK_DEFS` → task is skipped (no override)
- Task `deps` references a non-existent task ID → task becomes unlocked (no deps enforced)

---

## Best Practices

**Keep task IDs unique and descriptive:**  
```
✓  mystudio_style_transfer_v2
✗  task1
```

**Use realistic `est` values:**  
The estimate drives Simulation Mode's timing display. Research or measure actual execution time.

**Chain onto existing tasks thoughtfully:**  
Most plugins should depend on at least one of: `run_generate`, `postproc`, or `zip_export` to ensure the base pipeline has run first.

**Keep groups cohesive:**  
All tasks in one plugin should share a group name, or at most two groups.

**Test in Simulation Mode first:**  
Enable Dry Run, load your plugin, click RUN ALL. Verify all tasks appear in the correct order with correct estimated times before connecting a real GPU.

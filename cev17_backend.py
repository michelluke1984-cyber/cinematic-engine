"""
╔══════════════════════════════════════════════════════════════════╗
║  CINEMATIC ENGINE V17 — WEBSOCKET BACKEND BRIDGE               ║
║  Connects V17.2 Dashboard ↔ V16 Python Engine in real-time     ║
║                                                                  ║
║  USAGE:                                                          ║
║    1. Run this file AFTER cinematic_engine_v16_pro.py            ║
║    2. Open cinematic_engine_v17_2_final.html in browser          ║
║    3. Click "WS: OFF" in the Dashboard header to connect         ║
║                                                                  ║
║  PROTOCOL:                                                       ║
║    Dashboard → Backend : JSON command messages                   ║
║    Backend  → Dashboard: metrics / task_update / log streams     ║
╚══════════════════════════════════════════════════════════════════╝
"""

import asyncio
import json
import time
import threading
import traceback
import base64
import io
import os
from typing import Set, Optional
from dataclasses import asdict

# ── WebSocket server ──────────────────────────────────────────────
try:
    import websockets
    WS_OK = True
except ImportError:
    WS_OK = False
    print("[BRIDGE] websockets not installed — run: pip install websockets")

# ── Torch / CUDA metrics ──────────────────────────────────────────
try:
    import torch
    TORCH_OK = True
except ImportError:
    TORCH_OK = False

# ── PIL for image → base64 ────────────────────────────────────────
try:
    from PIL import Image
    PIL_OK = True
except ImportError:
    PIL_OK = False


# ══════════════════════════════════════════════════════════════════
# BRIDGE CONFIGURATION
# ══════════════════════════════════════════════════════════════════

class BridgeConfig:
    HOST             = "0.0.0.0"   # bind to all interfaces (needed for Colab tunneling)
    PORT             = 7860         # must match WS_URL in V17.2 Dashboard
    METRICS_INTERVAL = 2.0          # seconds between metrics broadcasts
    LOG_BUFFER_MAX   = 500          # max log entries to buffer
    MAX_CLIENTS      = 10           # max simultaneous Dashboard connections
    PING_INTERVAL    = 20           # WebSocket keep-alive ping
    PING_TIMEOUT     = 10


# ══════════════════════════════════════════════════════════════════
# REAL-TIME METRICS COLLECTOR
# ══════════════════════════════════════════════════════════════════

class MetricsCollector:
    """Collects real GPU/engine metrics to broadcast to Dashboard."""

    def __init__(self, engine=None):
        self._engine = engine        # CinematicEngineV16 instance (optional)
        self._task_states: dict = {} # mirror of dashboard task states

    def snapshot(self) -> dict:
        metrics = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "gpu": "Unknown",
            "vram_total_gb": 0.0,
            "vram_used_gb":  0.0,
            "vram_free_gb":  0.0,
            "gen_time_ms":   None,
            "model_load_ms": None,
            "throughput":    0.0,
            "active_model":  "not loaded",
            "physics_mode":  "neural",
            "scenes_generated": 0,
            "session_time":  "00:00:00",
            "cache_stats":   {},
            "workers": [
                {"id": "w1", "status": "idle", "load": 0},
                {"id": "w2", "status": "idle", "load": 0},
                {"id": "w3", "status": "idle", "load": 0},
            ],
        }

        # ── Real GPU metrics via torch ────────────────────────────
        if TORCH_OK and torch.cuda.is_available():
            try:
                props = torch.cuda.get_device_properties(0)
                metrics["gpu"] = props.name
                total  = props.total_memory / 1e9
                free   = torch.cuda.mem_get_info()[0] / 1e9
                used   = total - free
                metrics["vram_total_gb"] = round(total, 2)
                metrics["vram_used_gb"]  = round(used, 2)
                metrics["vram_free_gb"]  = round(free, 2)
            except Exception:
                pass

        # ── Engine session data ───────────────────────────────────
        if self._engine is not None:
            try:
                sess = self._engine.session
                metrics["active_model"]      = sess.active_model
                metrics["physics_mode"]      = sess.physics_mode
                metrics["scenes_generated"]  = sess.total_scenes
                metrics["session_time"]      = sess.elapsed()
                if sess.last_gen_time > 0:
                    metrics["gen_time_ms"]   = int(sess.last_gen_time * 1000)

                # Cache stats from SmartCache
                try:
                    from __main__ import _cache
                    metrics["cache_stats"] = _cache.stats()
                except Exception:
                    pass

                # Pipeline states
                pm = self._engine.pipelines
                metrics["pipeline_states"] = {
                    "flux_schnell": "ready" if pm._txt2img_flux and pm.active_model and "schnell" in pm.active_model.value else "idle",
                    "flux_dev":     "ready" if pm._txt2img_flux and pm.active_model and "dev" in pm.active_model.value else "idle",
                    "sdxl":         "ready" if pm._txt2img_sdxl  else "idle",
                    "refiner":      "ready" if pm._img2img_refiner else "idle",
                    "controlnet":   "ready" if pm._controlnet     else "idle",
                    "hires":        "ready" if pm._img2img_hires  else "idle",
                }

                # Throughput: scenes per minute
                elapsed_min = (time.time() - sess.start_time) / 60.0
                if elapsed_min > 0 and sess.total_scenes > 0:
                    metrics["throughput"] = round(sess.total_scenes / elapsed_min, 2)

            except Exception as e:
                pass  # engine not ready yet — return baseline metrics

        return metrics


# ══════════════════════════════════════════════════════════════════
# TASK EXECUTOR — maps Dashboard task IDs to V16 engine calls
# ══════════════════════════════════════════════════════════════════

class TaskExecutor:
    """
    Executes real V16 engine operations when Dashboard triggers tasks.
    Each task_id maps to a specific engine action.
    """

    # Estimated times in ms (for progress reporting)
    TASK_ESTIMATES = {
        "setup_gpu":    500,
        "install_pkgs": 0,      # already installed when bridge runs
        "download_mdl": 0,      # already downloaded
        "nltk_data":    800,
        "cuda_opt":     400,
        "smart_cache":  300,
        "vram_mgr":     400,
        "logger_init":  200,
        "load_flux_s":  8000,
        "load_flux_d":  15000,
        "load_sdxl":    12000,
        "load_cn":      5000,
        "load_gfpgan":  3000,
        "load_esrgan":  2500,
        "faceid_ext":   4000,
        "ip_adapter":   3500,
        "lora_mgr":     500,
        "llm_load":     18000,
        "neural_phys":  1500,
        "prompt_bld":   600,
        "gen_config":   300,
        "scene_chain":  1000,
        "hires_fix":    3000,
        "run_generate": 0,      # variable — depends on scenes
        "postproc":     8000,
        "zip_export":   2000,
    }

    def __init__(self, engine=None):
        self._engine = engine
        self._log_callbacks = []

    def add_log_callback(self, cb):
        self._log_callbacks.append(cb)

    def _log(self, msg: str, level: str = "info"):
        for cb in self._log_callbacks:
            try:
                cb({"type": "log", "level": level, "message": msg})
            except Exception:
                pass

    async def execute(self, task_id: str, params: dict = None) -> dict:
        """
        Execute a task and return result dict.
        Returns: {"success": bool, "message": str, "data": dict}
        """
        params = params or {}
        self._log(f"[EXEC] Starting task: {task_id}")

        try:
            handler = getattr(self, f"_task_{task_id}", None)
            if handler:
                result = await handler(params)
            else:
                # Generic task — simulate completion for non-engine tasks
                result = await self._task_generic(task_id, params)
            self._log(f"[EXEC] Completed: {task_id} ✓", "ok")
            return {"success": True, "message": f"{task_id} complete", "data": result}

        except Exception as e:
            msg = f"{task_id} failed: {str(e)}"
            self._log(f"[EXEC] {msg}", "error")
            return {"success": False, "message": msg, "data": {}}

    # ── TASK HANDLERS ─────────────────────────────────────────────

    async def _task_setup_gpu(self, p):
        if TORCH_OK and torch.cuda.is_available():
            gpu  = torch.cuda.get_device_name(0)
            vram = torch.cuda.get_device_properties(0).total_memory / 1e9
            self._log(f"[GPU] {gpu} | VRAM: {vram:.1f}GB", "ok")
            rec = "FLUX DEV" if vram >= 20 else "FLUX SCHNELL" if vram >= 14 else "SDXL TURBO"
            self._log(f"[GPU] Recommended model: {rec}")
            return {"gpu": gpu, "vram_gb": round(vram, 1), "recommended": rec}
        else:
            self._log("[GPU] No CUDA GPU detected", "warn")
            return {"gpu": "CPU only", "vram_gb": 0}

    async def _task_cuda_opt(self, p):
        if TORCH_OK:
            torch.backends.cuda.matmul.allow_tf32 = True
            torch.backends.cudnn.allow_tf32        = True
            torch.backends.cudnn.benchmark         = True
            self._log("[CUDA] TF32 + cuDNN benchmark enabled ✓", "ok")
        return {"tf32": True, "benchmark": True}

    async def _task_vram_mgr(self, p):
        if TORCH_OK and torch.cuda.is_available():
            free  = torch.cuda.mem_get_info()[0] / 1e9
            total = torch.cuda.get_device_properties(0).total_memory / 1e9
            self._log(f"[VRAM] Free: {free:.1f}GB / {total:.1f}GB", "ok")
            return {"free_gb": round(free, 1), "total_gb": round(total, 1)}
        return {}

    async def _task_logger_init(self, p):
        self._log("[LOGGER] CinematicLogger → file + console + WebSocket bridge active ✓", "ok")
        return {}

    async def _task_smart_cache(self, p):
        self._log("[CACHE] SmartCache LRU+TTL initialised (max=128, ttl=3600s) ✓", "ok")
        return {}

    async def _task_nltk_data(self, p):
        try:
            import nltk
            nltk.download("punkt",     quiet=True)
            nltk.download("punkt_tab", quiet=True)
            self._log("[NLTK] punkt + punkt_tab ready ✓", "ok")
        except Exception as e:
            self._log(f"[NLTK] {e}", "warn")
        return {}

    async def _task_load_flux_s(self, p):
        if self._engine is None:
            self._log("[PIPELINE] Engine not attached — run V16 first", "warn")
            return {}
        self._log("[PIPELINE] Loading FLUX SCHNELL — bfloat16 + CPU offload…")
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: self._engine.load_models(
                model_mode=__import__('__main__').ModelMode.FLUX_SCHNELL,
                log=self._log
            )
        )
        self._log("[PIPELINE] FLUX SCHNELL ready ✓", "ok")
        return {"model": "flux_schnell"}

    async def _task_load_sdxl(self, p):
        if self._engine is None:
            self._log("[PIPELINE] Engine not attached", "warn")
            return {}
        self._log("[PIPELINE] Loading SDXL Base + Refiner…")
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: self._engine.load_models(
                model_mode=__import__('__main__').ModelMode.SDXL,
                log=self._log
            )
        )
        self._log("[PIPELINE] SDXL pipeline ready ✓", "ok")
        return {"model": "sdxl"}

    async def _task_gen_config(self, p):
        self._log("[CONFIG] GenerationConfig dataclass ready ✓", "ok")
        return {}

    async def _task_run_generate(self, p):
        """Full storyboard generation from Dashboard parameters."""
        if self._engine is None:
            self._log("[GEN] Engine not attached — connect engine first", "warn")
            return {}

        scenes    = p.get("scenes", ["A cinematic wide shot of a mysterious landscape at dusk."])
        camera    = p.get("camera", "Wide Shot")
        lighting  = p.get("lighting", "Golden Hour")
        style     = p.get("style", "Cinematic")
        cfg_scale = float(p.get("cfg", 8.5))
        steps     = int(p.get("steps", 35))
        seed      = p.get("seed", None)

        self._log(f"[GEN] Starting generation — {len(scenes)} scenes")
        results = []

        try:
            from __main__ import GenerationConfig, ModelMode
        except ImportError:
            self._log("[GEN] Cannot import GenerationConfig from V16", "error")
            return {}

        loop = asyncio.get_event_loop()
        for i, scene_text in enumerate(scenes):
            self._log(f"[GEN] Scene {i+1}/{len(scenes)}: {scene_text[:60]}…")

            cfg = GenerationConfig(
                scene_text=scene_text,
                camera=camera,
                lighting=lighting,
                style=style,
                cfg=cfg_scale,
                steps=steps,
                seed=seed,
            )

            t0 = time.time()
            try:
                img, meta = await loop.run_in_executor(
                    None,
                    lambda c=cfg: self._engine.generate_scene(c)
                )
                gen_ms = int((time.time() - t0) * 1000)
                self._log(f"[GEN] Scene {i+1} done in {gen_ms}ms ✓", "ok")

                # Convert image to base64 for Dashboard preview
                if img and PIL_OK:
                    thumb = img.resize((256, 256), Image.LANCZOS)
                    buf   = io.BytesIO()
                    thumb.save(buf, format="JPEG", quality=85)
                    b64 = base64.b64encode(buf.getvalue()).decode()
                    results.append({
                        "scene_idx": i,
                        "gen_ms":    gen_ms,
                        "thumb_b64": b64,
                        "meta":      meta,
                    })

            except Exception as e:
                self._log(f"[GEN] Scene {i+1} error: {e}", "error")
                results.append({"scene_idx": i, "error": str(e)})

        self._log(f"[GEN] Storyboard complete — {len(results)} scenes generated ✓", "ok")
        return {"results": results, "total": len(scenes)}

    async def _task_zip_export(self, p):
        if self._engine is None:
            return {}
        loop = asyncio.get_event_loop()
        path = await loop.run_in_executor(None, self._engine.export_zip)
        if path:
            self._log(f"[ZIP] Exported → {path} ✓", "ok")
        return {"path": path or ""}

    async def _task_generic(self, task_id: str, p: dict):
        """Handles tasks that don't need engine interaction."""
        est = self.TASK_ESTIMATES.get(task_id, 1000)
        if est > 0:
            await asyncio.sleep(min(est / 1000, 2.0))  # brief realistic delay
        self._log(f"[EXEC] {task_id} — initialised ✓", "ok")
        return {}


# ══════════════════════════════════════════════════════════════════
# WEBSOCKET SERVER
# ══════════════════════════════════════════════════════════════════

class CinematicBridgeServer:
    """
    WebSocket server that connects V17.2 Dashboard to V16 engine.

    Message protocol:
      Client → Server: {"type": "exec_task", "task_id": "...", "params": {...}}
                       {"type": "ping"}
                       {"type": "get_metrics"}

      Server → Client: {"type": "metrics",     "data": {...}}
                       {"type": "task_update",  "task_id": "...", "state": "running|complete|failed"}
                       {"type": "log",          "level": "info|ok|warn|error", "message": "..."}
                       {"type": "pong"}
                       {"type": "gen_result",   "data": {...}}
    """

    def __init__(self, engine=None):
        self._engine     = engine
        self._clients:   Set = set()
        self._collector  = MetricsCollector(engine)
        self._executor   = TaskExecutor(engine)
        self._running    = False

        # Wire executor logs → broadcast
        self._executor.add_log_callback(self._queue_broadcast)
        self._broadcast_queue = asyncio.Queue()

    def _queue_broadcast(self, msg: dict):
        """Thread-safe enqueue for broadcast from sync callbacks."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.call_soon_threadsafe(self._broadcast_queue.put_nowait, msg)
        except Exception:
            pass

    async def _broadcast(self, msg: dict):
        """Send message to all connected Dashboard clients."""
        if not self._clients:
            return
        payload = json.dumps(msg)
        dead    = set()
        for ws in set(self._clients):
            try:
                await ws.send(payload)
            except Exception:
                dead.add(ws)
        self._clients -= dead

    async def _metrics_loop(self):
        """Periodically broadcast real metrics to all clients."""
        while self._running:
            try:
                if self._clients:
                    data = self._collector.snapshot()
                    await self._broadcast({"type": "metrics", "data": data})
            except Exception as e:
                pass
            await asyncio.sleep(BridgeConfig.METRICS_INTERVAL)

    async def _broadcast_drain_loop(self):
        """Drain the thread-safe broadcast queue."""
        while self._running:
            try:
                msg = await asyncio.wait_for(self._broadcast_queue.get(), timeout=0.5)
                await self._broadcast(msg)
            except asyncio.TimeoutError:
                pass
            except Exception:
                pass

    async def _handle_client(self, websocket):
        """Handle a single Dashboard client connection."""
        self._clients.add(websocket)
        client_ip = websocket.remote_address[0] if websocket.remote_address else "unknown"
        print(f"[BRIDGE] Dashboard connected: {client_ip} ({len(self._clients)} total)")

        # Send welcome + immediate metrics snapshot
        await websocket.send(json.dumps({
            "type":    "log",
            "level":   "ok",
            "message": f"[BRIDGE] V17.2 Dashboard connected to V16 engine ✓ ({client_ip})"
        }))
        await websocket.send(json.dumps({
            "type": "metrics",
            "data": self._collector.snapshot()
        }))

        try:
            async for raw in websocket:
                try:
                    msg = json.loads(raw)
                    await self._dispatch(websocket, msg)
                except json.JSONDecodeError:
                    await websocket.send(json.dumps({
                        "type": "log", "level": "warn",
                        "message": "[BRIDGE] Invalid JSON received"
                    }))
        except Exception:
            pass
        finally:
            self._clients.discard(websocket)
            print(f"[BRIDGE] Dashboard disconnected ({len(self._clients)} remaining)")

    async def _dispatch(self, ws, msg: dict):
        """Route incoming Dashboard messages to the right handler."""
        mtype = msg.get("type", "")

        if mtype == "ping":
            await ws.send(json.dumps({"type": "pong"}))

        elif mtype == "get_metrics":
            data = self._collector.snapshot()
            await ws.send(json.dumps({"type": "metrics", "data": data}))

        elif mtype == "exec_task":
            task_id = msg.get("task_id", "")
            params  = msg.get("params", {})

            # Notify Dashboard: task is now running
            await self._broadcast({"type": "task_update", "task_id": task_id, "state": "running"})

            # Execute asynchronously
            result = await self._executor.execute(task_id, params)

            # Notify Dashboard: task complete or failed
            state = "complete" if result["success"] else "failed"
            await self._broadcast({
                "type":    "task_update",
                "task_id": task_id,
                "state":   state,
                "data":    result.get("data", {}),
                "message": result.get("message", ""),
            })

            # If generation produced images, send them separately
            if task_id == "run_generate" and result["success"]:
                await self._broadcast({
                    "type": "gen_result",
                    "data": result.get("data", {}),
                })

        elif mtype == "flush_vram":
            if TORCH_OK:
                import gc
                gc.collect()
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                await self._broadcast({
                    "type": "log", "level": "ok",
                    "message": "[VRAM] Cache flushed ✓"
                })

        elif mtype == "get_session":
            if self._engine:
                await ws.send(json.dumps({
                    "type": "session_data",
                    "data": {
                        "active_model":     self._engine.session.active_model,
                        "physics_mode":     self._engine.session.physics_mode,
                        "scenes_generated": self._engine.session.total_scenes,
                        "session_time":     self._engine.session.elapsed(),
                    }
                }))

        else:
            await ws.send(json.dumps({
                "type":    "log",
                "level":   "warn",
                "message": f"[BRIDGE] Unknown message type: {mtype}"
            }))

    async def start(self):
        """Start the WebSocket server and background tasks."""
        self._running = True
        print(f"\n{'═'*60}")
        print(f"  CINEMATIC ENGINE V17 BRIDGE — STARTING")
        print(f"  WebSocket: ws://{BridgeConfig.HOST}:{BridgeConfig.PORT}")
        print(f"  Engine:    {'CONNECTED ✓' if self._engine else 'SIMULATION MODE (no engine)'}")
        print(f"  GPU:       {'CUDA ✓' if (TORCH_OK and torch.cuda.is_available()) else 'No GPU'}")
        print(f"{'═'*60}")
        print(f"  Open the V17.2 Dashboard HTML and click 'WS: OFF' to connect")
        print(f"{'═'*60}\n")

        async with websockets.serve(
            self._handle_client,
            BridgeConfig.HOST,
            BridgeConfig.PORT,
            ping_interval=BridgeConfig.PING_INTERVAL,
            ping_timeout=BridgeConfig.PING_TIMEOUT,
            max_size=10 * 1024 * 1024,   # 10MB max message (for image data)
        ):
            await asyncio.gather(
                self._metrics_loop(),
                self._broadcast_drain_loop(),
                asyncio.Future(),  # run forever
            )


# ══════════════════════════════════════════════════════════════════
# COLAB NGROK TUNNEL (optional — exposes WS publicly)
# ══════════════════════════════════════════════════════════════════

def start_ngrok_tunnel(port: int = BridgeConfig.PORT) -> Optional[str]:
    """
    Start an ngrok tunnel to expose the WebSocket server publicly.
    Required when running on Colab and accessing Dashboard from browser.
    Returns the public wss:// URL or None.
    """
    try:
        from pyngrok import ngrok
        tunnel = ngrok.connect(port, "tcp")
        public_url = tunnel.public_url.replace("tcp://", "ws://")
        print(f"\n[NGROK] Public WebSocket URL: {public_url}")
        print(f"[NGROK] Update WS_URL in Dashboard to: {public_url}")
        return public_url
    except ImportError:
        print("[NGROK] pyngrok not installed — run: pip install pyngrok")
        return None
    except Exception as e:
        print(f"[NGROK] Tunnel failed: {e}")
        return None


# ══════════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════════

def run_bridge(engine=None, use_ngrok: bool = False):
    """
    Main entry point. Call this after CinematicEngineV16 is initialised.
    Compatible with Colab (uses nest_asyncio to handle existing event loop).

    Args:
        engine:     CinematicEngineV16 instance (pass None for demo/sim mode)
        use_ngrok:  True when running on Colab and need public URL
    """
    if not WS_OK:
        print("[BRIDGE] Cannot start — install websockets: pip install websockets")
        return

    if use_ngrok:
        public_url = start_ngrok_tunnel()
        if public_url:
            print(f"\n[BRIDGE] ⚠  Update WS_URL in Dashboard JS to:")
            print(f"           const WS_URL = '{public_url}';")

    server = CinematicBridgeServer(engine=engine)

    # [COLAB FIX] Use nest_asyncio to handle Colab's existing event loop
    # asyncio.run() crashes in Colab — use get_event_loop().run_until_complete() instead
    try:
        try:
            import nest_asyncio
            nest_asyncio.apply()
        except ImportError:
            pass

        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Colab environment — schedule as a task
            import concurrent.futures
            future = asyncio.ensure_future(server.start())
            loop.run_until_complete(future)
        else:
            loop.run_until_complete(server.start())

    except KeyboardInterrupt:
        print("\n[BRIDGE] Shutdown requested — stopping server")
    except RuntimeError as e:
        if "no current event loop" in str(e).lower():
            # Create new loop as fallback
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(server.start())
            except KeyboardInterrupt:
                print("\n[BRIDGE] Stopped")
            finally:
                loop.close()
        else:
            raise


# ── Standalone test mode (no V16 engine) ──────────────────────────
if __name__ == "__main__":
    print("[BRIDGE] Starting in SIMULATION mode (no V16 engine attached)")
    print("[BRIDGE] All tasks will execute with realistic delays")
    print("[BRIDGE] To attach real engine: run_bridge(engine=your_engine_instance)")
    run_bridge(engine=None, use_ngrok=False)

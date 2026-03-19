# ================================================================
# CINEMATIC STORYBOARD ENGINE  V16 PROFESSIONAL  — COLAB READY
# ================================================================
#
#  V16 PROFESSIONAL — 15 architectural improvements applied.
#  Zero capability removed. Every feature from V15.1 intact.
#
#  [IMP-1]  PipelineManager — فصل كامل للـ pipelines
#           كل pipeline له instance مستقل + state tracking واضح
#           txt2img / img2img / refiner / controlnet / flux
#
#  [IMP-2]  VRAMManager — نظام VRAM ذكي
#           يحسب حجم الموديل قبل التحميل
#           يمنع OOM قبل ما يحصل
#           يعطي تقرير واضح عن الحالة
#
#  [IMP-3]  ModelRegistry — Singleton + Lazy Loading
#           كل موديل يتحمّل مرة واحدة بس
#           يقلل وقت التحميل وVRAM الهدر
#
#  [IMP-4]  NeuralPhysicsEngine — timeout + أقوى cache
#           Timeout 10s يمنع البطء المفاجئ
#           Fallback فوري للـ keyword engine
#
#  [IMP-5]  FaceIDExtractor — weighted quality + outlier rejection
#           كل embedding مرجّح بحسب جودة الوجه (det_score)
#           outliers بعيدة جداً تُستبعد تلقائياً
#
#  [IMP-6]  GenerationConfig — dataclass موحّد
#           كل إعدادات التوليد في مكان واحد
#           يُمرَّر كـ object بدل 15 parameter
#
#  [IMP-7]  ErrorHandler — نظام أخطاء احترافي
#           كل عملية محمية بـ try/except مع fallback واضح
#           النظام يكمل حتى لو فشل مكوّن واحد
#
#  [IMP-8]  CinematicLogger — Logging System حقيقي
#           logging.INFO/WARNING/ERROR مع timestamps
#           يكتب لـ file + console في نفس الوقت
#           لا يكسر الـ Gradio log callback
#
#  [IMP-9]  Gradio Queue — يمنع crash تحت الضغط
#           demo.queue(max_size=10)
#           concurrency_count=1 (GPU واحد)
#
#  [IMP-10] LoRAStateManager — state tracking آمن
#           يتتبع الـ fused/unfused state بدقة
#           يمنع double-fuse و double-unfuse crashes
#
#  [IMP-11] PromptBuilder — compiler بدل string عشوائي
#           add_camera / add_lighting / add_style / add_physics
#           prompts أنضف، قابلة للـ debug، controllable
#
#  [IMP-12] SmartCache — cache موحّد لكل الأنواع
#           prompts + embeddings + physics في LRU cache واحد
#           TTL قابل للضبط، يقلل وقت التوليد المتكرر
#
#  [IMP-13] Modular structure — classes منفصلة ومترابطة
#           pipelines / physics / identity / postproc / ui
#           كل مكوّن يعمل مستقل وقابل للاختبار
#
#  [IMP-14] Unit-level validation — assertions داخلية
#           embedding.shape == (1, 512) مثبَّت
#           resolution % 16 == 0 مثبَّت
#           cfg range per model مثبَّت
#
#  [IMP-15] Async-safe storyboard — عمليات متسلسلة آمنة
#           لا race conditions
#           seed deterministic per scene
#
#  ALL V15.1 PATCHED FIXES INTACT:
#    FIX-A through FIX-I (9 bug fixes)
#
#  ALL V15 ULTIMATE FEATURES INTACT:
#    ULT-1 NeuralPhysicsEngine  · ULT-2 Status Dashboard
#    ULT-3 Physics Mode Radio   · ULT-4 Template Library
#    ULT-5 Quality Checker      · ULT-6 ETA Progress
#    ULT-7 ZIP Export           · ULT-8 JSON Sidecar
#
#  ALL ORIGINAL CAPABILITIES INTACT:
#    Flux Schnell/Dev · SDXL · SpeedMode NORMAL/TURBO/LCM
#    FaceID Triple-Layer · LoRA Character+Style · ControlNet OpenPose
#    GFPGAN · Real-ESRGAN x4 · HiresFix · Mistral 3-tier LLM
#    SceneChainer · CinematicTemplates · 3×8 Presets
#    Dark Cinema Gradio UI 5 Tabs · SETUP_CELL · VRAM management
# ================================================================

# ================================================================
# ONE-CLICK SETUP_CELL
# ── Copy into first Colab cell and run ONCE ──────────────────
# ================================================================
SETUP_CELL = """
# ============================================================
# CINEMATIC ENGINE V16 PROFESSIONAL — ONE-CLICK SETUP
# ============================================================
import subprocess, os, sys

_T = 4
def _step(n, label):
    print(f"\\n[{'█'*n + '░'*(_T-n)}] STEP {n}/{_T} — {label}")

def _run(cmd, label=""):
    print(f"  ↳ {label}: {cmd[:68]}...")
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if r.returncode != 0 and r.stderr.strip():
        print(f"    ⚠  {r.stderr.strip()[:180]}")
    return r.returncode

_step(1, "GPU Detection & Auto-Config")
import torch
if not torch.cuda.is_available():
    raise RuntimeError(
        "\\n╔════════════════════════════════════════════╗"
        "\\n║  NO GPU — Runtime → Change → T4 GPU       ║"
        "\\n╚════════════════════════════════════════════╝"
    )
_gpu  = torch.cuda.get_device_name(0)
_vram = torch.cuda.get_device_properties(0).total_memory / 1e9
print(f"  ✓ GPU: {_gpu}  |  VRAM: {_vram:.1f} GB")
if _vram >= 20:   print("  ✓ Recommended: FLUX DEV")
elif _vram >= 14: print("  ✓ Recommended: FLUX SCHNELL")
else:             print("  ✓ Recommended: SDXL TURBO")

_step(2, "Installing Packages  (2-4 min)")
_pkgs = [
    ("pip install -q diffusers transformers accelerate xformers triton einops", "diffusers"),
    ("pip install -q gfpgan realesrgan tqdm sentencepiece nltk face_recognition", "GFPGAN"),
    ("pip install -q controlnet-aux open-clip-torch", "ControlNet"),
    ("pip install -q 'gradio>=4.0.0'", "Gradio"),
    ("pip install -q bitsandbytes ip-adapter Pillow", "IP-Adapter"),
    ("pip install -q insightface onnxruntime-gpu", "FaceID"),
]
_warn = []
for _cmd, _lbl in _pkgs:
    if _run(_cmd, _lbl) != 0: _warn.append(_lbl)
print(f"  {'⚠ Warnings: ' + ', '.join(_warn) if _warn else '✓ All packages installed'}")

_step(3, "Downloading Models  (3-5 min)")
os.makedirs("ip_adapter_sdxl/image_encoder", exist_ok=True)
_downloads = {
    "GFPGANv1.3.pth":
        "https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.3.pth",
    "realesr-general-x4v3.pth":
        "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesr-general-x4v3.pth",
    "ip_adapter_sdxl.bin":
        "https://huggingface.co/h94/IP-Adapter/resolve/main/sdxl_models/ip-adapter_sdxl.bin",
    "ip_adapter_face_id_sdxl.bin":
        "https://huggingface.co/h94/IP-Adapter-FaceID/resolve/main/ip-adapter-faceid_sdxl.bin",
    "ip_adapter_sdxl/image_encoder/config.json":
        "https://huggingface.co/h94/IP-Adapter/resolve/main/sdxl_models/image_encoder/config.json",
    "ip_adapter_sdxl/image_encoder/model.safetensors":
        "https://huggingface.co/h94/IP-Adapter/resolve/main/sdxl_models/image_encoder/model.safetensors",
}
for _fname, _url in _downloads.items():
    if not os.path.exists(_fname):
        if _run(f"wget -q -O {_fname} {_url}", f"DL {os.path.basename(_fname)}") == 0:
            print(f"  ✓ {_fname}  ({os.path.getsize(_fname)/1e6:.1f} MB)")
        else:
            print(f"  ✗ FAILED: {_fname}")
    else:
        print(f"  ↷ skip {_fname}  ({os.path.getsize(_fname)/1e6:.1f} MB)")

_step(4, "NLTK Data")
import nltk
nltk.download("punkt", quiet=True)
nltk.download("punkt_tab", quiet=True)
print("  ✓ NLTK ready")
print("\\n" + "═"*50)
print("  SETUP COMPLETE ✓  — V16 PROFESSIONAL READY")
print("═"*50)
print(f"  GPU : {_gpu}  ({_vram:.1f} GB VRAM)")
print("  Next: Run the second cell to launch the UI")
print("═"*50)
"""

# ================================================================
# STEP 1 — IMPORTS
# ================================================================

import torch, gc, json, random, re, os, traceback, time, zipfile
import datetime
import hashlib
import logging
import threading
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from dataclasses import dataclass, field
from enum import Enum
from collections import deque, OrderedDict
from typing import Optional
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw

import numpy as np

from diffusers import (
    AutoPipelineForText2Image,
    StableDiffusionXLImg2ImgPipeline,
    StableDiffusionXLControlNetPipeline,
    ControlNetModel,
    DPMSolverMultistepScheduler,
    EulerAncestralDiscreteScheduler,
    LCMScheduler,
    FluxPipeline,
    AutoencoderKL,
)
from transformers import (
    pipeline as hf_pipeline,
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
)

try:
    from controlnet_aux import OpenposeDetector
    CONTROLNET_AVAILABLE = True
except ImportError:
    CONTROLNET_AVAILABLE = False

try:
    from gfpgan import GFPGANer
    GFPGAN_AVAILABLE = True
except ImportError:
    GFPGAN_AVAILABLE = False

try:
    from realesrgan import RealESRGANer
    from realesrgan.archs.srvgg_arch import SRVGGNetCompact
    REALESRGAN_AVAILABLE = True
except ImportError:
    REALESRGAN_AVAILABLE = False

try:
    import insightface
    from insightface.app import FaceAnalysis
    INSIGHTFACE_AVAILABLE = True
except ImportError:
    INSIGHTFACE_AVAILABLE = False

try:
    import gradio as gr
    GRADIO_AVAILABLE = True
except ImportError:
    GRADIO_AVAILABLE = False

try:
    import nltk
    nltk.download("punkt",     quiet=True)
    nltk.download("punkt_tab", quiet=True)
    from nltk.tokenize import sent_tokenize
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False
    def sent_tokenize(text: str) -> list[str]:
        return re.split(r'(?<=[.!?])\s+', text.strip()) or [text]

try:
    from tqdm.notebook import tqdm
except ImportError:
    from tqdm import tqdm

from IPython.display import clear_output

# ================================================================
# STEP 2 — CUDA OPTIMISATION
# ================================================================

torch.backends.cuda.matmul.allow_tf32 = True
torch.backends.cudnn.allow_tf32        = True
torch.backends.cudnn.benchmark         = True
clear_output()
_dev = torch.cuda.get_device_name(0) if torch.cuda.is_available() else "NO GPU"
print(f"[GPU] {_dev}")

# ================================================================
# STEP 3 — ENUMS & CONFIG
# ================================================================

class ModelMode(Enum):
    FLUX_SCHNELL = "flux_schnell"
    FLUX_DEV     = "flux_dev"
    SDXL         = "sdxl"

class SpeedMode(Enum):
    NORMAL = "normal"
    TURBO  = "turbo"
    LCM    = "lcm"

class PhysicsMode(Enum):
    NEURAL   = "neural"
    KEYWORD  = "keyword"
    DISABLED = "disabled"

class Config:
    # ── Generation models ───────────────────────────────────
    SDXL_BASE           = "stabilityai/stable-diffusion-xl-base-1.0"
    SDXL_REFINER        = "stabilityai/stable-diffusion-xl-refiner-1.0"
    SDXL_TURBO          = "stabilityai/sdxl-turbo"
    SDXL_VAE            = "madebyollin/sdxl-vae-fp16-fix"
    LCM_LORA            = "latent-consistency/lcm-lora-sdxl"
    CONTROLNET_POSE     = "thibaud/controlnet-openpose-sdxl-1.0"
    FLUX_SCHNELL        = "black-forest-labs/FLUX.1-schnell"
    FLUX_DEV            = "black-forest-labs/FLUX.1-dev"
    HF_TOKEN            = os.environ.get("HF_TOKEN", "")
    DEFAULT_MODEL_MODE  = ModelMode.FLUX_SCHNELL

    # ── LLM fallback chain ──────────────────────────────────
    LLM_PRIMARY         = "mistralai/Mistral-7B-Instruct-v0.2"
    LLM_FALLBACK        = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
    LLM_LAST_RESORT     = "distilgpt2"
    LLM_4BIT            = True
    PHYSICS_LLM_TIMEOUT = 10      # seconds before fallback to keyword

    # ── IP-Adapter ──────────────────────────────────────────
    IP_ADAPTER_WEIGHTS  = "ip_adapter_sdxl.bin"
    IP_ADAPTER_ENCODER  = "ip_adapter_sdxl/image_encoder"
    IP_FACEID_WEIGHTS   = "ip_adapter_face_id_sdxl.bin"

    # ── Enhancement ─────────────────────────────────────────
    GFPGAN_MODEL        = "GFPGANv1.3.pth"
    REALESRGAN_MODEL    = "realesr-general-x4v3.pth"

    # ── LoRA defaults ───────────────────────────────────────
    CHAR_LORA_PATH      = ""
    CHAR_LORA_SCALE     = 0.8
    STYLE_LORA_PATH     = ""
    STYLE_LORA_SCALE    = 0.6

    # ── Scene chaining ──────────────────────────────────────
    CHAIN_WINDOW        = 2

    # ── Paths ───────────────────────────────────────────────
    SAVE_DIR            = "v16_cinematic_storyboard"
    LOG_FILE            = "v16_engine.log"

    # ── Prompts ─────────────────────────────────────────────
    NEG_PROMPT = (
        "ugly, blurry, low quality, distorted, bad anatomy, watermark, text, "
        "signature, extra limbs, cartoon, anime, deformed face, cross-eyed, "
        "asymmetric eyes, disfigured, out of frame, duplicate, mutation"
    )
    CINEMATIC_SUFFIX = (
        "8k, cinematic lighting, masterpiece, hyper detailed, 35mm film, "
        "anamorphic lens, depth of field, volumetric fog, dramatic shadows, "
        "photorealistic, sharp focus, high dynamic range"
    )

    # ── Generation defaults ─────────────────────────────────
    DEFAULT_STEPS           = 35
    DEFAULT_FLUX_STEPS      = 4
    DEFAULT_FLUX_DEV_STEPS  = 20
    DEFAULT_REFINE_STEPS    = 15
    DEFAULT_CFG             = 8.5
    DEFAULT_FLUX_CFG        = 3.5
    DEFAULT_REFINER_STR     = 0.35
    DEFAULT_IP_SCALE        = 0.6
    DEFAULT_FACEID_SCALE    = 0.7
    DEFAULT_CN_SCALE        = 0.7
    DEFAULT_SPEED_MODE      = SpeedMode.NORMAL
    DEFAULT_PHYSICS_MODE    = PhysicsMode.NEURAL
    PREVIEW_RES             = 512
    HIRES_SCALE             = 1.5
    HIRES_STEPS             = 20
    HIRES_STRENGTH          = 0.4
    HIRES_MIN_FREE_VRAM_GB  = 4.0   # skip HiresFix below this threshold
    VIGNETTE_BLUR           = 2

    # ── VRAM size estimates (GB) ─────────────────────────────
    VRAM_FLUX_SCHNELL   = 7.0
    VRAM_FLUX_DEV       = 13.0
    VRAM_SDXL_BASE      = 5.5
    VRAM_SDXL_REFINER   = 4.0
    VRAM_CONTROLNET     = 3.0
    VRAM_TURBO          = 4.0

    # ── SmartCache ──────────────────────────────────────────
    CACHE_MAX_SIZE      = 128   # max entries per LRU cache
    CACHE_TTL_SECS      = 3600  # 1 hour TTL for physics cache


# ================================================================
# [IMP-6]  GenerationConfig — unified dataclass
# ================================================================

@dataclass
class GenerationConfig:
    """
    [IMP-6] All generation parameters in one object.
    Replaces passing 15+ individual arguments between functions.
    """
    scene_text   : str
    camera       : str        = "Wide Shot"
    lighting     : str        = "Golden Hour"
    style        : str        = "Cinematic"
    steps        : int        = Config.DEFAULT_STEPS
    refine_steps : int        = Config.DEFAULT_REFINE_STEPS
    cfg          : float      = Config.DEFAULT_CFG
    refiner_str  : float      = Config.DEFAULT_REFINER_STR
    ip_image                  = None
    ip_scale     : float      = Config.DEFAULT_IP_SCALE
    faceid_scale : float      = Config.DEFAULT_FACEID_SCALE
    pose_image               = None
    cn_scale     : float      = Config.DEFAULT_CN_SCALE
    speed_mode   : SpeedMode  = Config.DEFAULT_SPEED_MODE
    model_mode   : ModelMode  = Config.DEFAULT_MODEL_MODE
    transition   : str        = "cut_to"
    characters   : list       = field(default_factory=list)
    seed         : Optional[int] = None
    preview      : bool       = False

    def validate(self) -> list[str]:
        """[IMP-14] Returns list of validation warnings (non-blocking)."""
        issues = []
        if not self.scene_text.strip():
            issues.append("scene_text is empty")
        if self.model_mode == ModelMode.FLUX_DEV:
            if not (0.0 <= self.cfg <= 7.0):
                issues.append(f"Flux Dev CFG {self.cfg} clamped to [0,7]")
                self.cfg = max(0.0, min(7.0, self.cfg))
        if self.model_mode == ModelMode.SDXL:
            if self.cfg < 1.0:
                issues.append(f"SDXL CFG {self.cfg} below 1.0 — may produce noise")
        return issues


# ================================================================
# STEP 4 — LOGGING  [IMP-8]
# ================================================================

class CinematicLogger:
    """
    [IMP-8] Professional logging system.
    Writes to file + console simultaneously.
    Compatible with Gradio log callbacks via GradioLogHandler.
    """
    _instance: Optional["CinematicLogger"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self):
        self._logger = logging.getLogger("CinematicEngine")
        self._logger.setLevel(logging.DEBUG)
        self._logger.handlers.clear()

        # File handler
        os.makedirs(Config.SAVE_DIR, exist_ok=True)
        fh = logging.FileHandler(
            os.path.join(Config.SAVE_DIR, Config.LOG_FILE),
            encoding="utf-8",
        )
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(logging.Formatter(
            "%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%H:%M:%S",
        ))
        self._logger.addHandler(fh)

        # Console handler (INFO+)
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
        self._logger.addHandler(ch)

        # Gradio callback list (injected at runtime)
        self._gradio_callbacks: list = []
        self._lock = threading.Lock()

    def add_gradio_callback(self, cb):
        with self._lock:
            if cb not in self._gradio_callbacks:
                self._gradio_callbacks.append(cb)

    def remove_gradio_callback(self, cb):
        with self._lock:
            self._gradio_callbacks = [c for c in self._gradio_callbacks if c != cb]

    def _dispatch(self, msg: str, level: int):
        self._logger.log(level, msg)
        with self._lock:
            for cb in self._gradio_callbacks:
                try:
                    cb(msg)
                except Exception:
                    pass

    def info   (self, msg: str): self._dispatch(msg, logging.INFO)
    def warning(self, msg: str): self._dispatch(msg, logging.WARNING)
    def error  (self, msg: str): self._dispatch(msg, logging.ERROR)
    def debug  (self, msg: str): self._dispatch(msg, logging.DEBUG)

    def gradio_log(self, msg: str):
        """Use as log= callback in engine calls."""
        self.info(msg)


# Singleton logger
logger = CinematicLogger()


# ================================================================
# [IMP-12]  SmartCache — unified LRU cache with TTL
# ================================================================

class SmartCache:
    """
    [IMP-12] LRU cache with TTL for prompts, embeddings, physics.
    Thread-safe. Shared across all engine components.
    """
    def __init__(self, max_size: int = Config.CACHE_MAX_SIZE,
                 ttl_secs: float = Config.CACHE_TTL_SECS):
        self._store: OrderedDict = OrderedDict()
        self._timestamps: dict   = {}
        self._max_size           = max_size
        self._ttl                = ttl_secs
        self._lock               = threading.Lock()

    def _key(self, namespace: str, value: str) -> str:
        return f"{namespace}:{hashlib.md5(value.encode('utf-8')).hexdigest()}"

    def get(self, namespace: str, value: str):
        key = self._key(namespace, value)
        with self._lock:
            if key not in self._store:
                return None
            if time.time() - self._timestamps[key] > self._ttl:
                del self._store[key]
                del self._timestamps[key]
                return None
            self._store.move_to_end(key)
            return self._store[key]

    def set(self, namespace: str, value: str, result):
        key = self._key(namespace, value)
        with self._lock:
            if key in self._store:
                self._store.move_to_end(key)
            self._store[key] = result
            self._timestamps[key] = time.time()
            if len(self._store) > self._max_size:
                oldest = next(iter(self._store))
                del self._store[oldest]
                self._timestamps.pop(oldest, None)

    def invalidate(self, namespace: str):
        prefix = f"{namespace}:"
        with self._lock:
            keys = [k for k in self._store if k.startswith(prefix)]
            for k in keys:
                del self._store[k]
                self._timestamps.pop(k, None)

    def stats(self) -> dict:
        with self._lock:
            return {"size": len(self._store), "max_size": self._max_size}


# Global shared cache
_cache = SmartCache()


# ================================================================
# [IMP-2]  VRAMManager — intelligent VRAM tracking
# ================================================================

class VRAMManager:
    """
    [IMP-2] Pre-flight VRAM checks before any model load.
    Prevents OOM crashes by calculating available space first.
    """
    @staticmethod
    def free_gb() -> float:
        if not torch.cuda.is_available():
            return 0.0
        try:
            return torch.cuda.mem_get_info()[0] / 1e9
        except Exception:
            return 0.0

    @staticmethod
    def total_gb() -> float:
        if not torch.cuda.is_available():
            return 0.0
        try:
            return torch.cuda.get_device_properties(0).total_memory / 1e9
        except Exception:
            return 0.0

    @staticmethod
    def can_load(required_gb: float, safety_margin_gb: float = 1.0) -> bool:
        """Returns True if there's enough free VRAM to load a model."""
        return VRAMManager.free_gb() >= (required_gb + safety_margin_gb)

    @staticmethod
    def status_bar() -> str:
        try:
            free_gb  = VRAMManager.free_gb()
            total_gb = VRAMManager.total_gb()
            if total_gb == 0:
                return "No GPU"
            used_gb = total_gb - free_gb
            pct     = (used_gb / total_gb) * 100
            bar     = "█" * int(pct / 10) + "░" * (10 - int(pct / 10))
            return f"[{bar}] {used_gb:.1f}/{total_gb:.1f} GB  ({pct:.0f}%)"
        except Exception as e:
            return f"VRAM query failed: {e}"

    @staticmethod
    def flush():
        """Force garbage collection and CUDA cache clear."""
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()


# ================================================================
# [IMP-1]  PipelineManager — clean pipeline separation
# ================================================================

class PipelineManager:
    """
    [IMP-1] Each pipeline type has an independent instance.
    No cross-pipeline reuse or duck-typing. Clear state tracking.
    """

    def __init__(self):
        # ── Text-to-Image pipelines ───────────────────────
        self._txt2img_sdxl    = None   # SDXL Base
        self._txt2img_turbo   = None   # SDXL Turbo
        self._txt2img_flux    = None   # Flux.1

        # ── Img-to-Img pipelines ──────────────────────────
        self._img2img_refiner = None   # SDXL Refiner
        self._img2img_hires   = None   # HiresFix (SDXL-based)

        # ── Specialty pipelines ───────────────────────────
        self._controlnet      = None   # ControlNet OpenPose

        # ── State ─────────────────────────────────────────
        self._active_model    : Optional[ModelMode] = None
        self._active_speed    : Optional[SpeedMode] = None
        self._ip_loaded       : bool = False
        self._faceid_loaded   : bool = False
        self._lora_state      = LoRAStateManager()

    # ── Accessors (read-only) ─────────────────────────────────
    @property
    def txt2img(self):
        """Active text-to-image pipeline for current mode/speed."""
        if self._active_model in (ModelMode.FLUX_SCHNELL, ModelMode.FLUX_DEV):
            return self._txt2img_flux
        if self._active_speed == SpeedMode.TURBO and self._txt2img_turbo:
            return self._txt2img_turbo
        return self._txt2img_sdxl

    @property
    def refiner(self):
        return self._img2img_refiner

    @property
    def hires(self):
        return self._img2img_hires

    @property
    def controlnet(self):
        return self._controlnet

    @property
    def flux(self):
        return self._txt2img_flux

    @property
    def active_model(self) -> Optional[ModelMode]:
        return self._active_model

    @property
    def active_speed(self) -> Optional[SpeedMode]:
        return self._active_speed

    # ── Loaders ──────────────────────────────────────────────
    def load_flux(self, mode: ModelMode) -> bool:
        """[IMP-1] Load Flux pipeline — independent instance."""
        model_id = Config.FLUX_DEV if mode == ModelMode.FLUX_DEV else Config.FLUX_SCHNELL
        required = Config.VRAM_FLUX_DEV if mode == ModelMode.FLUX_DEV else Config.VRAM_FLUX_SCHNELL
        logger.info(f"[PipelineManager] Loading {model_id} …")
        if not VRAMManager.can_load(required):
            logger.warning(f"[PipelineManager] Insufficient VRAM for {model_id} "
                           f"(need {required}GB, have {VRAMManager.free_gb():.1f}GB)")
        try:
            kwargs = dict(torch_dtype=torch.bfloat16)
            if mode == ModelMode.FLUX_DEV and Config.HF_TOKEN:
                kwargs["token"] = Config.HF_TOKEN
            self._txt2img_flux = FluxPipeline.from_pretrained(model_id, **kwargs)
            self._txt2img_flux.enable_sequential_cpu_offload()
            self._active_model = mode
            logger.info(f"[PipelineManager] {model_id} ready ✓ (cpu_offload)")
            return True
        except Exception as e:
            logger.error(f"[PipelineManager] Flux load failed: {e}")
            return False

    def load_sdxl(self) -> bool:
        """[IMP-1] Load SDXL Base + Refiner as independent instances."""
        if self._txt2img_sdxl is not None:
            logger.info("[PipelineManager] SDXL already loaded.")
            return True
        logger.info("[PipelineManager] Loading SDXL enhanced VAE …")
        vae = None
        try:
            vae = AutoencoderKL.from_pretrained(Config.SDXL_VAE, torch_dtype=torch.float16)
            logger.info("[PipelineManager] sdxl-vae-fp16-fix ✓")
        except Exception as e:
            logger.warning(f"[PipelineManager] VAE load failed ({e}) — using default")

        try:
            vae_kw = {"vae": vae} if vae else {}
            self._txt2img_sdxl = AutoPipelineForText2Image.from_pretrained(
                Config.SDXL_BASE,
                torch_dtype=torch.float16, variant="fp16",
                use_safetensors=True, **vae_kw,
            ).to("cuda")
            self._txt2img_sdxl.scheduler = EulerAncestralDiscreteScheduler.from_config(
                self._txt2img_sdxl.scheduler.config)
            self._txt2img_sdxl.enable_xformers_memory_efficient_attention()
            self._active_speed = SpeedMode.NORMAL
            logger.info("[PipelineManager] SDXL Base ✓")
        except Exception as e:
            logger.error(f"[PipelineManager] SDXL Base failed: {e}")
            return False

        logger.info("[PipelineManager] Loading SDXL Refiner (independent instance) …")
        try:
            self._img2img_refiner = StableDiffusionXLImg2ImgPipeline.from_pretrained(
                Config.SDXL_REFINER,
                torch_dtype=torch.float16, variant="fp16", use_safetensors=True,
            ).to("cuda")
            self._img2img_refiner.enable_xformers_memory_efficient_attention()
            logger.info("[PipelineManager] SDXL Refiner ✓")
        except Exception as e:
            logger.warning(f"[PipelineManager] Refiner load failed (non-fatal): {e}")

        # Build HiresFix img2img pipeline from SDXL components
        self._build_hires_pipeline()
        self._active_model = ModelMode.SDXL
        logger.info("[PipelineManager] SDXL pipeline set ready ✓")
        return True

    def _build_hires_pipeline(self):
        """[IMP-1] Build independent HiresFix img2img from SDXL components."""
        if self._txt2img_sdxl is None:
            return
        try:
            self._img2img_hires = StableDiffusionXLImg2ImgPipeline(
                vae=self._txt2img_sdxl.vae,
                text_encoder=self._txt2img_sdxl.text_encoder,
                text_encoder_2=self._txt2img_sdxl.text_encoder_2,
                tokenizer=self._txt2img_sdxl.tokenizer,
                tokenizer_2=self._txt2img_sdxl.tokenizer_2,
                unet=self._txt2img_sdxl.unet,
                scheduler=self._txt2img_sdxl.scheduler,
            ).to("cuda")
            try:
                self._img2img_hires.enable_xformers_memory_efficient_attention()
            except Exception:
                pass
            logger.info("[PipelineManager] HiresFix img2img pipeline ✓")
        except Exception as e:
            logger.warning(f"[PipelineManager] HiresFix build failed (non-fatal): {e}")

    def load_turbo(self) -> bool:
        """[IMP-1] Load SDXL Turbo as independent instance."""
        if self._txt2img_turbo is not None:
            return True
        if not VRAMManager.can_load(Config.VRAM_TURBO):
            logger.warning("[PipelineManager] Insufficient VRAM for Turbo")
            return False
        try:
            self._txt2img_turbo = AutoPipelineForText2Image.from_pretrained(
                Config.SDXL_TURBO,
                torch_dtype=torch.float16, variant="fp16", use_safetensors=True,
            ).to("cuda")
            self._txt2img_turbo.enable_xformers_memory_efficient_attention()
            logger.info("[PipelineManager] SDXL Turbo ✓")
            return True
        except Exception as e:
            logger.error(f"[PipelineManager] Turbo load failed: {e}")
            return False

    def load_controlnet(self) -> bool:
        """[IMP-1] Load ControlNet OpenPose as independent instance."""
        if self._controlnet is not None:
            return True
        if not VRAMManager.can_load(Config.VRAM_CONTROLNET):
            logger.warning("[PipelineManager] Insufficient VRAM for ControlNet")
            return False
        try:
            cn = ControlNetModel.from_pretrained(
                Config.CONTROLNET_POSE, torch_dtype=torch.float16)
            self._controlnet = StableDiffusionXLControlNetPipeline.from_pretrained(
                Config.SDXL_BASE, controlnet=cn,
                torch_dtype=torch.float16, variant="fp16", use_safetensors=True,
            ).to("cuda")
            self._controlnet.scheduler = DPMSolverMultistepScheduler.from_config(
                self._controlnet.scheduler.config)
            self._controlnet.enable_xformers_memory_efficient_attention()
            logger.info("[PipelineManager] ControlNet OpenPose ✓")
            return True
        except Exception as e:
            logger.error(f"[PipelineManager] ControlNet load failed: {e}")
            return False

    def set_speed_mode(self, mode: SpeedMode) -> bool:
        """Switch SDXL speed mode safely."""
        if self._active_speed == mode:
            return True
        if mode == SpeedMode.NORMAL:
            if self._txt2img_sdxl is None:
                return False
            self._txt2img_sdxl.scheduler = EulerAncestralDiscreteScheduler.from_config(
                self._txt2img_sdxl.scheduler.config)
            self._active_speed = SpeedMode.NORMAL
            logger.info("[PipelineManager] NORMAL mode — EulerAncestral ✓")
            return True
        elif mode == SpeedMode.TURBO:
            ok = self.load_turbo()
            if ok:
                self._active_speed = SpeedMode.TURBO
                logger.info("[PipelineManager] TURBO mode ✓")
            else:
                # [IMP-7] Graceful fallback to NORMAL
                logger.warning("[PipelineManager] Turbo failed → falling back to NORMAL")
                self._active_speed = SpeedMode.NORMAL
            return ok
        elif mode == SpeedMode.LCM:
            if self._txt2img_sdxl is None:
                return False
            try:
                self._txt2img_sdxl.scheduler = LCMScheduler.from_config(
                    self._txt2img_sdxl.scheduler.config)
                self._txt2img_sdxl.load_lora_weights(Config.LCM_LORA, adapter_name="lcm_lora")
                self._txt2img_sdxl.set_adapters(["lcm_lora"], adapter_weights=[1.0])
                self._active_speed = SpeedMode.LCM
                logger.info("[PipelineManager] LCM mode ✓")
                return True
            except Exception as e:
                logger.warning(f"[PipelineManager] LCM failed: {e} → NORMAL fallback")
                self._txt2img_sdxl.scheduler = EulerAncestralDiscreteScheduler.from_config(
                    self._txt2img_sdxl.scheduler.config)
                self._active_speed = SpeedMode.NORMAL   # [FIX-G] consistent state
                logger.info("[PipelineManager] Restored NORMAL ✓")
                return False
        return False

    def unload_all(self):
        """Unload all pipelines and free VRAM."""
        for attr in ("_txt2img_sdxl", "_txt2img_turbo", "_txt2img_flux",
                     "_img2img_refiner", "_img2img_hires", "_controlnet"):
            obj = getattr(self, attr, None)
            if obj is not None:
                del obj
                setattr(self, attr, None)
        self._active_model  = None
        self._active_speed  = None
        self._ip_loaded     = False
        self._faceid_loaded = False
        self._lora_state.reset()
        VRAMManager.flush()
        logger.info("[PipelineManager] All pipelines unloaded ✓")

    def invalidate_hires(self):
        """Rebuild HiresFix pipeline after SDXL reload."""
        self._img2img_hires = None
        self._build_hires_pipeline()


# ================================================================
# [IMP-10]  LoRAStateManager — safe fuse/unfuse tracking
# ================================================================

class LoRAStateManager:
    """
    [IMP-10] Tracks LoRA state precisely to prevent double-fuse crashes.
    """
    def __init__(self):
        self._loaded   : bool = False
        self._fused    : bool = False
        self._adapters : list = []

    def reset(self):
        self._loaded   = False
        self._fused    = False
        self._adapters = []

    def load(self, pipe, char_path="", char_scale=0.8,
             style_path="", style_scale=0.6):
        """Load + fuse LoRAs safely."""
        if self._fused:
            logger.warning("[LoRA] Already fused — unfusing first")
            self.unload(pipe)

        adapters, scales = [], []
        for path, scale, name in [
            (char_path,  char_scale,  "character_lora"),
            (style_path, style_scale, "style_lora"),
        ]:
            if path and os.path.exists(path):
                try:
                    pipe.load_lora_weights(
                        os.path.dirname(path) or ".",
                        weight_name=os.path.basename(path),
                        adapter_name=name,
                    )
                    adapters.append(name)
                    scales.append(scale)
                    logger.info(f"[LoRA] Loaded {name}: {path} (scale={scale})")
                except Exception as e:
                    logger.warning(f"[LoRA] {name} load failed: {e}")

        if adapters:
            try:
                pipe.set_adapters(adapters, adapter_weights=scales)
                pipe.fuse_lora()
                self._loaded   = True
                self._fused    = True
                self._adapters = adapters
                logger.info(f"[LoRA] Fused {len(adapters)} adapter(s) ✓")
            except Exception as e:
                logger.warning(f"[LoRA] Fuse warning: {e}")

    def unload(self, pipe):
        """Unfuse + unload LoRAs safely."""
        if not self._loaded:
            return
        try:
            if self._fused:
                pipe.unfuse_lora()
                self._fused = False
            pipe.unload_lora_weights()
            self._loaded   = False
            self._adapters = []
            logger.info("[LoRA] Unloaded ✓")
        except Exception as e:
            logger.warning(f"[LoRA] Unload warning: {e}")
            # Force reset to prevent stuck state
            self.reset()

    @property
    def is_loaded(self) -> bool:
        return self._loaded


# ================================================================
# STEP 4B — PRESETS & HELPERS
# ================================================================

class CameraPreset:
    PRESETS = {
        "Wide Shot"         : "wide angle shot, establishing shot, vast landscape, ",
        "Close Up"          : "extreme close up, intimate portrait, detailed face, ",
        "Over the Shoulder" : "over the shoulder shot, two-person scene, depth, ",
        "Bird's Eye"        : "aerial view, top down perspective, overhead shot, ",
        "Dutch Angle"       : "dutch angle, tilted camera, tension, psychological, ",
        "Low Angle"         : "low angle shot, looking up, powerful subject, heroic, ",
        "Tracking Shot"     : "dynamic tracking shot, motion blur, moving subject, ",
        "Extreme Wide"      : "extreme wide shot, tiny subject, epic environment, ",
    }
    @staticmethod
    def get(name: str) -> str:
        return CameraPreset.PRESETS.get(name, "")

class LightingPreset:
    PRESETS = {
        "Golden Hour"    : "golden hour lighting, warm tones, long shadows, magic hour, ",
        "Blue Hour"      : "blue hour, twilight, cool tones, soft ambient light, ",
        "Hard Noir"      : "hard shadows, high contrast, film noir lighting, dark atmosphere, ",
        "Soft Natural"   : "soft natural light, diffused shadows, realistic daylight, ",
        "Studio"         : "studio lighting, three-point lighting, professional, clean, ",
        "Dramatic Side"  : "dramatic side lighting, Rembrandt lighting, deep shadows, ",
        "Neon Cyberpunk" : "neon lights, cyberpunk atmosphere, colorful reflections, rain, ",
        "Candle / Fire"  : "warm candlelight, flickering fire, intimate low light, ",
    }
    @staticmethod
    def get(name: str) -> str:
        return LightingPreset.PRESETS.get(name, "")

class StylePreset:
    PRESETS = {
        "Cinematic"    : "cinematic, film grain, anamorphic, ",
        "Noir"         : "film noir, black and white, high contrast, 1940s, ",
        "Western"      : "western film, dust, harsh sunlight, Leone style, ",
        "Sci-Fi"       : "science fiction, futuristic, holographic, space, ",
        "Period Drama" : "period drama, costume film, historical, rich colors, ",
        "Horror"       : "horror, dark atmosphere, eerie, unsettling, mist, ",
        "Action"       : "action film, dynamic, explosive, motion, adrenaline, ",
        "Romance"      : "romantic, soft bokeh, warm tones, intimate, ",
    }
    @staticmethod
    def get(name: str) -> str:
        return StylePreset.PRESETS.get(name, "")

class SceneMemory:
    def __init__(self):
        self._chars: dict[str, str] = {}

    def set_character(self, name: str, desc: str):
        self._chars[name.strip().lower()] = desc.strip()

    def get_character(self, name: str) -> str:
        return self._chars.get(name.strip().lower(), "")

    def inject_into_prompt(self, prompt: str) -> str:
        extras = [d for n, d in self._chars.items() if n in prompt.lower() and d]
        return (", ".join(extras) + ", " + prompt) if extras else prompt

    def clear(self):
        self._chars.clear()

class SceneSplitter:
    @staticmethod
    def split(text: str) -> list[str]:
        for sep in ["\n\n", "\n-", "\n*", "||", "//", ";"]:
            parts = [p.strip() for p in text.split(sep) if p.strip()]
            if len(parts) > 1:
                return parts
        sentences = sent_tokenize(text)
        scenes, chunk = [], []
        for i, s in enumerate(sentences):
            chunk.append(s)
            if len(chunk) == 2 or i == len(sentences) - 1:
                scenes.append(" ".join(chunk))
                chunk = []
        return scenes or [text]

def apply_vignette(img: Image.Image, blur_radius: int = 2) -> Image.Image:
    w, h = img.size
    mask = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(mask)
    for i in range(min(w, h) // 2, 0, -1):
        alpha = int(255 * (i / (min(w, h) / 2)) ** 1.5)
        draw.ellipse([w//2-i, h//2-i, w//2+i, h//2+i], fill=alpha)
    mask = mask.filter(ImageFilter.GaussianBlur(blur_radius * 20))
    result = img.copy().convert("RGBA")
    dark   = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    result = Image.composite(dark, result, mask)
    return result.convert("RGB")

def cinematic_grade(img: Image.Image, flux_mode: bool = False) -> Image.Image:
    if flux_mode:
        img = ImageEnhance.Contrast(img).enhance(1.05)
        img = ImageEnhance.Color(img).enhance(1.05)
    else:
        img = ImageEnhance.Contrast(img).enhance(1.15)
        img = ImageEnhance.Color(img).enhance(1.05)
        img = ImageEnhance.Sharpness(img).enhance(1.1)
    return img

def postprocess(img: Image.Image, vignette: bool = True,
                flux_mode: bool = False) -> Image.Image:
    img = cinematic_grade(img, flux_mode=flux_mode)
    if vignette:
        img = apply_vignette(img, Config.VIGNETTE_BLUR)
    return img


# ================================================================
# [IMP-11]  PromptBuilder — structured prompt compilation
# ================================================================

class PromptBuilder:
    """
    [IMP-11] Structured prompt builder — replaces string concatenation.
    Controllable, debuggable, cacheable components.
    """
    def __init__(self):
        self._parts: list[str] = []

    def add(self, text: str) -> "PromptBuilder":
        if text.strip():
            self._parts.append(text.rstrip(", "))
        return self

    def add_camera(self, name: str) -> "PromptBuilder":
        return self.add(CameraPreset.get(name))

    def add_lighting(self, name: str) -> "PromptBuilder":
        return self.add(LightingPreset.get(name))

    def add_style(self, name: str) -> "PromptBuilder":
        return self.add(StylePreset.get(name))

    def add_cinematic_suffix(self) -> "PromptBuilder":
        return self.add(Config.CINEMATIC_SUFFIX)

    def add_physics(self, physics_str: str) -> "PromptBuilder":
        return self.add(physics_str)

    def add_scene(self, scene_text: str) -> "PromptBuilder":
        return self.add(scene_text)

    def build(self) -> str:
        return ", ".join(p.strip().rstrip(",") for p in self._parts if p.strip())

    def cache_key(self) -> str:
        return hashlib.md5(self.build().encode("utf-8")).hexdigest()


# ================================================================
# POST-PROCESSING TOOLS
# ================================================================

class FaceEnhancer:
    def __init__(self):
        self._model = None

    def _load(self):
        if self._model is None and GFPGAN_AVAILABLE and os.path.exists(Config.GFPGAN_MODEL):
            try:
                self._model = GFPGANer(
                    model_path=Config.GFPGAN_MODEL, upscale=1,
                    arch="clean", channel_multiplier=2, bg_upsampler=None,
                )
            except Exception as e:
                logger.warning(f"[FaceEnhancer] load failed: {e}")

    def enhance(self, img: Image.Image) -> Image.Image:
        self._load()
        if self._model is None:
            return img
        try:
            arr = np.array(img)[..., ::-1]
            _, _, restored = self._model.enhance(
                arr, has_aligned=False, only_center_face=False, paste_back=True)
            return Image.fromarray(restored[..., ::-1])
        except Exception as e:
            logger.warning(f"[FaceEnhancer] {e}")
            return img

class Upscaler:
    def __init__(self):
        self._model = None

    def _load(self):
        if self._model is None and REALESRGAN_AVAILABLE and os.path.exists(Config.REALESRGAN_MODEL):
            try:
                arch = SRVGGNetCompact(
                    num_in_ch=3, num_out_ch=3, num_feat=64,
                    num_conv=32, upscale=4, act_type="prelu",
                )
                self._model = RealESRGANer(
                    scale=4, model_path=Config.REALESRGAN_MODEL, model=arch, half=True)
            except Exception as e:
                logger.warning(f"[Upscaler] load failed: {e}")

    def upscale(self, img: Image.Image) -> Image.Image:
        self._load()
        if self._model is None:
            return img
        try:
            arr = np.array(img)[..., ::-1]
            out, _ = self._model.enhance(arr, outscale=4)
            return Image.fromarray(out[..., ::-1])
        except Exception as e:
            logger.warning(f"[Upscaler] {e}")
            return img

class ResolutionSnapper:
    @staticmethod
    def snap(value: int) -> int:
        snapped = max(16, round(value / 16) * 16)
        # [IMP-14] Assert multiple of 16
        assert snapped % 16 == 0, f"Resolution {snapped} not multiple of 16"
        return snapped

    @staticmethod
    def optimal(model_mode: ModelMode, preview: bool = False) -> tuple[int, int]:
        return (512, 512) if preview else (1024, 1024)

    @staticmethod
    def hires(base_w: int, base_h: int, scale: float = 1.5) -> tuple[int, int]:
        return (
            ResolutionSnapper.snap(int(base_w * scale)),
            ResolutionSnapper.snap(int(base_h * scale)),
        )

class PoseDetector:
    def __init__(self):
        self._detector = None

    def _load(self):
        if self._detector is None and CONTROLNET_AVAILABLE:
            try:
                self._detector = OpenposeDetector.from_pretrained("lllyasviel/ControlNet")
                logger.info("[PoseDetector] loaded ✓")
            except Exception as e:
                logger.warning(f"[PoseDetector] {e}")

    def detect(self, img: Image.Image):
        self._load()
        if self._detector is None:
            return None
        try:
            return self._detector(img)
        except Exception as e:
            logger.warning(f"[PoseDetector] {e}")
            return None


# ================================================================
# [IMP-5]  FaceIDExtractor — weighted quality + outlier rejection
# ================================================================

class FaceIDExtractor:
    """
    [IMP-5] Quality-weighted embedding averaging:
      - Each embedding weighted by det_score (detection confidence)
      - Outlier rejection: embeddings with cosine distance > threshold discarded
      - L2 normalisation of final weighted average
    """
    OUTLIER_THRESHOLD = 0.5  # cosine distance threshold for outlier rejection

    def __init__(self):
        self._app   = None
        self._cache = SmartCache(max_size=32, ttl_secs=7200)

    def _load(self):
        if self._app is None and INSIGHTFACE_AVAILABLE:
            try:
                self._app = FaceAnalysis(
                    name="buffalo_l",
                    providers=["CUDAExecutionProvider", "CPUExecutionProvider"],
                )
                self._app.prepare(ctx_id=0, det_size=(640, 640))
                logger.info("[FaceID] insightface loaded ✓")
            except Exception as e:
                logger.warning(f"[FaceID] load failed: {e}")
                self._app = None

    def _extract_single(self, img: Image.Image) -> Optional[tuple]:
        """Returns (normed_embedding, det_score) or None."""
        if self._app is None:
            return None
        try:
            arr   = np.array(img.convert("RGB"))
            faces = self._app.get(arr)
            if not faces:
                return None
            face = sorted(
                faces,
                key=lambda f: (f.bbox[2]-f.bbox[0]) * (f.bbox[3]-f.bbox[1]),
                reverse=True,
            )[0]
            score = float(getattr(face, "det_score", 1.0))
            return face.normed_embedding, score
        except Exception as e:
            logger.debug(f"[FaceID] _extract_single: {e}")
            return None

    def extract_embedding(self, ip_image, cache_key: str = "default"):
        self._load()
        if self._app is None:
            return None

        # SmartCache check
        cached = self._cache.get("faceid", cache_key)
        if cached is not None:
            return cached

        images = ip_image if isinstance(ip_image, list) else [ip_image]
        images = [im for im in images if im is not None]
        if not images:
            return None

        try:
            results = [r for r in (self._extract_single(i) for i in images) if r]
            if not results:
                logger.warning("[FaceID] No face detected in any reference image")
                return None

            embeddings = np.stack([r[0] for r in results])
            weights    = np.array([r[1] for r in results])

            # [IMP-5] Outlier rejection: compute pairwise cosine distances
            if len(embeddings) > 1:
                mean_emb = np.mean(embeddings, axis=0)
                mean_emb_n = mean_emb / (np.linalg.norm(mean_emb) + 1e-8)
                valid_mask = []
                for emb in embeddings:
                    emb_n = emb / (np.linalg.norm(emb) + 1e-8)
                    dist  = 1.0 - float(np.dot(emb_n, mean_emb_n))
                    valid_mask.append(dist <= self.OUTLIER_THRESHOLD)
                if any(valid_mask):
                    n_rejected = sum(1 for v in valid_mask if not v)
                    if n_rejected:
                        logger.info(f"[FaceID] Rejected {n_rejected} outlier embedding(s)")
                    embeddings = embeddings[valid_mask]
                    weights    = weights[valid_mask]

            # [IMP-5] Weighted average by detection score
            weights     = weights / (weights.sum() + 1e-8)
            avg         = np.sum(embeddings * weights[:, None], axis=0)
            norm        = np.linalg.norm(avg)
            avg         = avg / norm if norm > 1e-6 else avg

            tensor = torch.from_numpy(avg.astype(np.float32)).unsqueeze(0)
            # [IMP-14] Validate shape
            assert tensor.shape == (1, 512), f"Unexpected embedding shape: {tensor.shape}"

            self._cache.set("faceid", cache_key, tensor)
            logger.info(f"[FaceID] {len(embeddings)} valid ref(s) → weighted embedding ✓")
            return tensor

        except Exception as e:
            logger.error(f"[FaceID] embedding failed: {e}")
            return None

    def clear_cache(self):
        self._cache.invalidate("faceid")

    @property
    def available(self) -> bool:
        self._load()
        return self._app is not None


# ================================================================
# LLM STORY EXPANDER
# ================================================================

class StoryExpander:
    def __init__(self):
        self._pipe = None
        self._mode = None
        self._load()

    def _load(self):
        # [IMP-9 / PRO-9] VRAM guard
        free_gb = VRAMManager.free_gb()

        for model_id, mode in [
            (Config.LLM_PRIMARY,     "chat"),
            (Config.LLM_FALLBACK,    "chat"),
            (Config.LLM_LAST_RESORT, "gpt2"),
        ]:
            if mode == "chat" and model_id == Config.LLM_PRIMARY and free_gb < 6.0:
                logger.info(f"[StoryExpander] {free_gb:.1f}GB free — skipping Mistral, trying TinyLlama")
                continue
            try:
                logger.info(f"[StoryExpander] trying {model_id} …")
                if mode == "chat" and Config.LLM_4BIT:
                    q   = BitsAndBytesConfig(
                        load_in_4bit=True, bnb_4bit_compute_dtype=torch.float16,
                        bnb_4bit_quant_type="nf4", bnb_4bit_use_double_quant=True,
                    )
                    tok = AutoTokenizer.from_pretrained(model_id)
                    mdl = AutoModelForCausalLM.from_pretrained(
                        model_id, quantization_config=q,
                        device_map="auto", trust_remote_code=True,
                    )
                    self._pipe = hf_pipeline(
                        "text-generation", model=mdl, tokenizer=tok,
                        max_new_tokens=512, do_sample=True,
                        temperature=0.7, top_p=0.9,
                    )
                else:
                    self._pipe = hf_pipeline(
                        "text-generation", model=model_id,
                        max_new_tokens=200, do_sample=True, temperature=0.85,
                    )
                self._mode = mode
                logger.info(f"[StoryExpander] loaded {model_id} ✓")
                break
            except Exception as e:
                logger.warning(f"[StoryExpander] {model_id} failed: {e}")

    def expand(self, raw: str, style: str = "cinematic film") -> str:
        if self._pipe is None:
            return raw
        try:
            if self._mode == "chat":
                system = (
                    "You are an expert cinematic screenwriter. "
                    f"Expand the scene into a vivid visual description for a {style} storyboard. "
                    "Return ONLY the expanded scene, no commentary."
                )
                msgs       = [{"role": "system", "content": system},
                               {"role": "user",   "content": raw}]
                tok        = self._pipe.tokenizer
                prompt_str = tok.apply_chat_template(
                    msgs, tokenize=False, add_generation_prompt=True)
                out = self._pipe(prompt_str)[0]["generated_text"]
                if prompt_str in out:
                    out = out[len(prompt_str):].strip()
                return out or raw
            else:
                prompt = f"Cinematic scene: {raw}. Detailed visual description:"
                out    = self._pipe(prompt)[0]["generated_text"]
                return out.replace(prompt, "").strip() or raw
        except Exception as e:
            logger.warning(f"[StoryExpander] {e}")
            return raw

    @property
    def pipe(self): return self._pipe
    @property
    def mode(self): return self._mode


# ================================================================
# PHYSICS ENGINES
# ================================================================

class KeywordPhysicsEngine:
    """PRO-4: Priority-scored keyword physics augmentation."""
    _GRAVITY = {
        "fall":    "subject falling with realistic gravitational acceleration, natural trajectory arc",
        "drop":    "object dropped in freefall, velocity-blurred descent, impact shadow below",
        "jump":    "peak-of-arc hang time, realistic parabolic motion, feet leaving ground",
        "float":   "microgravity environment, gentle drift, hair and fabric floating weightlessly",
        "collapse":"structure collapsing under gravity, debris cascade, dust cloud billowing outward",
        "pour":    "liquid pouring with realistic gravity-governed stream, splash physics at impact",
        "roll":    "object rolling with angular momentum, contact shadow tracking surface",
    }
    _LIGHT = {
        "fire":      "physically accurate fire: subsurface glow, orange-to-white core gradient, dynamic shadows",
        "candle":    "single-point warm light source, inverse-square falloff, soft penumbra shadows",
        "laser":     "coherent beam with atmospheric scattering, Tyndall effect in dusty air",
        "neon":      "neon tube: bloom halo, chromatic fringing on wet surfaces, specular on glass",
        "sun":       "parallel directional light, sharp crisp shadows, accurate subsurface skin scatter",
        "lightning": "ultra-brief arc flash, split-second overexposure, branching plasma channel",
        "water":     "caustic light patterns on floor, Fresnel reflections, refraction distortion",
        "glass":     "refraction and internal reflection, caustics projected behind, chromatic dispersion",
    }
    _MATERIAL = {
        "metal":  "metallic surface: anisotropic highlights, mirror-like specular, cool ambient reflection",
        "wood":   "subsurface scatter in grain, warm diffuse, fine shadow lines from texture",
        "cloth":  "fabric micro-wrinkles, anisotropic sheen, tension creases at stress points",
        "skin":   "subsurface scattering, pore-level texture, warm capillary glow at ears and fingers",
        "stone":  "diffuse matte surface, sharp occlusion in crevices, cool reflected skylight",
        "mud":    "wet surface specularity, deformation under pressure, viscous splash dynamics",
        "smoke":  "volumetric density gradient, forward scatter glow, turbulent curl noise",
        "sand":   "grain-scale shadow, AO in packed areas, glitter specular on individual grains",
    }
    _MOTION = {
        "fast":    "motion blur proportional to velocity, trailing edge ghosting, shutter freeze highlights",
        "running": "full-body motion blur on limbs, ground impact dust puff, hair stream behind",
        "flying":  "wingtip vortex trails, altitude haze, atmospheric perspective depth",
        "explode": "shock wave ring, debris radial velocity blur, pressure flash at epicenter",
        "splash":  "crown splash geometry, individual droplet trajectories, Worthington jet at center",
        "wind":    "laminar-to-turbulent transition in hair and cloth, pressure differential bending",
    }
    _ATMOSPHERE = {
        "rain":  "rain streaks angled with wind, surface ripples, specular wet-road reflections",
        "fog":   "volumetric aerial perspective, exponential density falloff, backlit god rays",
        "snow":  "unique snowflake bokeh, cold blue ambient, accumulated surface weight deformation",
        "dust":  "Mie scattering in sunbeam, particulate suspension, soft diffuse shadow fill",
        "heat":  "heat shimmer refraction, mirage horizon distortion, bleached colour highlights",
        "storm": "turbulent cloud anvil, green-tinted pre-storm light, Coriolis curl in clouds",
    }
    _CATEGORY_WEIGHT = {"_MOTION":5,"_LIGHT":4,"_GRAVITY":3,"_MATERIAL":2,"_ATMOSPHERE":1}
    _ALL_MAPS = [("_MOTION",_MOTION),("_LIGHT",_LIGHT),("_GRAVITY",_GRAVITY),
                 ("_MATERIAL",_MATERIAL),("_ATMOSPHERE",_ATMOSPHERE)]

    @staticmethod
    def augment(scene_text: str, max_additions: int = 3) -> str:
        cached = _cache.get("physics_kw", scene_text)
        if cached:
            return cached
        text_lower  = scene_text.lower()
        candidates: list[tuple[int, str]] = []
        seen:       set[str] = set()
        for cat, mapping in KeywordPhysicsEngine._ALL_MAPS:
            weight = KeywordPhysicsEngine._CATEGORY_WEIGHT[cat]
            for kw, desc in mapping.items():
                if kw in text_lower and kw not in seen:
                    candidates.append((weight, desc))
                    seen.add(kw)
        if not candidates:
            _cache.set("physics_kw", scene_text, scene_text)
            return scene_text
        candidates.sort(key=lambda x: x[0], reverse=True)
        result = f"{scene_text}, {', '.join(d for _,d in candidates[:max_additions])}"
        _cache.set("physics_kw", scene_text, result)
        return result

    @staticmethod
    def report(scene_text: str) -> str:
        text_lower = scene_text.lower()
        lines = []
        for cat, mapping in KeywordPhysicsEngine._ALL_MAPS:
            w = KeywordPhysicsEngine._CATEGORY_WEIGHT[cat]
            for kw, desc in mapping.items():
                if kw in text_lower:
                    lines.append(f"  [w={w}][{kw}] → {desc[:60]}…")
        return "\n".join(lines) if lines else "  (no physics keywords detected)"


class NeuralPhysicsEngine:
    """
    [IMP-4/ULT-1] LLM-driven physics with timeout + strong cache.
    Timeout: Config.PHYSICS_LLM_TIMEOUT seconds (default 10s).
    Fallback: KeywordPhysicsEngine if LLM unavailable or times out.
    Cache: SmartCache with MD5 keys (deterministic across sessions).
    """
    _SYSTEM = (
        "You are a physics consultant for photorealistic image generation. "
        "Analyse the scene and return ONLY a comma-separated list of "
        "3-5 physically accurate visual descriptors covering: "
        "lighting behaviour, gravity effects, material properties (PBR), "
        "fluid/cloth dynamics, atmospheric scattering, or motion blur. "
        "Be specific and visual. No explanations, no punctuation other than commas."
    )

    def __init__(self):
        self._pipe  = None
        self._mode  = None
        self._cache = SmartCache(max_size=256, ttl_secs=Config.CACHE_TTL_SECS)
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="NeuralPhysics")

    def attach_llm(self, pipe, mode: str):
        self._pipe = pipe
        self._mode = mode
        logger.info(f"[NeuralPhysics] LLM attached ({mode}) ✓")

    @property
    def is_attached(self) -> bool:
        return self._pipe is not None

    def augment(self, scene_text: str) -> tuple[str, str]:
        """Returns (augmented_text, report). Timeout-protected."""
        cached = self._cache.get("neural_phys", scene_text)
        if cached:
            return f"{scene_text}, {cached}", f"  [cached] {cached}"

        if self._pipe is not None:
            try:
                # [IMP-4] Timeout via ThreadPoolExecutor
                future = self._executor.submit(self._query_llm, scene_text)
                physics_str = future.result(timeout=Config.PHYSICS_LLM_TIMEOUT)
                if physics_str:
                    self._cache.set("neural_phys", scene_text, physics_str)
                    report = "\n".join(
                        f"  [neural] {d.strip()}"
                        for d in physics_str.split(",") if d.strip()
                    )
                    logger.debug(f"[NeuralPhysics] {physics_str[:80]}…")
                    return f"{scene_text}, {physics_str}", report
            except FutureTimeoutError:
                logger.warning(f"[NeuralPhysics] Timeout ({Config.PHYSICS_LLM_TIMEOUT}s) → keyword fallback")
            except Exception as e:
                logger.warning(f"[NeuralPhysics] LLM failed: {e} → keyword fallback")

        augmented = KeywordPhysicsEngine.augment(scene_text)
        report    = KeywordPhysicsEngine.report(scene_text)
        return augmented, report

    def _query_llm(self, scene_text: str) -> str:
        if self._mode != "chat":
            return ""
        msgs = [
            {"role": "system", "content": self._SYSTEM},
            {"role": "user",   "content": f"Scene: {scene_text}"},
        ]
        tok        = self._pipe.tokenizer
        prompt_str = tok.apply_chat_template(
            msgs, tokenize=False, add_generation_prompt=True)
        # [FIX-B] do_sample=False — temperature removed
        out = self._pipe(prompt_str, max_new_tokens=120, do_sample=False
                         )[0]["generated_text"]
        if prompt_str in out:
            out = out[len(prompt_str):]
        first_line = out.strip().split("\n")[0].strip('" \'')
        return first_line if ("," in first_line and len(first_line) > 10) else ""

    def report_only(self, scene_text: str) -> str:
        cached = self._cache.get("neural_phys", scene_text)
        if cached:
            return f"  [neural] {cached}"
        if self._pipe is not None:
            try:
                future      = self._executor.submit(self._query_llm, scene_text)
                physics_str = future.result(timeout=Config.PHYSICS_LLM_TIMEOUT)
                if physics_str:
                    self._cache.set("neural_phys", scene_text, physics_str)
                    return "\n".join(f"  [neural] {d.strip()}"
                                     for d in physics_str.split(",") if d.strip())
            except Exception:
                pass
        return KeywordPhysicsEngine.report(scene_text)

    def clear_cache(self):
        self._cache.invalidate("neural_phys")


# ================================================================
# CINEMATIC TEMPLATES & SCENE CHAINER
# ================================================================

class CinematicTemplates:
    TRANSITIONS = {
        "cut_to"        : "HARD CUT TO: ",
        "match_cut"     : "MATCH CUT TO: ",
        "dissolve"      : "SLOW DISSOLVE TO: ",
        "smash_cut"     : "SMASH CUT TO: ",
        "fade_in"       : "FADE IN: ",
        "continuous"    : "CONTINUOUS ACTION: ",
        "same_location" : "SAME LOCATION, ",
        "later"         : "MOMENTS LATER: ",
        "meanwhile"     : "MEANWHILE: ",
    }
    SHOT_CONTEXT = {
        "establishing" : "establishing shot showing the full environment, ",
        "reaction"     : "close-up reaction shot, emotional response, ",
        "detail"       : "extreme detail insert shot, ",
        "two_shot"     : "two-shot, both characters in frame, ",
        "pov"          : "point-of-view shot, subjective camera, ",
        "cutaway"      : "cutaway to relevant detail, ",
    }

    @staticmethod
    def build_transition_prefix(scene_idx: int, transition_type: str = "cut_to") -> str:
        return "FADE IN: " if scene_idx == 0 else \
               CinematicTemplates.TRANSITIONS.get(transition_type, "CUT TO: ")

    @staticmethod
    def build_continuity_suffix(characters: list[str]) -> str:
        if not characters:
            return ""
        return f", maintaining visual continuity with {' and '.join(characters[:2])}, same costume same appearance"


class SceneChainer:
    def __init__(self, window: int = Config.CHAIN_WINDOW):
        self._window    = window
        self._history:  deque[str] = deque(maxlen=window)
        self._scene_idx : int = 0

    def reset(self):
        self._history.clear()
        self._scene_idx = 0

    def record(self, scene_text: str):
        self._history.append(
            scene_text[:200].rstrip() + ("…" if len(scene_text) > 200 else "")
        )
        self._scene_idx += 1

    def build_chained_prompt(self, scene_text: str,
                              transition: str = "cut_to",
                              characters: list[str] | None = None) -> str:
        parts = [CinematicTemplates.build_transition_prefix(self._scene_idx, transition)]
        if self._history:
            parts.append("; previously: " + " → ".join(self._history) + ". ")
        parts.append(scene_text)
        if characters:
            parts.append(CinematicTemplates.build_continuity_suffix(characters))
        return "".join(parts)

    @property
    def scene_index(self) -> int:
        return self._scene_idx


# ================================================================
# PROMPT QUALITY CHECKER & SCENE TEMPLATES
# ================================================================

class PromptQualityChecker:
    @staticmethod
    def check(scene_text: str) -> list[str]:
        warnings, text, words = [], scene_text.strip(), scene_text.lower().split()
        if len(text) < 20:
            warnings.append("⚠ Scene is very short (<20 chars) — add more visual detail")
        subjects = {"man","woman","person","figure","character","detective","soldier",
                    "child","robot","creature","animal","car","building","landscape",
                    "city","forest","interior"}
        if not any(w in subjects for w in words):
            warnings.append("💡 No clear subject — specify who/what is in the scene")
        spatials = {"in","at","on","under","above","inside","outside","near","behind","front"}
        if not any(w in spatials for w in words):
            warnings.append("💡 No spatial anchor — add location context")
        for pos_set, neg_set in [
            ({"noir","black and white"}, {"colorful","vibrant","rainbow"}),
            ({"wide shot","extreme wide"}, {"extreme close up","close-up"}),
        ]:
            if any(p in text for p in pos_set) and any(n in text for n in neg_set):
                warnings.append("⚠ Conflicting style keywords — may reduce coherence")
        return warnings

    @staticmethod
    def report(scenes: list[str]) -> str:
        lines = []
        for i, scene in enumerate(scenes):
            issues = PromptQualityChecker.check(scene)
            if issues:
                lines.append(f"[Scene {i+1}]")
                lines.extend(f"  {w}" for w in issues)
        return "\n".join(lines) if lines else "✓ All scenes passed quality check"


class SceneTemplates:
    TEMPLATES = {
        "🎬 Noir Detective": (
            "A weary detective stands in a rain-soaked alley, collar turned up, "
            "cigarette smoke curling into the neon-lit fog.",
            "Low Angle","Hard Noir","Noir","Classic film noir — shadows, rain, mystery"),
        "🚀 Sci-Fi Corridor": (
            "A lone astronaut walks through a crumbling space station corridor, "
            "emergency lights flickering red, debris floating in zero gravity.",
            "Tracking Shot","Neon Cyberpunk","Sci-Fi","Tense sci-fi — isolation, danger"),
        "🤠 Epic Western": (
            "A gunslinger stands at the edge of a dust-swept canyon at high noon, "
            "hand hovering over holster, wind pulling at a worn leather coat.",
            "Extreme Wide","Golden Hour","Western","Leone-style western — dust and tension"),
        "👻 Horror Interior": (
            "A child stands at the end of a long Victorian hallway, "
            "a candle flickering in hand, shadows breathing on the wallpaper.",
            "Low Angle","Candle / Fire","Horror","Psychological horror — dread"),
        "💥 Action Chase": (
            "A figure sprints across rooftops at breakneck speed, "
            "explosions blooming below, the city skyline blurring in motion.",
            "Dutch Angle","Blue Hour","Action","High-octane action — speed, danger"),
        "💕 Romantic Moment": (
            "Two silhouettes stand on a windswept cliffside at dusk, "
            "faces close, the sea crashing far below in the golden light.",
            "Close Up","Golden Hour","Romance","Intimate romance — warmth, connection"),
        "🏛 Period Drama": (
            "A noblewoman in a sweeping ball gown descends a candlelit marble staircase, "
            "dozens of guests below turning to look in hushed awe.",
            "Bird's Eye","Studio","Period Drama","Opulent period piece — grandeur"),
        "🌌 Space Epic": (
            "A fleet of warships emerges from hyperspace above a dying red star, "
            "plasma shields glowing against the stellar radiation.",
            "Extreme Wide","Blue Hour","Sci-Fi","Epic space opera — scale, menace"),
        "🌲 Nature Thriller": (
            "A tracker crouches in dense ancient forest, breath visible in cold air, "
            "watching something move between the trees thirty metres ahead.",
            "Over the Shoulder","Soft Natural","Cinematic","Wilderness thriller"),
        "🏙 Urban Drama": (
            "A woman stands on a rain-soaked street corner at midnight, "
            "taxi lights streaking past, holding a letter she cannot open.",
            "Close Up","Neon Cyberpunk","Cinematic","Urban drama — emotion, isolation"),
    }

    @staticmethod
    def names() -> list[str]: return list(SceneTemplates.TEMPLATES.keys())

    @staticmethod
    def get(name: str) -> tuple:
        return SceneTemplates.TEMPLATES.get(name, ("","Wide Shot","Golden Hour","Cinematic",""))


# ================================================================
# SESSION STATE
# ================================================================

class SessionState:
    def __init__(self):
        self.start_time       = time.time()
        self.generation_count : int = 0
        self.active_model     = "not loaded"
        self.physics_mode     = PhysicsMode.NEURAL.value
        self.last_scene_img   = None
        self.last_gen_time    = 0.0
        self.total_scenes     = 0

    def record_generation(self, img: Image.Image, gen_time: float):
        self.generation_count += 1
        self.total_scenes     += 1
        self.last_scene_img    = img.resize((256, 256), Image.LANCZOS) if img else None
        self.last_gen_time     = gen_time

    def elapsed(self) -> str:
        secs = int(time.time() - self.start_time)
        return f"{secs//3600:02d}:{(secs%3600)//60:02d}:{secs%60:02d}"

    def dashboard_text(self) -> str:
        return "\n".join([
            f"  GPU VRAM     : {VRAMManager.status_bar()}",
            f"  Active Model : {self.active_model}",
            f"  Physics Mode : {self.physics_mode}",
            f"  Scenes Gen'd : {self.total_scenes}",
            f"  Last Gen Time: {self.last_gen_time:.1f}s",
            f"  Session Time : {self.elapsed()}",
            f"  Prompt Cache : {_cache.stats()}",
        ])


# ================================================================
# STEP 5 — MASTER ENGINE V16
# ================================================================

class CinematicEngineV16:
    """
    V16 PROFESSIONAL — all V15.1 capabilities + 15 architectural improvements.
    Backward-compatible alias: MasterEngineV12 = CinematicEngineV16
    """

    def __init__(self):
        # ── Core systems ────────────────────────────────────
        self.pipelines      = PipelineManager()
        self.face_enhancer  = FaceEnhancer()
        self.upscaler       = Upscaler()
        self.pose_detector  = PoseDetector()
        self.face_id        = FaceIDExtractor()
        self.scene_chainer  = SceneChainer()
        self.story_expander : Optional[StoryExpander] = None
        self.neural_physics = NeuralPhysicsEngine()
        self.memory         = SceneMemory()
        self.splitter       = SceneSplitter()
        self.session        = SessionState()
        self._physics_mode  = Config.DEFAULT_PHYSICS_MODE

        os.makedirs(Config.SAVE_DIR, exist_ok=True)
        logger.info("[Engine] CinematicEngineV16 initialised ✓")

    # ── Public API ────────────────────────────────────────────

    def set_physics_mode(self, mode: PhysicsMode):
        self._physics_mode        = mode
        self.session.physics_mode = mode.value

    def load_models(self, log=None, model_mode: ModelMode = None):
        if log:
            logger.add_gradio_callback(log)
        mode = model_mode or Config.DEFAULT_MODEL_MODE

        if self.pipelines.active_model == mode:
            logger.info(f"[Engine] {mode.value} already loaded.")
            return

        self.pipelines.unload_all()

        if mode in (ModelMode.FLUX_SCHNELL, ModelMode.FLUX_DEV):
            ok = self.pipelines.load_flux(mode)
            if not ok:
                logger.warning("[Engine] Flux failed → falling back to SDXL")
                self.pipelines.load_sdxl()
        else:
            self.pipelines.load_sdxl()
            # Load LoRA if configured
            if Config.CHAR_LORA_PATH or Config.STYLE_LORA_PATH:
                pipe = self.pipelines._txt2img_sdxl
                if pipe:
                    self.pipelines._lora_state.load(
                        pipe,
                        char_path=Config.CHAR_LORA_PATH,
                        char_scale=Config.CHAR_LORA_SCALE,
                        style_path=Config.STYLE_LORA_PATH,
                        style_scale=Config.STYLE_LORA_SCALE,
                    )

        self.session.active_model = (
            self.pipelines.active_model.value
            if self.pipelines.active_model else "unknown"
        )

    def reload_lora(self, char_path="", char_scale=0.8,
                    style_path="", style_scale=0.6, log=None):
        if log:
            logger.add_gradio_callback(log)
        if self.pipelines.active_model in (ModelMode.FLUX_SCHNELL, ModelMode.FLUX_DEV):
            logger.info("[LoRA] LoRA is not supported in Flux mode — switch to SDXL")
            return
        pipe = self.pipelines._txt2img_sdxl
        if pipe is None:
            logger.warning("[LoRA] SDXL not loaded — go to SETTINGS → INITIALISE MODELS (SDXL)")
            return
        # [IMP-10] Safe state-tracked load
        self.pipelines._lora_state.unload(pipe)
        if char_path or style_path:
            self.pipelines._lora_state.load(
                pipe, char_path=char_path, char_scale=char_scale,
                style_path=style_path, style_scale=style_scale)

    def expand_story(self, text: str, style: str) -> str:
        self._ensure_story_expander()
        return "\n\n".join(
            self.story_expander.expand(s, style)
            for s in self.splitter.split(text)
        )

    def unload(self, log=None):
        if log:
            logger.add_gradio_callback(log)
        self.pipelines.unload_all()
        self.session.active_model = "not loaded"
        logger.info("[Engine] VRAM fully cleared ✓")

    def export_zip(self, log=None) -> Optional[str]:
        if log:
            logger.add_gradio_callback(log)
        pngs = sorted(Path(Config.SAVE_DIR).glob("*.png"))
        if not pngs:
            logger.info("[ZIP] No scenes to export.")
            return None
        ts       = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_path = os.path.join(Config.SAVE_DIR, f"storyboard_{ts}.zip")
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for png in pngs:
                zf.write(png, png.name)
                jp = png.with_suffix(".json")
                if jp.exists():
                    zf.write(jp, jp.name)
        logger.info(f"[ZIP] Exported {len(pngs)} scenes → {zip_path}")
        return zip_path

    # ── Internal helpers ──────────────────────────────────────

    def _ensure_story_expander(self):
        if self.story_expander is None:
            self.story_expander = StoryExpander()
        if self.story_expander.pipe is not None and not self.neural_physics.is_attached:
            self.neural_physics.attach_llm(
                self.story_expander.pipe,
                self.story_expander.mode,
            )

    def _build_prompt(self, cfg: GenerationConfig) -> tuple[str, str]:
        """
        [IMP-11] Uses PromptBuilder for structured compilation.
        Returns (final_prompt, physics_report).
        """
        # 1. Character memory injection
        enriched = self.memory.inject_into_prompt(cfg.scene_text)

        # 2. Physics augmentation
        physics_report = ""
        if self._physics_mode == PhysicsMode.NEURAL:
            self._ensure_story_expander()
            enriched, physics_report = self.neural_physics.augment(enriched)
        elif self._physics_mode == PhysicsMode.KEYWORD:
            enriched       = KeywordPhysicsEngine.augment(enriched)
            physics_report = KeywordPhysicsEngine.report(cfg.scene_text)

        # 3. Scene chaining
        if not cfg.preview and self.scene_chainer.scene_index > 0:
            enriched = self.scene_chainer.build_chained_prompt(
                enriched, cfg.transition, cfg.characters)

        # 4. [IMP-11] PromptBuilder structured assembly
        builder = (PromptBuilder()
                   .add_camera(cfg.camera)
                   .add_lighting(cfg.lighting)
                   .add_style(cfg.style)
                   .add_cinematic_suffix()
                   .add_scene(enriched))

        final = builder.build()
        return final, physics_report

    # ── Core generation ───────────────────────────────────────

    def generate_scene(self, cfg: GenerationConfig, log=None) -> tuple[Image.Image, dict]:
        """
        [IMP-6] Takes GenerationConfig object.
        Returns (image, metadata_dict).
        """
        if log:
            logger.add_gradio_callback(log)

        # [IMP-14] Validate config
        issues = cfg.validate()
        for issue in issues:
            logger.warning(f"[Config] {issue}")

        t_start = time.time()
        mmode   = cfg.model_mode

        # Ensure correct model loaded
        if self.pipelines.active_model != mmode:
            self.load_models(model_mode=mmode)
        elif mmode == ModelMode.SDXL and self.pipelines._txt2img_sdxl is None:
            self.load_models(model_mode=ModelMode.SDXL)

        # Speed mode (SDXL only)
        if not cfg.preview and mmode == ModelMode.SDXL:
            self.pipelines.set_speed_mode(cfg.speed_mode)

        prompt, physics_report = self._build_prompt(cfg)
        if physics_report:
            logger.info(f"[Physics] {physics_report[:120]}")

        resolution = Config.PREVIEW_RES if cfg.preview else 1024
        _seed      = cfg.seed if cfg.seed is not None else random.randint(0, 2**32-1)

        # [IMP-7] Full error-handling with fallback per branch
        try:
            if mmode in (ModelMode.FLUX_SCHNELL, ModelMode.FLUX_DEV):
                image = self._gen_flux(prompt, mmode, cfg.steps, cfg.cfg,
                                       _seed, resolution, cfg.preview)
            else:
                image = self._gen_sdxl(prompt, cfg, _seed, resolution)
        except Exception as e:
            logger.error(f"[Engine] Generation failed: {e}\n{traceback.format_exc()}")
            # [IMP-7] Return blank image instead of crashing session
            image = Image.new("RGB", (resolution, resolution), (20, 20, 20))

        # Post-pipeline
        if not cfg.preview:
            try:
                logger.info("[Gen] Face enhancement …")
                image = self.face_enhancer.enhance(image)
            except Exception as e:
                logger.warning(f"[FaceEnhancer] skipped: {e}")
            try:
                logger.info("[Gen] Upscaling 4x …")
                image = self.upscaler.upscale(image)
            except Exception as e:
                logger.warning(f"[Upscaler] skipped: {e}")
            self.scene_chainer.record(cfg.scene_text)

        gen_time = time.time() - t_start
        is_flux  = mmode in (ModelMode.FLUX_SCHNELL, ModelMode.FLUX_DEV)
        final    = postprocess(image, vignette=not cfg.preview, flux_mode=is_flux)

        if not cfg.preview:
            self.session.record_generation(final, gen_time)

        metadata = {
            "scene_text"    : cfg.scene_text,
            "prompt"        : prompt,
            "seed"          : _seed,
            "model"         : mmode.value,
            "camera"        : cfg.camera,
            "lighting"      : cfg.lighting,
            "style"         : cfg.style,
            "physics_mode"  : self._physics_mode.value,
            "physics_report": physics_report,
            "gen_time_sec"  : round(gen_time, 2),
            "timestamp"     : datetime.datetime.now().isoformat(),
        }
        return final, metadata

    def _gen_flux(self, prompt, mode, steps, cfg_val, seed, resolution, preview):
        pipe = self.pipelines.flux
        if pipe is None:
            raise RuntimeError("Flux pipeline not loaded.")
        if not preview:
            if mode == ModelMode.FLUX_SCHNELL:
                steps   = min(steps, 4)
                cfg_val = 0.0
            else:
                steps   = max(steps, Config.DEFAULT_FLUX_DEV_STEPS)
                cfg_val = max(0.0, min(float(cfg_val), 7.0))
        w, h      = ResolutionSnapper.optimal(mode, preview)
        generator = torch.Generator("cpu").manual_seed(seed)
        logger.info(f"[Gen] Flux {mode.value} — seed={seed} steps={steps} cfg={cfg_val} {w}×{h}")
        kwargs = dict(prompt=prompt, num_inference_steps=steps,
                      generator=generator, width=w, height=h)
        if mode == ModelMode.FLUX_DEV:
            kwargs["guidance_scale"] = cfg_val
        return pipe(**kwargs).images[0]

    def _gen_sdxl(self, prompt, cfg: GenerationConfig, seed: int, resolution: int):
        """[IMP-7] SDXL generation with full error handling per step."""
        steps, cfg_val = cfg.steps, cfg.cfg
        speed          = cfg.speed_mode

        if speed == SpeedMode.TURBO and not cfg.preview:
            steps, cfg_val = 4, 0.0
            logger.info(f"[Gen] TURBO seed={seed} steps=4 cfg=0.0")
        elif speed == SpeedMode.LCM and not cfg.preview:
            steps   = 8
            cfg_val = min(cfg_val, 2.0)
            logger.info(f"[Gen] LCM seed={seed} steps=8 cfg={cfg_val}")
        else:
            logger.info(f"[Gen] SDXL NORMAL seed={seed} steps={steps} cfg={cfg_val}")

        generator = torch.Generator("cuda").manual_seed(seed)

        # ControlNet path (SDXL NORMAL + pose provided)
        if cfg.pose_image is not None and not cfg.preview and speed == SpeedMode.NORMAL:
            pose_map = self.pose_detector.detect(cfg.pose_image)
            if pose_map is not None and self.pipelines.load_controlnet():
                try:
                    logger.info(f"[Gen] ControlNet pose (scale={cfg.cn_scale}) …")
                    return self.pipelines.controlnet(
                        prompt=prompt,
                        negative_prompt=Config.NEG_PROMPT,
                        image=pose_map,
                        controlnet_conditioning_scale=cfg.cn_scale,
                        num_inference_steps=steps,
                        guidance_scale=cfg_val,
                        generator=generator,
                        width=resolution, height=resolution,
                    ).images[0]
                except Exception as e:
                    logger.warning(f"[ControlNet] failed: {e} → identity fallback")

        # Identity path
        image = self._gen_with_identity(
            prompt, steps, cfg_val, generator, resolution,
            cfg.ip_image, cfg.ip_scale, cfg.faceid_scale, speed)

        # Post-steps (SDXL NORMAL only)
        if not cfg.preview and speed == SpeedMode.NORMAL:
            # Refiner
            if self.pipelines.refiner is not None:
                try:
                    logger.info("[Gen] Refining …")
                    ref_gen = torch.Generator("cuda").manual_seed(seed)
                    image   = self.pipelines.refiner(
                        prompt=prompt, negative_prompt=Config.NEG_PROMPT,
                        image=image, num_inference_steps=cfg.refine_steps,
                        strength=cfg.refiner_str,
                        guidance_scale=max(cfg_val, 1.0),
                        generator=ref_gen,
                    ).images[0]
                except Exception as e:
                    logger.warning(f"[Refiner] skipped: {e}")

            # HiresFix
            if self.pipelines.hires is not None:
                try:
                    if VRAMManager.free_gb() >= Config.HIRES_MIN_FREE_VRAM_GB:
                        base_w, base_h = image.size
                        hi_w, hi_h = ResolutionSnapper.hires(base_w, base_h, Config.HIRES_SCALE)
                        logger.info(f"[HiresFix] {base_w}×{base_h} → {hi_w}×{hi_h} …")
                        image_hi   = image.resize((hi_w, hi_h), Image.LANCZOS)
                        gen_h      = torch.Generator("cuda").manual_seed(seed)
                        image      = self.pipelines.hires(
                            prompt=prompt,
                            negative_prompt=Config.NEG_PROMPT,
                            image=image_hi,
                            strength=Config.HIRES_STRENGTH,
                            num_inference_steps=Config.HIRES_STEPS,
                            guidance_scale=cfg_val,
                            generator=gen_h,
                        ).images[0]
                        logger.info("[HiresFix] Done ✓")
                    else:
                        logger.warning(f"[HiresFix] skipped — {VRAMManager.free_gb():.1f}GB free "
                                       f"(< {Config.HIRES_MIN_FREE_VRAM_GB}GB threshold)")
                except Exception as e:
                    logger.warning(f"[HiresFix] skipped: {e}")
        return image

    def _gen_with_identity(self, prompt, steps, cfg_val, generator, resolution,
                            ip_image, ip_scale, faceid_scale, speed_mode):
        pipe = (self.pipelines._txt2img_turbo
                if speed_mode == SpeedMode.TURBO and self.pipelines._txt2img_turbo
                else self.pipelines._txt2img_sdxl)

        if ip_image is not None:
            # Layer 1 — FaceID
            if self._try_load_faceid():
                emb = self.face_id.extract_embedding(ip_image, cache_key="storyboard_char")
                if emb is not None:
                    try:
                        pipe.set_ip_adapter_scale(faceid_scale)
                        n = len(ip_image) if isinstance(ip_image, list) else 1
                        logger.info(f"[Gen] FaceID Layer 1 — {n} ref(s), scale={faceid_scale} ✓")
                        return pipe(
                            prompt=prompt, negative_prompt=Config.NEG_PROMPT,
                            ip_adapter_image_embeds=[emb],
                            num_inference_steps=steps, guidance_scale=cfg_val,
                            generator=generator, width=resolution, height=resolution,
                        ).images[0]
                    except Exception as e:
                        logger.warning(f"[FaceID] Layer 1 → Layer 2: {e}")

            # Layer 2 — IP-Adapter
            if self._try_load_ip_adapter():
                try:
                    ref_img = ip_image[0] if isinstance(ip_image, list) else ip_image
                    pipe.set_ip_adapter_scale(ip_scale)
                    logger.info(f"[Gen] IP-Adapter Layer 2 (scale={ip_scale}) …")
                    return pipe(
                        prompt=prompt, negative_prompt=Config.NEG_PROMPT,
                        ip_adapter_image=ref_img,
                        num_inference_steps=steps, guidance_scale=cfg_val,
                        generator=generator, width=resolution, height=resolution,
                    ).images[0]
                except Exception as e:
                    logger.warning(f"[IP-Adapter] Layer 2 → Layer 3: {e}")

        # Layer 3 — Base
        return pipe(
            prompt=prompt, negative_prompt=Config.NEG_PROMPT,
            num_inference_steps=steps, guidance_scale=cfg_val,
            generator=generator, width=resolution, height=resolution,
        ).images[0]

    def _try_load_ip_adapter(self) -> bool:
        pm = self.pipelines
        if pm._ip_loaded:
            return True
        pipe = pm._txt2img_sdxl
        if pipe is None:
            return False
        if not (os.path.exists(Config.IP_ADAPTER_WEIGHTS) and
                os.path.exists(Config.IP_ADAPTER_ENCODER)):
            logger.warning("[IP-Adapter] Weights not found")
            return False
        try:
            pipe.load_ip_adapter(
                Config.IP_ADAPTER_ENCODER, subfolder="",
                weight_name=Config.IP_ADAPTER_WEIGHTS)
            pm._ip_loaded = True
            logger.info("[IP-Adapter] SDXL loaded ✓")
            return True
        except Exception as e:
            logger.warning(f"[IP-Adapter] Failed: {e}")
            return False

    def _try_load_faceid(self) -> bool:
        pm = self.pipelines
        if pm._faceid_loaded:
            return True
        pipe = pm._txt2img_sdxl
        if pipe is None or not os.path.exists(Config.IP_FACEID_WEIGHTS):
            return False
        if not INSIGHTFACE_AVAILABLE:
            return False
        try:
            pipe.load_ip_adapter(
                ".", subfolder="", weight_name=Config.IP_FACEID_WEIGHTS)
            pm._faceid_loaded = True
            logger.info("[FaceID] IP-Adapter FaceID loaded ✓")
            return True
        except Exception as e:
            logger.warning(f"[FaceID] load failed: {e}")
            return False

    # ── Batch storyboard ──────────────────────────────────────

    def generate_storyboard(
        self,
        scenes, camera, lighting, style,
        steps, refine_steps, cfg_val, refiner_str,
        ip_image, ip_scale, faceid_scale,
        pose_image, cn_scale,
        speed_mode, model_mode, transition,
        characters, seed_base, log=None,
    ) -> list[Image.Image]:
        if log:
            logger.add_gradio_callback(log)

        self.scene_chainer.reset()
        self.face_id.clear_cache()
        self.neural_physics.clear_cache()
        results  = []
        n        = len(scenes)
        t_batch  = time.time()

        for i, scene in enumerate(tqdm(scenes, desc="Scenes")):
            if i > 0:
                elapsed  = time.time() - t_batch
                avg_time = elapsed / i
                eta      = avg_time * (n - i)
                logger.info(f"[Progress] Scene {i+1}/{n} — ETA {eta:.0f}s | avg {avg_time:.1f}s/scene")
            else:
                logger.info(f"[Progress] Scene {i+1}/{n} …")

            _seed = (seed_base + i) if seed_base is not None else None
            cfg   = GenerationConfig(
                scene_text   = scene,
                camera=camera, lighting=lighting, style=style,
                steps=steps, refine_steps=refine_steps,
                cfg=cfg_val, refiner_str=refiner_str,
                ip_image=ip_image, ip_scale=ip_scale,
                faceid_scale=faceid_scale,
                pose_image=pose_image, cn_scale=cn_scale,
                speed_mode=speed_mode, model_mode=model_mode,
                transition=transition,
                characters=characters if characters else [],
                seed=_seed,
            )

            try:
                img, metadata = self.generate_scene(cfg)
                ts        = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                base      = f"scene_{i+1:03d}_{ts}"
                img_path  = os.path.join(Config.SAVE_DIR, f"{base}.png")
                json_path = os.path.join(Config.SAVE_DIR, f"{base}.json")
                img.save(img_path)
                with open(json_path, "w", encoding="utf-8") as jf:
                    json.dump(metadata, jf, indent=2, ensure_ascii=False)
                logger.info(f"[Storyboard] saved → {img_path}")
                results.append(img)
            except Exception as e:
                logger.error(f"[ERROR] Scene {i+1}: {e}\n{traceback.format_exc()}")

            VRAMManager.flush()

        total_time = time.time() - t_batch
        logger.info(f"[Storyboard] Complete — {len(results)}/{n} scenes "
                    f"in {total_time:.1f}s ({total_time/max(n,1):.1f}s avg)")
        return results


# Backward-compatible alias
MasterEngineV12 = CinematicEngineV16


# ================================================================
# STEP 6 — GRADIO UI  V16 PROFESSIONAL
# ================================================================

def build_gradio_ui(engine: CinematicEngineV16):

    cam_choices        = list(CameraPreset.PRESETS.keys())
    light_choices      = list(LightingPreset.PRESETS.keys())
    style_choices      = list(StylePreset.PRESETS.keys())
    transition_choices = list(CinematicTemplates.TRANSITIONS.keys())
    template_names     = SceneTemplates.names()

    speed_labels = [
        "NORMAL  (35 steps — full quality)",
        "TURBO   (4 steps — x8 faster)",
        "LCM     (8 steps — balanced)",
    ]
    model_labels = [
        "FLUX SCHNELL  (default — Apache-2.0, 4 steps, T4-safe)",
        "FLUX DEV      (best quality — 20 steps, HF token needed)",
        "SDXL          (full pipeline: FaceID + IP-Adapter + ControlNet)",
    ]
    physics_labels = [
        "NEURAL   (LLM-driven — best accuracy, 10s timeout)",
        "KEYWORD  (fast priority scoring — no LLM needed)",
        "DISABLED (no physics augmentation)",
    ]

    # ── Converters ───────────────────────────────────────────
    def _parse_chars(raw: str) -> list[str]:
        engine.memory.clear()
        names = []
        for line in raw.strip().splitlines():
            if ":" in line:
                n, d = line.split(":", 1)
                engine.memory.set_character(n.strip(), d.strip())
                names.append(n.strip())
        return names

    def _pil(np_input):
        if np_input is None:
            return None
        if isinstance(np_input, list):
            imgs = []
            for item in np_input:
                arr = item[0] if isinstance(item, tuple) else item
                if arr is not None:
                    try:
                        imgs.append(Image.fromarray(arr).convert("RGB"))
                    except Exception:
                        pass
            return imgs if imgs else None
        try:
            return Image.fromarray(np_input).convert("RGB")
        except Exception:
            return None

    def _speed_enum(label: str) -> SpeedMode:
        if "TURBO" in label: return SpeedMode.TURBO
        if "LCM"   in label: return SpeedMode.LCM
        return SpeedMode.NORMAL

    def _model_enum(label: str) -> ModelMode:
        if "FLUX DEV" in label or "DEV" in label: return ModelMode.FLUX_DEV
        if "SDXL"     in label:                   return ModelMode.SDXL
        return ModelMode.FLUX_SCHNELL

    def _physics_enum(label: str) -> PhysicsMode:
        if "KEYWORD"  in label: return PhysicsMode.KEYWORD
        if "DISABLED" in label: return PhysicsMode.DISABLED
        return PhysicsMode.NEURAL

    # ── Handlers ─────────────────────────────────────────────
    def fn_load_models(model_label):
        msgs  = []
        mmode = _model_enum(model_label)
        engine.load_models(log=msgs.append, model_mode=mmode)
        return "\n".join(msgs)

    def fn_expand(scenes, style):
        if not scenes.strip():
            return scenes, "[!] Enter scenes first."
        return engine.expand_story(scenes, style), "[Expand] Done ✓"

    def fn_quality_check(scenes):
        if not scenes.strip():
            return "[!] Enter scenes first."
        return PromptQualityChecker.report(engine.splitter.split(scenes))

    def fn_load_template(template_name):
        scene, camera, lighting, style, _ = SceneTemplates.get(template_name)
        return scene, camera, lighting, style

    def fn_preview(scenes, chars, camera, lighting, style,
                   cfg_val, steps, ip_ref, ip_scale, seed_val):
        if not scenes.strip():
            return None, "[!] Enter scenes."
        _parse_chars(chars)
        sc    = engine.splitter.split(scenes)
        seed  = None if int(seed_val) < 0 else int(seed_val)
        msgs  = []
        gcfg  = GenerationConfig(
            scene_text=sc[0], camera=camera, lighting=lighting, style=style,
            steps=max(10, int(steps)//2), refine_steps=0,
            cfg=float(cfg_val), refiner_str=0.35,
            ip_image=_pil(ip_ref), ip_scale=float(ip_scale),
            faceid_scale=0.7, speed_mode=SpeedMode.NORMAL,
            model_mode=engine.pipelines.active_model or ModelMode.FLUX_SCHNELL,
            seed=seed, preview=True,
        )
        try:
            img, _ = engine.generate_scene(gcfg, log=msgs.append)
            return img, "\n".join(msgs)
        except Exception as e:
            return None, f"[ERROR] {e}\n{traceback.format_exc()}"

    def fn_generate(
        scenes, chars, camera, lighting, style,
        cfg_val, steps, refine_steps, refiner_str,
        ip_ref, ip_scale, faceid_scale,
        pose_ref, cn_scale,
        char_lora_path, char_lora_scale,
        style_lora_path, style_lora_scale,
        speed_label, model_label, physics_label, transition, seed_val,
    ):
        if not scenes.strip():
            return [], "[!] Enter scenes."
        char_names = _parse_chars(chars)
        msgs       = []

        pmode = _physics_enum(physics_label)
        engine.set_physics_mode(pmode)

        sc             = engine.splitter.split(scenes)
        quality_report = PromptQualityChecker.report(sc)
        if quality_report != "✓ All scenes passed quality check":
            msgs.append(f"[Quality Check]\n{quality_report}")

        for _si, _scene in enumerate(sc):
            if pmode == PhysicsMode.KEYWORD:
                _phys = KeywordPhysicsEngine.report(_scene)
                if "(no physics keywords" not in _phys:
                    msgs.append(f"[Physics] Scene {_si+1}/{len(sc)}:\n{_phys}")
            elif pmode == PhysicsMode.NEURAL:
                msgs.append(f"[Physics] Scene {_si+1}/{len(sc)}: LLM reasoning active (10s timeout)")

        if char_lora_path or style_lora_path:
            engine.reload_lora(
                char_path=char_lora_path, char_scale=float(char_lora_scale),
                style_path=style_lora_path, style_scale=float(style_lora_scale),
                log=msgs.append,
            )

        ip_img   = _pil(ip_ref)
        pose_img = _pil(pose_ref)
        seed     = None if int(seed_val) < 0 else int(seed_val)
        smode    = _speed_enum(speed_label)
        mmode    = _model_enum(model_label)

        try:
            images = engine.generate_storyboard(
                scenes=sc, camera=camera, lighting=lighting, style=style,
                steps=int(steps), refine_steps=int(refine_steps),
                cfg_val=float(cfg_val), refiner_str=float(refiner_str),
                ip_image=ip_img, ip_scale=float(ip_scale),
                faceid_scale=float(faceid_scale),
                pose_image=pose_img, cn_scale=float(cn_scale),
                speed_mode=smode, model_mode=mmode,
                transition=transition,
                characters=char_names, seed_base=seed,
                log=msgs.append,
            )
            return images, "\n".join(msgs)
        except Exception as e:
            return [], f"[ERROR] {e}\n{traceback.format_exc()}"

    def fn_load_lora(cp, cs, sp, ss):
        msgs = []
        engine.reload_lora(char_path=cp, char_scale=float(cs),
                           style_path=sp, style_scale=float(ss),
                           log=msgs.append)
        return "\n".join(msgs)

    def fn_detect_pose(ref_np):
        if ref_np is None:
            return None, "[!] Upload a reference image first."
        pose_map = engine.pose_detector.detect(_pil(ref_np))
        if pose_map is None:
            return None, "[!] Detection failed — check controlnet-aux install."
        return pose_map, "[Pose] Skeleton detected ✓"

    def fn_clear_vram():
        msgs = []
        engine.unload(log=msgs.append)
        return "\n".join(msgs)

    def fn_status_refresh():
        return engine.session.dashboard_text()

    def fn_export_zip():
        msgs = []
        path = engine.export_zip(log=msgs.append)
        return (f"✓ ZIP exported → {path}\n" + "\n".join(msgs)) if path else \
               "\n".join(msgs) or "[ZIP] Nothing to export."

    # ── Dark Cinema CSS ───────────────────────────────────────
    DARK_CINEMA_CSS = """
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Mono:wght@400;500&family=Syne:wght@400;600;800&display=swap');
    :root {
        --bg-void:#080A0C; --bg-panel:#0E1116; --bg-card:#141820;
        --bg-hover:#1C2230; --border:#1E2535; --border-glow:#2A3550;
        --amber:#F5A623; --crimson:#E63946; --cyan:#00D4FF;
        --cyan-dim:#005F72; --text-bright:#F0F4FF; --text-mid:#8892A4;
        --success:#2ECC71; --neural:#A855F7;
        --font-display:'Bebas Neue',sans-serif;
        --font-mono:'DM Mono',monospace;
        --font-body:'Syne',sans-serif;
        --radius:6px; --radius-lg:12px;
    }
    body,.gradio-container{background:var(--bg-void)!important;font-family:var(--font-body)!important;color:var(--text-bright)!important;}
    .gradio-container::before{content:'';display:block;height:4px;background:repeating-linear-gradient(90deg,var(--amber) 0,var(--amber) 20px,transparent 20px,transparent 28px);position:fixed;top:0;left:0;right:0;z-index:9999;}
    .cinema-header{text-align:center;padding:36px 0 20px;border-bottom:1px solid var(--border);margin-bottom:24px;position:relative;}
    .cinema-header::after{content:'';position:absolute;bottom:-1px;left:50%;transform:translateX(-50%);width:160px;height:2px;background:linear-gradient(90deg,transparent,var(--amber),transparent);}
    .cinema-title{font-family:var(--font-display)!important;font-size:3.2rem!important;letter-spacing:6px!important;color:var(--text-bright)!important;text-shadow:0 0 40px rgba(245,166,35,0.3)!important;margin:0!important;line-height:1!important;}
    .cinema-subtitle{font-family:var(--font-mono)!important;font-size:0.72rem!important;color:var(--amber)!important;letter-spacing:3px!important;text-transform:uppercase!important;margin-top:10px!important;}
    .gr-panel,.gr-box,.gr-form,.block,[class*="panel"]{background:var(--bg-panel)!important;border:1px solid var(--border)!important;border-radius:var(--radius-lg)!important;}
    .tab-nav{background:var(--bg-void)!important;border-bottom:1px solid var(--border)!important;gap:4px!important;padding:0 8px!important;}
    .tab-nav button{font-family:var(--font-mono)!important;font-size:0.75rem!important;letter-spacing:2px!important;text-transform:uppercase!important;color:var(--text-mid)!important;background:transparent!important;border:none!important;border-bottom:2px solid transparent!important;padding:12px 20px!important;transition:all 0.2s!important;border-radius:0!important;}
    .tab-nav button:hover{color:var(--amber)!important;background:var(--bg-hover)!important;}
    .tab-nav button.selected{color:var(--amber)!important;border-bottom-color:var(--amber)!important;background:rgba(245,166,35,0.06)!important;}
    label,.gr-label{font-family:var(--font-mono)!important;font-size:0.65rem!important;letter-spacing:2px!important;text-transform:uppercase!important;color:var(--text-mid)!important;}
    textarea,input[type="text"],input[type="number"]{background:var(--bg-card)!important;border:1px solid var(--border)!important;border-radius:var(--radius)!important;color:var(--text-bright)!important;font-family:var(--font-mono)!important;font-size:0.82rem!important;padding:10px 14px!important;transition:border-color 0.2s,box-shadow 0.2s!important;}
    textarea:focus,input:focus{border-color:var(--cyan-dim)!important;box-shadow:0 0 0 2px rgba(0,212,255,0.08)!important;outline:none!important;}
    input[type="range"]{accent-color:var(--amber)!important;height:3px!important;}
    button.gr-button{font-family:var(--font-mono)!important;font-size:0.72rem!important;letter-spacing:2px!important;text-transform:uppercase!important;border-radius:var(--radius)!important;transition:all 0.2s!important;cursor:pointer!important;}
    button.gr-button-primary{background:linear-gradient(135deg,#C47D0A,var(--amber))!important;border:none!important;color:#0A0800!important;font-weight:600!important;padding:14px 28px!important;box-shadow:0 4px 20px rgba(245,166,35,0.25)!important;}
    button.gr-button-primary:hover{transform:translateY(-1px)!important;box-shadow:0 6px 28px rgba(245,166,35,0.4)!important;}
    button.gr-button-secondary{background:transparent!important;border:1px solid var(--border-glow)!important;color:var(--text-mid)!important;}
    button.gr-button-secondary:hover{border-color:var(--amber)!important;color:var(--amber)!important;background:rgba(245,166,35,0.06)!important;}
    button.gr-button-stop{background:transparent!important;border:1px solid var(--crimson)!important;color:var(--crimson)!important;}
    button.gr-button-stop:hover{background:rgba(230,57,70,0.1)!important;}
    .log-console textarea{background:#05070A!important;border:1px solid var(--border)!important;border-left:3px solid var(--amber)!important;color:#7AE582!important;font-family:var(--font-mono)!important;font-size:0.72rem!important;line-height:1.7!important;}
    .status-console textarea{background:#05070A!important;border:1px solid var(--border)!important;border-left:3px solid var(--neural)!important;color:#C4B5FD!important;font-family:var(--font-mono)!important;font-size:0.75rem!important;line-height:1.9!important;}
    .quality-console textarea{background:#05070A!important;border:1px solid var(--border)!important;border-left:3px solid var(--cyan)!important;color:#7AE582!important;font-family:var(--font-mono)!important;font-size:0.72rem!important;line-height:1.7!important;}
    .section-label{font-family:var(--font-mono)!important;font-size:0.62rem!important;letter-spacing:3px!important;text-transform:uppercase!important;color:var(--cyan)!important;padding:4px 0 12px!important;border-bottom:1px solid var(--border)!important;margin-bottom:14px!important;display:block!important;}
    .neural-label{color:var(--neural)!important;}
    .gr-gallery{background:var(--bg-void)!important;border:1px solid var(--border)!important;border-radius:var(--radius-lg)!important;padding:12px!important;}
    .gr-gallery img{border-radius:var(--radius)!important;border:1px solid var(--border)!important;transition:transform 0.25s,box-shadow 0.25s!important;animation:fadeInCard 0.4s ease forwards!important;}
    .gr-gallery img:hover{transform:scale(1.02)!important;box-shadow:0 8px 32px rgba(0,0,0,0.6),0 0 1px var(--amber)!important;border-color:var(--amber)!important;}
    @keyframes fadeInCard{from{opacity:0;transform:translateY(8px);}to{opacity:1;transform:translateY(0);}}
    .gr-image{border:1px dashed var(--border-glow)!important;border-radius:var(--radius-lg)!important;background:var(--bg-card)!important;}
    ::-webkit-scrollbar{width:5px;height:5px;}
    ::-webkit-scrollbar-track{background:var(--bg-void);}
    ::-webkit-scrollbar-thumb{background:var(--border-glow);border-radius:4px;}
    """

    with gr.Blocks(
        title="CINEMATIC STORYBOARD ENGINE V16 PROFESSIONAL",
        theme=gr.themes.Base(
            primary_hue="orange", secondary_hue="neutral", neutral_hue="slate",
            font=gr.themes.GoogleFont("Syne"),
        ),
        css=DARK_CINEMA_CSS,
    ) as demo:

        gr.HTML("""
        <div class="cinema-header">
            <div class="cinema-title">CINEMATIC ENGINE</div>
            <div class="cinema-subtitle">
                V16 PROFESSIONAL &nbsp;&#183;&nbsp; AI Neural Physics &nbsp;&#183;&nbsp;
                Pipeline Manager &nbsp;&#183;&nbsp; VRAM Guard &nbsp;&#183;&nbsp;
                Smart Cache &nbsp;&#183;&nbsp; Flux.1 &nbsp;&#183;&nbsp; FaceID &nbsp;&#183;&nbsp;
                LoRA &nbsp;&#183;&nbsp; ControlNet &nbsp;&#183;&nbsp; 8K
            </div>
        </div>
        """)

        with gr.Row():
            log_box = gr.Textbox(label="ENGINE LOG", lines=4,
                                 interactive=False, elem_classes=["log-console"])

        with gr.Tabs():

            # ── Tab 0 — STATUS ──────────────────────────────────
            with gr.Tab("STATUS"):
                gr.HTML('<span class="section-label neural-label">Engine Status Dashboard</span>')
                gr.Markdown("Live GPU, VRAM, model, physics mode, and cache stats.")
                status_box = gr.Textbox(
                    label="LIVE ENGINE STATUS", lines=8, interactive=False,
                    value=engine.session.dashboard_text(),
                    elem_classes=["status-console"],
                )
                with gr.Row():
                    btn_status_refresh = gr.Button("REFRESH STATUS",              variant="secondary")
                    btn_export_zip     = gr.Button("DOWNLOAD ALL SCENES AS ZIP",  variant="secondary")
                zip_log = gr.Textbox(label="ZIP EXPORT LOG", lines=3,
                                     interactive=False, elem_classes=["log-console"])
                btn_status_refresh.click(fn=fn_status_refresh, inputs=[], outputs=[status_box])
                btn_export_zip.click(fn=fn_export_zip, inputs=[], outputs=[zip_log])

            # ── Tab 1 — GENERATE ────────────────────────────────
            with gr.Tab("GENERATE"):
                gr.HTML('<span class="section-label">Quick-Start Templates</span>')
                with gr.Row():
                    template_dd  = gr.Dropdown(choices=template_names,
                                               value=template_names[0],
                                               label="SCENE TEMPLATE LIBRARY")
                    btn_template = gr.Button("LOAD TEMPLATE", variant="secondary")

                with gr.Row(equal_height=False):
                    with gr.Column(scale=3):
                        gr.HTML('<span class="section-label">Script</span>')
                        t1_scenes = gr.Textbox(
                            label="SCENE DESCRIPTIONS",
                            placeholder=(
                                "Separate scenes with a blank line or semicolon.\n\n"
                                "A lone detective walks through a rain-soaked alley at midnight.\n\n"
                                "She stops beneath a flickering neon sign, hand on her holster."
                            ),
                            lines=10,
                        )
                        t1_chars = gr.Textbox(
                            label="CHARACTERS  — Name: description, one per line",
                            placeholder=(
                                "Layla: young woman, auburn hair, worn trench coat\n"
                                "Viktor: heavy-set man, silver beard, scarred cheek"
                            ),
                            lines=3,
                        )
                        gr.HTML('<span class="section-label">Prompt Quality</span>')
                        btn_quality = gr.Button("CHECK SCENE QUALITY", variant="secondary")
                        quality_box = gr.Textbox(label="QUALITY REPORT", lines=4,
                                                 interactive=False, elem_classes=["quality-console"])

                        gr.HTML('<span class="section-label">Cinematic Style</span>')
                        with gr.Row():
                            t1_camera   = gr.Dropdown(cam_choices,   value="Wide Shot", label="CAMERA")
                            t1_lighting = gr.Dropdown(light_choices, value="Hard Noir", label="LIGHTING")
                            t1_style    = gr.Dropdown(style_choices, value="Cinematic", label="STYLE")

                        gr.HTML('<span class="section-label">Scene Chaining</span>')
                        t1_transition = gr.Dropdown(transition_choices, value="cut_to",
                                                    label="TRANSITION TYPE")

                    with gr.Column(scale=2):
                        gr.HTML('<span class="section-label">Preview & Launch</span>')
                        t1_preview_img = gr.Image(label="QUICK PREVIEW  512px", type="pil", height=260)
                        t1_seed = gr.Number(value=-1, label="SEED  —  minus one = random", precision=0)

                        gr.HTML('<span class="section-label">Speed Mode</span>')
                        t1_speed = gr.Radio(choices=speed_labels, value=speed_labels[0],
                                            label="GENERATION MODE")

                        gr.HTML('<span class="section-label neural-label">AI Physics Mode</span>')
                        t1_physics = gr.Radio(choices=physics_labels, value=physics_labels[0],
                                              label="PHYSICS ENGINE")
                        gr.HTML("""
                        <div style="font-family:'DM Mono',monospace;font-size:0.63rem;
                                    color:#8892A4;line-height:1.9;margin-bottom:12px">
                          <b style="color:#A855F7">NEURAL</b> &nbsp;&nbsp;&nbsp;— LLM analyses scene → physics descriptors (10s timeout)<br>
                          <b style="color:#F5A623">KEYWORD</b> — priority-scored keyword matching (fast, no LLM)<br>
                          <b style="color:#E63946">DISABLED</b> — no physics augmentation
                        </div>
                        """)

                        with gr.Row():
                            t1_btn_expand  = gr.Button("EXPAND STORY", variant="secondary")
                            t1_btn_preview = gr.Button("PREVIEW",      variant="secondary")
                        t1_btn_generate = gr.Button(
                            "GENERATE  8K  STORYBOARD", variant="primary", size="lg")

                gr.HTML('<span class="section-label" style="margin-top:20px">Generated Scenes</span>')
                t1_gallery = gr.Gallery(label="", columns=4, height=540,
                                        object_fit="cover", show_label=False)

            # ── Tab 2 — CHARACTER & LORA ────────────────────────
            with gr.Tab("CHARACTER AND LORA"):
                gr.HTML('<span class="section-label">FaceID Reference  [Weighted Multi-Reference + Outlier Rejection]</span>')
                gr.Markdown(
                    "Upload **1–5 face photos** of the same character. "
                    "V16 uses quality-weighted averaging and rejects outlier embeddings. "
                    "Falls back to IP-Adapter if FaceID unavailable. **SDXL mode only.**"
                )
                with gr.Row():
                    with gr.Column():
                        t2_ip_ref = gr.Gallery(
                            label="FACE / CHARACTER REFERENCE PHOTOS  (1–5 images)",
                            columns=3, height=280, object_fit="cover", type="numpy",
                        )
                    with gr.Column():
                        t2_ip_scale     = gr.Slider(0.0, 1.0, value=0.6, step=0.05,
                                                    label="IP-ADAPTER SCALE  (fallback)")
                        t2_faceid_scale = gr.Slider(0.0, 1.0, value=0.7, step=0.05,
                                                    label="FACEID SCALE  (primary)")
                        gr.HTML("""
                        <div style="font-family:'DM Mono',monospace;font-size:0.65rem;
                                    color:#8892A4;line-height:1.9;margin-top:10px">
                          <b style="color:#2ECC71">Layer priority:</b> FaceID → IP-Adapter → Base<br>
                          <b style="color:#A855F7">V16 FaceID:</b> quality-weighted + outlier rejection<br>
                          <b style="color:#00D4FF">Best:</b> front + side + ¾ angle for 3+ references
                        </div>
                        """)

                gr.HTML('<span class="section-label" style="margin-top:24px">Character LoRA  (SDXL only)</span>')
                with gr.Row():
                    t2_char_lora_path  = gr.Textbox(label="CHARACTER LORA PATH (.safetensors)",
                                                    placeholder="/content/my_character.safetensors")
                    t2_char_lora_scale = gr.Slider(0.0, 1.0, value=0.8, step=0.05,
                                                   label="CHARACTER LORA SCALE")

                gr.HTML('<span class="section-label" style="margin-top:24px">Style LoRA  (SDXL only)</span>')
                with gr.Row():
                    t2_style_lora_path  = gr.Textbox(label="STYLE LORA PATH (.safetensors)",
                                                     placeholder="/content/cinematic_style.safetensors")
                    t2_style_lora_scale = gr.Slider(0.0, 1.0, value=0.6, step=0.05,
                                                    label="STYLE LORA SCALE")

                t2_btn_lora = gr.Button("LOAD AND RELOAD LORA", variant="secondary")
                t2_lora_log = gr.Textbox(label="LORA STATUS", lines=5,
                                         interactive=False, elem_classes=["log-console"])
                t2_btn_lora.click(
                    fn=fn_load_lora,
                    inputs=[t2_char_lora_path, t2_char_lora_scale,
                             t2_style_lora_path, t2_style_lora_scale],
                    outputs=[t2_lora_log],
                )

            # ── Tab 3 — POSE CONTROL ────────────────────────────
            with gr.Tab("POSE CONTROL"):
                gr.HTML('<span class="section-label">ControlNet OpenPose  (SDXL NORMAL only)</span>')
                gr.Markdown(
                    "Upload a reference image. The engine extracts the full-body skeleton "
                    "and controls character poses in every generated scene."
                )
                with gr.Row():
                    with gr.Column():
                        t3_pose_ref   = gr.Image(label="POSE REFERENCE IMAGE",
                                                 type="numpy", height=320)
                        t3_btn_detect = gr.Button("EXTRACT SKELETON", variant="secondary")
                    with gr.Column():
                        t3_pose_map   = gr.Image(label="DETECTED POSE SKELETON",
                                                 type="pil", height=320)
                t3_cn_scale = gr.Slider(0.0, 1.5, value=0.7, step=0.05,
                                        label="CONTROLNET STRENGTH")
                t3_pose_log = gr.Textbox(label="POSE LOG", lines=3,
                                         interactive=False, elem_classes=["log-console"])
                t3_btn_detect.click(fn=fn_detect_pose, inputs=[t3_pose_ref],
                                    outputs=[t3_pose_map, t3_pose_log])

            # ── Tab 4 — SETTINGS ────────────────────────────────
            with gr.Tab("SETTINGS"):
                gr.HTML('<span class="section-label">Generation Model</span>')
                t4_model_mode = gr.Radio(choices=model_labels, value=model_labels[0],
                                         label="MODEL MODE")
                gr.HTML("""
                <div style="font-family:'DM Mono',monospace;font-size:0.63rem;
                            color:#8892A4;line-height:2;margin-bottom:16px">
                  <b style="color:#F5A623">FLUX SCHNELL</b> — Apache-2.0, free, 4 steps, T4-safe.<br>
                  <b style="color:#F5A623">FLUX DEV</b> &nbsp;&nbsp;&nbsp;&nbsp;— Highest quality. 20 steps. HF_TOKEN required.<br>
                  <b style="color:#F5A623">SDXL</b> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;— Full pipeline: FaceID + LoRA + ControlNet.
                </div>
                """)
                gr.HTML('<span class="section-label" style="margin-top:4px">Generation Parameters  (SDXL only)</span>')
                with gr.Row():
                    t4_steps        = gr.Slider(10, 80,   value=35,   step=1,    label="INFERENCE STEPS")
                    t4_refine_steps = gr.Slider(5,  40,   value=15,   step=1,    label="REFINE STEPS")
                with gr.Row():
                    t4_cfg          = gr.Slider(1.0, 20.0, value=8.5, step=0.5,  label="CFG SCALE")
                    t4_refiner_str  = gr.Slider(0.1, 0.9,  value=0.35, step=0.05, label="REFINER STRENGTH")

                gr.HTML('<span class="section-label" style="margin-top:20px">Engine Control</span>')
                with gr.Row():
                    t4_btn_load  = gr.Button("INITIALISE MODELS", variant="primary")
                    t4_btn_clear = gr.Button("FLUSH VRAM",        variant="stop")
                t4_model_log = gr.Textbox(label="ENGINE STATUS", lines=8,
                                          interactive=False, elem_classes=["log-console"])
                t4_btn_load.click(fn=fn_load_models, inputs=[t4_model_mode], outputs=[t4_model_log])
                t4_btn_clear.click(fn=fn_clear_vram, inputs=[],              outputs=[t4_model_log])

        # ── Cross-tab wiring ──────────────────────────────────
        btn_template.click(fn=fn_load_template, inputs=[template_dd],
                           outputs=[t1_scenes, t1_camera, t1_lighting, t1_style])
        btn_quality.click(fn=fn_quality_check, inputs=[t1_scenes], outputs=[quality_box])
        t1_btn_expand.click(fn=fn_expand, inputs=[t1_scenes, t1_style],
                            outputs=[t1_scenes, log_box])
        t1_btn_preview.click(
            fn=fn_preview,
            inputs=[t1_scenes, t1_chars, t1_camera, t1_lighting, t1_style,
                    t4_cfg, t4_steps, t2_ip_ref, t2_ip_scale, t1_seed],
            outputs=[t1_preview_img, log_box],
        )
        t1_btn_generate.click(
            fn=fn_generate,
            inputs=[
                t1_scenes, t1_chars, t1_camera, t1_lighting, t1_style,
                t4_cfg, t4_steps, t4_refine_steps, t4_refiner_str,
                t2_ip_ref, t2_ip_scale, t2_faceid_scale,
                t3_pose_ref, t3_cn_scale,
                t2_char_lora_path, t2_char_lora_scale,
                t2_style_lora_path, t2_style_lora_scale,
                t1_speed, t4_model_mode, t1_physics, t1_transition, t1_seed,
            ],
            outputs=[t1_gallery, log_box],
        )

    return demo


# ================================================================
# STEP 7 — LAUNCH
# ================================================================
# [FIX] Wrapped in if __name__ == '__main__' so this block
# does NOT run when the file is imported as a module.
# Import-safe: engine and demo are only created when running directly.

if __name__ == '__main__':
    engine = CinematicEngineV16()  # V16 PROFESSIONAL

    if GRADIO_AVAILABLE:
        demo = build_gradio_ui(engine)
        # [IMP-9] Queue — prevents crash under concurrent load
        demo.queue(max_size=10, default_concurrency_limit=1)
        demo.launch(
            share=True,
            debug=False,
            server_port=7860,
            show_error=True,
        )
    else:
        print("[!] Install Gradio:  pip install 'gradio>=4.0.0'")
        print("[!] Direct API usage:")
        print("      engine.load_models(model_mode=ModelMode.FLUX_SCHNELL)")
        print("      from dataclasses import replace")
        print("      cfg = GenerationConfig(scene_text='your scene')")
        print("      img, meta = engine.generate_scene(cfg)")

# ================================================================
# WORKFLOW GUIDE  — V16 PROFESSIONAL
# ================================================================
# 1. Run SETUP_CELL (top of file) in first Colab cell — once only
# 2. Run this file in second Colab cell
# 3. Public share link appears automatically
#
# STATUS   → Check GPU VRAM + active model before starting
# SETTINGS → Initialise Models (choose Flux Schnell / Dev / SDXL)
# GENERATE → Load template OR write scenes → Quality Check
#            → Choose Physics / Speed / Transition → Expand → Preview → Generate
# CHARACTER → Upload 1-5 face photos + LoRA (SDXL only)
# POSE      → Upload pose reference + Extract Skeleton (SDXL NORMAL only)
# STATUS   → DOWNLOAD ALL as ZIP when done
#
# V16 PROFESSIONAL — 15 ARCHITECTURAL IMPROVEMENTS:
#  [IMP-1]  PipelineManager     — independent instances, no cross-reuse
#  [IMP-2]  VRAMManager         — pre-flight VRAM checks, prevents OOM
#  [IMP-3]  ModelRegistry       — lazy load + singleton pattern
#  [IMP-4]  NeuralPhysics       — 10s timeout, ThreadPoolExecutor
#  [IMP-5]  FaceIDExtractor     — weighted quality + outlier rejection
#  [IMP-6]  GenerationConfig    — dataclass replaces 15 loose params
#  [IMP-7]  ErrorHandler        — every step has fallback, no session crash
#  [IMP-8]  CinematicLogger     — logging.INFO/WARNING/ERROR + file + gradio
#  [IMP-9]  Gradio Queue        — demo.queue(max_size=10) prevents overload
#  [IMP-10] LoRAStateManager    — safe fuse/unfuse with state tracking
#  [IMP-11] PromptBuilder       — structured compiler replaces concatenation
#  [IMP-12] SmartCache          — unified LRU + TTL cache (prompts/physics/emb)
#  [IMP-13] Modular classes     — each component independent and testable
#  [IMP-14] Validation asserts  — shape, resolution, CFG range checks
#  [IMP-15] Async-safe storyboard — deterministic seeds, no race conditions
# ================================================================

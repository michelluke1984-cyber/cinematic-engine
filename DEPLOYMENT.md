# Deployment Guide — Cinematic Engine V17.2

Complete step-by-step deployment for every environment.

---

## Environments Covered

| Environment | Cost | Setup Time | Best For |
|-------------|------|------------|----------|
| [Google Colab Free](#google-colab-free-t4) | Free | 5 min | Testing, demos |
| [Google Colab Pro](#google-colab-pro) | $10–50/mo | 5 min | Regular use |
| [RunPod](#runpod) | ~$0.40/hr | 15 min | Always-on, public URL |
| [Vast.ai](#vastai) | ~$0.20/hr | 15 min | Budget cloud GPU |
| [Local Linux/Mac](#local-linuxmac) | Hardware cost | 20 min | Full control |
| [Local Windows](#local-windows) | Hardware cost | 25 min | Full control |

---

## Google Colab Free (T4)

**VRAM:** 15GB · **Best model:** FLUX SCHNELL

```python
# Cell 1 — run once per session
# Upload files: cinematic_engine_v16_pro.py, cev17_backend.py

import subprocess
subprocess.run("pip install -q websockets pyngrok diffusers transformers "
               "accelerate xformers gfpgan realesrgan gradio "
               "bitsandbytes insightface onnxruntime-gpu Pillow nltk",
               shell=True)

import nltk
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)

print("✓ Ready")
```

```python
# Cell 2 — load engine
import importlib.util, sys
spec = importlib.util.spec_from_file_location('cev16', 'cinematic_engine_v16_pro.py')
cev16 = importlib.util.module_from_spec(spec)
sys.modules['__main__'].__dict__.update(
    {k: v for k, v in cev16.__dict__.items() if not k.startswith('_')}
)
engine = CinematicEngineV16()
print("✓ Engine ready")
```

```python
# Cell 3 — start bridge (blocks until interrupted)
import importlib.util
spec = importlib.util.spec_from_file_location('bridge', 'cev17_backend.py')
bridge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge)
bridge.run_bridge(engine=engine, use_ngrok=False)
```

Open `cinematic_engine_v17_2_final.html` → click **WS: OFF**.

> **Note on Colab sessions:** Colab disconnects after ~90 min of browser inactivity.  
> The Dashboard persists its state locally — reconnect and continue from where you left off.

---

## Google Colab Pro

Same as free, but with A100 (40GB) or V100 (16GB) available.  
For A100, FLUX DEV becomes viable at full quality.

```python
# Cell 3 for Pro — with persistent ngrok tunnel
USE_NGROK = True
NGROK_TOKEN = 'your_token'   # from dashboard.ngrok.com

from pyngrok import ngrok, conf
conf.get_default().auth_token = NGROK_TOKEN

import importlib.util
spec = importlib.util.spec_from_file_location('bridge', 'cev17_backend.py')
bridge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge)
bridge.run_bridge(engine=engine, use_ngrok=True)
# → Output shows: [NGROK] Public URL: ws://abc123.ngrok.io
```

Update the Dashboard's `WS_URL` constant:
```javascript
// In cinematic_engine_v17_2_final.html, line ~1149
const WS_URL = 'ws://abc123.ngrok.io';   // your ngrok URL
```

---

## RunPod

**Recommended template:** RunPod PyTorch 2.1.0

### Step 1 — Create Pod

1. Go to [runpod.io](https://www.runpod.io)
2. Click **Deploy** → **GPU Cloud**
3. Select **RTX 3090** (24GB, ~$0.44/hr) or **RTX 4090** (24GB, ~$0.74/hr)
4. Template: **RunPod PyTorch 2.1.0**
5. Container Disk: 50GB minimum
6. **Expose Ports:** Add `7860` (TCP)
7. Deploy

### Step 2 — Setup

In the RunPod terminal:

```bash
# Clone / upload your files
wget https://your-repo/cinematic_engine_v16_pro.py
wget https://your-repo/cev17_backend.py

# Install dependencies
pip install diffusers transformers accelerate xformers gfpgan realesrgan \
            gradio bitsandbytes insightface onnxruntime-gpu Pillow \
            websockets nltk sentencepiece controlnet-aux open-clip-torch

# Download NLTK
python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab')"

# Download model weights
wget -q -O GFPGANv1.3.pth https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.3.pth
wget -q -O realesr-general-x4v3.pth https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesr-general-x4v3.pth
```

### Step 3 — Run

```bash
# Terminal 1 — start bridge (no ngrok needed, RunPod exposes the port directly)
python cev17_backend.py &

# Terminal 2 — optional: also run Gradio UI
python cinematic_engine_v16_pro.py
```

### Step 4 — Connect Dashboard

Find your pod's public URL in RunPod dashboard: `https://xyz.proxy.runpod.net:7860`

Update `WS_URL` in the Dashboard:
```javascript
const WS_URL = 'wss://xyz.proxy.runpod.net:7860/ws';   // note: wss (SSL)
```

> **Important:** RunPod uses `wss://` (SSL). Use `wss://` not `ws://`.

---

## Vast.ai

**Recommended:** RTX 3080 (10GB, ~$0.20/hr)

### Step 1 — Rent Instance

1. Go to [vast.ai](https://vast.ai)
2. Search: `gpu_ram >= 10 cuda_vers >= 11.8`
3. Select an instance with **PyTorch** pre-installed
4. Add port mapping: `7860 → 7860 (TCP)`

### Step 2 — Setup

Same as RunPod setup above.

### Step 3 — Connect

Vast.ai provides a direct IP:port — use `ws://IP:7860/ws` in `WS_URL`.

---

## Local Linux/Mac

**Requirements:** CUDA GPU, CUDA 11.8+, Python 3.10+

```bash
# Install CUDA (Ubuntu)
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt-get update
sudo apt-get install cuda-11-8

# Create environment
python3 -m venv ~/cev17-env
source ~/cev17-env/bin/activate

# Install PyTorch
pip install torch==2.1.0 torchvision==0.16.0 --index-url https://download.pytorch.org/whl/cu118

# Install all dependencies
pip install diffusers==0.27.0 transformers==4.38.0 accelerate xformers \
            gfpgan realesrgan tqdm sentencepiece nltk \
            controlnet-aux open-clip-torch gradio>=4.0.0 \
            bitsandbytes Pillow insightface onnxruntime-gpu \
            websockets pyngrok numpy einops triton

# Download NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab')"

# Download model weights
mkdir -p ip_adapter_sdxl/image_encoder
wget -q https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.3.pth
wget -q https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesr-general-x4v3.pth
wget -q -O ip_adapter_sdxl.bin https://huggingface.co/h94/IP-Adapter/resolve/main/sdxl_models/ip-adapter_sdxl.bin

# Run engine (background)
python cinematic_engine_v16_pro.py &

# Run bridge
python cev17_backend.py
```

Open `cinematic_engine_v17_2_final.html` in browser → click **WS: OFF**.

### Auto-start on Boot (systemd)

```ini
# /etc/systemd/system/cev17.service
[Unit]
Description=Cinematic Engine V17 Bridge
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/cinematic-engine
Environment="PATH=/home/ubuntu/cev17-env/bin"
ExecStart=/home/ubuntu/cev17-env/bin/python cev17_backend.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable cev17
sudo systemctl start cev17
```

---

## Local Windows

```powershell
# Install Python 3.10 from python.org
# Install CUDA 11.8 from developer.nvidia.com

# Create environment
python -m venv C:\cev17-env
C:\cev17-env\Scripts\activate

# Install PyTorch (CUDA 11.8)
pip install torch==2.1.0 torchvision==0.16.0 --index-url https://download.pytorch.org/whl/cu118

# Install dependencies
pip install diffusers transformers accelerate xformers gfpgan realesrgan `
            gradio bitsandbytes Pillow insightface onnxruntime-gpu `
            websockets pyngrok nltk sentencepiece

# Download NLTK
python -c "import nltk; nltk.download('punkt')"

# Run bridge
python cev17_backend.py
```

---

## Configuring the Bridge

All bridge settings are in `cev17_backend.py`:

```python
class BridgeConfig:
    HOST             = "0.0.0.0"   # "127.0.0.1" for local-only access
    PORT             = 7860         # WebSocket port
    METRICS_INTERVAL = 2.0          # Seconds between metrics broadcasts
    MAX_CLIENTS      = 10           # Max simultaneous Dashboard connections
    PING_INTERVAL    = 20           # WebSocket keep-alive ping (seconds)
    PING_TIMEOUT     = 10           # Ping timeout before disconnect
```

---

## GPU VRAM Requirements

| Model | Min VRAM | Recommended | Notes |
|-------|----------|-------------|-------|
| FLUX SCHNELL | 7 GB | 10 GB | 4-step, Apache-2.0, fastest |
| FLUX DEV | 13 GB | 16 GB | 20-step, HF_TOKEN required |
| SDXL Base | 5.5 GB | 8 GB | Full pipeline with refiner |
| SDXL + ControlNet | 8.5 GB | 12 GB | Add 3GB for ControlNet |
| SDXL + HiresFix | 9.5 GB | 12 GB | Add 4GB for HiresFix |
| Full SDXL stack | 12 GB | 16 GB | All features enabled |
| LLM Physics (Mistral) | 8 GB | 12 GB | Disable if VRAM tight |

---

## Environment Variables

```bash
export HF_TOKEN="your_huggingface_token"    # Required for FLUX DEV only
export CUDA_VISIBLE_DEVICES="0"             # GPU index to use
export PYTORCH_CUDA_ALLOC_CONF="max_split_size_mb:512"  # OOM prevention
```

---

## Production Checklist

Before going public:

- [ ] Change `HOST = "127.0.0.1"` if bridge should not be publicly accessible
- [ ] Use `wss://` (SSL) for any public deployment
- [ ] Set ngrok or reverse proxy with authentication
- [ ] Set `HF_TOKEN` environment variable for FLUX DEV
- [ ] Test `flush_vram` command works correctly
- [ ] Verify WebSocket reconnects after engine restart
- [ ] Test with multiple browser tabs simultaneously
- [ ] Check `v16_cinematic_storyboard/` directory has write permissions

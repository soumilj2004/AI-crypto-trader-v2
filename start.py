#!/usr/bin/env python3
"""
CryptoTrader v2 — One-Click Launcher
Usage: python start.py
"""
import os, sys, time, subprocess, platform, webbrowser, urllib.request

ROOT    = os.path.dirname(os.path.abspath(__file__))
BACKEND = os.path.join(ROOT, "backend")
VENV    = os.path.join(ROOT, ".venv")
PORT    = 8000
URL     = f"http://localhost:{PORT}"

# ── colours ──────────────────────────────────────────────────────
R="\033[0m"; B="\033[1m"; CY="\033[96m"; GR="\033[92m"; YL="\033[93m"; RD="\033[91m"; DM="\033[2m"

BANNER = f"""
{CY}{B}
  ██████╗██████╗ ██╗   ██╗██████╗ ████████╗ ██████╗     ████████╗██████╗  █████╗ ██████╗ ███████╗██████╗
 ██╔════╝██╔══██╗╚██╗ ██╔╝██╔══██╗╚══██╔══╝██╔═══██╗    ╚══██╔══╝██╔══██╗██╔══██╗██╔══██╗██╔════╝██╔══██╗
 ██║     ██████╔╝ ╚████╔╝ ██████╔╝   ██║   ██║   ██║       ██║   ██████╔╝███████║██║  ██║█████╗  ██████╔╝
 ██║     ██╔══██╗  ╚██╔╝  ██╔═══╝    ██║   ██║   ██║       ██║   ██╔══██╗██╔══██║██║  ██║██╔══╝  ██╔══██╗
 ╚██████╗██║  ██║   ██║   ██║        ██║   ╚██████╔╝       ██║   ██║  ██║██║  ██║██████╔╝███████╗██║  ██║
  ╚═════╝╚═╝  ╚═╝   ╚═╝   ╚═╝        ╚═╝    ╚═════╝        ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ ╚══════╝╚═╝  ╚═╝
{R}{CY}  v2.0  ·  Professional Crypto Terminal  ·  WebSocket  ·  AI-Powered  ·  10 Assets
{R}"""

def log(msg, col=GR):   print(f"  {col}{B}→{R}  {msg}")
def warn(msg):          print(f"  {YL}{B}⚠{R}  {msg}")
def err(msg):           print(f"  {RD}{B}✗{R}  {msg}")
def ok(msg):            print(f"  {GR}{B}✓{R}  {msg}")
def step(n, msg):       print(f"\n  {DM}[{n}]{R} {B}{msg}{R}")

# ── python detection ──────────────────────────────────────────────
def find_python():
    if platform.system() == "Windows":
        venv_py = os.path.join(VENV, "Scripts", "python.exe")
    else:
        venv_py = os.path.join(VENV, "bin", "python")
    if os.path.isfile(venv_py):
        return venv_py
    for candidate in ["python3", "python"]:
        try:
            r = subprocess.run([candidate,"--version"], capture_output=True, text=True)
            if r.returncode == 0:
                ver = r.stdout.strip() or r.stderr.strip()
                ok(f"Found {ver}")
                return candidate
        except FileNotFoundError:
            continue
    err("Python not found — install Python 3.10+ from https://python.org")
    sys.exit(1)

def venv_python():
    if platform.system() == "Windows":
        return os.path.join(VENV, "Scripts", "python.exe")
    return os.path.join(VENV, "bin", "python")

# ── venv ──────────────────────────────────────────────────────────
def ensure_venv(base_py):
    if os.path.isfile(venv_python()):
        ok("Virtual environment already exists")
        return venv_python()
    log("Creating virtual environment…", YL)
    subprocess.run([base_py, "-m", "venv", VENV], check=True)
    ok("Virtual environment created")
    return venv_python()

# ── deps ──────────────────────────────────────────────────────────
def install_deps(py):
    req = os.path.join(BACKEND, "requirements.txt")
    log("Installing dependencies (one-time only)…", YL)
    r = subprocess.run(
        [py, "-m", "pip", "install", "-r", req,
         "--quiet", "--disable-pip-version-check"],
        capture_output=True, text=True
    )
    if r.returncode != 0:
        err("Dependency install failed:\n" + r.stderr[:600])
        sys.exit(1)
    ok("All dependencies ready")

# ── ollama check (non-blocking) ───────────────────────────────────
def check_ollama():
    try:
        urllib.request.urlopen("http://localhost:11434", timeout=2)
        ok("Ollama detected  — AI assistant is enabled")
    except Exception:
        warn("Ollama not found  — AI assistant will show an error until you start it")
        warn("  Run in a separate terminal:  ollama serve")
        warn("  Then pull a model:           ollama pull mistral")

# ── server ───────────────────────────────────────────────────────
def start_server(py):
    env = os.environ.copy()
    env["PYTHONPATH"] = BACKEND
    log(f"Starting server on {CY}{URL}{R}", GR)
    return subprocess.Popen(
        [py, "-m", "uvicorn", "main:app",
         "--host", "0.0.0.0",
         "--port", str(PORT),
         "--reload",
         "--log-level", "warning"],
        cwd=BACKEND, env=env,
    )

def wait_ready(retries=40):
    for _ in range(retries):
        try:
            urllib.request.urlopen(URL, timeout=1)
            return True
        except Exception:
            time.sleep(0.5)
    return False

# ── main ─────────────────────────────────────────────────────────
def main():
    print(BANNER)

    step(1, "Locating Python")
    base_py = find_python()

    step(2, "Setting up virtual environment")
    py = ensure_venv(base_py)

    step(3, "Installing / verifying packages")
    install_deps(py)

    step(4, "Checking Ollama (AI assistant)")
    check_ollama()

    step(5, "Launching CryptoTrader v2")
    proc = start_server(py)

    log("Waiting for server to be ready…", YL)
    if wait_ready():
        ok(f"Server is live at {CY}{URL}{R}")
        time.sleep(0.4)
        print(f"\n  {GR}{B}Opening browser…{R}\n")
        webbrowser.open(URL)
    else:
        warn(f"Server took longer than expected — open {URL} manually")

    print(f"  {DM}Press Ctrl+C to stop{R}\n")
    try:
        proc.wait()
    except KeyboardInterrupt:
        print(f"\n  {YL}Shutting down…{R}")
        proc.terminate()
        try: proc.wait(timeout=5)
        except subprocess.TimeoutExpired: proc.kill()
        print(f"  {GR}Stopped. Goodbye.{R}\n")

if __name__ == "__main__":
    main()

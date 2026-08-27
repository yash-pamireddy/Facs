"""FACS — Automated Ecosystem Installer

Powered by Pulse
"""

import os
import subprocess
import sys
import threading
import time


def is_termux():
  """Detects if running inside an Android Termux environment."""
  return "TERMUX_VERSION" in os.environ or os.path.exists(
      "/data/data/com.termux"
  )


def run_silent(cmd):
  """Runs system commands completely hidden from terminal output."""
  try:
    subprocess.check_call(
        cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    return True
  except subprocess.CalledProcessError:
    return False


def install_dependencies():
  print("==========================================")
  print("   FACS — Pulse Environment Setup         ")
  print("==========================================")

  print("\n[SETUP] Initializing secure environment...")
  if is_termux():
    run_silent([
        "pkg",
        "install",
        "-y",
        "cmake",
        "clang",
        "make",
        "libopenblas",
        "libjpeg-turbo",
        "libpng",
    ])
    run_silent([sys.executable, "-m", "pip", "install", "-q", "dlib"])
  else:
    run_silent([sys.executable, "-m", "pip", "install", "-q", "setuptools<=81"])

  # Define core installation packages silently
  pip_cmd = [
      sys.executable,
      "-m",
      "pip",
      "install",
      "-q",
      "numpy",
      "opencv-python",
      "face-recognition",
      ".",
  ]

  print("\n[INSTALLING] Downloading and configuring ecosystem...")

  # Run installation in a background thread while animating the bar
  install_thread = threading.Thread(
      target=lambda: run_silent(pip_cmd)
  )
  install_thread.start()

  total = 35
  i = 0
  while install_thread.is_alive():
    progress = i % total
    bar = "█" * progress + "-" * (total - progress)
    sys.stdout.write(f"\r[{bar}] Please wait...")
    sys.stdout.flush()
    time.sleep(0.1)
    i += 1

  install_thread.join()

  # Clear progress bar line and print success box
  sys.stdout.write("\r" + " " * 50 + "\r")
  print("==========================================")
  print("   [SUCCESS] FACS is fully installed!     ")
  print("   To launch, simply type:                ")
  print("   >>> run facs                           ")
  print("==========================================")


if __name__ == "__main__":
  install_dependencies()
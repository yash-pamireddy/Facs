"""FACS — Automated Ecosystem Installer

Powered by Pulse
Automatically detects device architecture and sets up with a live progress bar.
"""

import os
import platform
import subprocess
import sys
import time


def show_loading_bar(task_name, duration=1.5):
  """Displays a sleek terminal progress bar for setup tasks."""
  print(f"\n[SETUP] {task_name}...")
  total = 30
  for i in range(total + 1):
    percent = int((i / total) * 100)
    bar = "█" * i + "-" * (total - i)
    sys.stdout.write(f"\r[{bar}] {percent}%")
    sys.stdout.flush()
    time.sleep(duration / total)
  print()


def is_termux():
  """Detects if the script is running inside an Android Termux environment."""
  return "TERMUX_VERSION" in os.environ or os.path.exists(
      "/data/data/com.termux"
  )


def install_dependencies():
  print("==========================================")
  print("   FACS — Pulse Environment Setup         ")
  print("   Powered by Pulse Ecosystem             ")
  print("==========================================")

  show_loading_bar("Initializing Pulse installer", 1.0)

  # Upgrade pip
  subprocess.check_call(
      [sys.executable, "-m", "pip", "install", "--upgrade", "pip"]
  )

  if is_termux():
    print(
        "\n[MOBILE DETECTED] Configuring mobile-friendly Termux packages..."
    )
    show_loading_bar("Installing system build tools", 2.0)
    subprocess.check_call(
        [
            "pkg",
            "install",
            "-y",
            "cmake",
            "clang",
            "make",
            "libopenblas",
            "libjpeg-turbo",
            "libpng",
        ]
    )
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "numpy", "opencv-python"]
    )
    subprocess.check_call([sys.executable, "-m", "pip", "install", "dlib"])
  else:
    print(
        "\n[STANDARD PC DETECTED] Configuring desktop biometric"
        " dependencies..."
    )
    show_loading_bar("Configuring environment settings", 1.0)
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "setuptools<=81"]
    )

  show_loading_bar("Downloading core face recognition models", 2.5)
  subprocess.check_call(
      [sys.executable, "-m", "pip", "install", "face-recognition"]
  )
  subprocess.check_call([sys.executable, "-m", "pip", "install", "."])

  print("\n==========================================")
  print("   [SUCCESS] FACS is fully installed!     ")
  print("   To launch, simply type:                ")
  print("   >>> run facs                           ")
  print("==========================================")


if __name__ == "__main__":
  install_dependencies()
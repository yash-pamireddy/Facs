"""FACS — Automated Ecosystem Installer

Powered by Pulse
"""

import os
import subprocess
import sys


def is_termux():
  """Detects if running inside an Android Termux environment."""
  return "TERMUX_VERSION" in os.environ or os.path.exists(
      "/data/data/com.termux"
  )


def install_dependencies():
  print("==========================================")
  print("   FACS — Pulse Environment Setup         ")
  print("==========================================")

  if is_termux():
    print(
        "\n[1/3] Installing mobile system tools (this may take a minute)..."
    )
    subprocess.call([
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

    print("\n[2/3] Installing mobile biometric packages...")
    subprocess.call([sys.executable, "-m", "pip", "install", "dlib"])
  else:
    print("\n[1/2] Configuring desktop environment settings...")
    subprocess.call([sys.executable, "-m", "pip", "install", "setuptools<=81"])

  print("\n[FINAL] Downloading core engine and models (please wait)...")
  subprocess.call([
      sys.executable,
      "-m",
      "pip",
      "install",
      "numpy",
      "opencv-python",
      "face-recognition",
      ".",
  ])

  print("\n==========================================")
  print("   [SUCCESS] FACS is fully installed!     ")
  print("   To launch, simply type:                ")
  print("   >>> facs                               ")
  print("==========================================")


if __name__ == "__main__":
  install_dependencies()
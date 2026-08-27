"""FACS — Powered by Pulse

Industry-grade biometric face authentication module.
"""

from facs.auth import authenticate_or_register


def main():
  print("==========================================")
  print("   FACS — Biometric Engine                ")
  print("   Powered by Pulse Ecosystem             ")
  print("==========================================")

  # Run the core multi-angle biometric pipeline
  authenticate_or_register()


if __name__ == "__main__":
  main()
"""
Standalone çalıştırma scripti
"""
import sys
import os

# Proje dizinini path'e ekle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.app import run_standalone

if __name__ == "__main__":
    run_standalone()

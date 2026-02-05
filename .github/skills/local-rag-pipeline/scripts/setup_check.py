#!/usr/bin/env python3
"""
Setup verification script for Local RAG Pipeline.
Checks GPU availability, dependencies, and model locations.
"""

import sys
import subprocess


def check_import(package_name, display_name=None):
    """Check if a package can be imported."""
    display = display_name or package_name
    try:
        __import__(package_name)
        print(f"✓ {display} installed")
        return True
    except ImportError:
        print(f"✗ {display} NOT installed")
        return False


def check_cuda():
    """Check CUDA availability."""
    try:
        import torch
        cuda_available = torch.cuda.is_available()
        if cuda_available:
            print(f"✓ CUDA available: {torch.version.cuda}")
            print(f"  GPU: {torch.cuda.get_device_name(0)}")
            print(f"  Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
        else:
            print("✗ CUDA not available (CPU mode)")
        return cuda_available
    except Exception as e:
        print(f"✗ Error checking CUDA: {e}")
        return False


def check_model_cache():
    """Check sentence-transformers model cache location."""
    try:
        from sentence_transformers import SentenceTransformer
        import os
        cache_folder = os.path.expanduser("~/.cache/torch/sentence_transformers/")
        print(f"✓ Model cache: {cache_folder}")
    except Exception as e:
        print(f"⚠ Could not determine model cache: {e}")


def main():
    print("=" * 60)
    print("Local RAG Pipeline - Setup Verification")
    print("=" * 60)
    
    print("\n1. Core Dependencies:")
    all_ok = True
    all_ok &= check_import("docling", "Docling")
    all_ok &= check_import("sentence_transformers", "sentence-transformers")
    all_ok &= check_import("chromadb", "ChromaDB")
    all_ok &= check_import("torch", "PyTorch")
    
    print("\n2. Supporting Libraries:")
    check_import("PyPDF2")
    check_import("docx", "python-docx")
    check_import("PIL", "Pillow")
    check_import("numpy")
    check_import("pandas")
    
    print("\n3. GPU Setup:")
    cuda_ok = check_cuda()
    
    print("\n4. Model Cache:")
    check_model_cache()
    
    print("\n" + "=" * 60)
    if all_ok:
        if cuda_ok:
            print("✓ All dependencies installed. GPU acceleration enabled.")
        else:
            print("⚠ Dependencies OK, but running in CPU mode (slower).")
    else:
        print("✗ Some dependencies missing. Run:")
        print("  pip install -r requirements.txt --break-system-packages")
    print("=" * 60)
    
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())

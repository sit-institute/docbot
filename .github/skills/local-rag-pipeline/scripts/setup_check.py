#!/usr/bin/env python3
"""
Setup verification script for Local RAG Pipeline.
Checks GPU availability, dependencies, and model locations.

Usage:
    python setup_check.py              # Quick status check
    python setup_check.py --quick      # Same as above
    python setup_check.py --install    # Install deps if missing, then verify
    python setup_check.py --full       # Full check with pip install attempt
"""

import sys
import argparse
import subprocess
import os


def check_import(package_name, display_name=None):
    """Check if a package can be imported."""
    display = display_name or package_name
    try:
        __import__(package_name)
        print(f"  ✓ {display}")
        return True
    except ImportError:
        print(f"  ✗ {display} NOT installed")
        return False


def check_cuda():
    """Check CUDA availability."""
    try:
        import torch

        cuda_available = torch.cuda.is_available()
        if cuda_available:
            print(f"  ✓ CUDA available: {torch.version.cuda}")
            print(f"    GPU: {torch.cuda.get_device_name(0)}")
            print(
                f"    Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB"
            )
        else:
            print("  ✗ CUDA not available (CPU mode)")
        return cuda_available
    except Exception as e:
        print(f"  ✗ Error checking CUDA: {e}")
        return False


def check_model_cache():
    """Check sentence-transformers model cache location."""
    try:
        from sentence_transformers import SentenceTransformer
        import os

        cache_folder = os.path.expanduser("~/.cache/torch/sentence_transformers/")
        print(f"  ✓ Model cache: {cache_folder}")
    except Exception as e:
        print(f"  ⚠ Could not determine model cache: {e}")


def check_directories():
    """Check required directories exist."""
    required_dirs = [
        (".rag/parsed", "Parsed documents"),
        (".rag/chunks", "Document chunks"),
        (".rag/embeddings", "Embeddings"),
        (".rag/chromadb", "Vector database"),
    ]

    all_ok = True
    for rel_path, description in required_dirs:
        abs_path = os.path.abspath(rel_path)
        if os.path.exists(abs_path):
            print(f"  ✓ {description}: {rel_path}/")
        else:
            print(f"  ✗ {description}: {rel_path}/ (missing)")
            all_ok = False
    return all_ok


def install_dependencies():
    """Install dependencies from requirements.txt."""
    req_file = os.path.join(os.path.dirname(__file__), "requirements.txt")

    if not os.path.exists(req_file):
        print(f"  ✗ Requirements file not found: {req_file}")
        return False

    print("  Installing dependencies...")
    try:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "-r",
                req_file,
                "--break-system-packages",
                "-q",
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print("  ✓ Dependencies installed successfully")
            return True
        else:
            print(f"  ✗ Installation failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"  ✗ Installation error: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Local RAG Pipeline Setup Verification"
    )
    parser.add_argument(
        "--quick", action="store_true", help="Quick status check (default)"
    )
    parser.add_argument(
        "--install",
        action="store_true",
        help="Install dependencies if missing, then verify",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Full check: install missing deps and verify",
    )
    parser.add_argument(
        "--dirs-only", action="store_true", help="Check directory structure only"
    )

    args = parser.parse_args()

    print("=" * 60)
    print("Local RAG Pipeline - Setup Verification")
    print("=" * 60)

    if args.dirs_only:
        print("\nDirectory Structure:")
        return 0 if check_directories() else 1

    if not args.install and not args.full:
        print("\n1. Core Dependencies (quick check):")
        core_packages = [
            ("docling", "Docling"),
            ("sentence_transformers", "sentence-transformers"),
            ("chromadb", "ChromaDB"),
            ("torch", "PyTorch"),
        ]
        missing = []
        for pkg, name in core_packages:
            if not check_import(pkg, name):
                missing.append((pkg, name))

        if missing:
            print("\n" + "=" * 60)
            print("⚠ Some dependencies missing.")
            print("Run one of:")
            print("  python scripts/setup_check.py --install    # Auto-install")
            print("  pip install -r scripts/requirements.txt --break-system-packages")
            print("=" * 60)
            return 1
        else:
            print("\n✓ All core dependencies available")
            return 0

    print("\n1. Core Dependencies:")
    all_ok = True
    all_ok &= check_import("docling", "Docling")
    all_ok &= check_import("sentence_transformers", "sentence-transformers")
    all_ok &= check_import("chromadb", "ChromaDB")
    all_ok &= check_import("torch", "PyTorch")

    if not all_ok and not args.full:
        if args.install:
            print("\nInstalling missing dependencies...")
            if not install_dependencies():
                print("\n" + "=" * 60)
                print("✗ Installation failed")
                print("=" * 60)
                return 1
        else:
            print("\n" + "=" * 60)
            print("✗ Some dependencies missing")
            print("=" * 60)
            return 1

    if args.full:
        print("\nInstalling dependencies...")
        install_dependencies()

    print("\n2. Supporting Libraries:")
    check_import("PyPDF2")
    check_import("docx", "python-docx")
    check_import("PIL", "Pillow")
    check_import("numpy")
    check_import("pandas")

    print("\n3. Directory Structure:")
    check_directories()

    print("\n4. GPU Setup:")
    cuda_ok = check_cuda()

    print("\n5. Model Cache:")
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

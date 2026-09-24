"""Vercel serverless entry point for the RSTAM FastAPI backend.

This wraps the FastAPI app for Vercel's Python runtime.
Uses lightweight text-only analyzers (no torch/whisper) to stay
within Vercel's 250MB serverless function size limit.
"""
import os
import sys

# Ensure the backend package is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Set environment variables for Vercel
os.environ.setdefault("DATABASE_URL", "sqlite:///tmp/rstam.db")
os.environ.setdefault("RSTAM_LITE_MODE", "1")  # Skip heavy ML deps

from app.main import app  # noqa: E402

# Vercel expects the ASGI app as `app`
# The variable name must match what Vercel looks for

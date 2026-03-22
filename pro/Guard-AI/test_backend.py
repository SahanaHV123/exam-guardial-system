#!/usr/bin/env python3
"""
Test script to verify Guard AI backend code is syntactically correct
and all imports work properly.
"""
import sys
import os


def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    try:
        import cv2  # type: ignore # noqa: F401
        print("✅ opencv-python imported successfully")
    except ImportError as e:
        print(f"❌ opencv-python import failed: {e}")
        return False

    try:
        import mediapipe as mp  # type: ignore # noqa: F401
        print("✅ mediapipe imported successfully")
    except ImportError as e:
        print(f"❌ mediapipe import failed: {e}")
        return False

    try:
        import numpy as np  # type: ignore # noqa: F401
        print("✅ numpy imported successfully")
    except ImportError as e:
        print(f"❌ numpy import failed: {e}")
        return False

    try:
        import sounddevice as sd  # type: ignore # noqa: F401
        print("✅ sounddevice imported successfully")
    except ImportError as e:
        print(f"❌ sounddevice import failed: {e}")
        return False

    try:
        import psutil  # type: ignore # noqa: F401
        print("✅ psutil imported successfully")
    except ImportError as e:
        print(f"❌ psutil import failed: {e}")
        return False

    try:
        from fpdf import FPDF  # type: ignore # noqa: F401
        print("✅ fpdf imported successfully")
    except ImportError as e:
        print(f"❌ fpdf import failed: {e}")
        return False

    try:
        from flask import Flask  # type: ignore # noqa: F401
        print("✅ flask imported successfully")
    except ImportError as e:
        print(f"❌ flask import failed: {e}")
        return False

    return True


def test_main_syntax():
    """Test that main.py has no syntax errors"""
    print("\nTesting main.py syntax...")
    try:
        with open("main.py", "r", encoding="utf-8") as f:
            code = f.read()
        compile(code, "main.py", "exec")
        print("✅ main.py has no syntax errors")
        return True
    except SyntaxError as e:
        print(f"❌ main.py has syntax error: {e}")
        return False


def test_app_syntax():
    """Test that app.py has no syntax errors"""
    print("\nTesting app.py syntax...")
    try:
        with open("app.py", "r", encoding="utf-8") as f:
            code = f.read()
        compile(code, "app.py", "exec")
        print("✅ app.py has no syntax errors")
        return True
    except SyntaxError as e:
        print(f"❌ app.py has syntax error: {e}")
        return False


def test_pdf_generation():
    """Test PDF generation functionality"""
    print("\nTesting PDF generation...")
    try:
        from fpdf import FPDF  # type: ignore # noqa: F401
        import textwrap  # noqa: F401

        # Create a simple test PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', size=16)
        pdf.cell(0, 10, "Test Report", ln=True, align='C')

        test_pdf_path = "logs/test_report.pdf"
        os.makedirs("logs", exist_ok=True)
        pdf.output(test_pdf_path)

        if os.path.exists(test_pdf_path):
            print(f"✅ PDF generation works - created {test_pdf_path}")
            os.remove(test_pdf_path)
            return True
        else:
            print("❌ PDF generation failed - file not created")
            return False
    except Exception as e:
        print(f"❌ PDF generation error: {e}")
        return False


def main():
    print("=" * 60)
    print("Guard AI Backend Verification Test")
    print("=" * 60)

    tests = [
        ("Import Test", test_imports),
        ("main.py Syntax Test", test_main_syntax),
        ("app.py Syntax Test", test_app_syntax),
        ("PDF Generation Test", test_pdf_generation),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n{'=' * 60}")
        result = test_func()
        results.append((test_name, result))

    print(f"\n{'=' * 60}")
    print("Test Summary:")
    print("=" * 60)

    all_passed = True
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False

    print("=" * 60)
    if all_passed:
        print("🎉 All tests passed! Backend is ready to use.")
        return 0
    else:
        print("⚠️  Some tests failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

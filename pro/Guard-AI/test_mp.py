import traceback
try:
    import mediapipe as mp  # type: ignore
    print("mediapipe version:", getattr(mp, '__version__', 'unknown'))
    print("Does mp have solutions?", hasattr(mp, 'solutions'))
    if not hasattr(mp, 'solutions'):
        import mediapipe.python.solutions  # type: ignore # noqa: F401
        print("Imported mediapipe.python.solutions directly")
except Exception:
    traceback.print_exc()

import importlib.util
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("symptoms_under_test", Path(__file__).parents[1] / "backend/services/symptom_service.py")
service = importlib.util.module_from_spec(spec)
spec.loader.exec_module(service)

class CleanupTests(unittest.TestCase):
    def run_transcription(self, fail_export=False, fail_recognition=False):
        class Segment:
            def export(self, path, format):
                Path(path).write_bytes(b"synthetic wav")
                if fail_export:
                    raise RuntimeError("conversion failed")
        class AudioFile:
            def __init__(self, path):
                self.path = path
            def __enter__(self):
                assert Path(self.path).exists()
                return self
            def __exit__(self, *args):
                pass
        class Recognizer:
            def record(self, source):
                return b"synthetic audio"
            def recognize_google(self, data):
                if fail_recognition:
                    raise RuntimeError("recognition failed")
                return "test transcription"
        mocks = {"speech_recognition": types.SimpleNamespace(Recognizer=Recognizer, AudioFile=AudioFile),
                 "pydub": types.SimpleNamespace(AudioSegment=types.SimpleNamespace(from_file=lambda path: Segment()))}
        with tempfile.TemporaryDirectory() as directory:
            original = tempfile.NamedTemporaryFile
            def temp_file(**kwargs):
                return original(dir=directory, **kwargs)
            with patch.dict(sys.modules, mocks), patch.object(service.tempfile, "NamedTemporaryFile", temp_file):
                result = service.transcribe_audio(b"synthetic", "clip.mp3")
            remaining = list(Path(directory).iterdir())
            self.assertEqual(remaining, [], "source and converted audio must both be removed")
            return result

    def test_conversion_success_cleans_both_files(self):
        self.assertEqual(self.run_transcription(), "test transcription")
    def test_recognition_failure_cleans_both_files(self):
        self.assertIn("Transcription unavailable", self.run_transcription(fail_recognition=True))
    def test_partial_export_failure_cleans_both_files(self):
        self.assertIn("Transcription unavailable", self.run_transcription(fail_export=True))

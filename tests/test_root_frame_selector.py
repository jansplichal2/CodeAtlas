import unittest
from atlas.stacktrace.parser import find_root_cause_frame

class TestRootFrameSelector(unittest.TestCase):
    def test_user_code_present(self):
        frames = [
            {"class": "lib.Foo", "method": "a", "file": "Foo.java", "line": 1, "is_user_code": False},
            {"class": "com.myorg.MyService", "method": "doStuff", "file": "MyService.java", "line": 42, "is_user_code": True},
            {"class": "lib.Bar", "method": "b", "file": "Bar.java", "line": 10, "is_user_code": False}
        ]
        result = find_root_cause_frame(frames)
        self.assertEqual(result["class"], "com.myorg.MyService")

    def test_no_user_code(self):
        frames = [
            {"class": "lib.Foo", "method": "a", "file": "Foo.java", "line": 1, "is_user_code": False},
            {"class": "lib.Bar", "method": "b", "file": "Bar.java", "line": 10, "is_user_code": False}
        ]
        result = find_root_cause_frame(frames)
        self.assertEqual(result["class"], "lib.Foo")

    def test_empty_frames(self):
        result = find_root_cause_frame([])
        self.assertIsNone(result)
import tempfile,unittest
from pathlib import Path
from sss_core import inspect,sha256
class CoreTests(unittest.TestCase):
 def test_hash(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"a.txt";p.write_text("hello",encoding="utf-8")
   self.assertEqual(sha256(p),"2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b982")
 def test_safe_text_low(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"plain.txt";p.write_text("ordinary notes",encoding="utf-8")
   self.assertEqual(inspect(p)["risk"],"Low")
 def test_script_review(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"demo.ps1";p.write_text("Write-Output 'hello'",encoding="utf-8")
   self.assertEqual(inspect(p)["risk"],"Review")
if __name__=="__main__":unittest.main()

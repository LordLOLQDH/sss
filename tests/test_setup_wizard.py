import os
os.environ.setdefault("QT_QPA_PLATFORM","offscreen")

import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from PySide6.QtWidgets import QApplication
from sss_main import FirstRunWizard

class FirstRunWizardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_private_defaults_need_no_school_server_or_ai(self):
        wizard = FirstRunWizard({})
        self.assertTrue(wizard.private_radio.isChecked())
        self.assertFalse(wizard.school_radio.isChecked())
        self.assertTrue(wizard.downloads_check.isChecked())
        self.assertTrue(wizard.desktop_check.isChecked())
        self.assertFalse(wizard.ai_check.isChecked())
        self.assertIn("Administratorrechte", wizard.intro.text())
        self.assertIn("ohne Schulserver", wizard.server_note.text())
        wizard.finish_setup()
        self.assertTrue(wizard.settings["setup_completed"])
        self.assertEqual(wizard.settings["profile"], "private")
        self.assertEqual(wizard.settings["scan_dirs"], [str(Path.home()/"Downloads"), str(Path.home()/"Desktop")])

    def test_school_and_ai_are_optional_choices(self):
        wizard = FirstRunWizard({})
        wizard.school_radio.setChecked(True)
        wizard.ai_check.setChecked(True)
        wizard.finish_setup()
        self.assertEqual(wizard.settings["profile"], "school")
        self.assertTrue(wizard.settings["ai_enabled"])
        self.assertIn("Schulserver", wizard.server_note.text())

if __name__ == "__main__":
    unittest.main()

"""Prevent derivative previews and changed source files from silently becoming references."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from import_voice import import_reference
from production_options import load_voices
from voice_studio import voice_reference
from voxcpm_voice import resolved_options, enhancement_fingerprint


class VoiceReferenceTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.audio = self.root / 'source.wav'
        self.text = self.root / 'source.txt'
        self.audio.write_bytes(b'original recording fixture')
        self.text.write_text('这是准确的原文。')
        self.personal = patch('voice_studio.PERSONAL_CATALOG', self.root/'personal/catalog.json')
        self.personal.start()

    def tearDown(self):
        self.personal.stop()
        self.temporary.cleanup()

    def test_packaged_derivative_is_unavailable_for_exact_source_voice(self):
        profile = next(item for item in load_voices(self.root) if item['id'] == 'bilibili-outro')
        self.assertFalse(profile['available'])
        with self.assertRaisesRegex(ValueError, 'Import'):
            voice_reference({'voice': 'bilibili-outro'}, self.root)

    def test_source_import_can_be_used_and_audio_changes_are_rejected(self):
        import_reference(self.root, 'bilibili-outro', '原片女声', self.audio, self.text, 'source_recording')
        audio, text = voice_reference({'voice': 'bilibili-outro'}, self.root)
        self.assertEqual(text, self.text.read_text())
        self.assertTrue(next(item for item in load_voices(self.root) if item['id'] == 'bilibili-outro')['available'])
        audio.write_bytes(b'replaced by generated preview')
        with self.assertRaisesRegex(ValueError, 'changed after import'):
            voice_reference({'voice': 'bilibili-outro'}, self.root)

    def test_synthetic_import_cannot_satisfy_an_original_reference(self):
        import_reference(self.root, 'bilibili-outro', '合成方向', self.audio, self.text, 'synthetic_direction')
        self.assertFalse(next(item for item in load_voices(self.root) if item['id'] == 'bilibili-outro')['available'])
        with self.assertRaisesRegex(ValueError, 'generated previews'):
            voice_reference({'voice': 'bilibili-outro'}, self.root)

    def test_transcript_changes_are_rejected(self):
        catalog = import_reference(self.root, 'custom', '自定义', self.audio, self.text)
        profile = json.loads(catalog.read_text())['voices'][0]
        Path(profile['reference_text']).write_text('不同的文本。')
        with self.assertRaisesRegex(ValueError, 'transcript changed'):
            voice_reference({'voice': 'custom'}, self.root)

    def test_personal_default_uses_source_recording_and_job_can_override_it(self):
        catalog = import_reference(self.root/'personal', 'bilibili-outro', '主力女声', self.audio, self.text, 'source_recording')
        personal = json.loads(catalog.read_text())
        personal['default'] = 'bilibili-outro'
        personal['voices'][0]['verified_generation_parameters'] = {'mode':'combined', 'cfg_value':1.5, 'timesteps':24}
        destination = self.root/'personal/catalog.json'
        destination.write_text(json.dumps(personal))
        reference, _ = voice_reference({}, self.root)
        self.assertEqual(reference, Path(personal['voices'][0]['reference_audio']))
        self.assertTrue(next(item for item in load_voices(self.root) if item['id']=='bilibili-outro')['preferred'])
        reference, _ = voice_reference({'voice':'iapetus'}, self.root)
        self.assertEqual(reference.name, 'iapetus.wav')
        self.assertEqual(resolved_options({}, self.root)['cfg_value'], 1.5)
        self.assertEqual(resolved_options({'cfg_value':1.7}, self.root)['cfg_value'], 1.7)

    def test_cleanup_model_is_local_and_model_change_invalidates_cache(self):
        self.assertIsNone(enhancement_fingerprint(None))
        with self.assertRaisesRegex(ValueError, 'installed local model'):
            enhancement_fingerprint(self.root/'missing')
        directory = self.root/'cleanup-model'
        directory.mkdir()
        weights = directory/'model.safetensors'
        weights.write_bytes(b'first fixture')
        original = enhancement_fingerprint(directory)
        weights.write_bytes(b'changed fixture')
        self.assertNotEqual(original, enhancement_fingerprint(directory))


if __name__ == '__main__':
    unittest.main()

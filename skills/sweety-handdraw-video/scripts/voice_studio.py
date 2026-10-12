#!/usr/bin/env python3
"""Required narration adapter for local VoiceStudio; no hidden remote fallback."""
from pathlib import Path
import argparse
import hashlib
import json
import urllib.parse
import requests

PACKAGE = Path(__file__).resolve().parents[1]


def voice_reference(options, root):
    if options.get('reference_audio'):
        if not options.get('reference_text'):
            raise ValueError('A custom voice requires its exact reference transcript')
        return root/options['reference_audio'],options['reference_text']
    directory=PACKAGE/'assets'/'voices'
    catalog=json.loads((directory/'catalog.json').read_text())
    identifier=options.get('voice',catalog['default'])
    profile=next((voice for voice in catalog['voices'] if voice['id']==identifier),None)
    if profile is None:
        raise ValueError('Unknown voice: '+identifier)
    return directory/profile['reference_audio'],(directory/profile['reference_text']).read_text().strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('job', type=Path)
    parser.add_argument('--url', help='Override voice_studio.url; local HTTP only')
    parser.add_argument('--transcribe', action='store_true', help='Save ASR evidence for existing or generated clips')
    arguments = parser.parse_args()
    root = arguments.job.resolve()
    manifest = json.loads((root / 'job.json').read_text())
    options = manifest.get('voice_studio', {})
    service_url = (arguments.url or options.get('url','http://127.0.0.1:3900')).rstrip('/')
    endpoint = urllib.parse.urlparse(service_url)
    if endpoint.scheme != 'http' or endpoint.hostname not in ('127.0.0.1', 'localhost', '::1') or endpoint.username or endpoint.password:
        raise ValueError('This adapter accepts only an unauthenticated local VoiceStudio service')
    reference_audio,reference_text = voice_reference(options,root)
    try:
        response=requests.get(service_url + '/engines/tts', timeout=10)
        response.raise_for_status()
        engine=response.json()
    except requests.RequestException as error:
        raise SystemExit('VoiceStudio 未安装、未启动或服务不可达：本任务没有旁白，不会交付无声视频冒充完整成片。请安装并启动 VoiceStudio，或在 VoiceStudio 编辑后导出旁白。') from error
    backend = options.get('backend', 'mlx-audio')
    expected_model = options.get('model', 'mlx-community/Qwen3-TTS-12Hz-1.7B-Base-bf16')
    if engine.get('active') != backend or engine.get('active_model') != expected_model:
        raise ValueError('VoiceStudio active engine/model differs from the configured voice; no global settings were changed')
    for page in manifest['pages']:
        for beat in page['beats']:
            target = (root / beat['audio']).resolve()
            if not target.is_relative_to(root):
                raise ValueError('Generated voice clips must stay inside the job directory')
            target.parent.mkdir(parents=True, exist_ok=True)
            fields = {'text': beat['text'], 'ref_text': reference_text, 'language': options.get('language', 'Chinese'),
                      'engine': backend, 'seed': str(options.get('seed', 2026)), 'speed': str(options.get('speed', 1.03)),
                      'effect_preset': options.get('effect_preset', 'broadcast'), 'max_chunk_chars': '0'}
            signature = hashlib.sha256(json.dumps({'fields': fields, 'model': expected_model}, sort_keys=True).encode() + reference_audio.read_bytes()).hexdigest()
            record_path = target.with_suffix('.voice.json')
            cached = target.is_file() and record_path.is_file() and json.loads(record_path.read_text()).get('signature') == signature
            if not cached:
                if target.exists() and not record_path.exists():
                    raise ValueError(f'Existing untracked audio will not be overwritten: {target}')
                print('GENERATING', beat.get('id', target.stem), flush=True)
                with reference_audio.open('rb') as reference:
                    response = requests.post(service_url + '/generate', data=fields,
                        files={'ref_audio': ('reference.wav', reference, 'audio/wav')}, timeout=600)
                response.raise_for_status()
                if not response.headers.get('Content-Type', '').startswith('audio/'):
                    raise ValueError('VoiceStudio did not return audio')
                temporary = target.with_suffix('.generating.wav')
                temporary.write_bytes(response.content)
                temporary.replace(target)
                record_path.write_text(json.dumps({'signature': signature, 'text': beat['text'], 'model': expected_model,
                    'duration': response.headers.get('X-Audio-Duration')}, ensure_ascii=False, indent=2))
            if arguments.transcribe:
                with target.open('rb') as audio_file:
                    response = requests.post(service_url + '/transcribe', files={'audio': (target.name, audio_file, 'audio/wav')},
                        data={'mode': 'reference', 'language': options.get('asr_language', 'zh')}, timeout=300)
                response.raise_for_status()
                target.with_suffix('.asr.json').write_text(json.dumps({'expected': beat['text'], 'response': response.json()}, ensure_ascii=False, indent=2))
            print('READY', beat.get('id', target.stem), flush=True)


if __name__ == '__main__':
    main()

"""Reject unreviewed image inputs or stale art-direction records before rendering."""
from pathlib import Path
import hashlib
import json

PACKAGE=Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def image_inputs(manifest, root):
    inputs=[(manifest['cover']['source'],None)]
    for page in manifest['pages']:
        actions=[action for beat in page['beats'] for action in beat.get('actions',[])]
        actions.extend(action for group in page.get('visual_groups',[]) for action in group['actions'])
        inputs.extend((action['source'],action.get('crop')) for action in actions if action['type']=='illustration')
    hand=manifest.get('hand',{})
    if hand.get('source'):
        inputs.append((hand['source'],None))
    return [(Path(path).expanduser().resolve() if Path(path).expanduser().is_absolute() else (root/path).resolve(),crop) for path,crop in inputs]


def check_record(record_path, required, dependency_hash):
    record_path=Path(record_path)
    record=json.loads(record_path.read_text())
    if record.get('dependency_sha256')!=dependency_hash:
        raise ValueError('Art-direction record does not match the bundled mandatory dependency')
    entries={Path(entry['source']).resolve() if Path(entry['source']).is_absolute() else (record_path.parent/entry['source']).resolve():entry for entry in record['images']}
    for source,crop in required:
        entry=entries.get(source)
        if not entry or entry.get('status')!='pass' or not entry.get('evidence'):
            raise ValueError('Image has no completed art-direction review: '+str(source))
        if entry.get('sha256')!=digest(source):
            raise ValueError('Image changed after art-direction review: '+str(source))
        if entry.get('method') not in ('generated_under_guidance','composed_with_verified_layers'):
            raise ValueError('Image lacks a supported guided-generation/composition method')
        regions=entry.get('approved_crops')
        if regions is not None and (crop is None or list(crop) not in regions):
            raise ValueError('This illustration crop was not approved: '+str(source))
        for field in ('brief_file','prompt_file'):
            if not entry.get(field) or not (record_path.parent/entry[field]).is_file():
                raise ValueError('Missing pre-generation art-direction evidence: '+field)
    return len(required)


def verify_art_direction(root, manifest):
    if manifest.get('runtime_fixture'):
        return {'fixture_only':True,'delivery_allowed':False}
    design_path=root/manifest.get('design_file','design.json')
    if not design_path.is_file():
        raise ValueError('A model-authored design.json is required before production')
    design=json.loads(design_path.read_text())
    route=design.get('narrative_route',{})
    if not route.get('decision') or not route.get('reason') or not route.get('director_review'):
        raise ValueError('Narrative route requires a model decision, reason and director review')
    if route['decision']!='default_life_concept' and not route.get('director_plan'):
        raise ValueError('A non-default narrative requires an omniailab director plan')
    dependency=PACKAGE/'dependencies/sweety-image-art-direction/GUIDE.md'
    if not dependency.is_file():
        raise ValueError('Mandatory sweety-image-art-direction dependency is missing')
    dependency_hash=digest(dependency)
    reference=manifest.get('art_direction',{}).get('record')
    if not reference:
        raise ValueError('All images require an art_direction.record before build')
    count=check_record(root/reference,image_inputs(manifest,root),dependency_hash)
    hand=manifest.get('hand',{})
    if not hand.get('source'):
        catalog=json.loads((PACKAGE/'assets/hands/catalog.json').read_text())
        identity=hand.get('preset',catalog['default'])
        profile=next((entry for entry in catalog['presets'] if entry['id']==identity),None)
        if profile is None:
            raise ValueError('Unknown hand preset: '+identity)
        count+=check_record(PACKAGE/'assets/hands/art-direction.json',[(PACKAGE/'assets/hands'/profile['source'],None)],dependency_hash)
    return {'dependency_sha256':dependency_hash,'reviewed_image_uses':count}

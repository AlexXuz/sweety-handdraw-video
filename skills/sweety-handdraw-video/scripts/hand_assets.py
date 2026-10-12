"""Resolve calibrated hand presets and fit an optional label to the pen barrel."""
from pathlib import Path
import json
import math
from PIL import Image, ImageDraw, ImageFont
import numpy as np

PACKAGE = Path(__file__).resolve().parents[1]


def prepare_hand(options, root, work, canvas_height, font_path, font_index):
    catalog = json.loads((PACKAGE/'assets/hands/catalog.json').read_text())
    identity = options.get('preset', catalog['default'])
    if options.get('source'):
        if 'nib' not in options:
            raise ValueError('A custom hand requires its measured nib coordinates')
        source = Path(options['source']).expanduser()
        source = source if source.is_absolute() else root/source
        calibration = options
    else:
        calibration = next((entry for entry in catalog['presets'] if entry['id']==identity), None)
        if calibration is None:
            raise ValueError('Unknown hand preset: '+identity)
        source = PACKAGE/'assets/hands'/calibration['source']
    hand = Image.open(source).convert('RGBA')
    nib = calibration['nib']
    if not (0<=nib[0]<hand.width and 0<=nib[1]<hand.height):
        raise ValueError('Nib coordinates lie outside hand asset')
    alpha = np.array(hand)[:,:,3]
    if (alpha[-1]>128).sum()<8:
        raise ValueError('The forearm must continue through the bottom edge of its source')
    # Even at the highest tip position, the cut edge must remain below the canvas.
    minimum_scale = (canvas_height+24)/max(1,hand.height-nib[1]-1)
    wrist=calibration.get('wrist')
    calibrated_scale=(canvas_height/1080*410/np.linalg.norm(np.array(wrist)-nib)) if wrist else canvas_height/1080*.66
    scale = max(float(options.get('scale',calibrated_scale)), minimum_scale)
    label = str(options.get('pen_text','')).strip()
    if label:
        if len(label)>20:
            raise ValueError('pen_text must be at most 20 characters; use a concise legible label')
        segment = calibration.get('label_segment')
        if not segment:
            raise ValueError('Custom pen text requires a calibrated exposed barrel segment')
        first, last = np.array(segment[0]),np.array(segment[1])
        length = np.linalg.norm(last-first)
        font = ImageFont.truetype(font_path, 28, index=font_index)
        bbox=font.getbbox(label)
        plate=Image.new('RGBA',(max(1,bbox[2]-bbox[0]+4),max(1,bbox[3]-bbox[1]+4)))
        ImageDraw.Draw(plate).text((2-bbox[0],2-bbox[1]),label,font=font,fill=options.get('pen_text_color',calibration.get('label_color','#EEE9D7')))
        ratio=min(length/plate.width,calibration.get('label_height',20)/plate.height)
        plate=plate.resize((max(1,round(plate.width*ratio)),max(1,round(plate.height*ratio))),Image.Resampling.LANCZOS)
        angle=-math.degrees(math.atan2(last[1]-first[1],last[0]-first[0]))
        plate=plate.rotate(angle,Image.Resampling.BICUBIC,expand=True)
        center=(first+last)/2
        hand.alpha_composite(plate,(round(center[0]-plate.width/2),round(center[1]-plate.height/2)))
        source=work/'branded-hand.png'
        hand.save(source)
    return {'preset':identity,'source':str(source.resolve()),'nib':nib,'scale':scale,'pen_text':label,
            'arm_bottom_at_highest_tip':(hand.height-nib[1])*scale-12}

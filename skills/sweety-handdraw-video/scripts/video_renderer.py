"""Render measured story timelines with path-based text, artwork and marker motion."""
from pathlib import Path
import bisect
import json
import math
import subprocess
import wave
import numpy as np
from PIL import Image, ImageColor


def ease(fraction):
    fraction=float(np.clip(fraction,0,1))
    return fraction*fraction*(3-2*fraction)


def point_on_asset(metadata,progress):
    previous = None
    for segment in metadata['segments']:
        if progress < segment['start']:
            if previous:
                fraction = ease((progress-previous['end'])/max(1e-7,segment['start']-previous['end']))
                origin=np.array(previous['points'][-1]); destination=np.array(segment['points'][0])
                return origin+fraction*(destination-origin)+[0,-10*math.sin(math.pi*fraction)]
            return np.array(segment['points'][0])
        if segment['start']<=progress<=segment['end']:
            fraction=(progress-segment['start'])/max(1e-7,segment['end']-segment['start'])
            points=np.array(segment['points'])
            if segment['kind']=='travel':
                return points[0]+ease(fraction)*(points[-1]-points[0])+[0,-10*math.sin(math.pi*fraction)]
            distances=np.array(segment['lengths'])
            target=fraction*distances[-1]
            return np.array([np.interp(target,distances,points[:,0]),np.interp(target,distances,points[:,1])])
        previous=segment
    if progress<metadata['segments'][0]['start']:
        return np.array(metadata['segments'][0]['points'][0])
    return np.array(metadata['segments'][-1]['points'][-1])


class Renderer:
    def __init__(self, job_directory):
        self.root=Path(job_directory).resolve()
        self.work=self.root/'work'
        self.output=self.root/'outputs'
        self.timeline=json.loads((self.work/'timeline.json').read_text())
        self.width=self.timeline['canvas']['width']
        self.height=self.timeline['canvas']['height']
        self.fps=self.timeline['canvas']['fps']
        self.paper=ImageColor.getrgb(self.timeline['paper'])+(255,)
        self.starts=[page['start'] for page in self.timeline['pages']]
        self.artwork={name:Image.open(self.work/'assets'/f'{name}.png').convert('RGBA') for name in self.timeline['assets']}
        self.pixels={name:np.array(image) for name,image in self.artwork.items()}
        self.maps={name:np.load(self.work/'assets'/f'{name}.npz') for name in self.timeline['assets']}
        self.cover=Image.open(self.output/'cover.png').convert('RGBA')
        hand=Image.open(self.timeline['hand']['source']).convert('RGBA')
        scale=self.timeline['hand']['scale']
        self.hand=hand.resize((round(hand.width*scale),round(hand.height*scale)),Image.Resampling.LANCZOS)
        self.nib=np.array(self.timeline['hand']['nib'])*scale

    def layer(self,event,time):
        name=event['asset']
        if time>=event['end']:
            return self.artwork[name]
        progress=np.clip((time-event['start'])/(event['end']-event['start']),0,1)
        maps=self.maps[name]
        pixels=self.pixels[name].copy()
        if 'ink' in maps:
            ink_fraction=np.clip((progress-maps['ink'])*250,0,1)
            color_fraction=np.clip((progress-maps['color'])*250,0,1)
            fraction=maps['ink_weight']*ink_fraction+(1-maps['ink_weight'])*color_fraction
        else:
            fraction=np.clip((progress-maps['reveal'])*250,0,1)
        pixels[:,:,3]=np.rint(pixels[:,:,3]*fraction).astype(np.uint8)
        return Image.fromarray(pixels)

    def event_tip(self,event,progress):
        metadata=self.timeline['assets'][event['asset']]
        return np.array([event['x'],event['y']])+point_on_asset(metadata,progress)

    def pen(self,page,time):
        events=sorted((event for event in page['events'] if not event['caption']),key=lambda event:event['start'])
        previous=None
        for event in events:
            if event['start']<=time<=event['end']:
                progress=(time-event['start'])/(event['end']-event['start'])
                return self.event_tip(event,progress)
            if time<event['start']:
                following=self.event_tip(event,0)
                if previous and event['start']-previous['end']<.25:
                    origin=self.event_tip(previous,1)
                    progress=ease((time-previous['end'])/(event['start']-previous['end']))
                    return origin+progress*(following-origin)+[0,-12*math.sin(math.pi*progress)]
                if previous and time<previous['end']+.22:
                    origin=self.event_tip(previous,1)
                    return origin+ease((time-previous['end'])/.22)*np.array([650,750])
                if event['start']-time<.16:
                    return following+(1-ease(1-(event['start']-time)/.16))*np.array([650,750])
                return None
            previous=event
        if previous and time<previous['end']+.22:
            return self.event_tip(previous,1)+ease((time-previous['end'])/.22)*np.array([650,750])
        return None

    def page_frame(self,index,time,include_hand=True,include_captions=True):
        page=self.timeline['pages'][index]
        frame=Image.new('RGBA',(self.width,self.height),self.paper)
        events=sorted(page['events'],key=lambda event:(event['z'],event['start']))
        for event in events:
            if event['caption']:
                continue
            if event['start']<=time<event['hide']:
                frame.alpha_composite(self.layer(event,time),(event['x'],event['y']))
        if include_hand:
            point=self.pen(page,time)
            if point is not None:
                frame.alpha_composite(self.hand,tuple(np.rint(point-self.nib).astype(int)))
        if include_captions:
            for event in events:
                if event['caption'] and event['start']<=time<event['hide']:
                    frame.alpha_composite(self.layer(event,time),(event['x'],event['y']))
        return frame

    def frame(self,time):
        if time<self.timeline['cover_seconds']:
            frame=self.cover.copy()
            if time>.5:
                canvas=Image.new('RGBA',(self.width,self.height),self.paper)
                frame=Image.blend(frame,canvas,(time-.5)/.5)
            return frame.convert('RGB')
        index=min(len(self.starts)-1,max(0,bisect.bisect_right(self.starts,time)-1))
        page=self.timeline['pages'][index]
        frame=self.page_frame(index,time)
        remaining=page['end']-time
        if remaining<.24 and index<len(self.starts)-1:
            offset=round(self.width*ease(1-remaining/.24))
            canvas=Image.new('RGBA',(self.width,self.height),self.paper)
            canvas.alpha_composite(frame,(-offset,0))
            frame=canvas
        return frame.convert('RGB')


def mix_audio(root,timeline):
    root=Path(root)/'work'
    with wave.open(str(root/'narration.wav'),'rb') as stream:
        rate=stream.getframerate()
        samples=np.frombuffer(stream.readframes(stream.getnframes()),dtype='<i2')
    music=np.zeros(len(samples),dtype=np.float32)
    chords=[(146.83,196.,246.94,293.66),(130.81,164.81,220.,261.63),(123.47,164.81,196.,246.94),(110.,146.83,196.,220.)]
    for beat in np.arange(0,timeline['duration'],1.45):
        chord=chords[int(beat/11.6)%len(chords)]
        frequency=chord[int(beat/1.45)%4]
        start=round(beat*rate)
        end=min(len(samples),start+round(3.6*rate))
        local=np.arange(end-start)/rate
        envelope=np.minimum(local/.025,1)*np.exp(-local/1.15)
        tone=np.sin(2*np.pi*frequency*local)+.18*np.sin(4*np.pi*frequency*local)
        music[start:end]+=.009*tone*envelope
    times=np.arange(len(samples))/rate
    music*=np.minimum(1,np.maximum(0,(timeline['duration']-times)/1.1))
    with wave.open(str(root/'music.wav'),'wb') as stream:
        stream.setparams((1,2,rate,0,'NONE','not compressed'))
        stream.writeframes((np.clip(music,-1,1)*32767).astype('<i2').tobytes())
    subprocess.run(['ffmpeg','-y','-v','error','-i',str(root/'narration.wav'),'-i',str(root/'music.wav'),'-filter_complex','[0:a]loudnorm=I=-17:TP=-2:LRA=7[v];[v][1:a]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.89:level=false[out]','-map','[out]','-ar','48000','-ac','2',str(root/'mix.wav')],check=True)


def encode(renderer,path,start=0.,duration=None):
    duration=renderer.timeline['duration']-start if duration is None else duration
    if start < 0 or duration <= 0 or start+duration > renderer.timeline['duration']+.001:
        raise ValueError('Preview interval must stay within the narration timeline')
    temporary_path=path.with_name(path.stem+'.rendering'+path.suffix)
    command=['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{renderer.width}x{renderer.height}','-r',str(renderer.fps),'-i','-','-ss',str(start),'-i',str(renderer.work/'mix.wav'),'-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-t',str(duration),'-movflags','+faststart','-map_metadata','-1',str(temporary_path)]
    process=subprocess.Popen(command,stdin=subprocess.PIPE)
    for index in range(math.ceil(duration*renderer.fps)):
        process.stdin.write(renderer.frame(start+index/renderer.fps).tobytes())
        if index%(15*renderer.fps)==0:
            print('RENDER',index/renderer.fps,'/',round(duration,2),flush=True)
    process.stdin.close()
    if process.wait()!=0:
        raise RuntimeError('ffmpeg failed to encode the video')
    temporary_path.replace(path)



def export_storyboard(renderer):
    review=renderer.work/'review'
    review.mkdir(parents=True,exist_ok=True)
    rows=math.ceil((len(renderer.timeline['pages'])+1)/2)
    sheet=Image.new('RGB',(1280,360*rows),renderer.paper[:3])
    frames=[renderer.cover.convert('RGB')]
    for page in renderer.timeline['pages']:
        frame=renderer.page_frame(page['index'],page['speech_end']-.15,False).convert('RGB')
        frame.save(review/f"page-{page['index']:02d}.jpg",quality=94)
        frames.append(frame)
    for index,frame in enumerate(frames):
        frame.thumbnail((640,360))
        sheet.paste(frame,((index%2)*640,(index//2)*360))
    sheet.save(review/'storyboard-contact.jpg',quality=95)


def render_job(job_directory,start=0.,duration=None,preview=False):
    from video_verifier import build_fingerprint, file_hash, verify_assets
    from art_direction import verify_art_direction
    renderer=Renderer(job_directory)
    verify_art_direction(renderer.root,json.loads((renderer.root/'job.json').read_text()))
    verify_assets(renderer.root,renderer.timeline)
    from timeline_contract import validate_timeline,validate_cover
    validate_timeline(renderer.timeline)
    validate_cover(renderer)
    export_storyboard(renderer)
    mix_audio(renderer.root,renderer.timeline)
    path=renderer.work/'review'/'preview.mp4' if preview else renderer.output/'film.mp4'
    if not preview and (start or duration is not None):
        raise ValueError('Use --preview for partial renders; delivery film must include the complete timeline')
    encode(renderer,path,start,duration)
    if not preview:
        record={'video_sha256':file_hash(path),'build_fingerprint':build_fingerprint(renderer.root)}
        (renderer.work/'render-record.json').write_text(json.dumps(record,indent=2))
    print(str(path))
    return path

import re as _re, io, asyncio, os, subprocess, tempfile

def clean_for_tts(text):
    """Strip markdown, citations, tables. Preserve sentence structure."""
    t = _re.sub(r'#{1,6}\s+', '', text)
    t = _re.sub(r'\*{1,2}([^*]+)\*{1,2}', r'\1', t)
    t = _re.sub(r'\([A-Z]{2,}[0-9]+[^)]*\)', '', t)
    t = _re.sub(r'\|[^\n]+', '', t)
    t = _re.sub(r'\n{2,}', '. ', t)
    t = _re.sub(r'\n', ' ', t)
    t = _re.sub(r'\s+', ' ', t).strip()
    words = t.split()
    if len(words) > 400:
        t = ' '.join(words[:400]) + '.'
    return t

def build_lincoln_ssml(text):
    """
    Wrap cleaned text in SSML for en-US-GuyNeural.
    Historical basis:
      rate -15%  → ~100wpm (Herndon: "talked slowly, never in a hurry")
      pitch +20Hz → tenor quality (Lamon, White, Villard: "clear ringing tenor")
      Pauses at em-dash/semicolon/sentence end → Lincoln's rhetorical cadence
    """
    t = text
    t = _re.sub(r'\s*—\s*', '<break time="500ms"/> ', t)
    t = _re.sub(r';\s*', ';<break time="350ms"/> ', t)
    t = _re.sub(r':\s+', ':<break time="300ms"/> ', t)
    t = _re.sub(r'\.\s+', '.<break time="500ms"/> ', t)
    t = _re.sub(r',\s+', ',<break time="180ms"/> ', t)
    # XML-escape bare ampersands only
    t = _re.sub(r'&(?!amp;|lt;|gt;|quot;)', '&amp;', t)
    return f'''<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis"
   xmlns:mstts="http://www.w3.org/2001/mstts" xml:lang="en-US">
  <voice name="en-US-GuyNeural">
    <mstts:express-as style="newscast-formal" styledegree="0.5">
      <prosody rate="-15%" pitch="+20Hz" volume="+5%">
        {t}
      </prosody>
    </mstts:express-as>
  </voice>
</speak>'''

async def _edge_tts_async(text):
    import edge_tts
    ssml = build_lincoln_ssml(clean_for_tts(text))
    buf  = io.BytesIO()
    communicate = edge_tts.Communicate(ssml, "en-US-GuyNeural")
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            buf.write(chunk["data"])
    data = buf.getvalue()
    if not data:
        raise RuntimeError("edge-tts returned empty audio")
    return data

def text_to_lincoln_mp3(text):
    """Generate MP3 via Microsoft Edge neural TTS; fall back to espeak-ng."""
    try:
        return asyncio.run(_edge_tts_async(text))
    except Exception as e:
        # espeak-ng fallback
        clean = clean_for_tts(text)
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as wf:
            wav_path = wf.name
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as mf:
            mp3_path = mf.name
        try:
            subprocess.run(['espeak-ng','-v','en-us','-p','38','-s','120',
                            '-g','9','-a','180', clean,'-w',wav_path],
                           check=True, capture_output=True)
            subprocess.run(['ffmpeg','-y','-i',wav_path,
                            '-codec:a','libmp3lame','-q:a','3', mp3_path],
                           check=True, capture_output=True)
            with open(mp3_path,'rb') as f:
                return f.read()
        finally:
            for p in [wav_path, mp3_path]:
                try: os.unlink(p)
                except: pass

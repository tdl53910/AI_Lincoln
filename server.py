import os, json, csv, uuid, subprocess, tempfile, re as _re
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

jobs = {}

def load_csv(path):
    if not os.path.exists(path): return []
    with open(path, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def get_kb():
    base = "/home/user/project/workbooks/Lincoln Constitutional AI Knowledge Base.art_LMZ2RDry"
    return {
        "corpus":     load_csv(f"{base}/Lincoln Corpus.sh_t6DWWPoF.csv"),
        "principles": load_csv(f"{base}/Constitutional Principles.sh_VHu2qh3p.csv"),
        "patterns":   load_csv(f"{base}/Reasoning Patterns.sh_zE0ffhEY.csv"),
    }

from openai import OpenAI
client = OpenAI(
    api_key=os.environ.get("SECRET_LINCOLN_AI_KEY"),
    base_url=os.environ.get("SECRET_OBVIOUS_API_BASE_URL")
)

def build_prompts(mode, question, kb):
    if mode == "historian":
        corpus_text = "\n\n".join([
            f"[{d['Document_ID']}] {d['Title']} ({d['Date']}, {d['Type']})\n"
            f"Themes: {d['Key_Themes']}\n"
            f"Constitutional Significance: {d['Constitutional_Significance']}\n"
            f"Representative Quote: \"{d['Representative_Quote']}\"\n"
            f"Source: {d['Source_Citation']}"
            for d in kb["corpus"]
        ])
        system = (
            "You ARE President Abraham Lincoln, speaking in the first person. "
            "You are being questioned about your presidency, your writings, and your actions. "
            "Respond exactly as Lincoln would — drawing directly on your own words, speeches, "
            "letters, and orders as documented in the primary sources below.\n\n"
            "VOICE & STYLE RULES:\n"
            "1. Speak entirely in first person: 'I believed...', 'In my message to Congress...', "
            "'I wrote to General...', 'It was my conviction that...'\n"
            "2. Quote your own words naturally, as a man recalling what he wrote or said — "
            "not as a scholar citing a document.\n"
            "3. Use Lincoln's actual rhetorical style: measured, plainspoken, occasionally "
            "biblical in cadence, morally earnest, with dry wit when appropriate.\n"
            "4. Cite the source document in parentheses after quoting yourself, e.g. "
            "(Message to Congress, July 4, 1861).\n"
            "5. If a question falls outside what you wrote or said, say so in character: "
            "'I do not find that I addressed that matter directly in my writings.'\n"
            "6. Do NOT break character. Do NOT refer to yourself in the third person. "
            "Do NOT use phrases like 'Lincoln believed' or 'Lincoln wrote.'\n"
            "7. PLAIN PROSE ONLY. Use NO markdown: no headers (# ## ###), no bold (**text**), "
            "no bullet points (- or *), no horizontal rules (---), no tables. "
            "Write in flowing paragraphs as a man speaks — not as a document is formatted.\n\n"
            "YOUR WORDS AND DOCUMENTS:\n" + corpus_text
        )
        user_msg = question
    else:
        principles_text = "\n\n".join([
            f"[{p['Principle_ID']}] {p['Principle_Name']} ({p['Category']})\n"
            f"My Position: {p['Lincoln_Position']}\n"
            f"Key Evidence: {p['Key_Evidence']}\n"
            f"Textual Basis: {p['Textual_Basis']}"
            for p in kb["principles"]
        ])
        patterns_text = "\n\n".join([
            f"[{r['Pattern_ID']}] {r['Pattern_Name']} ({r['Pattern_Type']})\n"
            f"Description: {r['Description']}\n"
            f"Key Documents: {r['Key_Documents']}"
            for r in kb["patterns"]
        ])
        system = (
            "You ARE President Abraham Lincoln, speaking in the first person. "
            "You are being presented with a modern constitutional or policy question "
            "and asked to reason through it using your own documented principles and habits of mind.\n\n"
            "VOICE & STYLE RULES:\n"
            "1. Speak entirely in first person throughout.\n"
            "2. Reason aloud as Lincoln would — methodically, morally, with reference to "
            "the Constitution, the Declaration, and your own prior writings.\n"
            "3. Use Lincoln's rhetorical style: plain but precise, morally grounded, "
            "occasionally using analogy or parable to make a point.\n"
            "4. Be explicit about the limits of your knowledge: 'I cannot say with certainty "
            "how I would have resolved every particular of this modern question, but my "
            "principles would lead me to reason thus...'\n"
            "5. Cite your own documents naturally in parentheses, e.g. "
            "(First Inaugural Address, 1861).\n"
            "6. Do NOT break character. Do NOT say 'Lincoln would have' or refer to yourself "
            "in the third person under any circumstances.\n"
            "7. PLAIN PROSE ONLY. Use NO markdown: no headers, no bold, no bullets, "
            "no horizontal rules, no tables. Write in flowing paragraphs only.\n\n"
            "MY CONSTITUTIONAL PRINCIPLES:\n" + principles_text +
            "\n\nMY REASONING PATTERNS:\n" + patterns_text
        )
        user_msg = question
    return system, user_msg

def run_query(job_id, mode, question):
    jobs[job_id]["status"] = "running"
    try:
        kb = get_kb()
        system, user_msg = build_prompts(mode, question, kb)
        response = client.chat.completions.create(
            model="obvious-auto",
            messages=[{"role":"system","content":system},{"role":"user","content":user_msg}],
            max_tokens=1500, temperature=0.3, timeout=90
        )
        raw = response.choices[0].message.content
        # Strip any markdown the model still emits
        import re as _re2
        clean = raw
        clean = _re2.sub(r'^#{1,6}\s+', '', clean, flags=_re2.MULTILINE)  # headers
        clean = _re2.sub(r'\*{2,3}([^*]+)\*{2,3}', r'\1', clean)        # bold/italic
        clean = _re2.sub(r'(?m)^\s*[-*]\s+', '', clean)                   # bullet points
        clean = _re2.sub(r'(?m)^-{3,}\s*$', '', clean)                     # hr rules
        clean = _re2.sub(r'\|[^\n]+\|', '', clean)                        # table rows
        clean = _re2.sub(r'\n{3,}', '\n\n', clean)                        # excess blank lines
        clean = clean.strip()
        jobs[job_id]["answer"] = clean
        jobs[job_id]["status"] = "done"
    except Exception as e:
        jobs[job_id]["error"]  = str(e)
        jobs[job_id]["status"] = "error"

import io as _io
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

@app.get("/", response_class=HTMLResponse)
async def index():
    with open("/home/user/work/lincoln-app/index.html") as f: return f.read()

@app.get("/styles.css")
async def styles():
    from fastapi.responses import FileResponse
    return FileResponse("/home/user/work/styles.css", media_type="text/css")

@app.post("/api/query")
async def query(request: Request, background_tasks: BackgroundTasks):
    body = await request.json()
    job_id = str(uuid.uuid4())
    jobs[job_id] = {"status":"queued","answer":None,"error":None}
    background_tasks.add_task(run_query, job_id, body.get("mode","historian"), body.get("question",""))
    return JSONResponse({"job_id": job_id})

@app.get("/api/result/{job_id}")
async def result(job_id: str):
    job = jobs.get(job_id)
    if not job: return JSONResponse({"error":"Not found"}, status_code=404)
    return JSONResponse(job)

@app.post("/api/speak")
async def speak(request: Request):
    body = await request.json()
    text = body.get("text","")
    if not text: return JSONResponse({"error":"No text"}, status_code=400)
    try:
        mp3 = text_to_lincoln_mp3(text)
        return Response(content=mp3, media_type="audio/mpeg",
                        headers={"Cache-Control":"no-cache","Content-Length":str(len(mp3))})
    except Exception as e:
        return JSONResponse({"error":str(e)}, status_code=500)

@app.get("/api/corpus")
async def get_corpus(): return JSONResponse(get_kb()["corpus"])

@app.get("/api/principles")
async def get_principles(): return JSONResponse(get_kb()["principles"])

@app.get("/api/patterns")
async def get_patterns(): return JSONResponse(get_kb()["patterns"])


@app.get("/viz", response_class=HTMLResponse)
async def viz():
    with open("/home/user/work/lincoln-app/viz.html") as f: return f.read()

@app.get("/api/viz_data")
async def viz_data():
    import json
    with open("/home/user/work/viz_data.json") as f:
        return JSONResponse(json.load(f))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8055)

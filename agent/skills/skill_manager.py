import os, json, shutil, zipfile, subprocess
from pathlib import Path

SKILLS_DIR = os.path.expanduser("~/whatsapp-video-agent/data/skills")
REGISTRY = os.path.join(SKILLS_DIR, "registry.json")
os.makedirs(SKILLS_DIR, exist_ok=True)

def _load_registry():
    if not os.path.exists(REGISTRY): return {}
    with open(REGISTRY) as f: return json.load(f)

def _save_registry(data):
    with open(REGISTRY, "w") as f: json.dump(data, f, indent=2)

def _read_skill_files(skill_dir):
    TEXT_EXT = {".md",".txt",".json",".py",".js",".ts",".jsx",".tsx",".yaml",".yml",".sh",".html",".css"}
    files = {}
    for root, dirs, filenames in os.walk(skill_dir):
        dirs[:] = [d for d in dirs if d not in {".git","node_modules","__pycache__"}]
        for fname in filenames:
            full = os.path.join(root, fname)
            rel = os.path.relpath(full, skill_dir)
            ext = Path(fname).suffix.lower()
            if ext in TEXT_EXT:
                try:
                    with open(full, encoding="utf-8", errors="ignore") as f:
                        files[rel] = f.read()
                except: files[rel] = "[unreadable]"
            else: files[rel] = f"[{ext} binary]"
    return files

def _analyze(skill_name, files):
    from agent.providers.groq import GroqProvider
    brain = GroqProvider()
    summary = ""
    for path, content in list(files.items())[:15]:
        summary += f"\n### {path}\n{content[:800]}\n"
    messages = [
        {"role":"system","content":"You are a skill analyzer. Return ONLY valid JSON."},
        {"role":"user","content":f"""Skill: {skill_name}\nFiles:\n{summary}\nReturn JSON:\n{{"description":"what this skill does","topics":["topic1"],"templates":["template1"],"visuals":["visual1"],"styles":["style1"],"video_types":["animated-explainer"],"complexity":"beginner","can_make":["video idea 1","video idea 2"]}}"""}
    ]
    response = brain.generate(messages)
    clean = response.replace("```json","").replace("```","").strip()
    try: return json.loads(clean)
    except: return {"description":"Skill loaded","topics":["general"],"templates":["default"],"visuals":["basic"],"styles":["minimal"],"video_types":["animated-explainer"],"complexity":"intermediate","can_make":["explainer video"]}

def install_from_github(url):
    name = url.rstrip("/").split("/")[-1].replace(".git","")
    skill_dir = os.path.join(SKILLS_DIR, name)
    print(f"📥 Downloading: {name}")
    if os.path.exists(skill_dir):
        subprocess.run(["git","-C",skill_dir,"pull"], capture_output=True)
    else:
        result = subprocess.run(["git","clone","--depth=1",url,skill_dir], capture_output=True, text=True)
        if result.returncode != 0: raise RuntimeError(f"Clone failed: {result.stderr}")
    print(f"📖 Reading files...")
    files = _read_skill_files(skill_dir)
    print(f"🧠 Analyzing {len(files)} files...")
    meta = _analyze(name, files)
    registry = _load_registry()
    registry[name] = {"name":name,"dir":skill_dir,"source":url,"files":list(files.keys()),"meta":meta}
    _save_registry(registry)
    return registry[name]

def install_from_zip(zip_path):
    name = Path(zip_path).stem
    skill_dir = os.path.join(SKILLS_DIR, name)
    os.makedirs(skill_dir, exist_ok=True)
    print(f"📦 Extracting: {name}")
    with zipfile.ZipFile(zip_path,'r') as z: z.extractall(skill_dir)
    print(f"📖 Reading files...")
    files = _read_skill_files(skill_dir)
    print(f"🧠 Analyzing {len(files)} files...")
    meta = _analyze(name, files)
    registry = _load_registry()
    registry[name] = {"name":name,"dir":skill_dir,"source":zip_path,"files":list(files.keys()),"meta":meta}
    _save_registry(registry)
    return registry[name]

def list_skills():
    return list(_load_registry().values())

def get_skill(name):
    reg = _load_registry()
    if name not in reg: raise ValueError(f"Skill '{name}' not found!")
    return reg[name]

def delete_skill(name):
    reg = _load_registry()
    if name not in reg: raise ValueError(f"Skill '{name}' nahi mili!")
    shutil.rmtree(reg[name]["dir"], ignore_errors=True)
    del reg[name]
    _save_registry(reg)

def get_options(skill_name, option_type):
    skill = get_skill(skill_name)
    return skill.get("meta",{}).get(option_type,[])

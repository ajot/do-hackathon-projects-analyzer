#!/usr/bin/env python3
"""Generates index.html by reading analysis_compact.json and applying analysis logic."""

import json, re
from pathlib import Path
from datetime import datetime, timezone

repos = json.loads(Path("analysis_compact.json").read_text())

HACKATHON_START = "2026-06-27"
HACKATHON_END   = "2026-06-28"

# Manual overrides: repo num -> partial dict to merge into auto-analysis
OVERRIDES = {
    1:  {"ucq":1,"uniq":1,"diff":1,"dod":1,"tldr":"Placeholder test submission.","notes":"Test entry — ignore."},
    2:  {"ucq":4,"uniq":4,"diff":4,"dod":1,"tldr":"Evolutionary tournament where AI agents compete on the same web task, learn from the winner via skill grafting, and get smarter every round.","notes":"Elegant RSI via SKILL.md patching. TypeScript. Strong entry for hackathon theme."},
    3:  {"ucq":3,"uniq":4,"diff":4,"dod":1,"tldr":"Recursive self-improving AI that fine-tunes its own weights from failures via LoRA.","notes":"Empty repo. Description sounds interesting."},
    4:  {"ucq":3,"uniq":4,"diff":3,"dod":1,"tldr":"Interactive 3D earthquake prediction simulator for the SF Bay Area with real seismic data and damage estimation, rendered entirely in-browser with Three.js.","notes":"Creative geo-relevant demo. Deployed on Google Cloud Run."},
    5:  {"ucq":4,"uniq":5,"diff":5,"dod":1,"tldr":"Self-improving PCB layout compiler: feed it a KiCad schematic and it autonomously places, routes, and scores a real board.","notes":"Empty repo but genuinely novel concept."},
    6:  {"ucq":3,"uniq":5,"diff":5,"dod":1,"tldr":"RL agent (GRPO + LoRA) that learns person-specific privacy attacks that bypass universal safety filters, recursively improving its own curriculum.","notes":"Empty repo. Interesting adversarial RSI angle."},
    7:  {"ucq":3,"uniq":3,"diff":4,"dod":1,"tldr":"Eight AI agents continuously analyze live Fed data, synthesized into a DeFi/crypto regime verdict backed by an ontology knowledge graph.","notes":"Anthropic API. Multi-agent ontology approach."},
    8:  {"ucq":2,"uniq":2,"diff":2,"dod":1,"tldr":"Uses golden summaries from Omnicon conversations to improve and benchmark conversation summarizers.","notes":"Empty repo. Description vague."},
    9:  {"ucq":4,"uniq":4,"diff":4,"dod":3,"tldr":"Training-free RSI via a 'lessons memory' — small model improves at BBH tasks with zero weight updates; DO Inference is the external lesson proposer.","sales":True,"sales_reason":"Actively calling DO Inference API as external LLM proposer. Real inference customer.","notes":"DO used for external proposals. Clean RSI loop. Solo."},
    10: {"ucq":4,"uniq":4,"diff":4,"dod":1,"tldr":"AI agent that teaches itself to operate NandGame (logic circuit browser game) by writing its own reusable skill library from real sessions — deletes skills and measures capability drop.","notes":"Compelling capability-regression proof. Gemini + browser-use."},
    11: {"ucq":4,"uniq":4,"diff":3,"dod":1,"tldr":"Turns domain experts into 'bonsai gardeners': they shape an ideal form once; the system watches a cited-answer agent and clusters failures by meaning.","notes":"Empty repo. Interesting human-guided RSI framing."},
    12: {"ucq":4,"uniq":4,"diff":4,"dod":1,"tldr":"Silent AI agent that fact-checks live meetings in real time across 70+ languages, matching spoken claims against a local database in 2ms.","notes":"Gemini 3.5 Live Translate + LiveKit. Strong real-world use case."},
    13: {"ucq":3,"uniq":4,"diff":4,"dod":1,"tldr":"Self-improving Dyna-Q world model combining Neo4j graph representation with the SIA loop, visualizing learned room market dynamics in real time.","notes":"DO mentioned as optional GPU host in runbook. SIA + GraphWorldModels combo."},
    14: {"ucq":4,"uniq":4,"diff":5,"dod":3,"tldr":"Auditable LoRA fine-tuning loop: MiniMax agent plans training, model trains on GPU, DigitalOcean serves the LLM judge (llama3.3-70b-instruct) to score results.","sales":True,"sales_reason":"3-person team using DO Inference as LLM judge. Claimed $200 DO credits onsite. Training loop is repeatable — ongoing inference spend likely.","notes":"Claimed DO credits at table. Auditable ML loop. 3-person team."},
    15: {"ucq":4,"uniq":4,"diff":4,"dod":1,"tldr":"Self-improving QA agent that learns a product via Gemini 3.5 Computer Use, then reviews PRs by visually testing the running app.","notes":"Gemini 3.5 Computer Use + Managed Agents + Playwright."},
    16: {"ucq":4,"uniq":4,"diff":4,"dod":1,"tldr":"Satellite land-cover classifier that improves from its own mistakes without retraining — a Gemini Strategist writes plain-English lessons from classification failures.","notes":"Well-built 3-person project. Real NASA/ESA satellite data."},
    17: {"ucq":4,"uniq":5,"diff":5,"dod":1,"tldr":"Continuous-learning memory separating durable beliefs (PEFT weight edits) from facts (RAG) and preferences (context), with hot-loading of weight edits live.","notes":"Tripartite memory architecture is genuinely novel. Hot-loading weight edits is ambitious."},
    18: {"ucq":5,"uniq":5,"diff":5,"dod":2,"tldr":"Robot manipulation agent that scans a scene into 3D Gaussian Splat, runs physics rollouts, and LoRA fine-tunes on DO H100 Droplets — zero new human labels.","sales":True,"sales_reason":"Using DO H100 GPU Droplets for robotics LoRA training. Serious compute workload if project continues.","notes":"Most ambitious project technically. 3DGS + sim-to-real + LoRA in 24h. 2-person team."},
    19: {"ucq":5,"uniq":4,"diff":4,"dod":1,"tldr":"Self-improving policy engine for ops teams: trains safe decision policies for billing, fraud, SLA exceptions without rigid scripts. Live at opsgym.pdt.dev.","notes":"Live demo. AI alignment for operational decisions is a real market."},
    20: {"ucq":4,"uniq":3,"diff":4,"dod":1,"tldr":"Fine-tunes company-specific customer support models with EffectTS REST API, MCP Server, and a custom AcmeBox Bench eval benchmark.","notes":"TypeScript monorepo. Custom eval bench is interesting."},
    21: {"ucq":4,"uniq":4,"diff":3,"dod":1,"tldr":"Chrome extension where a managed agent with persistent memory decides per-user whether to apply, reject, or adapt product UI changes — using X as a case study.","notes":"Gemini Antigravity Interactions API. Personalized UI adaptation is interesting."},
    22: {"ucq":4,"uniq":3,"diff":3,"dod":1,"tldr":"Chrome extension that captures lecture video/audio, sends frames to Gemini Computer Use, and builds a learner knowledge base that sharpens each session.","notes":"OKF learner model is the interesting persistent layer. Gemini Computer Use."},
    23: {"ucq":3,"uniq":4,"diff":5,"dod":1,"tldr":"RL curriculum where Vertex AI Gemini designs environments, writes MuJoCo reward functions, and extracts lessons — real PPO agents train in Stable-Baselines3.","notes":"Technically deep. World design + reward synthesis loop. Vertex AI, not DO."},
    24: {"ucq":5,"uniq":5,"diff":5,"dod":4,"tldr":"Autonomous pipeline finding a small model's UI-coding blind spots, curating them as training data, and LoRA fine-tuning on DO H100 GPUs. Deployed live on DO App Platform.","sales":True,"sales_reason":"Multi-service DO customer: App Platform (live deployment), H100 GPU Droplets (training), Inference (fallback). Highest priority DO prospect.","notes":"Strongest multi-service DO integration. Loss metric improving (6.17→5.68) in demo. 2-person team."},
    25: {"ucq":4,"uniq":4,"diff":5,"dod":1,"tldr":"Self-improving supply chain optimizer using modular execution graphs that evolve via selective breeding of successful subgraphs.","notes":"DO listed as one of several optional LLM providers. 3-person team."},
    26: {"ucq":4,"uniq":3,"diff":4,"dod":3,"tldr":"Self-improving SRE system using DO Inference as its primary LLM — detects incidents, proposes resolutions, and learns from outcomes.","sales":True,"sales_reason":"DO Inference hardcoded as primary in config.py. SRE = recurring inference usage for real operational workload.","notes":"config.py hardcodes DO endpoint. Clean integration. Solo."},
    27: {"ucq":4,"uniq":3,"diff":3,"dod":1,"tldr":"Drift detection and automated self-improvement for AI agents: detects accuracy degradation and makes agents recover from their own failures autonomously.","notes":"4-person team, empty repo. Concept is solid."},
    28: {"ucq":3,"uniq":4,"diff":4,"dod":1,"tldr":"Continual learning system over prediction markets using Gemma E4B with on-policy self-distillation and Exa search — learns from being wrong every hour.","notes":"Committed in final 10 minutes. 3-person team."},
    29: {"ucq":5,"uniq":5,"diff":5,"dod":3,"tldr":"AI geospatial screening platform for solar site selection producing GO/INVESTIGATE/KILL decisions from real NREL/PVGIS data. Deployed on DO App Platform; report artifacts stored in Spaces.","sales":True,"sales_reason":"DO App Platform + Spaces for production solar screening app. Real commercial use case with ongoing data storage. High priority.","notes":"Exceptional real-world problem — saves millions by killing bad sites early. Solo developer."},
    30: {"ucq":5,"uniq":4,"diff":4,"dod":1,"tldr":"Self-improving guardrails: Attack Agent discovers vulnerabilities in customer-facing AI, Defender learns patterns each round — producing stronger defenses without human input.","sales":True,"sales_reason":"Self-improving adversarial guardrails for production agents is a real enterprise security product. Worth tracking.","notes":"Important problem space. Solo developer."},
    31: {"ucq":4,"uniq":4,"diff":4,"dod":1,"tldr":"On-call agent for GPU datacenter clusters: responds to NVIDIA sensor failures and updates its own small ML prediction model from each incident.","notes":"4-person team, empty repo. GPU datacenter SRE is a real gap."},
    32: {"ucq":4,"uniq":4,"diff":4,"dod":2,"tldr":"Ambient pair programmer watching a shared LiveKit room, learning which interventions help, and nudging teams before merge conflicts or missed handoffs — hosted on DO Droplet.","sales":True,"sales_reason":"Live production app (podman.live) on DO Droplet. 4-person team. Real app = recurring cloud spend.","notes":"podman.live is live. Full stack on DO Droplet: app, API, workers, Caddy."},
    33: {"ucq":5,"uniq":5,"diff":5,"dod":1,"tldr":"Self-healing proxy that supervises running AI apps, auto-catches errors, has Gemini write a patch, runs through security scanner, and hot-swaps the fix if it passes.","sales":True,"sales_reason":"Self-healing proxy for production AI is a real enterprise need. DO Droplet for hosting — potential App Platform conversion.","notes":"Animated arch demo at omniforge-anim.vercel.app. 2-person team. Impressive concept."},
    34: {"ucq":3,"uniq":5,"diff":3,"dod":1,"tldr":"Multi-agent Pac-Man where ghost agents learn cooperative teamwork by rewriting their strategies in plain English via Reflexion — teamwork emerges without anyone coding it.","notes":"Creative interpretability demo. First commit was just a README (5-min window on June 27)."},
    35: {"ucq":4,"uniq":4,"diff":5,"dod":1,"tldr":"LLM-driven drone agent in AirSim simulator: natural language mission → flight task → Unreal execution, with live 3D Cesium San Francisco dashboard.","notes":"Gemma + Modal + MongoDB. C++ codebase. Ambitious."},
    36: {"ucq":5,"uniq":5,"diff":5,"dod":1,"tldr":"Vision agent swarm that maps legacy GUI software (Citrix EHRs, mainframes) into a shared world-model by consensus, then operates the app cheaply from the map.","sales":True,"sales_reason":"Computer use for legacy healthcare software is a massive enterprise market. DO token configured. Product team should follow up.","notes":"Excellent real-world problem. Citrix/mainframe computer use is genuinely underserved. Solo."},
    37: {"ucq":5,"uniq":4,"diff":4,"dod":1,"tldr":"Human-in-the-loop DICOM de-identification pipeline that recursively improves PHI detection accuracy, with a review UI for medical data anonymization.","sales":True,"sales_reason":"HIPAA-compliant medical PHI de-identification is a real compliance need. Product team should follow up for healthcare vertical.","notes":"Gemini for medical imaging. DICOM format. Niche but real market."},
    38: {"ucq":5,"uniq":4,"diff":5,"dod":1,"tldr":"Autonomous litigation engine running four Gemini Computer Use agents in parallel to draft a court-ready Motion for Summary Judgment in under 4 minutes.","sales":True,"sales_reason":"AI paralegal automating legal motions = high-value legal tech market. Real demo (4-min MSJ). Sales outreach worthwhile.","notes":"Adversarial Alpha/Beta drafting loop. React real-time dashboard. Solo."},
    39: {"ucq":4,"uniq":5,"diff":5,"dod":1,"tldr":"Guardrail system for browser-use trading agents that blocks audio prompt-injection attacks at the tool boundary before state changes occur.","notes":"4-person team. Novel attack vector (audio prompt injection for trading). Strong security angle."},
    40: {"ucq":3,"uniq":4,"diff":3,"dod":1,"tldr":"macOS desktop app for AI coding harnesses that runs a 'Sleep Cycle' scoring collaboration quality and turning daily friction into reviewable improvements.","notes":"2-person team. Interesting meta-health layer for AI harnesses."},
    41: {"ucq":4,"uniq":4,"diff":5,"dod":2,"tldr":"Autonomous SRE agents using bounded tree-search code synthesis on a live DOKS cluster — LLM proposes actions, synthesized verifier prunes unsafe branches.","sales":True,"sales_reason":"Using DOKS for SRE agent testing. K8s-native automation = enterprise infrastructure customer. 3-person team.","notes":"DeepMind-derived REx tree search. No fine-tuning. DOKS for live cluster tests."},
    42: {"ucq":4,"uniq":4,"diff":3,"dod":1,"tldr":"Environment-level evaluator that tests the harness around a model (system prompt, skill files, tools) rather than the model itself, auto-remediating what it finds.","notes":"3-person team. 'Model cards test the model — TEMPER tests everything around it.' Gemini track."},
    43: {"ucq":5,"uniq":4,"diff":4,"dod":1,"tldr":"Stack Overflow for the agentic era: passively monitors coding sessions, captures error/fix traces, and distills them into a public reusable debugging memory layer.","notes":"2-person team. Public debugging memory across Swift macOS + FastAPI. DO models mentioned in docs."},
    44: {"ucq":4,"uniq":4,"diff":3,"dod":3,"tldr":"Synthetic AI student swarm deployed on DO App Platform that tests tutoring effectiveness by simulating student sessions and scoring them with Gemini and MiniMax evaluators.","sales":True,"sales_reason":"Live production app at ferbai-fastapi-ingestor-ej6yt.ondigitalocean.app. Education AI on DO App Platform.","notes":"App is live and responding. Multiple real endpoints documented in README."},
    45: {"ucq":3,"uniq":3,"diff":3,"dod":1,"tldr":"Stock prediction system combining Chronos time-series models, news ingestion, and LLM reasoning for modular AI trading research with paper-trading focus.","notes":"Python. Solo. Financial prediction is a commodity space."},
    46: {"ucq":4,"uniq":5,"diff":5,"dod":3,"tldr":"AI that researches quant trading alphas using Gemini, kills weak signals, breeds strong ones, and compounds memory — DO Gradient Inference serves the MiniMax M2.5 reasoning proposer.","sales":True,"sales_reason":"DO Inference load-bearing for trading signal proposer. 3-person team with quantified results (+119% more profitable signals with memory).","notes":"Measurable improvement is compelling. DO Gradient Inference badge explicit in README. Antigravity integration too."},
    47: {"ucq":3,"uniq":4,"diff":3,"dod":1,"tldr":"Self-improving LLM-as-judge for pairwise QA that evaluates answers, then rewrites its own evaluation policy (SKILL.md) by reflecting on its mistakes.","notes":"Solo Python. Reflexion applied to the judge itself — interesting meta-eval concept."},
    48: {"ucq":3,"uniq":3,"diff":3,"dod":1,"tldr":"Training-free skill acquisition for Gemini 3.5 Flash Computer Use: watches failures, distills a reusable skill, retries, and keeps it only if a verified retry proves it works.","notes":"Clean methodology for verified skill retention. YouTube demo playlist."},
    49: {"ucq":4,"uniq":5,"diff":5,"dod":1,"tldr":"Gemini-powered self-learning loop for Autonomous Surface Vessel manufacturers: tests ships against real Navy mission briefs with persistent memory of component failures.","sales":True,"sales_reason":"ASV simulation + Navy mission testing = defense/maritime market. Niche but high-value. 4-person team.","notes":"Rust codebase. Interesting military/maritime angle. README just says 'wsg' — hard to evaluate."},
    50: {"ucq":4,"uniq":5,"diff":4,"dod":1,"tldr":"Chat interface that adapts in real time based on webcam iris tracking — a Reward Agent scores gaze zones and a Prompt Agent rebuilds the system prompt from your reading profile.","notes":"2-person team, empty repo. Very creative concept (eye-tracking adaptive UX)."},
    51: {"ucq":4,"uniq":3,"diff":4,"dod":1,"tldr":"Rigorous infrastructure for agent self-improvement: MCP trajectory recorder, skill versioning, and sandboxed evaluation to prevent overfitting and reward-hacking. Deployed on DO App Platform.","notes":"Solo. Experiment ledger + trajectory logging. DO App Platform for selfimprove.ai."},
    52: {"ucq":4,"uniq":3,"diff":3,"dod":1,"tldr":"Education marketplace where human tutoring sessions teach the AI tutor to improve — persistent memory accumulates better strategies across sessions without weight updates.","notes":"Solo. Interesting: human tutoring improves AI tutor. .do/app.yaml deployment configured."},
    53: {"ucq":4,"uniq":3,"diff":4,"dod":3,"tldr":"Recursive Autonomous Customer Experience system that solves underlying tickets rather than just answering them — backed by DigitalOcean Managed Postgres for persistence.","sales":True,"sales_reason":"DO Managed Postgres with actual integration code (db.ts, initDb.ts). 3-person team building CX platform. Recurring DB customer.","notes":"TypeScript monorepo. One team member owns DO integration. LiveKit voice. Real DB code."},
    54: {"ucq":4,"uniq":4,"diff":4,"dod":1,"tldr":"Gemini 3.5 Computer Use agent that compiles successful runs into reusable keyboard-first skills, then replays them deterministically with zero model calls.","notes":"4-person team. Verified replay without model in loop is the key insight. MongoDB for skill storage."},
    55: {"ucq":4,"uniq":5,"diff":4,"dod":3,"tldr":"GLSL shader artist agent where you steer with 1-5 ratings; it learns your visual taste over time via PLUS preference memory. DO Inference is the primary AI provider.","sales":True,"sales_reason":"DO Inference is primary provider in lib/ai.js with callDigitalOcean() function. Production-ready creative tool. Ongoing inference customer.","notes":"2-person team. callDigitalOcean() in production code. Port 8080. Beautiful continual preference learning."},
    56: {"ucq":5,"uniq":5,"diff":5,"dod":1,"tldr":"Trust layer for production web agents: Gemini 3.5 predicts screens, Gemma LoRA acts, a never-worse gate blocks regressions, and every action ships a tamper-evident signed receipt.","notes":"Technically very ambitious. 24 tests passing. First commit June 28 19:15 — final 15 minutes of hackathon."},
    57: {"ucq":4,"uniq":5,"diff":5,"dod":1,"tldr":"AI scientist that discovers the physics of an unknown 3D world through autonomous experiments, fitting models to evidence without any prior equations.","notes":"DO Inference configured as experimental option but Modal vLLM is primary. Fascinating concept."},
    58: {"ucq":4,"uniq":4,"diff":3,"dod":1,"tldr":"Music composition feedback tool that accumulates a per-composer profile across six dimensions (Harmony, Melody, Rhythm, Form, Orchestration) over sessions.","notes":"Solo. Anthropic API called from browser. Clean UI concept for creative feedback."},
    59: {"ucq":4,"uniq":3,"diff":3,"dod":1,"tldr":"Agentic coding manager that continuously improves to deliver high-quality PRs with minimum human input, coordinating GitHub, Linear, and Slack.","notes":"2-person team. PR automation is a well-trodden space."},
    60: {"ucq":4,"uniq":4,"diff":3,"dod":1,"tldr":"Self-improving auto-negotiator: lists your secondhand items, negotiates with buyers, and gets better at it from its own past negotiations via continual self-play — no human labeling.","notes":"3-person team, empty repo. Demo at gambit.nudepineapple.com/video. Good idea."},
    61: {"ucq":4,"uniq":4,"diff":4,"dod":1,"tldr":"Mission control cockpit for autonomous ML experiment loops — trajectory-centric interface with mode A (Kun drives) and mode B (researcher drives).","notes":"Solo Python. Interesting trajectory-centric research interface."},
    62: {"ucq":4,"uniq":4,"diff":4,"dod":2,"tldr":"Self-evolving multi-agent framework that synthesizes agents, builds adaptive workflows, and refines through experience — Qdrant + ClickHouse run on a live DO Droplet.","sales":True,"sales_reason":"Real DO Droplet (IP 147.182.239.133) running Qdrant + ClickHouse. Active infrastructure customer. Could convert to managed DO databases.","notes":"2-person team. Live demo video. Specific Droplet IP in README."},
    63: {"ucq":4,"uniq":4,"diff":3,"dod":1,"tldr":"QA agent for AI agent launches: reads Slack threads, uses Gemini Computer Use to test like a human QA tester, and generates a Slack-ready launch-readiness report.","notes":"Solo TypeScript. DO explicitly listed as 'out of scope for now' in README."},
    64: {"ucq":4,"uniq":4,"diff":3,"dod":1,"tldr":"Shared memory and self-evolving skills for agent teams — skills gain context without the method changing, backed by a repo-wide super memory store.","notes":"Solo Python. Skill body never changes, only context evolves. Backed by SkillsBench data. DO just an example in docs."},
    65: {"ucq":5,"uniq":4,"diff":4,"dod":1,"tldr":"Governance, context, and reputation layer for autonomous enterprise finance agents — earns broader autonomy as reputation improves across sessions.","sales":True,"sales_reason":"Enterprise agent governance for finance = real compliance/risk product. 3-person team. Worth following up.","notes":"FastAPI + Gemini/Antigravity. Reputation-gated autonomy is interesting trust model."},
    66: {"ucq":5,"uniq":4,"diff":4,"dod":1,"tldr":"Governance layer for agentic work that catches agent drift, enforces corrections as real operating state, and turns corrections into evals for the next pass.","sales":True,"sales_reason":"AI governance/drift detection for enterprise agents. Growing compliance need. TypeScript, 2-person team.","notes":"Well-positioned in enterprise governance space."},
    67: {"ucq":4,"uniq":3,"diff":3,"dod":1,"tldr":"End-to-end AI pipeline that transforms a character idea into a fully illustrated, publish-ready children's storybook using Google's agent pipeline and a three-skill architecture.","notes":"Solo Python. EPUB production pipeline. Last-minute submission (first commit June 28 18:48)."},
    68: {"ucq":5,"uniq":5,"diff":5,"dod":1,"tldr":"Language-controlled robotics platform connecting Gemini agents to physical robots (Booster K1 humanoid, SO-101 arm) via LiveKit WebRTC and YOLOv8 stereo depth.","notes":"DATE FLAGGED: First commit 2026-02-07 — project started 4 months before hackathon. Disqualify for integrity."},
    69: {"ucq":5,"uniq":4,"diff":5,"dod":1,"tldr":"Real-time multimodal lip-reading assistive communication tool for people with ALS, translating lip movements to speech as vocal ability progressively degrades.","notes":"Empty repo. The cause (ALS communication) is impactful if executed."},
}

SALES_OVERRIDES = {
    30: True, 33: True, 36: True, 37: True, 38: True, 41: True, 49: True, 65: True, 66: True
}

SALES_REASONS = {
    30: "Self-improving adversarial guardrails for production agents = enterprise security product. Worth tracking.",
    33: "Self-healing proxy for production AI is a real enterprise need. DO Droplet hosting — potential App Platform conversion.",
    36: "Computer use for legacy healthcare EHR/mainframe = massive enterprise market. DO token configured. Product team should follow up.",
    37: "HIPAA-compliant medical PHI de-identification is a real compliance need. Worth product follow-up for healthcare vertical.",
    38: "AI paralegal automating legal motions = high-value legal tech. Real demo (4-min MSJ). Sales outreach worthwhile.",
    41: "Using DOKS for SRE agent testing. K8s-native automation = enterprise infrastructure customer. 3-person team.",
    49: "ASV simulation + Navy mission testing = defense/maritime market. Niche but high-value. 4-person team.",
    65: "Enterprise agent governance for finance = real compliance/risk product. 3-person team.",
    66: "AI governance/drift detection for enterprise agents. Growing compliance need. TypeScript, 2-person team.",
}

def detect_do(signals, description, partner_tech):
    services = []
    text = " ".join(signals + [description, partner_tech]).lower()
    sig_text = " ".join(signals).lower()

    if any(x in sig_text for x in ["inference.do-ai.run", "digital_ocean_model_access_key", "digitalocean_model_access_key", "digitalocean inference", "do genai", "api.digitalocean.com/v2/gen-ai"]):
        evidence = next((s for s in signals if any(x in s.lower() for x in ["inference.do-ai.run","model_access_key","v2/gen-ai"])), "DO Inference API configured")
        services.append(("Inference", evidence[:100]))
    if "digitaloceanspaces.com" in text or "do_spaces" in text:
        evidence = next((s for s in signals if "spaces" in s.lower()), "DO Spaces configured")
        services.append(("Spaces", evidence[:100]))
    if "ondigitalocean.app" in text or ("app.yaml" in text and "digitalocean" in text) or ("digitalocean app platform" in text):
        evidence = next((s for s in signals if "ondigitalocean.app" in s.lower() or "app platform" in s.lower()), "DO App Platform deployment")
        services.append(("App Platform", evidence[:100]))
    if "db.ondigitalocean.com" in text or ("digitalocean" in text and ("postgres" in text or "database" in text or "db.ts" in text)):
        evidence = next((s for s in signals if "postgres" in s.lower() or "db" in s.lower()), "DO Managed DB")
        services.append(("Managed DB", evidence[:100]))
    if "doks" in text or ("digitalocean kubernetes" in text):
        evidence = next((s for s in signals if "doks" in s.lower() or "kubernetes" in s.lower()), "DOKS referenced")
        services.append(("Kubernetes", evidence[:100]))
    if any(x in sig_text for x in ["digitalocean droplet", "do droplet", "h100 gpu droplet", "digitalocean h100"]):
        evidence = next((s for s in signals if "droplet" in s.lower()), "DO Droplet referenced")
        services.append(("Droplets", evidence[:100]))
    elif any(x in sig_text for x in ["digitalocean_token", "digitalocean_api_key", "digital_ocean_api_key"]) and not services:
        evidence = next((s for s in signals if "token" in s.lower() or "api_key" in s.lower()), "DO API token configured")
        services.append(("General DO", evidence[:100]))
    # Partial: mentioned in README/description without code
    if not services:
        combined = " ".join(signals + [description]).lower()
        if "digitalocean" in combined or "do droplet" in combined:
            # find evidence
            ev = next((s for s in signals if "digitalocean" in s.lower()), "DO mentioned")
            if "droplet" in ev.lower():
                services.append(("Droplets", ev[:100]))
            elif "inference" in ev.lower():
                services.append(("Inference", ev[:100]))
            else:
                services.append(("General DO", ev[:100]))
    return services

def determine_legitimacy(services, signals):
    if not services:
        return "Superficial", "No DO signals found."
    sig_text = " ".join(signals).lower()
    strong_patterns = ["inference.do-ai.run", "digital_ocean_model_access_key", "ondigitalocean.app", "digitaloceanspaces.com",
                       "db.ondigitalocean.com", "db.ts", "digitalocean postgres", "calldigitalocean", "do_base_url"]
    if any(p in sig_text for p in strong_patterns):
        return "Strong", "DO APIs or SDK called in actual source code or configs."
    return "Partial", "DO mentioned in README/description/partner_technologies but no direct API call found."

def flag_date(first_commit):
    if not first_commit:
        return False
    d = first_commit[:10]
    return not (HACKATHON_START <= d <= HACKATHON_END)

def score_color(s):
    return f"s{s}"

def fmt_date(dt):
    if not dt:
        return '<span class="date-unknown">—</span>'
    d = dt[:10]
    flagged = not (HACKATHON_START <= d <= HACKATHON_END)
    cls = "date-flag" if flagged else "date-ok"
    return f'<span class="{cls}">{d}</span>'

def badge_class(service):
    m = {"Inference":"badge-inference","AI Routing":"badge-routing","Spaces":"badge-spaces",
         "App Platform":"badge-appplatform","Managed DB":"badge-database","Kubernetes":"badge-droplet",
         "Droplets":"badge-droplet","General DO":"badge-appplatform"}
    return m.get(service, "badge-appplatform")

def make_row(r):
    num = r.get("num") or ""
    name = r.get("name") or r.get("owner_repo","").split("/")[-1]
    owner_repo = r.get("owner_repo","")
    url = r.get("url","")
    demo = r.get("demo_url")
    members = r.get("members",1)
    partner = r.get("partner_technologies","") or ""
    description = r.get("description","") or ""
    signals = r.get("do_signal_lines",[])
    fc = r.get("first_commit")
    lc = r.get("last_commit")

    ov = OVERRIDES.get(num, {})
    tldr = ov.get("tldr", description[:200])
    ucq  = ov.get("ucq", 3)
    uniq = ov.get("uniq", 3)
    diff = ov.get("diff", 3)
    dod  = ov.get("dod", 1)
    notes = ov.get("notes","")
    sales = ov.get("sales", SALES_OVERRIDES.get(num, False))
    sales_reason = ov.get("sales_reason", SALES_REASONS.get(num,""))

    do_services = detect_do(signals, description, partner)
    leg, leg_reason = determine_legitimacy(do_services, signals)
    dod_auto = min(len(do_services) + 1, 5) if do_services else 1
    if dod == 1 and do_services:
        dod = dod_auto

    is_flagged = flag_date(fc)
    is_verified = leg in ("Strong","Partial")

    row_cls = "flagged-date" if is_flagged else ""
    data_attrs = f'data-num="{num}" data-name="{name.lower()}" data-tldr="{tldr[:80].lower()}" data-notes="{notes.lower()}" data-sales="{str(sales).lower()}" data-flagged="{str(is_flagged).lower()}" data-verified="{str(is_verified).lower()}"'

    # Project cell
    demo_html = f'<div class="demo-link"><a href="{demo}" target="_blank">Demo</a></div>' if demo else ""
    proj_html = f'<td class="project-cell"><a href="{url}" target="_blank">{name}</a><div class="repo-path">{owner_repo}</div>{demo_html}</td>'

    # DO badges
    if do_services:
        badges = "".join(f'<span class="badge {badge_class(s)}" title="{ev}">{s}</span>' for s,ev in do_services)
    else:
        badges = '<span class="badge-none badge">None</span>'

    # Legitimacy
    leg_cls = {"Strong":"leg-strong","Partial":"leg-partial","Superficial":"leg-superficial"}[leg]
    leg_html = f'<span class="leg {leg_cls}" title="{leg_reason}">{leg}</span>'

    # Scores
    def sc(v): return f'<td class="score {score_color(v)}">{v}</td>'

    # Sales
    if sales:
        sales_html = f'<span class="sales-yes" title="{sales_reason}">Yes</span>'
    else:
        sales_html = '<span class="sales-no">—</span>'

    return f'''    <tr class="{row_cls}" {data_attrs}>
      <td class="num-cell">{num}</td>
      {proj_html}
      <td class="members-cell">{members}</td>
      <td class="tldr-cell">{tldr}</td>
      <td class="tech-cell">{partner}</td>
      <td>{badges}</td>
      <td>{leg_html}</td>
      {sc(ucq)}{sc(uniq)}{sc(diff)}{sc(dod)}
      <td>{sales_html}</td>
      <td>{fmt_date(fc)}</td>
      <td class="notes-cell">{notes}</td>
    </tr>'''

rows_html = "\n".join(make_row(r) for r in repos)

# Stats
total = len(repos)
do_strong = sum(1 for r in repos if determine_legitimacy(detect_do(r.get("do_signal_lines",[]),r.get("description",""),r.get("partner_technologies","")), r.get("do_signal_lines",[]))[0] == "Strong")
do_any    = sum(1 for r in repos if determine_legitimacy(detect_do(r.get("do_signal_lines",[]),r.get("description",""),r.get("partner_technologies","")), r.get("do_signal_lines",[]))[0] in ("Strong","Partial"))
sales_ct  = sum(1 for r in repos if OVERRIDES.get(r.get("num"),{}).get("sales", SALES_OVERRIDES.get(r.get("num"),False)))
flagged_ct= sum(1 for r in repos if flag_date(r.get("first_commit")))
gen_ts    = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

CSS = """*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Inter', 'Segoe UI', sans-serif;
  background: #f1f5f9; color: #0f172a; font-size: 14px;
  border-top: 3px solid #0069ff;
}
header {
  background: white; padding: 16px 28px;
  display: flex; align-items: center; justify-content: space-between;
  border-bottom: 1px solid #e2e8f0;
}
.header-left { display: flex; align-items: center; gap: 12px; }
.do-mark {
  width: 34px; height: 34px; background: #0069ff; border-radius: 7px;
  display: flex; align-items: center; justify-content: center;
  color: white; font-weight: 700; font-size: 12px; flex-shrink: 0;
}
header h1 { font-size: 15px; font-weight: 600; color: #0f172a; }
header p { font-size: 11px; color: #94a3b8; margin-top: 2px; }
.stats { display: flex; gap: 6px; }
.chip { padding: 4px 11px; border-radius: 20px; font-size: 11px; font-weight: 500; border: 1px solid #e2e8f0; background: #f8fafc; color: #64748b; }
.chip-blue  { background: #eff6ff; color: #1d4ed8; border-color: #bfdbfe; }
.chip-green { background: #f0fdf4; color: #166534; border-color: #bbf7d0; }
.chip-amber { background: #fffbeb; color: #92400e; border-color: #fde68a; }
.chip-red   { background: #fef2f2; color: #991b1b; border-color: #fecaca; }
.toolbar { padding: 10px 28px; background: white; border-bottom: 1px solid #e2e8f0; display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
.toolbar input { padding: 6px 11px; border: 1px solid #e2e8f0; border-radius: 6px; font-size: 13px; width: 250px; outline: none; background: #f8fafc; color: #0f172a; }
.toolbar input:focus { border-color: #0069ff; background: white; box-shadow: 0 0 0 3px rgba(0,105,255,0.1); }
.filters { display: flex; gap: 6px; }
.filter-btn { padding: 5px 13px; border-radius: 20px; border: 1px solid #e2e8f0; background: white; cursor: pointer; font-size: 12px; color: #64748b; transition: all 0.12s; font-weight: 500; }
.filter-btn:hover { border-color: #0069ff; color: #0069ff; }
.filter-btn.active { background: #0069ff; color: white; border-color: #0069ff; }
.count { margin-left: auto; color: #94a3b8; font-size: 12px; }
.table-wrap { padding: 20px 28px 48px; overflow-x: auto; }
table { width: 100%; border-collapse: collapse; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.07); min-width: 1400px; }
thead tr { background: #0f172a; }
th { padding: 10px 14px; text-align: left; font-weight: 500; font-size: 10px; white-space: nowrap; cursor: pointer; user-select: none; position: sticky; top: 0; background: #0f172a; color: #64748b; text-transform: uppercase; letter-spacing: 0.06em; z-index: 10; }
th:hover { background: #1e293b; color: #cbd5e1; }
th.no-sort { cursor: default; }
th.no-sort:hover { background: #0f172a; color: #64748b; }
.sort-icon { margin-left: 3px; opacity: 0.5; font-style: normal; }
td { padding: 10px 14px; border-bottom: 1px solid #f1f5f9; vertical-align: top; color: #334155; }
tr:last-child td { border-bottom: none; }
tr:hover td { background: #f8fafc; }
tr.flagged-date td { background: #fff5f5; }
tr.flagged-date td:first-child { border-left: 3px solid #fca5a5; padding-left: 11px; }
tr.flagged-date:hover td { background: #fef2f2; }
tr.hidden { display: none !important; }
a { color: #0069ff; text-decoration: none; font-weight: 500; }
a:hover { text-decoration: underline; }
.badge { display: inline-block; padding: 2px 7px; border-radius: 4px; color: white; font-size: 10px; font-weight: 600; margin: 1px 2px 1px 0; cursor: help; letter-spacing: 0.01em; }
.badge-inference   { background: #0069ff; }
.badge-routing     { background: #6e3fff; }
.badge-spaces      { background: #00b4d8; }
.badge-appplatform { background: #0096c7; }
.badge-database    { background: #0077b6; }
.badge-droplet     { background: #023e8a; }
.badge-functions   { background: #48cae4; color: #0f172a; }
.badge-none { background: #f1f5f9; color: #94a3b8; cursor: default; border: 1px solid #e2e8f0; }
.leg { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; }
.leg-strong      { background: #dcfce7; color: #15803d; }
.leg-partial     { background: #fef3c7; color: #b45309; }
.leg-superficial { background: #fee2e2; color: #b91c1c; }
.score    { text-align: center; font-weight: 700; font-size: 13px; }
.s5 { color: #15803d; }
.s4 { color: #16a34a; }
.s3 { color: #d97706; }
.s2 { color: #ea580c; }
.s1 { color: #dc2626; }
.sales-yes { display: inline-block; background: #dcfce7; color: #15803d; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; cursor: help; }
.sales-no { color: #cbd5e1; font-size: 12px; }
.date-flag    { color: #ef4444; font-weight: 600; font-size: 11px; }
.date-ok      { color: #10b981; font-size: 11px; }
.date-unknown { color: #cbd5e1; font-size: 11px; }
.project-cell { min-width: 140px; }
.project-cell .repo-path { color: #94a3b8; font-size: 10px; margin-top: 2px; }
.project-cell .demo-link { font-size: 10px; margin-top: 3px; }
.num-cell     { color: #94a3b8; font-size: 11px; text-align: center; width: 32px; }
.tech-cell    { font-size: 10px; color: #64748b; max-width: 120px; line-height: 1.5; }
.tldr-cell    { max-width: 220px; font-size: 12px; line-height: 1.5; color: #475569; }
.notes-cell   { max-width: 180px; font-size: 11px; color: #94a3b8; line-height: 1.5; }
.members-cell { text-align: center; font-size: 12px; color: #64748b; }
.no-results   { text-align: center; padding: 56px; color: #94a3b8; font-size: 14px; }"""

JS = """
let currentFilter = 'all';
let sortCol = -1, sortAsc = true;

function applyFilters() {
  const q = document.getElementById('search').value.toLowerCase();
  const rows = document.querySelectorAll('#tbody tr');
  let visible = 0;
  rows.forEach(r => {
    const name  = r.dataset.name  || '';
    const tldr  = r.dataset.tldr  || '';
    const notes = r.dataset.notes || '';
    const matchSearch = !q || name.includes(q) || tldr.includes(q) || notes.includes(q);
    const matchFilter =
      currentFilter === 'all'      ? true :
      currentFilter === 'verified' ? r.dataset.verified === 'true' :
      currentFilter === 'flagged'  ? r.dataset.flagged  === 'true' :
      currentFilter === 'sales'    ? r.dataset.sales    === 'true' : true;
    const show = matchSearch && matchFilter;
    r.classList.toggle('hidden', !show);
    if (show) visible++;
  });
  document.getElementById('count').textContent = visible + ' project' + (visible !== 1 ? 's' : '');
}

function setFilter(btn, f) {
  currentFilter = f;
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  applyFilters();
}

function sortTable(col) {
  if (sortCol === col) sortAsc = !sortAsc;
  else { sortCol = col; sortAsc = true; }
  document.querySelectorAll('.sort-icon').forEach((el,i) => {
    el.innerHTML = i === col ? (sortAsc ? '&#8593;' : '&#8595;') : '&#8597;';
  });
  const tbody = document.getElementById('tbody');
  const rows = Array.from(tbody.querySelectorAll('tr'));
  rows.sort((a, b) => {
    const av = a.cells[col]?.innerText.trim() || '';
    const bv = b.cells[col]?.innerText.trim() || '';
    const an = parseFloat(av), bn = parseFloat(bv);
    const cmp = (!isNaN(an) && !isNaN(bn)) ? an - bn : av.localeCompare(bv);
    return sortAsc ? cmp : -cmp;
  });
  rows.forEach(r => tbody.appendChild(r));
}
"""

HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AIE Hackathon 2026 - Project Analysis</title>
<style>{CSS}</style>
</head>
<body>
<header>
  <div class="header-left">
    <div class="do-mark">DO</div>
    <div>
      <h1>AIE Hackathon 2026 &middot; Project Analysis</h1>
      <p>June 27&ndash;28, 2026 &nbsp;&middot;&nbsp; Generated {gen_ts} &nbsp;&middot;&nbsp; Internal use only</p>
    </div>
  </div>
  <div class="stats">
    <span class="chip">{total} projects</span>
    <span class="chip chip-blue">{do_strong} DO strong</span>
    <span class="chip chip-green">{do_any} DO detected</span>
    <span class="chip chip-amber">{sales_ct} sales flags</span>
    <span class="chip chip-red">{flagged_ct} date flagged</span>
  </div>
</header>
<div class="toolbar">
  <input type="text" id="search" placeholder="Search projects, TLDRs, notes..." oninput="applyFilters()">
  <div class="filters">
    <button class="filter-btn active" onclick="setFilter(this,'all')">All</button>
    <button class="filter-btn" onclick="setFilter(this,'verified')">DO Detected</button>
    <button class="filter-btn" onclick="setFilter(this,'flagged')">Date Flagged</button>
    <button class="filter-btn" onclick="setFilter(this,'sales')">Sales Flag</button>
  </div>
  <span class="count" id="count">{total} projects</span>
</div>
<div class="table-wrap">
<table id="report-table">
  <thead>
    <tr>
      <th onclick="sortTable(0)"># <i class="sort-icon" id="si-0">&#8597;</i></th>
      <th onclick="sortTable(1)">Project <i class="sort-icon" id="si-1">&#8597;</i></th>
      <th onclick="sortTable(2)">Team <i class="sort-icon" id="si-2">&#8597;</i></th>
      <th class="no-sort">TLDR</th>
      <th class="no-sort">Partner Tech</th>
      <th class="no-sort">DO Services</th>
      <th onclick="sortTable(6)">Legitimacy <i class="sort-icon" id="si-6">&#8597;</i></th>
      <th onclick="sortTable(7)">Use Case <i class="sort-icon" id="si-7">&#8597;</i></th>
      <th onclick="sortTable(8)">Unique <i class="sort-icon" id="si-8">&#8597;</i></th>
      <th onclick="sortTable(9)">Difficulty <i class="sort-icon" id="si-9">&#8597;</i></th>
      <th onclick="sortTable(10)">DO Depth <i class="sort-icon" id="si-10">&#8597;</i></th>
      <th onclick="sortTable(11)">Sales <i class="sort-icon" id="si-11">&#8597;</i></th>
      <th onclick="sortTable(12)">First Commit <i class="sort-icon" id="si-12">&#8597;</i></th>
      <th class="no-sort">Notes</th>
    </tr>
  </thead>
  <tbody id="tbody">
{rows_html}
  </tbody>
</table>
<div class="no-results" id="no-results" style="display:none">No projects match your filters.</div>
</div>
<script>{JS}</script>
</body>
</html>"""

Path("index.html").write_text(HTML)
print(f"Written index.html")
print(f"  {total} projects | {do_strong} DO strong | {do_any} DO detected | {sales_ct} sales flags | {flagged_ct} date flagged")

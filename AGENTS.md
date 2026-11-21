# AGENTS.md

Canonical agent instructions for this repo. Read by opencode (DeepSeek V4, MiniMax M3, Kimi K2.7, etc.), Claude Code (via `CLAUDE.md` import), and any other agent runner. Keep this file stable — see "Cache discipline" at the bottom.

## Project

Static React site presenting the FYDP research proposal **"Trust-Calibrated Multi-Agent Scientific Deliberation for Mitigating Sycophantic Consensus in LLM Reasoning"** (Group 6 · Team Phantom Devs).

Core thesis: in multi-agent LLM debate, a confidently wrong majority can pressure a correct minority agent into abandoning its answer (sycophantic collapse). The proposal re-weights each agent's influence *during* the debate using an evidence-grounded trust score derived from retrieved external evidence, not a majority vote. This repo holds both the presentation site (`frontend/`) and the P0 implementation of the mechanism (`trustcal/`, Python + vLLM) — the pipeline has its own agent file: `trustcal/AGENTS.md`.

## Tech stack

- React 19 + TypeScript + Vite 8
- Tailwind CSS 4 (via `@tailwindcss/vite`, not a PostCSS config)
- React Router 7
- `@xyflow/react` for architecture/pipeline diagrams
- `lucide-react` for icons
- Oxlint for linting
- Puppeteer for post-build static prerendering

## Commands

| Command | Purpose |
| --- | --- |
| `npm install` (in `frontend/`) | Install deps |
| `npm run dev` (in `frontend/`) | Vite dev server with HMR |
| `npm run build` (in `frontend/`) | `tsc -b` typecheck → `vite build` → prerender all routes |
| `npm run preview` (in `frontend/`) | Serve the production build |
| `npm run lint` (in `frontend/`) | Oxlint |

All app commands run from the `frontend/` directory — that's the Vercel root. Always run `npm run build` after changing `.tsx`/`.ts` — it typechecks *and* prerenders, so it is the single source of truth for "did I break it". There is no test runner configured; do not invent one unless asked. The Python research pipeline is separate: its commands run from `trustcal/` and are documented in `trustcal/AGENTS.md`. From `trustcal/`, `pytest` and `python scripts/p0_gate.py` are the local gates.

## Layout

```text
frontend/            React app (Vite root; see Routes below)
  src/
    components/layout/   SiteNav, SiteFooter, PageHeader
    components/shared/   Diagrams (ArchitectureFlow, PipelineFlow), TrustSimulator,
                         tables, Timeline, Callout, and reusable UI
    context/             ThemeContext provider
    data/                Page content (ideas.ts, overview.ts, papers.ts)
    pages/               One component per route
  scripts/prerender.mjs  Headless-Chrome prerender, runs after vite build
trustcal/              Python pipeline (P0 released; vLLM serving + debate runner; see trustcal/AGENTS.md)
  configs/             models.yaml (Dev/Four-bit/Final switch), experiments.yaml (Core matrix),
                       phase.yaml (default stack), datasets.yaml (revisions/provenance)
  src/trustcal/        inference · agents · orchestrator (injection) · trust · retrieval ·
                       eval · runner · preflight
  setup.sh (top level); scripts/ serve.sh, run_experiment.py, run_matrix.py, p0_gate.py,
                       check_stack.py, preflight.py, mock_vllm.py, annotate.py, smoke_test.py
experiments/           Per-run reports + committed artifacts and `next/WP-*.md` planning
                       records (index in experiments/README.md)
docs/                  Research blueprint + literature-review guide
roadmap.md             Phase-by-phase execution plan (blueprint §12–13)
literature_review/
  index.md             Master paper matrix / gap map / verification log
  papers/              One detailed review file per paper (NN-slug-author-year.md)
```

## Routes

Defined in `frontend/src/App.tsx`; the prerender list in `frontend/scripts/prerender.mjs` must match.

| Path | Page | Notes |
| --- | --- | --- |
| `/` | OverviewPage | |
| `/idea/1` | IdeaDetailPage | The proposal detail |
| `/roadmap` | RoadmapPage | |
| `/papers` | PapersPage | Literature review |
| `/proposal` | ProposalPage | |
| `/slide` | SlidePage | Main projector deck, not in nav; keyboard-nav only |
| `/slide/ce` | SlidesCePage | Complex Engineering deck, not in nav |
| `/slide/final` | FinalSlidePage | Final defence deck (18 slides), not in nav |
| `/slide/final/1` | FinalCompactSlidePage | Compact final deck (14 slides), not in nav |

When you add or remove a route, update **both** `frontend/src/App.tsx` and the `routes` array in `frontend/scripts/prerender.mjs`, or the new page won't be prerendered.

## Conventions

- **Imports:** use the `@/` alias for `src/` (e.g. `@/lib/utils`). It's configured in `vite.config.ts` and `tsconfig`.
- **Class names:** merge with `cn()` from `@/lib/utils` (clsx + tailwind-merge). Don't hand-concatenate class strings.
- **Icons:** import individually from `lucide-react`.
- **Content vs. presentation:** page copy that's naturally data lives in `src/data/*.ts`; one-off layout lives in the page/component. Match whichever pattern the page you're editing already uses.
- **Slides:** `SlidePage.tsx` uses container-query units (`cqw`/`cqh`) so text scales with the 16:9 canvas, not the window. Reuse the existing `Card` and `Bullet` helpers and the `NEAR_BLACK`/`ACCENT`/`TEAL`/`AMBER`/`ROSE` color constants. New slides are functions added to the `SLIDES` array.
- **Lint:** respect `.oxlintrc.json` (react/rules-of-hooks is an error). The repo uses `flex-shrink-0` etc.; match surrounding style rather than "fixing" it.
- Match the comment density, naming, and idioms of the file you're editing. Prefer prose in docs; use tables only where they earn their keep.

## Literature review

Paper reviews live in `literature_review/papers/NN-slug-author-year.md` and follow a fixed expert template (see `01-imad-fan-2026.md` as the reference format): header block (status / threat-to-novelty / verified date / summary / relevance / gap), then a Section 2 with a Q1–Q9 quick-reference table and deeper analysis. When adding a paper, also update `literature_review/index.md` (comparison matrix, quick triage, gap map, verification log). Verify citations against the primary source (ACL Anthology, DOI, DBLP), not just the PDF footer.

## Branches

- `main` — release trunk and deployed frontend. Never push directly.
- `dev` — long-lived integration branch; slice from here.
- `next/<slice>` — short-lived work branch in its own worktree; push after each green checkpoint, merge into `dev`, then delete.
- Release tags mark promoted commits (`p0-gate`, `p0-release`). Only `main` and `dev` are long-lived; `feat/*` and `p0/wp-*` slices are retired.

## Safety / scope

- The frontend is static, but the repo is not secret-free: `trustcal/` runs three local vLLM servers on `127.0.0.1:8000-8002` and reads `.env` (`HF_TOKEN`, `OPENAI_API_KEY` for B7, optional retrieval keys). Never commit `.env`, keys, `results/`, or model caches.
- `pdfs/` and `markdowns/` are gitignored source material; don't commit them.
- Don't commit unless explicitly asked. Never push to `main` directly; use a branch.
- `dist/` is build output — never edit it by hand.

## University H200 access

The university GPU is the current approved compute path. Use it only for this project, and only under these rules. If an action is not explicitly allowed here, ask the user first.

- **Access:** SSH through the local alias `uiu-h200` only. Do not expose ports or create another connection method.
- **Project directory:** clone this repo into a dedicated `trustcal-fydp/` directory. Never work inside or modify the existing `tool-observation/` project, its venv, or its configs. Share the Hugging Face cache read-only.
- **GPU:** H200 MIG `1g.18gb`, 18 GB VRAM maximum. Use only this slice.
- **Driver / CUDA:** NVIDIA driver `580.178.04`, CUDA `13.5`. Do not change, overwrite, reinstall, or upgrade either; do not replace system libraries.
- **Host changes:** do not change GPU clocks, power limits, MIG settings, the SSH daemon, host keys, the account name, the login method, or other users' `authorized_keys`.
- **Storage:** 200 GB maximum. Check `df -h` and `du -sh`; stay inside the project space; do not change mounts, quotas, or permissions; do not delete other users' files.
- **Python:** use a project-local venv or conda environment only. No system-wide packages and no `sudo` without administrator approval.
- **Jobs:** use `tmux` or `screen`; stop idle GPU jobs. No mining, public services, port scanning, or unrelated workloads.
- **Secrets:** never commit a server address, hostname, username, account ID, password, SSH key, or host fingerprint. Allowed identifiers are `uiu-h200`, `H200 1g.18gb`, driver `580.178.04`, and CUDA `13.5`.
- **Policy:** follow the university's monitoring, acceptable-use, and data-handling policies.
- **Change control:** record approved hardware, driver, CUDA, or environment changes in `docs/DECISIONS.md` before confirmatory work.

The 18 GB slice cannot hold the 53.26 GB 4-bit matrix stack, the 73.68 GB FP8 stack, or the ~25 GB dev trio. Do not schedule the Core/Full matrices, the multi-model smoke, or the FP8 precision replication on it. Use it only for single-model interface, prompt, parser, or retrieval checks: 8–9B AWQ with vLLM, or Q4_K_M main models with llama.cpp at 4k context, one model at a time. Do not download Q4_K_M test files on a cloud host; download them on the university host and keep the project under 200 GB.

Budget rule: run Core/Full matrix work on the 80 GB on-demand 4-bit path; reserve the 96 GB class for FP8-specific checks only after their smoke passes. Ask the user before any paid GPU run and record the chosen offer and cost in the run notes; keep a retry/bandwidth reserve.

## Cloud GPU rental (Vast.ai and similar)

Rent by **all-in cost and stability**, not the headline GPU rate. At rent time,
check every field below and record the chosen offer in the run notes.

- **Fit:** `gpu_ram` must hold weights plus KV cache. The 4-bit 24-27B trio is
  sized for an 80 GB card at 0.90 utilization; the FP8 stack needs 96 GB. Read
  `num_gpus`, `gpu_frac` and `gpu_total_ram` so a fractional or multi-GPU offer
  is not mistaken for one full card.
- **Rate:** `dph_total` is only the GPU. Add storage: at $1.00/GB/month a
  200 GB disk costs ~$0.28/h (~$185 over 667 GPU-hours); at $0.20/GB/month it is
  ~$0.06/h. Storage can exceed the GPU line on cheap hosts.
- **Bandwidth:** `inet_down_cost` / `inet_up_cost` are per GB. A 53 GB 4-bit
  download costs $0.14 at $0.0026/GB but $2.07 at $0.039/GB; FP8 adds 74 GB.
- **Reliability:** prefer `reliability >= 0.98` and a host with no recent stops.
  Single-GPU hosts are the most likely to preempt spot when an on-demand renter
  appears; multi-GPU hosts are safer.
- **Speed:** `inet_down` (Mbps) and `disk_bw` (MB/s). 1 Gbps rebuilds 53 GB in
  ~7 min, 4 Gbps in ~2-3 min; disk below ~1 GB/s makes model loading slow.
  Speed matters most on spot hosts, which may need rebuilding.
- **Driver:** the pinned stack needs driver >= 580 / CUDA 13
  (`cuda_max_good >= 13.0`); older Ampere hosts fail the cu130 wheels.
- **Spot vs on-demand:** use on-demand for runs longer than about an hour.
  80-96 GB spot prices move 50-100% within minutes and evict the instance; the
  re-download and re-setup often cost more than the on-demand premium. Use spot
  only for short, resumable runs, and mirror results locally every 10 minutes.
  Exception: a resumable matrix prefix may stay on spot beyond an hour when the
  rebuild is cheap and fast (<=15 min, <=$0.5: low storage and bandwidth cost,
  >=1 Gbps) and reliability is >=0.98. Records checkpoint per question, so a
  stop costs time, not data; a 1-hour host still yields ~9-10 debates.
- **Default hardware:** the 4-bit Core runs on an 80 GB A100 on-demand; the
  96 GB class is for FP8 and for short spot tests when it is materially cheaper.
- **Compute the real number:** `all-in/h = dph_total + storage_cost * disk_GB /
  720`; `run_cost = hours * all-in/h + download_GB * inet_down_cost`. Never
  compare two hosts on `dph_total` alone.

## Cache discipline (why this file is structured this way)

To maximize prompt-cache hits across agent tools and models (DeepSeek V4, MiniMax M3, Kimi K2.7, Claude Code), this file is the **single canonical instruction block**:

- `CLAUDE.md` contains only `@AGENTS.md` so both entry points load the *same* byte sequence — one cached prefix, not two divergent ones.
- Keep this file **static**: no dates, no "current status", no volatile counts, no per-session notes. Anything that changes often belongs in code, `README.md`, or `literature_review/index.md` — never here. A stable prefix is what lets the cache hit across sessions.
- Put the most stable, general content first and edit lower sections when possible; edits near the top invalidate the cached prefix for every model.
- Prefer editing existing lines over reordering; reordering churns the cache even when meaning is unchanged.

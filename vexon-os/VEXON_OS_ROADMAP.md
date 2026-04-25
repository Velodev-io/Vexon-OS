# Vexon OS Roadmap

## Product Vision

Vexon OS is intended to become a standalone operating system, in the same category as Windows, Ubuntu, or Kali, but with AI agents as the core interaction model rather than an optional application layer.

The architecture should evolve through four major stages:

1. A localhost prototype proving the agent kernel.
2. A native desktop runtime.
3. A custom Linux-based system image.
4. A bootable ISO that runs directly on hardware.

The major design principle across all phases is continuity of the agent kernel. Query routing, memory, tool execution, session state, and system control should begin inside the web stack and progressively become the real shell of the operating system.

## Core Principle

The same agent kernel must survive every transition:

- Query routing
- Memory
- Tool execution
- Session state
- System control

The current web app is not throwaway code. It is the first form of the OS brain.

## Phase 1: AI Core Prototype

Phase 1 is the localhost and LAN-based agent workspace running on the MacBook and Mac Mini. It proves the intelligence layer before building the native shell and the OS body around it.

### Current Progress

- Researcher Agent: around 90%
- Web Search Tool: around 95%
- Real-time streaming: around 95%
- Subprocess-based code execution exists
- Gemini `text-embedding-004` is the current memory embedding direction
- Groq is already chosen for supervisor planning

### Phase 1 Goal

Build a reliable AI operating layer with:

- Agent orchestration
- Real-time event streaming
- Working memory and long-term memory
- Safe-enough tool execution for development
- Session persistence
- Local auth
- A polished UI that behaves like the future desktop shell

### Phase 1 Deliverables

- Intent parsing and routing to specialist agents
- Researcher Agent with search, evaluation, and synthesis pipeline
- WebSocket and Redis streaming loop
- Session storage and reload support
- JWT auth with email and password only, replacing Firebase entirely
- Working memory in Redis
- Long-term memory via embeddings and vector DB
- Basic sandboxed code execution
- Persistent chat and workspace UI that feels like an OS shell

### Phase 1 Current Gaps

- Database migrations not initialized
- Session persistence missing
- Hardcoded user identity in the frontend
- Memory stubs not fully wired
- Code execution sandbox not production-safe
- Error handling and resilience are incomplete
- Firebase must be replaced with local JWT auth

### Phase 1 Execution Order

1. Database and migrations
2. JWT auth
3. Session persistence
4. Working memory integration
5. Long-term memory recall
6. Safer code execution
7. UI reliability and error feedback
8. Basic supervisor delegation

### Phase 1 Exit Criteria

Phase 1 is complete when:

- A user logs in locally with JWT auth
- Sessions survive refresh and restart
- Agents can recall short-term and long-term context
- Queries stream live with robust reconnect behavior
- Code execution is isolated enough for trusted local use
- The app feels like a real AI workspace, not a demo

## Phase 2: Native Desktop Shell

Phase 2 turns the current agent workspace into a packaged desktop runtime, likely through Electron or Tauri. At this stage, Vexon OS should feel like a true local environment rather than a browser page.

### Phase 2 Goal

Turn the workspace into a local-first desktop environment with:

- Native windowing
- File-system access
- System tray and background services
- Local process control
- Better resource management on the Mac Mini and later Linux machines

### Phase 2 Core Architecture

- Frontend becomes a desktop shell UI
- Backend runs as a bundled local daemon
- Ollama and local models run as background services, ideally on the Mac Mini or target Linux machine
- Memory, sessions, and logs move from web app persistence into OS-style workspace persistence
- Tool calls begin to include local file management, terminal execution, project operations, and indexed search over the machine

### Phase 2 Key Features

- Native launcher or home screen
- Session manager
- File explorer backed by AI actions
- Local terminal controlled by agent workflows
- Multi-panel workspace for chat, files, logs, agents, and tasks
- Notification center for agent events
- Local model manager
- System settings for memory, model routing, permissions, themes, and devices

### Phase 2 Security Model

This phase starts the real permission system:

- Which agent can read which folders
- Which tools can execute shell commands
- Which agent can access network
- Whether code execution is isolated in Docker or a stricter sandbox
- Per-workspace permission boundaries

### Phase 2 Exit Criteria

Phase 2 is complete when:

- Vexon OS runs as a native desktop shell
- A browser is no longer required
- Local files, processes, and models are first-class citizens
- The user can spend hours inside Vexon OS as a working environment

## Phase 3: Custom Linux Distribution Layer

Phase 3 is where Vexon OS stops being an app wrapper and becomes the main desktop environment on top of Linux.

### Phase 3 Goal

Build a Linux-based Vexon OS image where:

- Linux provides drivers, kernel, boot, networking, and hardware compatibility
- Vexon OS provides the shell, desktop UX, session layer, memory, and AI control plane

### Phase 3 Architectural Model

- Linux kernel underneath
- Minimal distro userspace above it
- Display server and compositor
- Vexon Shell as the primary desktop and session
- Agent services launched on boot
- Local models and memory services started as system services

### Phase 3 Major Workstreams

- Build on a stable Linux base, likely Ubuntu or Debian first
- Create a custom login and session that opens directly into Vexon Shell
- Run the agent backend, memory services, vector DB, and local model manager as `systemd` services
- Add AI-native file search, command execution, project launch, and workflow automation
- Integrate system controls like Wi-Fi, battery, devices, updates, and storage into the AI shell

### Phase 3 Subsystems

- Vexon Session Manager: starts the shell and recovers prior sessions
- Agent Runtime Service: long-running orchestration engine
- Model Service: routes local vs remote models, Ollama, Groq, and others
- Memory Service: Redis, vector layer, and summarization pipelines
- System Tool Layer: wrappers around shell, file ops, package management, logs, and process control
- Permission Broker: asks the user before risky actions
- Observability Layer: traces tool calls, task trees, errors, and performance metrics

### Phase 3 UX Target

When the machine logs in, the user should land in Vexon Shell instead of a GNOME or KDE-style workflow. AI becomes the main launcher, system control panel, and automation engine, while traditional windows still exist as tools underneath.

### Phase 3 Exit Criteria

Phase 3 is complete when:

- A Linux installation boots to Vexon Shell by default
- Agent services auto-start on login or boot
- Files, apps, system actions, and automations are managed from the AI shell
- Vexon OS is usable as the primary day-to-day environment on a Linux install

## Phase 4: Bootable Vexon OS ISO

Phase 4 is the final product target: a bootable and installable Vexon OS that can run directly on real machines.

### Phase 4 Goal

Ship a bootable, installable Vexon OS that:

- Boots on real hardware
- Launches directly into the AI-native shell
- Runs local models where possible
- Offers offline-first operation
- Feels like an operating system, not a packaged app

### Phase 4 Components

- Custom ISO build pipeline
- Installer flow
- Hardware compatibility defaults
- Boot splash and branding
- First-run onboarding
- Model setup and download flow
- Offline and local mode with optional cloud connectors
- Recovery mode and safe mode
- Update channel and rollback mechanism

### Phase 4 Installer Experience

The installer should:

1. Choose language and region
2. Partition or choose target disk
3. Create local user
4. Set Vexon OS password
5. Configure model and runtime defaults
6. Initialize memory store
7. Reboot into Vexon Shell

### Phase 4 Required Platform Capabilities

- Reliable boot on common x86 hardware first, ARM later
- GPU-aware model routing where available
- Persistent encrypted local workspace
- Crash recovery and boot logs
- Signed updates or at least verified update bundles
- Safe fallback if AI services fail, so the OS remains usable

### Phase 4 Exit Criteria

Phase 4 is complete when:

- A user can flash a USB, boot a PC, and install Vexon OS
- The system lands directly in Vexon Shell after installation
- Core AI features work locally
- Sessions, memory, tools, and system controls persist across reboots
- The OS can function as a real primary machine for focused workflows

## Canonical Stack

| Layer | Recommended Direction |
| --- | --- |
| UI shell | React/Tailwind now, native shell in Phase 2 |
| Agent backend | FastAPI + Redis + WebSocket streaming |
| Planner / supervisor | Groq in Phase 1, later local fallback too |
| Research agent | Web search + synthesis pipeline |
| Working memory | Redis |
| Long-term memory | Embeddings + vector DB, currently Gemini `text-embedding-004` direction |
| Auth | Local JWT with email/password only |
| Code execution | Subprocess now, then containerized sandbox, then stricter OS-level isolation |
| Desktop runtime | Electron/Tauri in Phase 2 |
| OS base | Ubuntu/Debian-derived Linux in Phase 3 |
| Final packaging | Bootable ISO in Phase 4 |

## Strategic Rules

These rules keep the project coherent from Phase 1 through Phase 4:

1. Do not treat the current web app as throwaway. It is the brain prototype of the OS.
2. Every Phase 1 subsystem should later map to an OS subsystem.
   Sessions become workspace state, tool calls become system actions, memory becomes user-state intelligence, and the shell UI becomes the desktop.
3. Remove external dependencies when they do not fit the final OS vision.
   Moving from Firebase to local JWT is correct.
4. Build local-first and offline-first wherever possible, especially because the Mac Mini is intended to run local LLM workloads.
5. Prioritize reliability before adding more agents.
   A bootable AI OS cannot be built on fragile session state and stub memory.

## Short North Star

Vexon OS starts as a web-based agent workspace, becomes a native desktop shell, evolves into the primary Linux session, and ultimately ships as a bootable AI-first operating system where the agent kernel is the real shell of the machine.

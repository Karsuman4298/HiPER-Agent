# HiPER-Agent | Advanced Multi-Agent Intelligence 2.0

**HiPER-Agent** is a production-grade, autonomous digital assistant built on a modular multi-agent orchestration framework. Inspired by advanced research into hierarchical planning and execution, this system coordinates a team of specialized AI agents to autonomously solve complex research, data analysis, and coding tasks with industrial-strength reliability.

**Official Repository:** [https://github.com/Karsuman4298/HiPER-Agent](https://github.com/Karsuman4298/HiPER-Agent)

---

## 🛡️ "Always Available" High-Availability Architecture
To ensure zero-downtime, HiPER-Agent features a **Strategic Model Rotation** and fallback system:
- **Primary Engine**: Defaults to **Groq** (`llama-3.1-8b-instant`) for blazing-fast inference and high rate-limit quotas on the free tier.
- **Auto-Fallback Layer**: Automatically pivots to **Google Gemini** (`gemini-1.5-flash`) or alternative models if the primary provider hits a quota or rate limit.
- **Local Resilience**: Fully supports **Ollama** for 100% offline, private, and unlimited execution using local models like `llama3`.
<img width="1260" height="835" alt="Screenshot 2026-04-05 171518" src="https://github.com/user-attachments/assets/f010c36b-85fb-4c9f-8b2b-01ea5ae4d8fc" />

---<img width="1273" height="559" alt="Screenshot 2026-04-05 164253" src="https://github.com/user-attachments/assets/9e79289c-2926-4ef8-a2e7-b05e071328a7" />
<img width="1246" height="848" alt="Screenshot 2026-04-05 164030" src="https://github.com/user-attachments/assets/bf0c59d6-fb9d-4acf-8874-76c4bd5d501e" />


## 🧠 The Multi-Agent Teaming Framework
HiPER-Agent utilizes **LangGraph** to manage a deterministic yet flexible state machine between specialized nodes. Rather than a single monolithic prompt, tasks are routed through experts:

| Agent Role | Responsibility |
| :--- | :--- |
| **Planner** | Strategic architect; breaks complex user tasks into step-by-step assignments. |
| **Researcher** | Fact-based intelligence gathering; uses deep web-search context and strict anti-hallucination guards. |
| **Coder / Executor** | Systems engineer; translates research findings into executable Python/Bash logic and simulates code safely. |
| **Data Analyst** | Quantitative expert; parses complex datasets and identifies statistical patterns. |
| **Evaluator** | Quality gatekeeper; rigorously synthesizes final responses and ensures premium, GPT-style streaming output. |

---

## 🛠️ Complete Technology Stack
HiPER-Agent is built on modern, robust Python technologies:
- **Core Orchestration**: `LangChain`, `LangGraph` for stateful agent workflows.
- **Inference Providers**: Native integrations for `Groq API`, `Google AI Studio (Gemini)`, `OpenAI`, `Anthropic`, and `Ollama`.
- **Search & Tools**: Modern `DuckDuckGo Search (DDGS)` for real-time web intelligence.
- **Memory Layers**: `ConversationBufferMemory` ensures persistent contextual awareness during interactive terminal sessions.
- **UI & Interface**: `Rich` for a beautiful, distinct, and color-coded Windows-compatible terminal UI; `Typer` for rapid, modular CLI commands.
- **Configuration**: `Pydantic-Settings` for type-safe environment variable management.

---

## 🚀 Quick Start

### 1. Requirements
- Python 3.10+
- [Ollama](https://ollama.ai/) (Optional, strictly for local, private execution)

### 2. Installation
```powershell
# Clone and enter directory
git clone https://github.com/Karsuman4298/HiPER-Agent.git
cd HiPER-Agent

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration
Copy the sample environment file to `.env` and add your API keys:
```env
# Default setting for high availability
LLM_PROVIDER=groq

# API Keys
GROQ_API_KEY=your_groq_key_here
GOOGLE_API_KEY=your_google_key_here
```

### 4. Usage Commands
Interact with HiPER-Agent securely via the terminal.

**Interactive Chat Mode (Recommended)**
Simply run the main script to enter a continuous, interactive chat loop. Press `Ctrl+C` to exit.
```powershell
python main.py
```

**Single-Shot Commands**
Alternatively, execute isolated tasks directly from the CLI:

```powershell
# Unified task execution
python main.py run "Research the impact of quantum computing on cryptography"

# Specialized Research Task
python main.py research "Latest advancements in Solid State Batteries"

# Specialized Code Task
python main.py code "Create a script that fetches the current weather using a public API"

# Data Analysis
python main.py analyze "sales_data.csv"
```

---

## ⚖️ License
Released under the **MIT License**. Built for speed, privacy, and autonomous excellence.

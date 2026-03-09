# PM Coworker AI

> **Product Vision:** To provide an instant, high-signal sounding board for Product Managers by synthesizing the best frameworks and insights from top tech leaders into actionable, day-to-day advice.

## The Problem

Product Managers constantly face complex, ambiguous challenges—from designing pricing strategies to aligning stubborn stakeholders. While incredible resources exist (like Lenny's Podcast and curated strategy repositories), finding the exact framework you need in the middle of a chaotic workday requires hours of searching, listening, and synthesizing.

## The Solution

**PM Coworker AI** is a localized, Retrieval-Augmented Generation (RAG) application. It acts as a senior PM counterpart that has perfectly internalized hundreds of hours of top-tier product conversations and structured AI product strategy frameworks.

Instead of functioning as a search engine that spits out podcast quotes, it operates as an experienced colleague. You ask it a product question, and it retrieves the most relevant mental models to return a synthesized, actionable playbook—no name-dropping, just pure, practical strategy.

---

## Architecture & Tech Stack

This application was architected and generated using **Google Antigravity** (Agent-Assisted Development).

* **Frontend:** Next.js (App Router), Tailwind CSS, shadcn/ui
* **Backend:** Python, FastAPI, LangChain
* **Vector Database:** LanceDB (Local, serverless)
* **LLM Engine:** Google Gemini (via `langchain-google-genai`)
* **Embedding Model:** HuggingFace `all-MiniLM-L6-v2`
* **Core Data Sources:** * Podcast Transcripts: `ChatPRD/lennys-podcast-transcripts`
* Structured Frameworks: `RefoundAI/lenny-skills`



---

## Getting Started (Local Deployment)

### 1. Prerequisites

* Node.js & npm installed
* Python 3.9+ installed
* A free [Google Gemini API Key](https://aistudio.google.com/)

### 2. Clone the Repository

```bash
git clone https://github.com/yourusername/pm-coworker-ai.git
cd pm-coworker-ai

```

### 3. Build the Brain (Data Ingestion)

The application relies on a local LanceDB vector database. You must ingest the data first.

```bash
# Navigate to the backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Run the ingestion scripts to build lenny_brain.lance
python ingest_transcripts.py
python ingest_skills.py

```

### 4. Configure Environment Variables

Create a `.env` file in the `/backend` directory and add your Gemini API key:

```env
GEMINI_API_KEY=your_actual_api_key_here

```

### 5. Launch the Application

You will need to run both the FastAPI backend and the Next.js frontend concurrently.

**Terminal 1 (Backend):**

```bash
cd backend
uvicorn main:app --reload

```

**Terminal 2 (Frontend):**

```bash
cd frontend
npm install
npm run dev

```

Navigate to `http://localhost:3000` in your browser to start collaborating with your new PM coworker.

---

## Product Roadmap (Future Iterations)

* **Phase 1 (Current):** Read-only RAG pipeline with static podcast and framework data.
* **Phase 2:** Integrate `youtube-transcript-api` to autonomously pull and ingest new episodes from the 20VC YouTube channel.
* **Phase 3:** Implement conversational memory (session history) so the PM Coworker remembers the context of an ongoing product launch across multiple chat messages.
* **Phase 4:** Connect to Jira/Linear via API so the agent can draft tickets directly from the strategic chat interface.

# SyncScribe - AI-Powered Meeting Assistant

SyncScribe turns unstructured meeting recordings and documents into searchable institutional knowledge. It automates transcription, generates concise summaries, and powers question-answering across your knowledge base so teams can move from discussion to decisions faster.

---

## Overview
- **Frontend**: Streamlit application (`ui.py`) that provides login, upload, chat, and knowledge base viewing experiences.
- **Backend**: Django + DRF API that handles authentication, file ingestion, Bedrock/Claude powered analysis, and DynamoDB-backed credential management.
- **Storage**: Amazon S3 buckets for uploads, transcripts, summaries, and embeddings; DynamoDB for long-lived AWS credentials.
- **AI Models**: Supports Amazon Bedrock (Claude Sonnet, Titan Embeddings) and Amazon Transcribe for speech-to-text.

---

## Feature Highlights
- Upload meeting recordings or documents and receive synchronized transcripts and multi-section summaries.
- Chat with SyncScribe about a single meeting or a curated knowledge base of meetings using Retrieval-Augmented Generation (RAG).
- Render flowchart-style answers using Mermaid.js for fast visual understanding.
- Manage AWS credentials securely and rotate temporary credentials for production usage.
- Access summaries, uploads, and embeddings through a unified frontend while the backend exposes RESTful APIs for automation.

---

## Architecture at a Glance
- **Streamlit UI** communicates with the Django API via `DJANGO_API`.
- **Django API** orchestrates AWS services, persists metadata, and exposes endpoints (`/upload`, `/ask`, `/api/kb/...`, `/api/login`).
- **AWS Integration** uses S3 for artifact storage, DynamoDB for credential storage, and STS for temporary sandbox roles.
- **Knowledge Base** stores embeddings in S3 and uses LangChain + FAISS for semantic search.

---

## Tech Stack
- Python 3.11+
- Django 5
- Django REST Framework
- Streamlit
- LangChain + FAISS
- Amazon Bedrock (Claude Sonnet, Titan Embeddings)
- Amazon Transcribe
- Amazon S3, DynamoDB, STS

---

## Repository Layout
```text
.
├── ai_meeting_assistant/      # Django project settings (kept generic for import paths)
├── api/                       # Django app exposing REST endpoints and AWS integrations
├── templates/                 # Shared HTML templates used by the frontend
├── ui.py                      # Streamlit entry point for the full SyncScribe experience
├── kb_summary_viewer.py       # Streamlit utility for browsing knowledge-base summaries
├── requirements.txt           # Python dependencies for both frontend and backend
├── terraform/                 # Infrastructure-as-code assets (optional deployment helpers)
├── manage.py                  # Django management script
└── README.md
```

---

## Prerequisites
- Python 3.11+ with `pip`
- Virtualenv (`python -m venv`) or conda for dependency isolation
- AWS account with access to S3, DynamoDB, and Bedrock (for production features)
- Git (for cloning and deployment tracking)

---

## Quick Start
1. **Clone the repository**
   ```bash
   git clone https://github.com/PrashamanP/AI-meeting-assistant.git
   cd AI-meeting-assistant
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv env
   source env/bin/activate            # On Windows use: env\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Create a `.env` file in the project root**
   ```text
   DJANGO_API=http://localhost:8000
   AWS_REGION=us-east-1
   MEETING_UPLOADS_BUCKET=aima-meeting-uploads
   MEETING_TRANSCRIPTS_BUCKET=aima-meeting-transcripts
   MEETING_SUMMARIES_BUCKET=aima-meeting-summaries
   MEETING_EMBEDDINGS_BUCKET=aima-meeting-embeddings
   # Optional: ENV=production to enable STS role assumption
   ```

---

## Running the Backend (Django API)
```bash
python manage.py migrate
python manage.py createsuperuser  # Creates login credentials for SyncScribe
python manage.py runserver 0.0.0.0:8000
```

Key endpoints:
- `POST /upload/`: upload files for transcription & summarization.
- `POST /ask/`: ask questions about a single meeting.
- `POST /api/kb/<kb_id>/files/`: list files available for a knowledge base.
- `POST /api/kb/<kb_id>/summaries/`: fetch generated summaries.
- `POST /api/kb/ask/`: ask questions across the knowledge base.
- `POST /api/login/`: authenticate Streamlit users via Django.

---

## Running the Frontend (Streamlit)
In a separate terminal with the virtual environment activated:
```bash
streamlit run ui.py
```

The app defaults to http://localhost:8501 and will prompt for the Django credentials you created with `createsuperuser`.

---

## Development Tips
- `kb_summary_viewer.py` offers a lightweight Streamlit interface focused on knowledge-base summaries.
- Update `DJANGO_API` in your `.env` if the API runs on a different host or port.
- `terraform/` contains starting points for provisioning AWS infrastructure; adjust bucket names and IAM roles to match your environment.
- Keep large media files out of Git by extending `.gitignore` if needed (e.g., `*.mp4`, `*.wav`).

---

## Testing & Quality
- Run Django tests (add tests under `api/tests/` as you build features):
  ```bash
  python manage.py test
  ```
- For Streamlit components, rely on manual verification or framework-specific testing such as Selenium or Playwright (not included by default).

---

## Deployment Notes
- Collect static files if serving the Django admin in production:
  ```bash
  python manage.py collectstatic
  ```
- Use reverse proxies (NGINX, Traefik) to route `/api/` traffic to Django and `/` to Streamlit.
- Configure HTTPS, environment variables, and AWS credentials on the target host. For production environments set `ENV=production` to enable STS-based credential rotation.
- Consider containerizing the API and frontend separately for scalable deployments.

---

## Troubleshooting
- **Login issues**: ensure the Django server is running and `DJANGO_API` matches the backend URL.
- **AWS permission errors**: verify DynamoDB entries for long-lived credentials or the IAM role used for STS.
- **Large upload failures**: the backend accepts files up to 1 GB by default; check network limits or adjust `DATA_UPLOAD_MAX_MEMORY_SIZE` as needed.
- **Streamlit caching quirks**: clear cache with `streamlit cache clear` if data looks stale.

---

## Contributing
1. Fork the repository and create a feature branch.
2. Make your changes with clear commit messages.
3. Run `python manage.py test` and manual UI checks.
4. Open a pull request referencing any related issues or feature requests.

---

SyncScribe is evolving quickly - feel free to open issues or feature proposals to shape the roadmap.

# 🧠 AI Powered Meeting Assistant 

AI Meeting Assistant is a streamlined assistant that helps teams get the most out of their meetings. Upload a video or document, get automatic transcripts, summaries, and ask deep questions with flowchart-style answers – all powered by Claude and Bedrock models.

---

## 🔧 Tech Stack

- **Frontend**: [Streamlit](https://streamlit.io/)  
- **Backend**: [Django](https://www.djangoproject.com/) + Django REST Framework  
- **AI Models**: Claude via Amazon Bedrock (Sonnet), Titan Embeddings  
- **Storage**: Amazon S3 (uploads, summaries, embeddings)  
- **Database**: DynamoDB (AWS credentials, embedding tracking)  
- **Auth**: Streamlit-based login with Django user validation  

---

## 🚀 Features

✅ Upload meeting recordings  
✅ Automatic transcription + summarization  
✅ Ask questions and get AI-generated answers  
✅ Mermaid.js-based flowchart rendering  
✅ Knowledge Base mode to combine insights from multiple meetings  
✅ Admins can upload temporary AWS credentials  
✅ Seamless separation of frontend (Streamlit) and backend (Django API)


---

## 🧪 Local Setup

### ✅ 1. Clone the Repo

```bash
git clone https://github.com/PrashamanP/AI-meeting-assistant.git
```


✅ 2. Install dependencies  

# Backend
cd ai_meeting_assistant
python -m venv env
source env/bin/activate  # or env\Scripts\activate on Windows
pip install -r requirements.txt

# Frontend
cd ..
pip install streamlit  

✅ 3. Set environment variables
Create a .env file in the project root:

env

DJANGO_API=http://localhost:8000  
AWS_REGION=us-east-1  


✅ 4. Run the backend

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver  


✅ 5. Run the frontend (in a second terminal)  

streamlit run ui.py
Visit: http://localhost:8501


🧠 AI Features
Feature	Model
Transcription	Amazon Transcribe
Summarization	Claude Sonnet via Bedrock
Embedding	Titan Embeddings
RAG-style Q&A	LangChain + FAISS
Flowcharts	Mermaid.js rendering in Streamlit

📁 S3 Bucket Structure

aima-meeting-uploads/
├── single-uploads/
├── coalition-kb/
│   └── R01 - Budget Discussion.mp4

aima-meeting-transcripts/
aima-meeting-summaries/
aima-meeting-embeddings/  


⚙️ Deployment
Can be deployed on a single EC2 instance:

Django runs on :8000

Streamlit runs on :8501

Use NGINX to route:

/api/ → Django

/ → Streamlit

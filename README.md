# LMSilo Translate

AI-powered translation service using Meta's NLLB-200 model, supporting 200+ languages including low-resource languages.

## Features

- **200+ Languages**: Full NLLB-200 language coverage
- **Auto-Detection**: Automatic source language detection
- **Model Management**: Download and manage NLLB variants
- **Shared Workspace**: All users see translation job queue
- **Audit Logging**: Full usage tracking with export

## Architecture

```
translate/
├── backend/
│   ├── main.py           # FastAPI application
│   ├── api/
│   │   ├── models.py     # Model management API
│   │   └── jobs.py       # Translation job API
│   ├── models/
│   │   ├── database.py   # Model registry
│   │   └── job.py        # Translation jobs
│   ├── services/
│   │   └── model_downloader.py
│   ├── workers/
│   │   ├── celery_app.py
│   │   └── tasks.py      # Translation task
│   └── nllb_lang_codes.py
├── frontend/
│   └── src/
│       ├── App.tsx
│       ├── pages/
│       │   ├── Models.tsx
│       │   └── Settings.tsx
│       └── components/
│           ├── JobList.tsx
│           └── AuditLogViewer.tsx
└── Dockerfile
```

## API Endpoints

### Translation
- `POST /translate` - Translate text
- `POST /translate/batch` - Batch translation
- `GET /languages` - List supported languages

### Jobs
- `POST /api/jobs` - Create translation job
- `GET /api/jobs` - List all jobs
- `GET /api/jobs/{id}` - Get job status
- `DELETE /api/jobs/{id}` - Delete job

### Models
- `GET /models` - List installed models
- `GET /models/builtin` - List NLLB variants
- `POST /models` - Register model
- `POST /models/{id}/download` - Download model
- `DELETE /models/{id}` - Delete model

## NLLB Models

| Model | Size | Quality |
|-------|------|---------|
| nllb-200-distilled-600M | 1.2GB | Good |
| nllb-200-distilled-1.3B | 2.6GB | Better |
| nllb-200-1.3B | 5.2GB | High |
| nllb-200-3.3B | 13GB | Best |

## Development

```bash
cd translate

# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

## License

MIT

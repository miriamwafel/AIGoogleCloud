# Chat z Vertex AI

Prosta aplikacja czatu używająca Google Vertex AI (Gemini) uruchamiana na Cloud Run.

## Bez klucza API!

Aplikacja używa **Application Default Credentials (ADC)** - na Google Cloud automatycznie uwierzytelnia się przez IAM bez potrzeby klucza API.

## Szybki deploy na Cloud Run

### 1. Włącz wymagane API

```bash
gcloud services enable run.googleapis.com
gcloud services enable aiplatform.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

### 2. Deploy z GitHub (Cloud Run)

**Opcja A: Przez konsolę Google Cloud**

1. Wejdź na https://console.cloud.google.com/run
2. Kliknij "Create Service"
3. Wybierz "Continuously deploy from a repository"
4. Połącz z GitHubem i wybierz to repo
5. Ustaw region (np. `us-central1`)
6. W "Advanced settings" > "Variables" dodaj:
   - `GOOGLE_CLOUD_PROJECT` = twój-project-id
   - `VERTEX_AI_LOCATION` = us-central1
7. Kliknij "Create"

**Opcja B: Przez CLI**

```bash
# Sklonuj repo
git clone https://github.com/TWOJ_USER/TWOJ_REPO.git
cd TWOJ_REPO

# Deploy
gcloud run deploy chat-vertex-ai \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "GOOGLE_CLOUD_PROJECT=$(gcloud config get-value project),VERTEX_AI_LOCATION=us-central1"
```

### 3. Uprawnienia IAM

Konto serwisowe Cloud Run musi mieć uprawnienia do Vertex AI:

```bash
# Pobierz konto serwisowe Cloud Run
PROJECT_ID=$(gcloud config get-value project)
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')
SA_EMAIL="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

# Nadaj uprawnienia Vertex AI
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/aiplatform.user"
```

## Struktura projektu

```
.
├── app.py              # Backend Flask + Vertex AI
├── templates/
│   └── index.html      # Frontend czatu
├── requirements.txt    # Zależności Python
├── Dockerfile          # Konfiguracja kontenera
└── README.md
```

## Lokalne testowanie

```bash
# Zaloguj się do GCP
gcloud auth application-default login

# Ustaw projekt
export GOOGLE_CLOUD_PROJECT=twoj-project-id
export VERTEX_AI_LOCATION=us-central1

# Zainstaluj zależności
pip install -r requirements.txt

# Uruchom
python app.py
```

Aplikacja będzie dostępna pod http://localhost:8080

## Jak to działa?

1. **ADC (Application Default Credentials)** - biblioteka `google-cloud-aiplatform` automatycznie szuka credentials:
   - Na Cloud Run: używa konta serwisowego przypisanego do usługi
   - Lokalnie: używa `gcloud auth application-default login`

2. **Vertex AI** - dostęp do modeli Gemini przez Google Cloud (nie potrzebujesz klucza API jak w Gemini API)

3. **Sesje czatu** - każdy użytkownik ma oddzielną sesję konwersacji

## Koszty

- Cloud Run: płacisz tylko za czas wykonywania requestów
- Vertex AI: płacisz za tokeny (input/output) - sprawdź cennik Gemini

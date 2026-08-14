

# Alzheimer's MRI Diagnosis System

A full-stack clinical decision support application for automated Alzheimer's disease diagnosis from brain MRI scans. The system features a **Django REST Framework** backend running a machine learning classification pipeline (ResNet-50 + SVM) and a **React + TypeScript** single-page application (SPA) tailored for clinical workflows (Doctors and Admins).

---

## 📐 Project Structure

```text
.
├── backend/                # Django REST Framework backend
│   ├── apps/               # Modular Django apps (accounts, patients, mri_analysis, reports)
│   ├── config/             # Split settings (base, dev, prod, test)
│   └── ml_models/          # ML weights and model artifacts (.pth, .pkl)
├── frontend/               # React + TypeScript (Vite) SPA
│   ├── src/                # Components, hooks, context, and feature modules
│   └── public/             # Static assets and fonts
├── .gitignore              # Unified Git ignore rules
└── README.md               # Unified project documentation

```

---

## ✨ Features Overview

### 💡 Backend (Django REST Framework)

* **Auth & Accounts**: Doctor self-registration, Admin approval/rejection queue, role-embedded JWT authentication, and password reset workflows.
* **Patient Management**: Doctor-owned patient records, soft-delete archiving, and privacy-preserving Admin oversight (`medical_history` is excluded from Admin views).
* **Synchronous AI Pipeline**: Direct DICOM/Raster image auto-detection → conversion → skull-stripping → resizing → feature extraction (ResNet-50) → classification (SVM).
* **Aggregated Medical History**: Single endpoint delivering a patient's complete diagnostic timeline (scans, AI results, and reports).
* **Immutable PDF Reports**: PDF snapshot generation via `reportlab` (pure Python). Finalized reports are cryptographically locked against edits/deletions.

### 🎨 Frontend (React 18/19 + TypeScript + Vite)

* **Role-Gated Dashboards**: Distinct workflows for Doctors (Patients, Scans, Reports) and Admins (Approval queue, Doctor account management, Paginated patient oversight).
* **Status-Aware Scan Manager**: Drag-and-drop DICOM/Image upload with status visualization (Queued → Analyzing → Completed / Failed).
* **Clinical Design System**: Clinical Teal/Slate palette, self-hosted IBM Plex Sans/Mono typography (designed for restricted clinical intranet environments), and unified 4-color disease severity scales.
* **Secure File Downloads**: Authenticated PDF report downloading via Bearer token blobs.

---

## 🛠️ Tech Stack

| Domain | Technology / Library |
| --- | --- |
| **Frontend** | React 18/19, TypeScript, Vite, React Router v6, TanStack Query v5, React Hook Form + Zod, Tailwind CSS v4, Recharts, Lucide Icons |
| **Backend** | Python 3.10+, Django 4+, Django REST Framework, djangorestframework-simplejwt, ReportLab |
| **Machine Learning** | PyTorch (ResNet-50 backbone), Scikit-Learn (SVM Classifier & StandardScaler), OpenCV / PIL |
| **Database** | PostgreSQL |

---

## 🚀 Quick Start & Local Setup

### Prerequisites

* Python 3.10+
* Node.js 18+ & `npm`
* PostgreSQL running locally or via Docker

---

### 1. Backend Setup

```bash
cd backend

# Configure environment variables
cp .env.example .env

# Spin up local PostgreSQL container (matches .env.example defaults)
docker compose up -d db

# Setup virtual environment and dependencies
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Database migrations & initial superuser
python manage.py migrate
python manage.py createsuperuser   # Default role set to ADMIN

# Run development server (http://localhost:8000)
python manage.py runserver

```

> **Important Note on ML Models:**
> Ensure model artifacts (`resnet50_alzheimer.pth`, `svm_classifier.pkl`, and `feature_scaler.pkl`) are placed inside the `backend/ml_models/` directory. If these files are absent, scan uploads will complete preprocessing but safely fail at the classification step with a clear error message.

---

### 2. Frontend Setup

```bash
cd frontend

# Configure environment variables
cp .env.example .env
# Set VITE_API_BASE_URL=http://localhost:8000/api in your .env file

# Install dependencies and start Vite dev server
npm install
npm run dev

```

The application will be accessible at `http://localhost:5173`.

---

## 🧪 Running Tests

### Backend Tests (PyTest)

```bash
cd backend
pytest

```

*Note: Tests requiring the real ResNet-50 backbone are marked `@pytest.mark.requires_backbone` and automatically skipped if `ml_models/resnet50_alzheimer.pth` is missing.*

### Frontend Type-checking & Build

```bash
cd frontend
npm run build      # Runs tsc -b then builds production bundle to dist/
npm run preview    # Preview the production build locally

```

---

```

```
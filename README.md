# 🔬 ForensicTrace AI — Digital Field Drug Testing Companion
### Smart India Hackathon 2026 | Problem Statement ID: SIH26231 | Team TECH TITANS

An AI-assisted digital companion for field narcotics officers that standardizes colorimetric drug test interpretation, corrects ambient illumination variations, and maintains an immutable SHA-256 cryptographic chain of custody.

---

## 🚀 Quick Local Setup

```bash
# 1. Clone repository
git clone (https://github.com/dnyaneshwaritech/ForensicTrace-AI.git)
cd digital-drug-detector

# 2. Create virtual environment & activate
python -m venv venv
.\venv\Scripts\activate       # Windows
source venv/bin/activate      # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Launch FastAPI REST Backend
python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000

# 5. Launch Streamlit Field Companion (in a separate terminal)
streamlit run app/main_app.py
```

---

## 🌐 Free Cloud Deployment Options

### Method 1: Streamlit Community Cloud (Recommended & 100% Free)
1. Push this project to your GitHub repository.
2. Go to **[share.streamlit.io](https://share.streamlit.io/)** and sign in with GitHub.
3. Click **"New app"**.
4. Select your repo, branch (`main`), and set **Main file path** to: `app/main_app.py`.
5. Click **"Deploy"**! Your public HTTPS link will be live in 1-2 minutes.

### Method 2: Docker Deployment
```bash
docker build -t field-drug-companion .
docker run -p 8501:8501 -p 8000:8000 field-drug-companion
```

---

## 🛡️ Core Features
- **CIEDE2000 ($\Delta E_{00}$) Optical Classifier**: CIELAB color space distance matching for Marquis, Duquenois-Levine, Scott, and Simon's reagents.
- **Hardware-Free Illumination Correction**: Gray-World White Balance algorithm.
- **SHA-256 Chain of Custody**: Tamper-evident ledger with integrity audit detection.
- **Automated Court Evidence PDF**: Generates downloadable legal reports.

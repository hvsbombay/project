# 🤝 VolunteerMatch — Data-Driven Volunteer Coordination for Social Impact

> **Hackathon Track:** `[Smart Resource Allocation]` — Open Innovation  
> **Team:** HVS Bombay

---

## 📋 Problem Statement

Volunteer-driven NGOs and social organisations face a critical inefficiency: **mismatched resource allocation**.

- Organisations spend 40–60% of coordination time manually searching for the right volunteers.
- Volunteers sign up but are assigned to tasks that don't align with their skills, schedules, or location — leading to dropout rates exceeding 50%.
- There is no data-driven layer to track *impact* (hours logged, outcomes) and continuously improve matching quality.

**The result:** talented people remain underutilised, urgent social causes go understaffed, and organisations burn coordinator bandwidth on spreadsheet gymnastics instead of delivering impact.

---

## 💡 Solution Overview

**VolunteerMatch** is a full-stack web application that replaces manual coordination with a **data-driven smart matching engine**.

### Core Features

| Feature | Description |
|---|---|
| 🧠 Smart Match Engine | Scores every volunteer–opportunity pair on **skill overlap (50%)**, **schedule overlap (35%)**, and **city match (15%)**. Surfaces only high-confidence pairings (>40%). |
| 👤 Volunteer Profiles | Self-registration with skills, availability days, hours/week, city, and bio. Searchable/filterable. |
| 📋 Opportunity Board | NGOs post volunteer needs with required skills, schedule, headcount, and dates. Filter by city or category. |
| ✅ Assignment Tracker | One-click assign from the match panel; status lifecycle (pending → confirmed → completed / cancelled). |
| ⏱ Impact Logging | Log volunteer hours per assignment; cumulative impact KPIs on the dashboard. |
| 📊 Live Dashboard | KPI cards + doughnut chart + recent-activity table — real-time, no refresh needed. |
| 🔌 REST API | `/api/match`, `/api/assign`, `/api/stats`, `/api/volunteers`, `/api/opportunities` — ready to integrate with external apps or mobile clients. |

### Matching Algorithm

```
score = 0.50 × skill_overlap
      + 0.35 × schedule_overlap
      + 0.15 × city_match
```

Where *overlap* is computed as set-intersection / set-size, giving a normalised 0–1 score that translates to a percentage match shown in the UI.

---

## 🏗️ Architecture

```
volunteer-coordination/
├── app.py              # Flask application — routes, REST API, matching engine
├── database.py         # SQLite init, schema, seed data
├── requirements.txt    # Python dependencies (Flask only)
├── static/
│   ├── css/style.css   # Custom styles (Bootstrap 5 + overrides)
│   └── js/main.js      # Client-side UX helpers
└── templates/
    ├── base.html           # Shared layout + navbar
    ├── index.html          # Dashboard (KPIs + charts + recent activity)
    ├── volunteers.html     # Volunteer directory (filterable cards)
    ├── add_volunteer.html  # Registration form
    ├── opportunities.html  # Opportunity board (filterable cards)
    ├── add_opportunity.html# Post-opportunity form
    ├── match.html          # Smart match panel + on-demand API match
    └── assignments.html    # Assignment tracker + impact logger
```

**Stack:** Python · Flask · SQLite · Jinja2 · Bootstrap 5 · Chart.js

---

## 🚀 Running Locally (Prototype Link)

```bash
cd volunteer-coordination
pip install -r requirements.txt
python app.py
```

Open **http://localhost:5000** in your browser.

> The app auto-initialises the database and seeds 12 volunteers, 12 opportunities,
> and 12 demo assignments on first run.

---

## 🔌 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/match` | `{"volunteer_id": N}` → top-10 ranked opportunities |
| `POST` | `/api/assign` | `{"volunteer_id": N, "opportunity_id": M}` → create assignment |
| `GET` | `/api/stats` | Platform-wide impact statistics |
| `GET` | `/api/volunteers` | All active volunteers |
| `GET` | `/api/opportunities` | All active opportunities |

---

## 📊 Impact Metrics (Demo Data)

| Metric | Value |
|---|---|
| Active Volunteers | 12 |
| Open Opportunities | 12 |
| Confirmed Matches | 10 |
| Completed Assignments | 3 |
| Total Hours of Impact | 151 h |
| Cities Covered | 7 (Mumbai, Delhi, Bangalore, Chennai, Hyderabad, Pune, Kolkata) |

---

## 🗺️ Roadmap (Post-MVP)

- [ ] Volunteer self-service portal (login, accept/decline assignments)
- [ ] Email/WhatsApp notifications on new assignment
- [ ] ML-based skill extraction from free-text bio
- [ ] Map view of opportunities (Leaflet.js)
- [ ] Impact reports PDF export for NGOs
- [ ] Multi-language support (Hindi, Marathi, Tamil, …)

---

## 📽️ Demo Video

> _Record a 3–5 minute walkthrough: Dashboard → Register Volunteer → Post Opportunity → Smart Match → Assign → Log Hours → Impact KPIs._  
> Upload to YouTube/Drive and paste the link here.

---

## 🔗 Links

| Resource | Link |
|---|---|
| GitHub Repository | https://github.com/hvsbombay/project |
| Live MVP | *(deploy to Render / Railway / HuggingFace Spaces and paste link here)* |
| Project Deck | *(paste PowerPoint / Google Slides link here)* |
| Demo Video | *(paste video link here)* |

---

## 👥 Team

> Add team member names, roles, and contact details here.

---

*Built with ❤️ for the HVS Bombay Hackathon 2026.*

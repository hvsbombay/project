"""
Database initialization and helper functions for VolunteerMatch.
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "volunteerdb.sqlite")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS volunteers (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            email       TEXT UNIQUE NOT NULL,
            phone       TEXT,
            city        TEXT NOT NULL,
            skills      TEXT NOT NULL,   -- comma-separated list
            availability TEXT NOT NULL,  -- JSON array of weekday names
            hours_week  INTEGER DEFAULT 5,
            bio         TEXT,
            joined_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
            active      INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS opportunities (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            title        TEXT NOT NULL,
            organization TEXT NOT NULL,
            city         TEXT NOT NULL,
            category     TEXT NOT NULL,
            description  TEXT,
            required_skills TEXT NOT NULL,  -- comma-separated
            schedule     TEXT NOT NULL,     -- JSON array of weekday names
            volunteers_needed INTEGER DEFAULT 1,
            start_date   TEXT,
            end_date     TEXT,
            created_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
            active       INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS assignments (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            volunteer_id    INTEGER NOT NULL REFERENCES volunteers(id),
            opportunity_id  INTEGER NOT NULL REFERENCES opportunities(id),
            match_score     REAL DEFAULT 0,
            status          TEXT DEFAULT 'pending',  -- pending/confirmed/completed/cancelled
            assigned_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
            hours_logged    REAL DEFAULT 0,
            UNIQUE(volunteer_id, opportunity_id)
        );

        CREATE TABLE IF NOT EXISTS impact_logs (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            assignment_id INTEGER NOT NULL REFERENCES assignments(id),
            hours         REAL NOT NULL,
            note          TEXT,
            logged_at     DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)

    conn.commit()
    conn.close()


def seed_demo_data():
    """Insert realistic demo data if tables are empty."""
    conn = get_db()
    cursor = conn.cursor()

    if cursor.execute("SELECT COUNT(*) FROM volunteers").fetchone()[0] > 0:
        conn.close()
        return  # already seeded

    volunteers = [
        ("Aarav Mehta",    "aarav@example.com",   "9876543210", "Mumbai",    "Teaching,Mentoring,Python",         '["Saturday","Sunday"]',       8,  "Passionate about education."),
        ("Priya Sharma",   "priya@example.com",   "9876543211", "Delhi",     "Healthcare,First Aid,Communication","[\"Saturday\",\"Wednesday\"]", 6,  "Nurse with 5 years experience."),
        ("Riya Patel",     "riya@example.com",    "9876543212", "Mumbai",    "Design,Social Media,Photography",   '["Friday","Saturday"]',        4,  "Graphic designer helping NGOs."),
        ("Karan Singh",    "karan@example.com",   "9876543213", "Bangalore", "Teaching,Mathematics,Python",       '["Sunday","Tuesday"]',         10, "Software engineer & maths tutor."),
        ("Sneha Reddy",    "sneha@example.com",   "9876543214", "Hyderabad", "Logistics,Driving,Communication",   '["Monday","Saturday"]',        6,  "Supply chain professional."),
        ("Amit Joshi",     "amit@example.com",    "9876543215", "Pune",      "Healthcare,Yoga,First Aid",         '["Saturday","Sunday"]',        5,  "Yoga instructor & wellness coach."),
        ("Neha Gupta",     "neha@example.com",    "9876543216", "Delhi",     "Teaching,English,Communication",    '["Wednesday","Saturday"]',     7,  "English teacher for underprivileged."),
        ("Raj Kumar",      "raj@example.com",     "9876543217", "Chennai",   "Carpentry,Construction,Driving",    '["Saturday","Sunday"]',        8,  "Civil engineer volunteering on weekends."),
        ("Sonal Verma",    "sonal@example.com",   "9876543218", "Mumbai",    "Social Media,Photography,Design",   '["Friday","Saturday","Sunday"]',3,  "Digital marketer for nonprofits."),
        ("Vikram Nair",    "vikram@example.com",  "9876543219", "Bangalore", "Python,Data Analysis,Mentoring",    '["Sunday"]',                   4,  "Data scientist passionate about social good."),
        ("Divya Iyer",     "divya@example.com",   "9876543220", "Chennai",   "Healthcare,Nutrition,Communication","[\"Monday\",\"Thursday\"]",    6,  "Nutritionist working with communities."),
        ("Rohit Das",      "rohit@example.com",   "9876543221", "Kolkata",   "Teaching,Science,Mentoring",        '["Saturday","Sunday"]',        9,  "Physics teacher inspiring students."),
    ]

    cursor.executemany(
        "INSERT INTO volunteers (name,email,phone,city,skills,availability,hours_week,bio) VALUES (?,?,?,?,?,?,?,?)",
        volunteers
    )

    opportunities = [
        ("Digital Literacy Bootcamp",  "Teach India Foundation",  "Mumbai",    "Education",
         "Teach basic computer skills to underprivileged youth.",
         "Teaching,Python,Communication", '["Saturday","Sunday"]',  4, "2026-05-01", "2026-07-31"),

        ("Mobile Health Camp",         "HealthBridge NGO",        "Delhi",     "Healthcare",
         "Conduct free health check-ups in rural areas.",
         "Healthcare,First Aid,Communication", '["Saturday"]',       3, "2026-04-20", "2026-06-30"),

        ("NGO Brand Revamp",           "GreenRoots Trust",        "Mumbai",    "Design",
         "Redesign social media assets and website banners.",
         "Design,Social Media,Photography", '["Friday","Saturday"]', 2, "2026-05-01", "2026-05-31"),

        ("Math Tutoring Program",      "EduReach Foundation",     "Bangalore", "Education",
         "Weekend maths tutoring for Class 8-10 students.",
         "Teaching,Mathematics", '["Sunday"]',                        2, "2026-04-25", "2026-08-31"),

        ("Food Relief Distribution",   "Hunger-Free India",       "Hyderabad", "Relief",
         "Coordinate food packet distribution to slum areas.",
         "Logistics,Driving,Communication", '["Monday","Saturday"]',  5, "2026-04-18", "2026-12-31"),

        ("Yoga & Wellness Camp",       "WellnessFirst NGO",       "Pune",      "Healthcare",
         "Free yoga sessions for elderly community members.",
         "Yoga,Healthcare,Communication", '["Saturday","Sunday"]',    3, "2026-05-05", "2026-09-30"),

        ("English Speaking Club",      "BridgeWords Society",     "Delhi",     "Education",
         "Run weekly spoken-English sessions for job-seekers.",
         "Teaching,English,Communication", '["Wednesday","Saturday"]', 2, "2026-04-22", "2026-10-31"),

        ("Community Housing Repair",   "Rebuild India Trust",     "Chennai",   "Construction",
         "Help repair homes damaged by floods.",
         "Carpentry,Construction,Driving", '["Saturday","Sunday"]',   4, "2026-05-10", "2026-06-30"),

        ("Social Impact Story Project","ImpactNarrators",         "Mumbai",    "Media",
         "Document and share NGO success stories on social media.",
         "Photography,Social Media,Design", '["Friday","Saturday","Sunday"]', 2, "2026-05-01", "2026-07-31"),

        ("Data for Good Hackathon",    "DataKind India",          "Bangalore", "Technology",
         "Analyse NGO datasets to surface actionable insights.",
         "Python,Data Analysis,Mentoring", '["Sunday"]',              1, "2026-06-01", "2026-06-01"),

        ("Child Nutrition Drive",      "NourishNext Foundation",  "Chennai",   "Healthcare",
         "Run nutrition awareness sessions in government schools.",
         "Healthcare,Nutrition,Communication", '["Monday","Thursday"]', 3, "2026-05-01", "2026-09-30"),

        ("Science Fair Mentorship",    "Curious Minds NGO",       "Kolkata",   "Education",
         "Guide students preparing science fair projects.",
         "Teaching,Science,Mentoring", '["Saturday","Sunday"]',       3, "2026-05-15", "2026-08-31"),
    ]

    cursor.executemany(
        """INSERT INTO opportunities
           (title,organization,city,category,description,required_skills,schedule,volunteers_needed,start_date,end_date)
           VALUES (?,?,?,?,?,?,?,?,?,?)""",
        opportunities
    )

    # Seed some confirmed assignments with logged hours
    assignments_data = [
        (1, 1, 0.92, "confirmed", 14),
        (2, 2, 0.88, "confirmed", 10),
        (3, 3, 0.85, "confirmed", 6),
        (4, 4, 0.91, "confirmed", 18),
        (5, 5, 0.87, "confirmed", 12),
        (6, 6, 0.90, "confirmed", 9),
        (7, 7, 0.89, "confirmed", 8),
        (8, 8, 0.84, "completed", 22),
        (9, 9, 0.86, "completed", 5),
        (10,10, 0.93, "completed", 16),
        (11,11, 0.88, "confirmed", 11),
        (12,12, 0.91, "confirmed", 20),
    ]
    cursor.executemany(
        "INSERT INTO assignments (volunteer_id,opportunity_id,match_score,status,hours_logged) VALUES (?,?,?,?,?)",
        assignments_data
    )

    conn.commit()
    conn.close()

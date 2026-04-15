"""
VolunteerMatch — Smart Resource Allocation for Social Impact
Flask REST API + Server-Side Rendered Frontend
"""
from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from database import init_db, seed_demo_data, get_db
import json
import math

import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "volunteermatch-dev-secret-change-in-prod")

# Custom Jinja2 filter so templates can parse JSON strings stored in the DB
app.jinja_env.filters["from_json"] = json.loads


# ---------------------------------------------------------------------------
# Matching engine
# ---------------------------------------------------------------------------

def compute_match_score(volunteer, opportunity):
    """Return a 0–1 match score based on skills, availability and city."""
    vol_skills   = {s.strip().lower() for s in volunteer["skills"].split(",")}
    req_skills   = {s.strip().lower() for s in opportunity["required_skills"].split(",")}
    vol_avail    = set(json.loads(volunteer["availability"]))
    opp_schedule = set(json.loads(opportunity["schedule"]))

    # Skill overlap (50 % weight)
    if req_skills:
        skill_score = len(vol_skills & req_skills) / len(req_skills)
    else:
        skill_score = 1.0

    # Availability overlap (35 % weight)
    if opp_schedule:
        avail_score = len(vol_avail & opp_schedule) / len(opp_schedule)
    else:
        avail_score = 1.0

    # City match (15 % weight)
    city_score = 1.0 if volunteer["city"].lower() == opportunity["city"].lower() else 0.0

    return round(0.50 * skill_score + 0.35 * avail_score + 0.15 * city_score, 4)


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    conn = get_db()
    total_vols   = conn.execute("SELECT COUNT(*) FROM volunteers WHERE active=1").fetchone()[0]
    total_opps   = conn.execute("SELECT COUNT(*) FROM opportunities WHERE active=1").fetchone()[0]
    total_assign = conn.execute("SELECT COUNT(*) FROM assignments WHERE status IN ('confirmed','completed')").fetchone()[0]
    total_hours  = conn.execute("SELECT COALESCE(SUM(hours_logged),0) FROM assignments").fetchone()[0]
    categories   = conn.execute(
        "SELECT category, COUNT(*) as cnt FROM opportunities WHERE active=1 GROUP BY category ORDER BY cnt DESC"
    ).fetchall()
    recent_matches = conn.execute("""
        SELECT a.id, v.name as vol_name, o.title as opp_title,
               a.match_score, a.status, a.assigned_at
        FROM assignments a
        JOIN volunteers v ON v.id = a.volunteer_id
        JOIN opportunities o ON o.id = a.opportunity_id
        ORDER BY a.assigned_at DESC LIMIT 6
    """).fetchall()
    conn.close()
    return render_template("index.html",
        total_vols=total_vols, total_opps=total_opps,
        total_assign=total_assign, total_hours=int(total_hours),
        categories=[dict(r) for r in categories],
        recent_matches=recent_matches)


@app.route("/volunteers")
def volunteers():
    conn = get_db()
    city_filter  = request.args.get("city", "")
    skill_filter = request.args.get("skill", "")
    query = "SELECT * FROM volunteers WHERE active=1"
    params = []
    if city_filter:
        query += " AND city=?"; params.append(city_filter)
    if skill_filter:
        query += " AND skills LIKE ?"; params.append(f"%{skill_filter}%")
    query += " ORDER BY joined_at DESC"
    vols  = conn.execute(query, params).fetchall()
    cities = conn.execute("SELECT DISTINCT city FROM volunteers ORDER BY city").fetchall()
    conn.close()
    return render_template("volunteers.html", volunteers=vols, cities=cities,
                           city_filter=city_filter, skill_filter=skill_filter)


@app.route("/volunteers/add", methods=["GET", "POST"])
def add_volunteer():
    if request.method == "POST":
        data = request.form
        skills = ",".join([s.strip() for s in data["skills"].split(",") if s.strip()])
        availability = json.dumps(request.form.getlist("availability"))
        conn = get_db()
        try:
            conn.execute(
                "INSERT INTO volunteers (name,email,phone,city,skills,availability,hours_week,bio) VALUES (?,?,?,?,?,?,?,?)",
                (data["name"], data["email"], data.get("phone",""), data["city"],
                 skills, availability, int(data.get("hours_week", 5)), data.get("bio",""))
            )
            conn.commit()
            flash("Volunteer registered successfully!", "success")
        except Exception as e:
            flash(f"Error: {e}", "danger")
        finally:
            conn.close()
        return redirect(url_for("volunteers"))
    return render_template("add_volunteer.html")


@app.route("/opportunities")
def opportunities():
    conn = get_db()
    city_filter = request.args.get("city", "")
    cat_filter  = request.args.get("category", "")
    query  = "SELECT * FROM opportunities WHERE active=1"
    params = []
    if city_filter:
        query += " AND city=?"; params.append(city_filter)
    if cat_filter:
        query += " AND category=?"; params.append(cat_filter)
    query += " ORDER BY created_at DESC"
    opps       = conn.execute(query, params).fetchall()
    cities     = conn.execute("SELECT DISTINCT city FROM opportunities ORDER BY city").fetchall()
    categories = conn.execute("SELECT DISTINCT category FROM opportunities ORDER BY category").fetchall()
    conn.close()
    return render_template("opportunities.html", opportunities=opps, cities=cities,
                           categories=categories, city_filter=city_filter, cat_filter=cat_filter)


@app.route("/opportunities/add", methods=["GET", "POST"])
def add_opportunity():
    if request.method == "POST":
        data = request.form
        req_skills = ",".join([s.strip() for s in data["required_skills"].split(",") if s.strip()])
        schedule   = json.dumps(request.form.getlist("schedule"))
        conn = get_db()
        try:
            conn.execute(
                """INSERT INTO opportunities
                   (title,organization,city,category,description,required_skills,schedule,volunteers_needed,start_date,end_date)
                   VALUES (?,?,?,?,?,?,?,?,?,?)""",
                (data["title"], data["organization"], data["city"], data["category"],
                 data.get("description",""), req_skills, schedule,
                 int(data.get("volunteers_needed", 1)),
                 data.get("start_date",""), data.get("end_date",""))
            )
            conn.commit()
            flash("Opportunity added successfully!", "success")
        except Exception as e:
            flash(f"Error: {e}", "danger")
        finally:
            conn.close()
        return redirect(url_for("opportunities"))
    return render_template("add_opportunity.html")


@app.route("/match")
def match():
    conn = get_db()
    volunteers_list  = conn.execute("SELECT * FROM volunteers WHERE active=1").fetchall()
    opportunities_list = conn.execute("SELECT * FROM opportunities WHERE active=1").fetchall()

    # Build top-5 recommended pairings not yet assigned
    existing = {
        (r["volunteer_id"], r["opportunity_id"])
        for r in conn.execute("SELECT volunteer_id,opportunity_id FROM assignments").fetchall()
    }

    suggestions = []
    for v in volunteers_list:
        for o in opportunities_list:
            if (v["id"], o["id"]) in existing:
                continue
            score = compute_match_score(v, o)
            if score > 0.4:
                suggestions.append({
                    "volunteer": dict(v),
                    "opportunity": dict(o),
                    "score": score,
                    "score_pct": int(score * 100)
                })
    suggestions.sort(key=lambda x: x["score"], reverse=True)

    conn.close()
    return render_template("match.html",
                           suggestions=suggestions[:20],
                           volunteers=volunteers_list,
                           opportunities=opportunities_list)


@app.route("/assignments")
def assignments():
    conn = get_db()
    rows = conn.execute("""
        SELECT a.*, v.name as vol_name, v.city as vol_city,
               o.title as opp_title, o.organization, o.category
        FROM assignments a
        JOIN volunteers v ON v.id = a.volunteer_id
        JOIN opportunities o ON o.id = a.opportunity_id
        ORDER BY a.assigned_at DESC
    """).fetchall()
    conn.close()
    return render_template("assignments.html", assignments=rows)


@app.route("/assignments/log_hours/<int:assignment_id>", methods=["POST"])
def log_hours(assignment_id):
    hours = float(request.form.get("hours", 0))
    note  = request.form.get("note", "")
    conn  = get_db()
    conn.execute("UPDATE assignments SET hours_logged = hours_logged + ? WHERE id=?", (hours, assignment_id))
    conn.execute("INSERT INTO impact_logs (assignment_id,hours,note) VALUES (?,?,?)",
                 (assignment_id, hours, note))
    conn.commit()
    conn.close()
    flash(f"Logged {hours} hours successfully.", "success")
    return redirect(url_for("assignments"))


@app.route("/assignments/update_status/<int:assignment_id>", methods=["POST"])
def update_status(assignment_id):
    status = request.form.get("status")
    conn   = get_db()
    conn.execute("UPDATE assignments SET status=? WHERE id=?", (status, assignment_id))
    conn.commit()
    conn.close()
    return redirect(url_for("assignments"))


# ---------------------------------------------------------------------------
# REST API
# ---------------------------------------------------------------------------

@app.route("/api/match", methods=["POST"])
def api_match():
    """Return ranked opportunities for a given volunteer_id."""
    volunteer_id = request.json.get("volunteer_id")
    conn = get_db()
    volunteer = conn.execute("SELECT * FROM volunteers WHERE id=?", (volunteer_id,)).fetchone()
    if not volunteer:
        conn.close()
        return jsonify({"error": "Volunteer not found"}), 404
    opps = conn.execute("SELECT * FROM opportunities WHERE active=1").fetchall()
    existing = {
        r["opportunity_id"]
        for r in conn.execute("SELECT opportunity_id FROM assignments WHERE volunteer_id=?",
                              (volunteer_id,)).fetchall()
    }
    results = []
    for o in opps:
        if o["id"] in existing:
            continue
        score = compute_match_score(volunteer, o)
        results.append({**dict(o), "match_score": score, "match_pct": int(score * 100)})
    results.sort(key=lambda x: x["match_score"], reverse=True)
    conn.close()
    return jsonify(results[:10])


@app.route("/api/assign", methods=["POST"])
def api_assign():
    """Create an assignment between a volunteer and an opportunity."""
    data         = request.json
    volunteer_id = data.get("volunteer_id")
    opp_id       = data.get("opportunity_id")
    conn         = get_db()
    volunteer    = conn.execute("SELECT * FROM volunteers WHERE id=?", (volunteer_id,)).fetchone()
    opp          = conn.execute("SELECT * FROM opportunities WHERE id=?", (opp_id,)).fetchone()
    if not volunteer or not opp:
        conn.close()
        return jsonify({"error": "Invalid IDs"}), 400
    score = compute_match_score(volunteer, opp)
    try:
        conn.execute(
            "INSERT INTO assignments (volunteer_id,opportunity_id,match_score,status) VALUES (?,?,?,'confirmed')",
            (volunteer_id, opp_id, score)
        )
        conn.commit()
        flash("Assignment created successfully!", "success")
        result = {"status": "ok", "match_score": score}
    except Exception:
        result = {"error": "Could not create assignment. It may already exist."}
    conn.close()
    return jsonify(result)


@app.route("/api/stats")
def api_stats():
    conn = get_db()
    stats = {
        "total_volunteers":   conn.execute("SELECT COUNT(*) FROM volunteers WHERE active=1").fetchone()[0],
        "total_opportunities":conn.execute("SELECT COUNT(*) FROM opportunities WHERE active=1").fetchone()[0],
        "total_assignments":  conn.execute("SELECT COUNT(*) FROM assignments").fetchone()[0],
        "confirmed":          conn.execute("SELECT COUNT(*) FROM assignments WHERE status='confirmed'").fetchone()[0],
        "completed":          conn.execute("SELECT COUNT(*) FROM assignments WHERE status='completed'").fetchone()[0],
        "total_hours":        conn.execute("SELECT COALESCE(SUM(hours_logged),0) FROM assignments").fetchone()[0],
        "by_category":        [dict(r) for r in conn.execute(
            "SELECT o.category, COUNT(*) as cnt FROM assignments a JOIN opportunities o ON o.id=a.opportunity_id GROUP BY o.category"
        ).fetchall()],
        "by_city":            [dict(r) for r in conn.execute(
            "SELECT v.city, COUNT(*) as cnt FROM assignments a JOIN volunteers v ON v.id=a.volunteer_id GROUP BY v.city"
        ).fetchall()],
    }
    conn.close()
    return jsonify(stats)


@app.route("/api/volunteers")
def api_volunteers():
    conn = get_db()
    rows = conn.execute("SELECT * FROM volunteers WHERE active=1 ORDER BY name").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route("/api/opportunities")
def api_opportunities():
    conn = get_db()
    rows = conn.execute("SELECT * FROM opportunities WHERE active=1 ORDER BY title").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    init_db()
    seed_demo_data()
    app.run(debug=os.environ.get("FLASK_DEBUG", "0") == "1", port=5000)

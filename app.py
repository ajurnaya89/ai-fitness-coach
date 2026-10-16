# -*- coding: utf-8 -*-
"""
AI Fitness Coach - Visual Web Application.
Zero external dependencies (uses Python's standard library).
"""

import http.server
import json
import os
import socketserver
import urllib.parse
from datetime import datetime
from typing import Any, Dict, List, Optional

import database
import engine
import heart_rate
from models import CompletedWorkoutLog, ExerciseFeedback

DEFAULT_PORT = 8000
HOST = "127.0.0.1"

# Initialize database
database.init_db()

PLANS_CACHE_FILE = os.path.join(database.DB_DIR, "active_plans.json")


def load_cached_plans() -> Dict[str, Any]:
    """Loads active plans from disk or generates initial default states."""
    if os.path.exists(PLANS_CACHE_FILE):
        try:
            with open(PLANS_CACHE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict) and "strength" in data and isinstance(data["strength"], list) and len(data["strength"]) == 5:
                    return data
        except Exception:
            pass

    # Generate initial 5-day cycle if not present or incomplete
    profile = database.get_user_profile()
    initial_5days = engine.generate_5day_program(
        sex=profile.get("sex", "female"),
        level=profile.get("level", "intermediate"),
        location=profile.get("location", "home"),
        injuries_to_avoid=profile.get("injuries_to_avoid", []),
        goal=profile.get("goal", "muscle_gain"),
        current_weight=profile.get("current_weight", 75.0),
        target_weight=profile.get("target_weight", 72.0),
        workout_format=profile.get("workout_format", "superset"),
        trx_anchor=profile.get("trx_anchor", "door"),
        age=profile.get("age", 30),
        custom_max_hr=profile.get("max_hr"),
        equipment_inventory=profile.get("equipment_inventory"),
        medical_conditions=profile.get("medical_conditions")
    )
    initial_plans = {
        "strength": [p.to_dict() for p in initial_5days],
        "mobility": None,
        "rehab": None,
        "current_day_index": profile.get("rolling_split_index", 0)
    }
    save_cached_plans(initial_plans)
    return initial_plans


def save_cached_plans(plans_dict: Dict[str, Any]):
    """Saves active plans to disk to persist across server restarts."""
    try:
        with open(PLANS_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(plans_dict, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


ACTIVE_PLANS = load_cached_plans()


class FitnessAppHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP Request Handler for AI Fitness Coach Visual UI and API endpoints."""

    def _send_json(self, data: Any, status: int = 200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def do_GET(self):
        global ACTIVE_PLANS
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        if path in ["/", "/index.html"]:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode("utf-8"))

        elif path == "/api/exercises":
            exercises = database.get_all_exercises()
            history = database.get_exercise_history()
            data = []
            for ex in exercises:
                ex_dict = ex.to_dict()
                ex_dict["stats"] = history.get(ex.id, {
                    "times_performed": 0,
                    "last_performed_date": None,
                    "times_skipped": 0,
                    "avg_difficulty": None
                })
                data.append(ex_dict)
            self._send_json({"status": "ok", "exercises": data})

        elif path == "/api/history":
            workouts = database.get_recent_workouts(limit=30)
            self._send_json({"status": "ok", "workouts": workouts})

        elif path == "/api/stats":
            stats = database.get_progress_stats()
            self._send_json({"status": "ok", "stats": stats})

        elif path == "/api/profile":
            profile = database.get_user_profile()
            self._send_json({"status": "ok", "profile": profile})

        elif path == "/api/current-plan":
            self._send_json({
                "status": "ok",
                "plan": ACTIVE_PLANS.get("strength", []),
                "strength_plan": ACTIVE_PLANS.get("strength", []),
                "mobility_plan": ACTIVE_PLANS.get("mobility"),
                "rehab_plan": ACTIVE_PLANS.get("rehab"),
                "day_index": ACTIVE_PLANS.get("current_day_index", 0)
            })

        elif path == "/api/rehab/departments":
            depts = engine.get_rehab_departments()
            self._send_json({"status": "ok", "departments": depts})

        elif path == "/api/mobility/zones":
            from mobility_data import MOBILITY_ZONES
            zones_list = [
                {
                    "id": k,
                    "name_en": v["name_en"],
                    "name_ua": v["name_ua"],
                    "icon": v["icon"],
                    "default_reps": v["default_reps"]
                }
                for k, v in MOBILITY_ZONES.items()
            ]
            self._send_json({"status": "ok", "zones": zones_list})

        elif path == "/api/heart-rate/zones":
            profile = database.get_user_profile()
            zones_data = heart_rate.get_heart_rate_zones(
                age=profile.get("age", 30),
                custom_max_hr=profile.get("max_hr")
            )
            self._send_json({"status": "ok", "zones_data": zones_data})

        elif path == "/api/agent/info":
            import agent
            self._send_json({
                "status": "ok",
                "framework": "Google ADK (Agent Development Kit)",
                "root_agent": agent.root_agent.name,
                "model": agent.root_agent.model,
                "sub_agents": [a.name for a in agent.root_agent.sub_agents],
                "adk_available": agent.ADK_AVAILABLE
            })

        else:
            self.send_error(404, "File not found")

    def do_POST(self):
        global ACTIVE_PLANS
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else ""
        data = json.loads(body) if body else {}

        if path == "/api/profile":
            updated_profile = database.save_user_profile(data)
            # Reactively re-filter & regenerate active strength plan if restrictions or venue changed
            if any(k in data for k in ["injuries_to_avoid", "medical_conditions", "location", "sex", "trx_anchor", "equipment_inventory"]):
                new_5days = engine.generate_5day_program(
                    force_new_cycle=False,
                    sex=updated_profile.get("sex", "female"),
                    level=updated_profile.get("level", "intermediate"),
                    location=updated_profile.get("location", "home"),
                    injuries_to_avoid=updated_profile.get("injuries_to_avoid", []),
                    goal=updated_profile.get("goal", "muscle_gain"),
                    current_weight=updated_profile.get("current_weight", 75.0),
                    target_weight=updated_profile.get("target_weight", 72.0),
                    workout_format=updated_profile.get("workout_format", "superset"),
                    trx_anchor=updated_profile.get("trx_anchor", "door"),
                    age=updated_profile.get("age", 30),
                    custom_max_hr=updated_profile.get("max_hr"),
                    equipment_inventory=updated_profile.get("equipment_inventory"),
                    medical_conditions=updated_profile.get("medical_conditions")
                )
                ACTIVE_PLANS["strength"] = [p.to_dict() for p in new_5days]
                save_cached_plans(ACTIVE_PLANS)
            self._send_json({"status": "ok", "profile": updated_profile, "strength_plan": ACTIVE_PLANS.get("strength", [])})

        elif path == "/api/onboarding":
            data["onboarding_completed"] = 1
            updated_profile = database.save_user_profile(data)
            # Generate initial fresh 5-day cycle
            new_5days = engine.generate_5day_program(
                force_new_cycle=True,
                sex=updated_profile.get("sex", "female"),
                level=updated_profile.get("level", "intermediate"),
                location=updated_profile.get("location", "home"),
                injuries_to_avoid=updated_profile.get("injuries_to_avoid", []),
                goal=updated_profile.get("goal", "muscle_gain"),
                current_weight=updated_profile.get("current_weight", 75.0),
                target_weight=updated_profile.get("target_weight", 72.0),
                workout_format=updated_profile.get("workout_format", "superset"),
                trx_anchor=updated_profile.get("trx_anchor", "door"),
                age=updated_profile.get("age", 30),
                custom_max_hr=updated_profile.get("max_hr"),
                equipment_inventory=updated_profile.get("equipment_inventory"),
                medical_conditions=updated_profile.get("medical_conditions")
            )
            ACTIVE_PLANS["strength"] = [p.to_dict() for p in new_5days]
            ACTIVE_PLANS["current_day_index"] = 0
            database.set_rolling_split_index(0)
            save_cached_plans(ACTIVE_PLANS)
            self._send_json({
                "status": "ok",
                "profile": updated_profile,
                "strength_plan": ACTIVE_PLANS["strength"],
                "day_index": 0
            })

        elif path == "/api/generate":
            force_new_cycle = bool(data.get("force_new_cycle", False))
            exclude_ids = data.get("exclude_ids", [])
            profile = database.get_user_profile()

            level = data.get("level", profile.get("level", "intermediate"))
            location = data.get("location", profile.get("location", "home"))
            injuries = data.get("injuries_to_avoid", profile.get("injuries_to_avoid", []))
            meds = data.get("medical_conditions", profile.get("medical_conditions", []))
            equip = data.get("equipment_inventory", profile.get("equipment_inventory", []))
            goal = data.get("goal", profile.get("goal", "muscle_gain"))
            current_weight = float(data.get("current_weight", profile.get("current_weight", 75.0)))
            target_weight = float(data.get("target_weight", profile.get("target_weight", 72.0)))
            workout_format = data.get("workout_format", profile.get("workout_format", "superset"))
            trx_anchor = data.get("trx_anchor", profile.get("trx_anchor", "door"))
            age = int(data.get("age", profile.get("age", 30)))
            custom_max_hr = int(data["custom_max_hr"]) if data.get("custom_max_hr") else profile.get("max_hr")
            sex = data.get("sex", profile.get("sex", "female"))

            database.save_user_profile({
                "sex": sex, "level": level, "location": location, "injuries_to_avoid": injuries,
                "medical_conditions": meds, "equipment_inventory": equip,
                "goal": goal, "current_weight": current_weight, "target_weight": target_weight,
                "workout_format": workout_format, "trx_anchor": trx_anchor,
                "age": age, "max_hr": custom_max_hr
            })

            new_5days = engine.generate_5day_program(
                force_new_cycle=force_new_cycle,
                exclude_ids=exclude_ids,
                sex=sex,
                level=level,
                location=location,
                injuries_to_avoid=injuries,
                goal=goal,
                current_weight=current_weight,
                target_weight=target_weight,
                workout_format=workout_format,
                trx_anchor=trx_anchor,
                age=age,
                custom_max_hr=custom_max_hr,
                equipment_inventory=equip,
                medical_conditions=meds
            )
            ACTIVE_PLANS["strength"] = [p.to_dict() for p in new_5days]
            if force_new_cycle:
                ACTIVE_PLANS["current_day_index"] = 0
                database.set_rolling_split_index(0)
            save_cached_plans(ACTIVE_PLANS)
            self._send_json({
                "status": "ok",
                "strength_plan": ACTIVE_PLANS["strength"],
                "day_index": ACTIVE_PLANS.get("current_day_index", 0)
            })

        elif path == "/api/strength/set-day":
            day_idx = int(data.get("day_index", 0))
            safe_idx = max(0, min(4, day_idx))
            ACTIVE_PLANS["current_day_index"] = safe_idx
            database.set_rolling_split_index(safe_idx)
            save_cached_plans(ACTIVE_PLANS)
            self._send_json({"status": "ok", "day_index": safe_idx})

        elif path == "/api/generate-custom":
            focus_areas = data.get("focus_areas", ["abs", "chest", "arms", "shoulders"])
            profile = database.get_user_profile()
            level = data.get("level", profile.get("level", "intermediate"))
            location = data.get("location", profile.get("location", "home"))
            injuries = data.get("injuries_to_avoid", profile.get("injuries_to_avoid", []))
            goal = data.get("goal", profile.get("goal", "muscle_gain"))
            current_weight = float(data.get("current_weight", profile.get("current_weight", 75.0)))
            target_weight = float(data.get("target_weight", profile.get("target_weight", 72.0)))
            workout_format = data.get("workout_format", profile.get("workout_format", "superset"))
            trx_anchor = data.get("trx_anchor", profile.get("trx_anchor", "door"))
            age = int(data.get("age", profile.get("age", 30)))
            custom_max_hr = int(data["custom_max_hr"]) if data.get("custom_max_hr") else profile.get("max_hr")
            sex = data.get("sex", profile.get("sex", "female"))

            custom_plan = engine.generate_custom_workout(
                focus_areas=focus_areas,
                level=level,
                location=location,
                injuries_to_avoid=injuries,
                goal=goal,
                current_weight=current_weight,
                target_weight=target_weight,
                workout_format=workout_format,
                trx_anchor=trx_anchor,
                age=age,
                custom_max_hr=custom_max_hr,
                sex=sex
            )
            custom_dict = custom_plan.to_dict()
            curr_idx = ACTIVE_PLANS.get("current_day_index", 0)
            if ACTIVE_PLANS.get("strength") and 0 <= curr_idx < len(ACTIVE_PLANS["strength"]):
                ACTIVE_PLANS["strength"][curr_idx] = custom_dict
            else:
                ACTIVE_PLANS["strength"] = [custom_dict]
                ACTIVE_PLANS["current_day_index"] = 0
            save_cached_plans(ACTIVE_PLANS)
            self._send_json({
                "status": "ok",
                "strength_plan": ACTIVE_PLANS["strength"],
                "custom_workout": custom_dict,
                "day_index": ACTIVE_PLANS.get("current_day_index", 0)
            })

        elif path == "/api/mobility/generate":
            focus_zones = data.get("focus_zones", [])
            profile = database.get_user_profile()
            location = data.get("location", profile.get("location", "home"))
            injuries = data.get("injuries_to_avoid", profile.get("injuries_to_avoid", []))
            level = data.get("level", profile.get("level", "intermediate"))
            age = int(data.get("age", profile.get("age", 30)))
            custom_max_hr = int(data["custom_max_hr"]) if data.get("custom_max_hr") else profile.get("max_hr")
            exclude_ids = data.get("exclude_ids", [])

            mob_plan = engine.generate_mobility_routine(
                focus_zones=focus_zones,
                location=location,
                injuries_to_avoid=injuries,
                level=level,
                age=age,
                custom_max_hr=custom_max_hr,
                sex=profile.get("sex", "female"),
                exclude_ids=exclude_ids
            )
            mob_dict = mob_plan.to_dict()
            ACTIVE_PLANS["mobility"] = mob_dict
            save_cached_plans(ACTIVE_PLANS)
            self._send_json({
                "status": "ok",
                "mobility_plan": mob_dict,
                "mobility_workout": mob_dict
            })

        elif path == "/api/rehab/generate":
            department = data.get("department", "pelvic_floor_diastasis")
            profile = database.get_user_profile()
            location = data.get("location", profile.get("location", "home"))
            injuries = data.get("injuries_to_avoid", profile.get("injuries_to_avoid", []))
            level = data.get("level", profile.get("level", "intermediate"))
            age = int(data.get("age", profile.get("age", 30)))
            custom_max_hr = int(data["custom_max_hr"]) if data.get("custom_max_hr") else profile.get("max_hr")
            exclude_ids = data.get("exclude_ids", [])

            rehab_plan = engine.generate_rehab_routine(
                department=department,
                location=location,
                injuries_to_avoid=injuries,
                level=level,
                age=age,
                custom_max_hr=custom_max_hr,
                exclude_ids=exclude_ids
            )
            rehab_dict = rehab_plan.to_dict()
            ACTIVE_PLANS["rehab"] = rehab_dict
            save_cached_plans(ACTIVE_PLANS)
            self._send_json({
                "status": "ok",
                "rehab_plan": rehab_dict,
                "rehab_workout": rehab_dict
            })

        elif path == "/api/toggle-exercise-complete":
            plan_type = data.get("plan_type", "strength")  # strength, mobility, rehab
            day_idx = int(data.get("day_index", 0))
            ex_id = data.get("exercise_id")
            completed = bool(data.get("completed", False))
            reps = str(data.get("actual_reps", ""))
            weight = str(data.get("actual_weight", ""))

            target_list = []
            if plan_type == "strength":
                s_plan = ACTIVE_PLANS.get("strength", [])
                if 0 <= day_idx < len(s_plan):
                    target_list = s_plan[day_idx].get("exercises", [])
            elif plan_type == "mobility":
                m_plan = ACTIVE_PLANS.get("mobility")
                if m_plan:
                    target_list = m_plan.get("exercises", [])
            elif plan_type == "rehab":
                r_plan = ACTIVE_PLANS.get("rehab")
                if r_plan:
                    target_list = r_plan.get("exercises", [])

            for ex in target_list:
                if ex.get("exercise_id") == ex_id:
                    ex["completed"] = completed
                    if reps:
                        ex["actual_reps"] = reps
                    if weight:
                        ex["actual_weight"] = weight
                    break

            save_cached_plans(ACTIVE_PLANS)
            self._send_json({"status": "ok"})

        elif path == "/api/complete":
            try:
                profile = database.get_user_profile()
                workout_id = data["workout_id"]
                avg_hr = data.get("avg_heart_rate")
                min_hr = data.get("min_heart_rate")
                max_hr = data.get("max_heart_rate")
                rpe = data.get("perceived_difficulty")

                if avg_hr:
                    try: avg_hr = int(avg_hr)
                    except: avg_hr = None
                if min_hr:
                    try: min_hr = int(min_hr)
                    except: min_hr = None
                if max_hr:
                    try: max_hr = int(max_hr)
                    except: max_hr = None
                if rpe:
                    try: rpe = int(rpe)
                    except: rpe = 3

                goal = data.get("goal") or profile.get("goal", "muscle_gain")
                fmt_type = data.get("format_type") or profile.get("workout_format", "standard")

                # Smartwatch Telemetry parameters
                watch_duration = data.get("watch_duration_minutes")
                if watch_duration:
                    try: watch_duration = int(watch_duration)
                    except: watch_duration = None

                active_cals = data.get("active_calories")
                if active_cals:
                    try: active_cals = int(active_cals)
                    except: active_cals = None

                total_cals = data.get("total_calories")
                if total_cals:
                    try: total_cals = int(total_cals)
                    except: total_cals = None

                z1 = data.get("zone1_mins")
                z2 = data.get("zone2_mins")
                z3 = data.get("zone3_mins")
                z4 = data.get("zone4_mins")
                z5 = data.get("zone5_mins")
                try: z1 = float(z1) if z1 is not None else None
                except: z1 = None
                try: z2 = float(z2) if z2 is not None else None
                except: z2 = None
                try: z3 = float(z3) if z3 is not None else None
                except: z3 = None
                try: z4 = float(z4) if z4 is not None else None
                except: z4 = None
                try: z5 = float(z5) if z5 is not None else None
                except: z5 = None

                training_load = data.get("training_load")
                if training_load:
                    try: training_load = float(training_load)
                    except: training_load = None

                recovery_hours = data.get("recovery_time_hours")
                if recovery_hours:
                    try: recovery_hours = int(recovery_hours)
                    except: recovery_hours = None

                hr_analysis = None
                hr_zone_achieved = 0
                hr_goal_achieved = False
                hr_analysis_feedback = ""

                if (avg_hr and avg_hr > 0) or (min_hr and min_hr > 0) or (max_hr and max_hr > 0) or active_cals or any([z1, z2, z3, z4, z5]):
                    hr_analysis = heart_rate.analyze_workout_heart_rate(
                        avg_hr=avg_hr,
                        max_hr_recorded=max_hr,
                        min_hr_recorded=min_hr,
                        perceived_difficulty=rpe,
                        goal=goal,
                        workout_format=fmt_type,
                        age=profile.get("age", 30),
                        custom_max_hr=profile.get("max_hr"),
                        medical_conditions=profile.get("medical_conditions", []),
                        watch_duration_minutes=watch_duration,
                        active_calories=active_cals,
                        total_calories=total_cals,
                        zone1_mins=z1,
                        zone2_mins=z2,
                        zone3_mins=z3,
                        zone4_mins=z4,
                        zone5_mins=z5,
                        watch_training_load=training_load,
                        recovery_time_hours=recovery_hours
                    )
                    hr_zone_achieved = hr_analysis["achieved_zone"]
                    hr_goal_achieved = hr_analysis["goal_achieved"]
                    hr_analysis_feedback = hr_analysis["feedback_en"]

                dominant_zone = None
                if hr_analysis and hr_analysis.get("dominant_zone"):
                    dominant_zone = hr_analysis["dominant_zone"]
                elif any(v is not None and v > 0 for v in [z1, z2, z3, z4, z5]):
                    z_map = {"Zone 1": z1 or 0, "Zone 2": z2 or 0, "Zone 3": z3 or 0, "Zone 4": z4 or 0, "Zone 5": z5 or 0}
                    dominant_zone = max(z_map, key=z_map.get)

                telemetry_json = json.dumps(hr_analysis) if hr_analysis else None

                exercise_logs = [
                    ExerciseFeedback(
                        exercise_id=el["exercise_id"],
                        sets_completed=int(el.get("sets_completed", 3)),
                        reps_completed=str(el.get("reps_completed", "10-12")),
                        weight_used=str(el.get("weight_used", "Bodyweight")),
                        skipped=bool(el.get("skipped", False)),
                        perceived_difficulty=int(el.get("perceived_difficulty", 3)),
                        notes=str(el.get("notes", ""))
                    )
                    for el in data.get("exercise_logs", [])
                ]

                log = CompletedWorkoutLog(
                    workout_id=workout_id,
                    date_completed=data.get("date_completed", datetime.now().strftime("%Y-%m-%d")),
                    duration_minutes=int(data.get("duration_minutes", 60)),
                    overall_rating=int(data.get("overall_rating", 4)),
                    overall_fatigue=int(data.get("overall_fatigue", 3)),
                    user_notes=data.get("user_notes", ""),
                    min_heart_rate=min_hr,
                    max_heart_rate=max_hr,
                    avg_heart_rate=avg_hr,
                    hr_zone_achieved=hr_zone_achieved,
                    hr_goal_achieved=hr_goal_achieved,
                    hr_analysis_feedback=hr_analysis_feedback,
                    watch_duration_minutes=watch_duration,
                    active_calories=active_cals,
                    total_calories=total_cals,
                    zone1_mins=z1,
                    zone2_mins=z2,
                    zone3_mins=z3,
                    zone4_mins=z4,
                    zone5_mins=z5,
                    dominant_zone=dominant_zone,
                    training_load=training_load,
                    recovery_time_hours=recovery_hours,
                    telemetry_analysis=telemetry_json,
                    exercise_logs=exercise_logs
                )
                database.save_completed_workout(log)
                self._send_json({
                    "status": "ok",
                    "message": "Workout saved successfully!",
                    "hr_analysis": hr_analysis
                })
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode("utf-8"))

        elif path == "/api/heart-rate/analyze":
            profile = database.get_user_profile()
            avg_hr = int(data["avg_hr"]) if data.get("avg_hr") else None
            max_hr_rec = int(data["max_hr_recorded"]) if data.get("max_hr_recorded") else None
            min_hr_rec = int(data["min_hr_recorded"]) if data.get("min_hr_recorded") else None
            rpe = int(data["perceived_difficulty"]) if data.get("perceived_difficulty") else 3
            goal = data.get("goal") or profile.get("goal", "muscle_gain")
            fmt = data.get("workout_format") or profile.get("workout_format", "standard")
            age = int(data.get("age", profile.get("age", 30)))
            custom_max = int(data["custom_max_hr"]) if data.get("custom_max_hr") else profile.get("max_hr")

            analysis = heart_rate.analyze_workout_heart_rate(
                avg_hr=avg_hr,
                max_hr_recorded=max_hr_rec,
                min_hr_recorded=min_hr_rec,
                perceived_difficulty=rpe,
                goal=goal,
                workout_format=fmt,
                age=age,
                custom_max_hr=custom_max,
                medical_conditions=profile.get("medical_conditions", [])
            )
            self._send_json({"status": "ok", "analysis": analysis})

        else:
            self.send_error(404, "Endpoint not found")


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AI Fitness Coach</title>
  <style>
    :root {
      --bg: #0b1120;
      --card-bg: #1e293b;
      --border: #334155;
      --primary: #38bdf8;
      --primary-hover: #0284c7;
      --text: #f8fafc;
      --muted: #94a3b8;
      --accent: #10b981;
      --accent-soft: rgba(16, 185, 129, 0.15);
      --guide-bg: #0f172a;
      --danger: #ef4444;
      --warning: #f59e0b;
      --purple: #a855f7;
      --purple-soft: rgba(168, 85, 247, 0.15);
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background-color: var(--bg);
      color: var(--text);
      line-height: 1.5;
      padding: 16px;
    }
    .container { max-width: 1140px; margin: 0 auto; }
    header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-bottom: 16px;
      border-bottom: 1px solid var(--border);
      margin-bottom: 20px;
      flex-wrap: wrap;
      gap: 12px;
    }
    .header-title h1 { font-size: 24px; font-weight: 800; color: #fff; display: flex; align-items: center; gap: 8px; }
    .header-title p { color: var(--muted); font-size: 13px; margin-top: 2px; }
    .header-actions { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }

    .toggle-group {
      display: inline-flex;
      background: #0f172a;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 3px;
    }
    .toggle-btn {
      background: none;
      border: none;
      color: var(--muted);
      padding: 6px 12px;
      font-size: 13px;
      font-weight: 600;
      border-radius: 6px;
      cursor: pointer;
      transition: all 0.2s;
    }
    .toggle-btn.active {
      background: var(--card-bg);
      color: var(--primary);
      box-shadow: 0 1px 3px rgba(0,0,0,0.3);
    }
    .lang-btn {
      background: #0f172a;
      border: 1px solid var(--border);
      color: var(--muted);
      padding: 6px 10px;
      font-size: 12px;
      font-weight: 700;
      border-radius: 6px;
      cursor: pointer;
    }
    .lang-btn.active {
      background: var(--primary);
      color: #0b1120;
      border-color: var(--primary);
    }

    .btn {
      background: var(--primary);
      color: #0b1120;
      border: none;
      padding: 8px 16px;
      border-radius: 8px;
      font-weight: 700;
      font-size: 13px;
      cursor: pointer;
      transition: all 0.2s;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }
    .btn:hover { background: var(--primary-hover); color: white; }
    .btn-secondary { background: #1e293b; color: var(--text); border: 1px solid var(--border); }
    .btn-secondary:hover { background: #334155; }
    .btn-accent { background: var(--accent); color: #0b1120; }
    .btn-accent:hover { background: #059669; color: white; }
    .btn-purple { background: var(--purple); color: white; }
    .btn-purple:hover { background: #9333ea; }
    .btn-sm { padding: 5px 10px; font-size: 12px; }

    /* Top Navigation Tabs */
    .tabs {
      display: flex;
      gap: 8px;
      border-bottom: 2px solid var(--border);
      margin-bottom: 20px;
      overflow-x: auto;
      padding-bottom: 2px;
    }
    .tab-btn {
      background: none;
      border: none;
      color: var(--muted);
      padding: 10px 16px;
      font-size: 14px;
      font-weight: 700;
      cursor: pointer;
      border-bottom: 2px solid transparent;
      margin-bottom: -4px;
      transition: all 0.2s;
      white-space: nowrap;
      display: inline-flex;
      align-items: center;
      gap: 8px;
    }
    .tab-btn:hover { color: var(--text); }
    .tab-btn.active {
      color: var(--primary);
      border-bottom-color: var(--primary);
    }
    .tab-btn.mob.active {
      color: #34d399;
      border-bottom-color: #34d399;
    }
    .tab-btn.rehab.active {
      color: #c084fc;
      border-bottom-color: #c084fc;
    }

    /* Banners & Cards */
    .banner {
      background: linear-gradient(135deg, #0f233a 0%, #1e293b 100%);
      border: 1px solid #1e40af;
      border-radius: 12px;
      padding: 16px 20px;
      margin-bottom: 20px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 14px;
    }
    .banner-rehab {
      background: linear-gradient(135deg, #2e1065 0%, #1e293b 100%);
      border-color: #7e22ce;
    }
    .banner-mob {
      background: linear-gradient(135deg, #064e3b 0%, #1e293b 100%);
      border-color: #059669;
    }
    .banner-info h3 { font-size: 16px; font-weight: 800; color: #93c5fd; display: flex; align-items: center; gap: 8px; }
    .banner-rehab .banner-info h3 { color: #d8b4fe; }
    .banner-mob .banner-info h3 { color: #6ee7b7; }
    .banner-info p { font-size: 13px; color: #cbd5e1; margin-top: 4px; }
    .banner-controls { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }

    /* Day Selector Pills */
    .day-selector {
      display: flex;
      gap: 8px;
      overflow-x: auto;
      margin-bottom: 18px;
      padding-bottom: 4px;
    }
    .day-pill {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 10px 18px;
      cursor: pointer;
      white-space: nowrap;
      transition: all 0.2s;
      flex-shrink: 0;
    }
    .day-pill:hover { border-color: var(--primary); }
    .day-pill.active {
      background: rgba(56, 189, 248, 0.18);
      border-color: var(--primary);
      box-shadow: 0 0 12px rgba(56, 189, 248, 0.25);
    }
    .day-pill h4 { font-size: 14px; font-weight: 700; color: #fff; }
    .day-pill span { font-size: 11px; color: var(--muted); }

    /* Chips */
    .chips-group {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      margin-bottom: 16px;
    }
    .chip {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 20px;
      padding: 7px 14px;
      font-size: 13px;
      font-weight: 600;
      color: var(--text);
      cursor: pointer;
      transition: all 0.2s;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }
    .chip:hover { border-color: var(--primary); }
    .chip.active {
      background: rgba(56, 189, 248, 0.2);
      border-color: var(--primary);
      color: var(--primary);
    }
    .chip.active-purple {
      background: rgba(168, 85, 247, 0.2);
      border-color: var(--purple);
      color: #d8b4fe;
    }
    .chip.active-green {
      background: rgba(16, 185, 129, 0.2);
      border-color: var(--accent);
      color: #6ee7b7;
    }

    /* Sandwich Ladder Banner */
    .sandwich-box {
      background: #0f172a;
      border: 1px solid #eab308;
      border-radius: 10px;
      padding: 14px 16px;
      margin-bottom: 18px;
    }
    .sandwich-title { font-size: 14px; font-weight: 800; color: #fde047; margin-bottom: 8px; display: flex; align-items: center; gap: 6px; }
    .sandwich-grid { display: flex; flex-wrap: wrap; gap: 6px; }
    .ladder-chip {
      background: #1e293b;
      border: 1px solid #475569;
      border-radius: 6px;
      padding: 4px 8px;
      font-size: 11px;
      font-weight: 700;
      cursor: pointer;
      color: #cbd5e1;
      transition: all 0.15s;
    }
    .ladder-chip:hover { border-color: #fde047; }
    .ladder-chip.checked {
      background: #eab308;
      color: #000;
      border-color: #eab308;
    }

    /* Circuit Tracker */
    .circuit-box {
      background: #0f172a;
      border: 1px solid #38bdf8;
      border-radius: 10px;
      padding: 12px 16px;
      margin-bottom: 18px;
      display: flex;
      align-items: center;
      gap: 16px;
      flex-wrap: wrap;
    }
    .circuit-title { font-size: 13px; font-weight: 800; color: #7dd3fc; }
    .circuit-rounds { display: flex; gap: 10px; }
    .circuit-round-btn {
      background: #1e293b;
      border: 1px solid #334155;
      padding: 6px 12px;
      border-radius: 6px;
      font-size: 12px;
      font-weight: 700;
      cursor: pointer;
      color: #cbd5e1;
    }
    .circuit-round-btn.checked {
      background: #0284c7;
      color: #fff;
      border-color: #38bdf8;
    }

    /* Exercise Card */
    .superset-block {
      background: rgba(30, 41, 59, 0.4);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 14px;
      margin-bottom: 16px;
    }
    .superset-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;
      padding-bottom: 8px;
      border-bottom: 1px dashed var(--border);
    }
    .superset-title { font-size: 14px; font-weight: 800; color: #38bdf8; }
    .superset-badge { background: #0f172a; color: var(--muted); font-size: 11px; padding: 2px 8px; border-radius: 4px; font-weight: 600; }

    .card {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 14px;
      margin-bottom: 10px;
      transition: all 0.2s;
    }
    .card:hover { border-color: #475569; }
    .card.completed-card {
      border-color: var(--accent);
      background: rgba(16, 185, 129, 0.05);
    }
    .card-top {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 10px;
      margin-bottom: 8px;
      flex-wrap: wrap;
    }
    .ex-index { font-weight: 800; color: var(--primary); font-size: 14px; margin-right: 6px; }
    .exercise-title { font-size: 15px; font-weight: 700; color: #fff; }
    .badge {
      display: inline-block;
      padding: 3px 8px;
      border-radius: 5px;
      font-size: 11px;
      font-weight: 700;
      background: #0f172a;
      color: #cbd5e1;
      border: 1px solid var(--border);
    }
    .badge-zone { background: #1e3a8a; color: #bfdbfe; border-color: #3b82f6; }
    .badge-last-perf { background: #3b0764; color: #e9d5ff; border-color: #a855f7; }
    .badge-tip {
      background: rgba(245, 158, 11, 0.1);
      border-left: 3px solid #f59e0b;
      padding: 6px 10px;
      font-size: 12px;
      color: #fde68a;
      border-radius: 4px;
      margin: 8px 0;
    }
    .badge-alt {
      background: rgba(56, 189, 248, 0.1);
      border: 1px dashed #0284c7;
      padding: 6px 10px;
      font-size: 12px;
      color: #7dd3fc;
      border-radius: 6px;
      margin: 8px 0;
    }

    /* Form Guide */
    .form-guide-toggle {
      font-size: 12px;
      color: var(--primary);
      cursor: pointer;
      user-select: none;
      margin-top: 6px;
      display: inline-block;
    }
    .form-guide-content {
      display: none;
      margin-top: 8px;
      padding: 10px 12px;
      background: var(--guide-bg);
      border-radius: 8px;
      font-size: 12px;
      color: #cbd5e1;
      line-height: 1.6;
      border: 1px solid var(--border);
    }
    .form-guide-content.open { display: block; }
    .guide-step { margin-bottom: 6px; }
    .guide-label { font-weight: 700; color: var(--primary); margin-right: 4px; }
    .guide-tip-label { color: var(--warning); }

    /* Exercise Input Controls */
    .exercise-inputs {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-top: 12px;
      padding-top: 10px;
      border-top: 1px solid var(--border);
      flex-wrap: wrap;
    }
    .check-btn {
      background: #0f172a;
      border: 1px solid var(--border);
      color: var(--text);
      padding: 6px 14px;
      border-radius: 6px;
      font-size: 12px;
      font-weight: 700;
      cursor: pointer;
      transition: all 0.2s;
    }
    .check-btn.checked {
      background: var(--accent);
      color: #0b1120;
      border-color: var(--accent);
    }
    .input-group {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 12px;
      color: var(--muted);
    }
    .input-group input, .input-group select {
      background: #0f172a;
      border: 1px solid var(--border);
      color: #fff;
      padding: 5px 8px;
      border-radius: 6px;
      font-size: 12px;
    }

    /* Modals */
    .modal-overlay {
      position: fixed;
      top: 0; left: 0; right: 0; bottom: 0;
      background: rgba(0, 0, 0, 0.8);
      display: none;
      align-items: center;
      justify-content: center;
      z-index: 1000;
      padding: 16px;
    }
    .modal-overlay.open { display: flex; }
    .modal {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 14px;
      width: 100%;
      max-width: 620px;
      max-height: 90vh;
      overflow-y: auto;
      padding: 24px;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
    }
    .modal-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 18px;
      padding-bottom: 12px;
      border-bottom: 1px solid var(--border);
    }
    .modal-header h3 { font-size: 18px; font-weight: 800; color: #fff; }
    .close-btn { background: none; border: none; color: var(--muted); font-size: 20px; cursor: pointer; }
    .close-btn:hover { color: #fff; }

    /* Tabata Modal */
    .tabata-neon {
      text-align: center;
      padding: 10px 0;
    }
    .tabata-ex-name {
      font-size: 24px;
      font-weight: 800;
      color: #fff;
      margin-bottom: 4px;
      text-shadow: 0 0 12px rgba(56, 189, 248, 0.5);
    }
    .tabata-next-name {
      font-size: 14px;
      color: #94a3b8;
      margin-bottom: 16px;
    }
    .tabata-phase-pill {
      display: inline-block;
      padding: 6px 18px;
      border-radius: 20px;
      font-size: 15px;
      font-weight: 800;
      letter-spacing: 1px;
      text-transform: uppercase;
      margin-bottom: 12px;
    }
    .phase-work { background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid #10b981; }
    .phase-rest { background: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid #f59e0b; }
    .phase-intermission { background: rgba(56, 189, 248, 0.2); color: #7dd3fc; border: 1px solid #0284c7; }
    .tabata-digits {
      font-size: 84px;
      font-weight: 900;
      font-family: monospace;
      line-height: 1;
      margin-bottom: 14px;
      text-shadow: 0 0 20px currentColor;
    }
    .digits-work { color: #10b981; }
    .digits-rest { color: #f59e0b; }
    .digits-intermission { color: #38bdf8; }

    /* Toast */
    #toast {
      position: fixed;
      bottom: 24px;
      right: 24px;
      background: #1e293b;
      border: 1px solid var(--primary);
      color: #fff;
      padding: 12px 20px;
      border-radius: 8px;
      font-size: 13px;
      font-weight: 600;
      box-shadow: 0 4px 12px rgba(0,0,0,0.5);
      z-index: 2000;
      display: none;
    }
  </style>
</head>
<body>
  <div class="container">
    <!-- Header -->
    <header>
      <div class="header-title">
        <h1>🏋️ <span id="app-title-text">AI Fitness Coach</span></h1>
        <p id="app-subtitle-text">Intelligent Split & Restoration Programming</p>
      </div>
      <div class="header-actions">
        <!-- Gender / Sex Toggle -->
        <div class="toggle-group" id="sex-toggle-group">
          <button class="toggle-btn" id="btn-sex-female" onclick="setSex('female')">👩 Female</button>
          <button class="toggle-btn" id="btn-sex-male" onclick="setSex('male')">👨 Male</button>
        </div>

        <!-- Venue / Location Toggle -->
        <div class="toggle-group" id="loc-toggle-group">
          <button class="toggle-btn" id="btn-loc-home" onclick="setVenue('home')">🏠 Home</button>
          <button class="toggle-btn" id="btn-loc-gym" onclick="setVenue('gym')">🏋️ Gym</button>
        </div>

        <!-- Level Toggle -->
        <div class="toggle-group" id="level-toggle-group">
          <button class="toggle-btn" id="btn-lvl-int" onclick="setLevel('intermediate')">⚡ Inter</button>
          <button class="toggle-btn" id="btn-lvl-adv" onclick="setLevel('advanced')">🔥 Adv</button>
        </div>

        <!-- Language Toggle -->
        <div class="toggle-group">
          <button class="lang-btn" id="btn-lang-en" onclick="setLanguage('en')">EN</button>
          <button class="lang-btn" id="btn-lang-ua" onclick="setLanguage('ua')">UA</button>
        </div>

        <!-- Smartwatch Bluetooth Sync -->
        <button class="btn btn-secondary btn-sm" id="btn-watch-sync" onclick="connectSmartwatch()" title="Sync Web Bluetooth Heart Rate">⌚ <span id="btn-watch-text">Sync Watch</span></button>
        <span id="watch-live-hr" class="badge" style="display:none; background:#ef4444; color:#fff; font-weight:700;">❤️ <span id="watch-bpm-val">--</span> BPM</span>

        <!-- Settings Button -->
        <button class="btn btn-secondary btn-sm" onclick="openOnboardingModal()" title="Settings & Questionnaire">⚙️ <span id="btn-settings-text">Settings</span></button>
      </div>
    </header>

    <!-- Navigation Tabs -->
    <div class="tabs">
      <button class="tab-btn active" id="tab-workout" onclick="switchView('workout')">🏋️ <span id="tab-workout-text">Strength & Formats</span></button>
      <button class="tab-btn mob" id="tab-mobility" onclick="switchView('mobility')">🧘 <span id="tab-mob-text">Dynamic Mobility</span></button>
      <button class="tab-btn rehab" id="tab-rehab" onclick="switchView('rehab')">❤️‍🩹 <span id="tab-rehab-text">Rehabilitation</span></button>
      <button class="tab-btn" id="tab-progress" onclick="switchView('progress')">📊 <span id="tab-prog-text">Progress & History</span></button>
      <button class="tab-btn" id="tab-library" onclick="switchView('library')">📚 <span id="tab-lib-text">Exercise Library</span></button>
    </div>

    <!-- VIEW 1: STRENGTH WORKOUTS (5 DAYS + FORMATS) -->
    <div id="view-workout">
      <!-- 5-Day Navigation Pills -->
      <div class="day-selector" id="strength-day-pills">
        <div class="day-pill active" onclick="selectStrengthDay(0)"><h4 id="pill-d1">Day 1</h4><span id="pill-sub-d1">Split 1</span></div>
        <div class="day-pill" onclick="selectStrengthDay(1)"><h4 id="pill-d2">Day 2</h4><span id="pill-sub-d2">Split 2</span></div>
        <div class="day-pill" onclick="selectStrengthDay(2)"><h4 id="pill-d3">Day 3</h4><span id="pill-sub-d3">Split 3</span></div>
        <div class="day-pill" onclick="selectStrengthDay(3)"><h4 id="pill-d4">Day 4</h4><span id="pill-sub-d4">Split 4</span></div>
        <div class="day-pill" onclick="selectStrengthDay(4)"><h4 id="pill-d5">Day 5</h4><span id="pill-sub-d5">Split 5</span></div>
      </div>

      <!-- Workout Banner -->
      <div class="banner">
        <div class="banner-info">
          <h3 id="workout-day-title">▶️ Day 1: Strength Workout</h3>
          <p id="workout-day-desc">5 Supersets × 2 Exercises (10 Stations)</p>
          <div style="margin-top: 8px; display: flex; gap: 8px; align-items: center; flex-wrap: wrap;">
            <span class="badge" id="hr-target-badge" style="background: #1e3a8a; color: #93c5fd;">❤️ Target HR Zone</span>
            <span class="badge" id="format-badge" style="background: #374151; color: #f3f4f6;">Supersets</span>
          </div>
        </div>
        <div class="banner-controls">
          <button class="btn btn-accent" id="btn-next-day" onclick="nextDay()">Next Day (Day 2) ➡️</button>
          <button class="btn btn-secondary" onclick="regenerateCurrentPlan()">⚡ <span id="btn-regen-text">Regenerate</span></button>
          <select id="workout-format-select" class="btn btn-secondary" onchange="changeFormat(this.value)">
            <option value="superset">⚡ Supersets 5×2</option>
            <option value="antagonist">⚔️ Antagonist Pairs</option>
            <option value="sandwich">🥪 Sandwich Pyramid</option>
            <option value="circuit">🔁 Circuit (3 Rounds)</option>
            <option value="tabata">⏱️ Tabata Protocol</option>
            <option value="standard">🎯 Standard Sets</option>
          </select>
          <button class="btn btn-secondary" onclick="openFocusModal()">🎯 <span id="btn-focus-text">Focus Workout</span></button>
          <button class="btn btn-purple" id="btn-tabata-trigger" onclick="openTabataModal()" style="display: none;">⏱️ <span id="btn-tabata-text">Tabata Timer</span></button>
        </div>
      </div>

      <!-- Format Specific Interactive Displays -->
      <!-- Sandwich Pyramid Ladder Display -->
      <div id="sandwich-ladder-box" class="sandwich-box" style="display: none;">
        <div class="sandwich-title">🥪 <span id="sandwich-title-text">Sandwich Pyramid Ladder: Tap rounds as completed</span></div>
        <div class="sandwich-grid" id="sandwich-chips-container"></div>
      </div>

      <!-- Circuit Training Round Tracker -->
      <div id="circuit-tracker-box" class="circuit-box" style="display: none;">
        <div class="circuit-title">🔁 <span id="circuit-title-text">Circuit Rounds Tracker (15s transition between exercises):</span></div>
        <div class="circuit-rounds">
          <button class="circuit-round-btn" id="c-round-1" onclick="toggleCircuitRound(1)">Round 1 [ ]</button>
          <button class="circuit-round-btn" id="c-round-2" onclick="toggleCircuitRound(2)">Round 2 [ ]</button>
          <button class="circuit-round-btn" id="c-round-3" onclick="toggleCircuitRound(3)">Round 3 [ ]</button>
        </div>
      </div>

      <!-- Completion Counter -->
      <div style="margin-bottom: 14px;">
        <div style="display: flex; justify-content: space-between; font-size: 12px; color: var(--muted); margin-bottom: 4px;">
          <span id="strength-comp-label">Progress:</span>
          <span id="strength-comp-counter">0 / 10 Completed (0%)</span>
        </div>
        <div style="background: #1e293b; height: 6px; border-radius: 3px; overflow: hidden;">
          <div id="strength-comp-bar" style="background: var(--accent); width: 0%; height: 100%; transition: width 0.3s;"></div>
        </div>
      </div>

      <!-- Exercise Cards List -->
      <div id="strength-exercise-list"></div>

      <!-- Workout Completion Card (Smartwatch Telemetry Hub) -->
      <div class="card" style="margin-top: 24px; border: 1px solid #1e40af; background: #0f172a;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; flex-wrap: wrap; gap: 8px;">
          <div>
            <h3 style="font-size: 16px; font-weight: 800; color: #93c5fd;" id="complete-card-title">💾 Finish & Save Workout (Smartwatch Telemetry Hub)</h3>
            <p style="font-size: 12px; color: var(--muted); margin-top: 2px;" id="telemetry-hint">Log your Apple Watch / Garmin / Polar telemetry or sync live via Bluetooth:</p>
          </div>
          <button class="btn btn-secondary btn-sm" onclick="connectSmartwatch()" id="btn-card-sync">⌚ <span id="btn-card-sync-text">Live Bluetooth Sync</span></button>
        </div>

        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 12px; margin-bottom: 14px;">
          <div class="input-group" style="flex-direction: column; align-items: flex-start;">
            <label id="lbl-dur">Duration (min)</label>
            <input type="number" id="session-duration" value="55" style="width: 100%;">
          </div>
          <div class="input-group" style="flex-direction: column; align-items: flex-start;">
            <label id="lbl-min-hr">Min HR (BPM)</label>
            <input type="number" id="session-min-hr" placeholder="e.g. 105" style="width: 100%;">
          </div>
          <div class="input-group" style="flex-direction: column; align-items: flex-start;">
            <label id="lbl-avg-hr">Avg HR (BPM)</label>
            <input type="number" id="session-avg-hr" placeholder="e.g. 138" style="width: 100%;">
          </div>
          <div class="input-group" style="flex-direction: column; align-items: flex-start;">
            <label id="lbl-max-hr">Max HR (BPM)</label>
            <input type="number" id="session-max-hr" placeholder="e.g. 165" style="width: 100%;">
          </div>
          <div class="input-group" style="flex-direction: column; align-items: flex-start;">
            <label id="lbl-active-cals">Active Cals (kcal)</label>
            <input type="number" id="session-active-cals" placeholder="e.g. 380" style="width: 100%;">
          </div>
          <div class="input-group" style="flex-direction: column; align-items: flex-start;">
            <label id="lbl-total-cals">Total Cals (kcal)</label>
            <input type="number" id="session-total-cals" placeholder="e.g. 460" style="width: 100%;">
          </div>
          <div class="input-group" style="flex-direction: column; align-items: flex-start;">
            <label id="lbl-training-load">Watch Load (1-5)</label>
            <input type="number" id="session-training-load" step="0.1" min="1.0" max="5.0" placeholder="e.g. 3.2" style="width: 100%;">
          </div>
          <div class="input-group" style="flex-direction: column; align-items: flex-start;">
            <label id="lbl-recovery-hours">Recovery (hours)</label>
            <input type="number" id="session-recovery-hours" placeholder="e.g. 24" style="width: 100%;">
          </div>
          <div class="input-group" style="flex-direction: column; align-items: flex-start;">
            <label id="lbl-rpe">RPE Difficulty (1-5)</label>
            <select id="session-rpe" style="width: 100%;">
              <option value="1">1 (Very Easy)</option>
              <option value="2">2 (Light)</option>
              <option value="3" selected>3 (Target Load)</option>
              <option value="4">4 (Challenging)</option>
              <option value="5">5 (Maximum Exertion)</option>
            </select>
          </div>
        </div>

        <!-- Heart Rate Zones Minutes Breakdown -->
        <div style="margin-bottom: 14px; background: #090d16; padding: 10px 12px; border-radius: 8px; border: 1px solid var(--border);">
          <label style="display: block; font-size: 12px; font-weight: 700; color: #93c5fd; margin-bottom: 6px;" id="lbl-zones-breakdown">⏱️ Smartwatch HR Zones Breakdown (Minutes in each zone):</label>
          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(90px, 1fr)); gap: 8px;">
            <div>
              <span style="font-size: 11px; color: #94a3b8; display: block;">Z1 Warmup</span>
              <input type="number" id="session-z1" step="0.5" placeholder="0 min" style="width: 100%; padding: 5px; background: #1e293b; border: 1px solid var(--border); border-radius: 4px; color: #fff; font-size: 12px;">
            </div>
            <div>
              <span style="font-size: 11px; color: #94a3b8; display: block;">Z2 Fat Burn</span>
              <input type="number" id="session-z2" step="0.5" placeholder="0 min" style="width: 100%; padding: 5px; background: #1e293b; border: 1px solid var(--border); border-radius: 4px; color: #fff; font-size: 12px;">
            </div>
            <div>
              <span style="font-size: 11px; color: #94a3b8; display: block;">Z3 Aerobic</span>
              <input type="number" id="session-z3" step="0.5" placeholder="0 min" style="width: 100%; padding: 5px; background: #1e293b; border: 1px solid var(--border); border-radius: 4px; color: #fff; font-size: 12px;">
            </div>
            <div>
              <span style="font-size: 11px; color: #94a3b8; display: block;">Z4 Threshold</span>
              <input type="number" id="session-z4" step="0.5" placeholder="0 min" style="width: 100%; padding: 5px; background: #1e293b; border: 1px solid var(--border); border-radius: 4px; color: #fff; font-size: 12px;">
            </div>
            <div>
              <span style="font-size: 11px; color: #94a3b8; display: block;">Z5 Anaerobic</span>
              <input type="number" id="session-z5" step="0.5" placeholder="0 min" style="width: 100%; padding: 5px; background: #1e293b; border: 1px solid var(--border); border-radius: 4px; color: #fff; font-size: 12px;">
            </div>
          </div>
        </div>

        <div style="margin-bottom: 14px;">
          <textarea id="session-notes" placeholder="Notes (how did your muscles feel, weights used, smartwatch feedback)..." style="width: 100%; height: 60px; background: #1e293b; border: 1px solid var(--border); border-radius: 6px; padding: 8px; color: #fff; font-size: 13px;"></textarea>
        </div>
        <button class="btn btn-accent" style="width: 100%; justify-content: center;" onclick="submitStrengthSession()">✅ <span id="btn-save-session-text">Complete & Analyze Telemetry</span></button>
      </div>
    </div>

    <!-- VIEW 2: DYNAMIC MOBILITY (10 DRILLS) -->
    <div id="view-mobility" style="display: none;">
      <div class="banner banner-mob">
        <div class="banner-info">
          <h3 id="mob-banner-title">🧘 Dynamic Joint Mobility (10 Drills Flow)</h3>
          <p id="mob-banner-desc">Dedicated restorative session to lubricate joints and open kinetic chains without strength fatigue.</p>
        </div>
        <div class="banner-controls">
          <button class="btn btn-accent" onclick="generateMobilityFlow()">🔄 <span id="btn-mob-regen-text">Generate / Regenerate (10 Drills)</span></button>
        </div>
      </div>

      <!-- Zone Selection Chips -->
      <div style="margin-bottom: 12px; font-size: 13px; font-weight: 700; color: #6ee7b7;" id="mob-filter-title">🎯 Select Targeted Zones (or leave blank for Full-Body):</div>
      <div class="chips-group" id="mob-zone-chips">
        <div class="chip" onclick="toggleMobZone('hips', this)">🦴 <span class="chip-label" data-en="Hips" data-ua="Кульшові суглоби">Hips</span></div>
        <div class="chip" onclick="toggleMobZone('spine', this)">🌀 <span class="chip-label" data-en="Thoracic Spine" data-ua="Грудний відділ">Thoracic Spine</span></div>
        <div class="chip" onclick="toggleMobZone('shoulders', this)">💪 <span class="chip-label" data-en="Shoulders" data-ua="Плечовий пояс">Shoulders</span></div>
        <div class="chip" onclick="toggleMobZone('ankles', this)">🦶 <span class="chip-label" data-en="Ankles" data-ua="Гомілковостоп">Ankles</span></div>
        <div class="chip" onclick="toggleMobZone('wrists_neck', this)">🤲 <span class="chip-label" data-en="Wrists & Neck" data-ua="Зап'ястя та шия">Wrists & Neck</span></div>
        <div class="chip" onclick="toggleMobZone('hamstrings', this)">🦵 <span class="chip-label" data-en="Hamstrings" data-ua="Задня поверхня">Hamstrings</span></div>
      </div>

      <!-- Mobility Progress -->
      <div style="margin-bottom: 14px;">
        <div style="display: flex; justify-content: space-between; font-size: 12px; color: var(--muted); margin-bottom: 4px;">
          <span id="mob-comp-label">Mobility Progress:</span>
          <span id="mob-comp-counter">0 / 10 Completed (0%)</span>
        </div>
        <div style="background: #1e293b; height: 6px; border-radius: 3px; overflow: hidden;">
          <div id="mob-comp-bar" style="background: #10b981; width: 0%; height: 100%; transition: width 0.3s;"></div>
        </div>
      </div>

      <!-- Mobility Drills List -->
      <div id="mobility-exercise-list"></div>

      <!-- Complete Mobility Button -->
      <div style="margin-top: 20px;">
        <button class="btn btn-accent" style="width: 100%; justify-content: center;" onclick="submitMobilitySession()">💾 <span id="btn-mob-complete-text">Save & Complete Mobility Session</span></button>
      </div>
    </div>

    <!-- VIEW 3: REHABILITATION (10 DRILLS) -->
    <div id="view-rehab" style="display: none;">
      <div class="banner banner-rehab">
        <div class="banner-info">
          <h3 id="rehab-banner-title">❤️‍🩹 Rehabilitation & Restoration (10 Drills)</h3>
          <p id="rehab-banner-desc">Evidence-based restorative protocols across 6 specialized departments for zero pain and joint healing.</p>
        </div>
        <div class="banner-controls">
          <button class="btn btn-purple" onclick="generateRehabRoutine()">🔄 <span id="btn-rehab-regen-text">Generate / Regenerate (10 Drills)</span></button>
        </div>
      </div>

      <!-- Department Selector Chips -->
      <div style="margin-bottom: 12px; font-size: 13px; font-weight: 700; color: #d8b4fe;" id="rehab-dept-title">🩺 Select Department:</div>
      <div class="chips-group" id="rehab-dept-chips">
        <div class="chip active-purple" onclick="toggleRehabDept('pelvic_floor_diastasis', this)">🌸 <span class="chip-label" data-en="Pelvic Floor & Diastasis" data-ua="Тазове дно та діастаз">Pelvic Floor & Diastasis</span></div>
        <div class="chip" onclick="toggleRehabDept('lower_back_lordosis', this)">🦴 <span class="chip-label" data-en="Lower Back & Lordosis" data-ua="Поперек та гіперлордоз">Lower Back & Lordosis</span></div>
        <div class="chip" onclick="toggleRehabDept('wrists_elbows', this)">🤲 <span class="chip-label" data-en="Wrists & Elbows" data-ua="Зап'ястя та лікті">Wrists & Elbows</span></div>
        <div class="chip" onclick="toggleRehabDept('knees_hips', this)">🦵 <span class="chip-label" data-en="Knees & Hips" data-ua="Коліна та кульшові">Knees & Hips</span></div>
        <div class="chip" onclick="toggleRehabDept('ankles_feet', this)">🦶 <span class="chip-label" data-en="Ankles & Anti-Edema" data-ua="Стопи та лімфодренаж">Ankles & Anti-Edema</span></div>
        <div class="chip" onclick="toggleRehabDept('neck_scapula', this)">🧘 <span class="chip-label" data-en="Neck & Scapula" data-ua="Шия та лопатки">Neck & Scapula</span></div>
      </div>

      <!-- Rehab Progress -->
      <div style="margin-bottom: 14px;">
        <div style="display: flex; justify-content: space-between; font-size: 12px; color: var(--muted); margin-bottom: 4px;">
          <span id="rehab-comp-label">Rehab Progress:</span>
          <span id="rehab-comp-counter">0 / 10 Completed (0%)</span>
        </div>
        <div style="background: #1e293b; height: 6px; border-radius: 3px; overflow: hidden;">
          <div id="rehab-comp-bar" style="background: var(--purple); width: 0%; height: 100%; transition: width 0.3s;"></div>
        </div>
      </div>

      <!-- Rehab Drills List -->
      <div id="rehab-exercise-list"></div>

      <!-- Complete Rehab Button -->
      <div style="margin-top: 20px;">
        <button class="btn btn-purple" style="width: 100%; justify-content: center;" onclick="submitRehabSession()">💾 <span id="btn-rehab-complete-text">Save & Complete Rehab Session</span></button>
      </div>
    </div>

    <!-- VIEW 4: PROGRESS & HISTORY -->
    <div id="view-progress" style="display: none;">
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 14px; margin-bottom: 24px;">
        <div class="card" style="text-align: center;">
          <div style="font-size: 28px; font-weight: 800; color: var(--primary);" id="stat-total-workouts">0</div>
          <div style="font-size: 12px; color: var(--muted); text-transform: uppercase;" id="lbl-total-wo">Workouts Completed</div>
        </div>
        <div class="card" style="text-align: center;">
          <div style="font-size: 28px; font-weight: 800; color: var(--accent);" id="stat-total-minutes">0</div>
          <div style="font-size: 12px; color: var(--muted); text-transform: uppercase;" id="lbl-total-min">Total Minutes</div>
        </div>
        <div class="card" style="text-align: center;">
          <div style="font-size: 28px; font-weight: 800; color: #f59e0b;" id="stat-streak">0</div>
          <div style="font-size: 12px; color: var(--muted); text-transform: uppercase;" id="lbl-streak">Weekly Streak</div>
        </div>
      </div>
      <div class="card">
        <h3 style="font-size: 16px; font-weight: 700; margin-bottom: 14px;" id="history-table-title">Recent Completed Sessions</h3>
        <div id="history-sessions-list"></div>
      </div>
    </div>

    <!-- VIEW 5: EXERCISE LIBRARY -->
    <div id="view-library" style="display: none;">
      <div class="card" style="margin-bottom: 18px;">
        <input type="text" id="lib-search" placeholder="Search 340+ exercises by name or muscle..." oninput="filterLibrary()" style="width: 100%; padding: 10px 14px; background: #0f172a; border: 1px solid var(--border); border-radius: 8px; color: #fff; font-size: 14px; margin-bottom: 12px;">
        <div style="display: flex; gap: 8px; flex-wrap: wrap;">
          <select id="lib-filter-pattern" class="btn btn-secondary btn-sm" onchange="filterLibrary()">
            <option value="">All Movement Patterns</option>
            <option value="Squat">Squat</option>
            <option value="Hinge">Hinge</option>
            <option value="Lunge">Lunge</option>
            <option value="Push">Push</option>
            <option value="Pull">Pull</option>
            <option value="Core">Core</option>
            <option value="Mobility">Mobility</option>
          </select>
          <select id="lib-filter-loc" class="btn btn-secondary btn-sm" onchange="filterLibrary()">
            <option value="">All Venues (Home & Gym)</option>
            <option value="home">Home</option>
            <option value="gym">Commercial Gym</option>
          </select>
        </div>
      </div>
      <div id="library-results-grid" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 12px;"></div>
    </div>
  </div>

  <!-- ONBOARDING & PROFILE QUESTIONNAIRE MODAL -->
  <div class="modal-overlay" id="onboarding-modal">
    <div class="modal">
      <div class="modal-header">
        <h3 id="modal-onb-title">📋 Athlete Profile & Biomechanics Setup</h3>
        <button class="close-btn" onclick="closeOnboardingModal()">✕</button>
      </div>

      <!-- Mode: Female vs Male -->
      <div style="margin-bottom: 16px;">
        <label style="display: block; font-size: 12px; font-weight: 700; color: var(--muted); margin-bottom: 6px;" id="lbl-onb-mode">TRAINING PROFILE MODE:</label>
        <div class="toggle-group" style="width: 100%; display: flex;">
          <button class="toggle-btn" id="onb-sex-female" style="flex: 1;" onclick="setOnboardingSex('female')">👩 Female Sculpt (Glutes, Hips, Waist, Adductors)</button>
          <button class="toggle-btn" id="onb-sex-male" style="flex: 1;" onclick="setOnboardingSex('male')">👨 Male Hypertrophy (Chest, Back, Arms, Legs)</button>
        </div>
      </div>

      <!-- Age, Current Weight, Target Weight, Goal -->
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 16px;">
        <div>
          <label style="font-size: 12px; color: var(--muted);" id="lbl-onb-age">Age</label>
          <input type="number" id="onb-age" value="30" style="width: 100%; padding: 8px; background: #0f172a; border: 1px solid var(--border); border-radius: 6px; color: #fff;">
        </div>
        <div>
          <label style="font-size: 12px; color: var(--muted);" id="lbl-onb-goal">Primary Goal</label>
          <select id="onb-goal" style="width: 100%; padding: 8px; background: #0f172a; border: 1px solid var(--border); border-radius: 6px; color: #fff;">
            <option value="muscle_gain">Muscle Gain / Hypertrophy</option>
            <option value="toning">Toning & Sculpt</option>
            <option value="weight_loss">Weight Loss / Fat Burn</option>
            <option value="strength">Maximum Strength</option>
          </select>
        </div>
        <div>
          <label style="font-size: 12px; color: var(--muted);" id="lbl-onb-cw">Current Weight (kg)</label>
          <input type="number" id="onb-cw" value="75" step="0.5" style="width: 100%; padding: 8px; background: #0f172a; border: 1px solid var(--border); border-radius: 6px; color: #fff;">
        </div>
        <div>
          <label style="font-size: 12px; color: var(--muted);" id="lbl-onb-tw">Target Weight (kg)</label>
          <input type="number" id="onb-tw" value="72" step="0.5" style="width: 100%; padding: 8px; background: #0f172a; border: 1px solid var(--border); border-radius: 6px; color: #fff;">
        </div>
      </div>

      <!-- Training Venue & TRX Anchor -->
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 16px;">
        <div>
          <label style="font-size: 12px; color: var(--muted);" id="lbl-onb-loc">Primary Location</label>
          <select id="onb-loc" style="width: 100%; padding: 8px; background: #0f172a; border: 1px solid var(--border); border-radius: 6px; color: #fff;" onchange="toggleOnboardingGearDisplay(this.value)">
            <option value="home">Home</option>
            <option value="gym">Commercial Gym</option>
          </select>
        </div>
        <div>
          <label style="font-size: 12px; color: var(--muted);" id="lbl-onb-trx">TRX Mounting Point</label>
          <select id="onb-trx" style="width: 100%; padding: 8px; background: #0f172a; border: 1px solid var(--border); border-radius: 6px; color: #fff;">
            <option value="door">Door Anchor (Strict Zero-Overhead)</option>
            <option value="bar">Pull-Up Bar / 360° Mount</option>
          </select>
        </div>
      </div>

      <!-- Home Equipment Inventory Checkboxes -->
      <div id="onb-gear-container" style="margin-bottom: 16px;">
        <label style="display: block; font-size: 12px; font-weight: 700; color: var(--muted); margin-bottom: 6px;" id="lbl-onb-gear">AVAILABLE GEAR (HOME INVENTORY):</label>
        <div id="onb-gear-checklist" style="display: grid; grid-template-columns: 1fr 1fr; gap: 6px; font-size: 12px;"></div>
      </div>

      <!-- CATEGORY A: JOINT, SPINE & BIOMECHANICAL ISOLATION (12) -->
      <div style="margin-bottom: 16px;">
        <label style="display: block; font-size: 12px; font-weight: 700; color: #f87171; margin-bottom: 6px;" id="lbl-onb-cat-a">CATEGORY A: JOINT, SPINE & BIOMECHANICAL ISOLATION (Strict Zero-Load):</label>
        <div class="chips-group" id="onb-injury-chips">
          <div class="chip" id="chip-inj-wrist" onclick="toggleOnbInjury('wrist', this)">🤲 <span class="chip-label" data-en="Wrist (Zero-Palm)" data-ua="Зап'ястя (без упору на долоні)">Wrist (Zero-Palm)</span></div>
          <div class="chip" id="chip-inj-knee" onclick="toggleOnbInjury('knee', this)">🦵 <span class="chip-label" data-en="Knee (Zero Shear)" data-ua="Коліна (без зсувного навантаження)">Knee (Zero Shear)</span></div>
          <div class="chip" id="chip-inj-no_kneeling" onclick="toggleOnbInjury('no_kneeling', this)">🚫 <span class="chip-label" data-en="No Kneeling (No All-Fours)" data-ua="Без опори на коліна (без четвереньок)">No Kneeling (No All-Fours)</span></div>
          <div class="chip" id="chip-inj-lower_back" onclick="toggleOnbInjury('lower_back', this)">🦴 <span class="chip-label" data-en="Lower Back / Hernia (No Axial)" data-ua="Поперек / Грижі (без осьового)">Lower Back / Hernia (No Axial)</span></div>
          <div class="chip" id="chip-inj-hyperlordosis" onclick="toggleOnbInjury('hyperlordosis', this)">📐 <span class="chip-label" data-en="Hyperlordosis (Tuck Pelvis)" data-ua="Гіперлордоз (без прогину в попереку)">Hyperlordosis (Tuck Pelvis)</span></div>
          <div class="chip" id="chip-inj-shoulder" onclick="toggleOnbInjury('shoulder', this)">💪 <span class="chip-label" data-en="Shoulder Impingement" data-ua="Плече / Імпіджмент">Shoulder Impingement</span></div>
          <div class="chip" id="chip-inj-elbow" onclick="toggleOnbInjury('elbow', this)">⚡ <span class="chip-label" data-en="Elbow Tendonitis" data-ua="Лікоть (епікондиліт)">Elbow Tendonitis</span></div>
          <div class="chip" id="chip-inj-ankle" onclick="toggleOnbInjury('ankle', this)">🦶 <span class="chip-label" data-en="Ankle Sprain / Mobility" data-ua="Гомілковостоп / Нестабільність">Ankle Sprain / Mobility</span></div>
          <div class="chip" id="chip-inj-hip" onclick="toggleOnbInjury('hip', this)">🦴 <span class="chip-label" data-en="Hip Impingement / Labrum" data-ua="Кульшовий суглоб / Імпіджмент">Hip Impingement / Labrum</span></div>
          <div class="chip" id="chip-inj-cervical_spine" onclick="toggleOnbInjury('cervical_spine', this)">🧘 <span class="chip-label" data-en="Neck / Cervical Spine Tension" data-ua="Шийний відділ хребта">Neck / Cervical Spine Tension</span></div>
          <div class="chip" id="chip-inj-sciatica" onclick="toggleOnbInjury('sciatica', this)">⚡ <span class="chip-label" data-en="Sciatica / Piriformis Syndrome" data-ua="Сідничний нерв / Грушоподібний">Sciatica / Piriformis Syndrome</span></div>
          <div class="chip" id="chip-inj-flat_feet" onclick="toggleOnbInjury('flat_feet', this)">🦶 <span class="chip-label" data-en="Flat Feet / Plantar Fasciitis" data-ua="Плоскостопість / Фасциїт">Flat Feet / Plantar Fasciitis</span></div>
        </div>
      </div>

      <!-- CATEGORY B: FEMALE HEALTH & POSTURE (4) -->
      <div style="margin-bottom: 16px;">
        <label style="display: block; font-size: 12px; font-weight: 700; color: #f472b6; margin-bottom: 6px;" id="lbl-onb-cat-b">CATEGORY B: FEMALE HEALTH & POSTURE:</label>
        <div class="chips-group" id="onb-cat-b-chips">
          <div class="chip" id="chip-med-diastasis_pelvic_floor" onclick="toggleOnbMed('diastasis_pelvic_floor', this)">🌸 <span class="chip-label" data-en="Diastasis & Pelvic Floor Safe" data-ua="Діастаз та слабкість тазового дна">Diastasis & Pelvic Floor Safe</span></div>
          <div class="chip" id="chip-med-pregnancy_safe" onclick="toggleOnbMed('pregnancy_safe', this)">🤰 <span class="chip-label" data-en="Pregnancy Safe Protocol" data-ua="Вагітність (безпечний протокол)">Pregnancy Safe Protocol</span></div>
          <div class="chip" id="chip-med-postpartum" onclick="toggleOnbMed('postpartum', this)">👶 <span class="chip-label" data-en="Postpartum Recovery" data-ua="Післяпологове відновлення">Postpartum Recovery</span></div>
          <div class="chip" id="chip-med-varicose_veins" onclick="toggleOnbMed('varicose_veins', this)">🩸 <span class="chip-label" data-en="Varicose Veins (Anti-Stagnation)" data-ua="Варикоз (без тривалого стояння)">Varicose Veins (Anti-Stagnation)</span></div>
        </div>
      </div>

      <!-- CATEGORY C: CARDIOVASCULAR & HEMODYNAMIC (3) -->
      <div style="margin-bottom: 16px;">
        <label style="display: block; font-size: 12px; font-weight: 700; color: #fb7185; margin-bottom: 6px;" id="lbl-onb-cat-c">CATEGORY C: CARDIOVASCULAR & HEMODYNAMIC:</label>
        <div class="chips-group" id="onb-cat-c-chips">
          <div class="chip" id="chip-med-hypertension" onclick="toggleOnbMed('hypertension', this)">🫀 <span class="chip-label" data-en="Hypertension (No Inversions/Valsalva)" data-ua="Гіпертонія (без натужування)">Hypertension (No Inversions/Valsalva)</span></div>
          <div class="chip" id="chip-med-hypotension" onclick="toggleOnbMed('hypotension', this)">📉 <span class="chip-label" data-en="Hypotension (Slow Level Shifts)" data-ua="Гіпотонія (повільна зміна рівнів)">Hypotension (Slow Level Shifts)</span></div>
          <div class="chip" id="chip-med-arrhythmia_tachycardia" onclick="toggleOnbMed('arrhythmia_tachycardia', this)">💓 <span class="chip-label" data-en="Arrhythmia / Tachycardia (Zone 1-2 Cap)" data-ua="Аритмія / Тахікардія (ліміт Зони 1-2)">Arrhythmia / Tachycardia (Zone 1-2 Cap)</span></div>
        </div>
      </div>

      <!-- CATEGORY D: ENDOCRINE, METABOLIC & RECOVERY (4) -->
      <div style="margin-bottom: 16px;">
        <label style="display: block; font-size: 12px; font-weight: 700; color: #c084fc; margin-bottom: 6px;" id="lbl-onb-cat-d">CATEGORY D: ENDOCRINE, METABOLIC & RECOVERY:</label>
        <div class="chips-group" id="onb-cat-d-chips">
          <div class="chip" id="chip-med-thyroid" onclick="toggleOnbMed('thyroid', this)">🦋 <span class="chip-label" data-en="Thyroid / Hypothyroidism (Anti-Cortisol)" data-ua="Щитоподібна залоза (протикортизоловий захист)">Thyroid / Hypothyroidism (Anti-Cortisol)</span></div>
          <div class="chip" id="chip-med-adrenal_fatigue" onclick="toggleOnbMed('adrenal_fatigue', this)">🔋 <span class="chip-label" data-en="Adrenal Fatigue (Extended Rest 90s+)" data-ua="Втома наднирників (відпочинок 90с+)">Adrenal Fatigue (Extended Rest 90s+)</span></div>
          <div class="chip" id="chip-med-type2_diabetes" onclick="toggleOnbMed('type2_diabetes', this)">🩺 <span class="chip-label" data-en="Type 2 Diabetes (Insulin Sensitivity)" data-ua="Діабет 2 типу (інсуліночутливість)">Type 2 Diabetes (Insulin Sensitivity)</span></div>
          <div class="chip" id="chip-med-edema" onclick="toggleOnbMed('edema', this)">💧 <span class="chip-label" data-en="Edema / Lymphatic Drainage" data-ua="Схильність до набряків / Лімфодренаж">Edema / Lymphatic Drainage</span></div>
        </div>
      </div>

      <!-- CATEGORY E: RESPIRATORY & GASTROINTESTINAL (2) -->
      <div style="margin-bottom: 20px;">
        <label style="display: block; font-size: 12px; font-weight: 700; color: #38bdf8; margin-bottom: 6px;" id="lbl-onb-cat-e">CATEGORY E: RESPIRATORY & GASTROINTESTINAL:</label>
        <div class="chips-group" id="onb-cat-e-chips">
          <div class="chip" id="chip-med-asthma" onclick="toggleOnbMed('asthma', this)">🫁 <span class="chip-label" data-en="Asthma Care (Controlled Cadence)" data-ua="Астма (контроль каденсу та дихання)">Asthma Care (Controlled Cadence)</span></div>
          <div class="chip" id="chip-med-gerd" onclick="toggleOnbMed('gerd', this)">🔥 <span class="chip-label" data-en="GERD / Reflux (No Inversions/Flat Supine)" data-ua="ГЕРХ / Рефлюкс (без перевертання)">GERD / Reflux (No Inversions/Flat Supine)</span></div>
        </div>
      </div>

      <button class="btn btn-accent" style="width: 100%; justify-content: center; padding: 12px;" onclick="saveOnboardingProfile()">💾 <span id="btn-save-onb-text">Save Profile & Generate Workouts</span></button>
    </div>
  </div>

  <!-- FOCUS WORKOUT MODAL -->
  <div class="modal-overlay" id="focus-modal">
    <div class="modal">
      <div class="modal-header">
        <h3 id="modal-focus-title">🎯 Custom Focus Workout Builder</h3>
        <button class="close-btn" onclick="closeFocusModal()">✕</button>
      </div>
      <p style="font-size: 13px; color: var(--muted); margin-bottom: 14px;" id="focus-modal-desc">Select 1 to 4 priority muscle zones to build a personalized 10-exercise workout:</p>
      <div class="chips-group" id="focus-chips-container">
        <div class="chip" onclick="toggleFocusArea('glutes', this)">🍑 <span class="chip-label" data-en="Glutes (All 3 Heads)" data-ua="Сідниці (3 площини)">Glutes</span></div>
        <div class="chip" onclick="toggleFocusArea('waist', this)">⏳ <span class="chip-label" data-en="Waist Narrowing & Core" data-ua="Звуження талії та кор">Waist & Core</span></div>
        <div class="chip" onclick="toggleFocusArea('abs', this)">🍫 <span class="chip-label" data-en="Flat Stomach & Abs" data-ua="Плоский живіт та прес">Flat Stomach</span></div>
        <div class="chip" onclick="toggleFocusArea('inner_thighs', this)">🦵 <span class="chip-label" data-en="Inner Thighs (Adductors)" data-ua="Внутрішня поверхня стегна">Inner Thighs</span></div>
        <div class="chip" onclick="toggleFocusArea('hamstrings', this)">⚡ <span class="chip-label" data-en="Hamstrings" data-ua="Біцепс стегна">Hamstrings</span></div>
        <div class="chip" onclick="toggleFocusArea('quads', this)">🦵 <span class="chip-label" data-en="Quads" data-ua="Квадрицепси">Quads</span></div>
        <div class="chip" onclick="toggleFocusArea('back', this)">🦅 <span class="chip-label" data-en="Back & Scapular Posture" data-ua="Спина та постава">Back</span></div>
        <div class="chip" onclick="toggleFocusArea('chest', this)">🛡️ <span class="chip-label" data-en="Chest & Sculpt" data-ua="Грудні м'язи">Chest</span></div>
        <div class="chip" onclick="toggleFocusArea('shoulders', this)">💪 <span class="chip-label" data-en="Shoulders & Delts" data-ua="Плечі та дельти">Shoulders</span></div>
        <div class="chip" onclick="toggleFocusArea('arms', this)">💥 <span class="chip-label" data-en="Arms (Biceps & Triceps)" data-ua="Руки (Біцепс / Трицепс)">Arms</span></div>
        <div class="chip" onclick="toggleFocusArea('calves_lymph', this)">🦶 <span class="chip-label" data-en="Calves & Anti-Edema" data-ua="Литки та лімфодренаж">Calves</span></div>
      </div>
      <button class="btn btn-accent" style="width: 100%; justify-content: center; padding: 12px;" onclick="generateFocusWorkout()">⚡ <span id="btn-gen-focus-text">Generate 10-Exercise Focus Workout</span></button>
    </div>
  </div>

  <!-- TABATA TIMER MODAL (LOUD, DYNAMIC WITH EXERCISES & VOICE) -->
  <div class="modal-overlay" id="tabata-modal">
    <div class="modal" style="max-width: 500px; text-align: center;">
      <div class="modal-header" style="justify-content: flex-end; border: none; margin-bottom: 0;">
        <button class="close-btn" onclick="closeTabataModal()">✕</button>
      </div>
      <div class="tabata-neon">
        <div style="font-size: 13px; font-weight: 700; color: #38bdf8; text-transform: uppercase; margin-bottom: 4px;" id="tabata-ex-counter">Exercise 1 of 10</div>
        <div class="tabata-ex-name" id="tabata-current-name">Squats</div>
        <div class="tabata-next-name" id="tabata-next-preview">Next up: Push-Ups</div>
        <div id="tabata-phase-badge" class="tabata-phase-pill phase-work">WORK (40s)</div>
        <div class="tabata-digits digits-work" id="tabata-digits">40</div>
        <div style="font-size: 13px; color: var(--muted); margin-bottom: 16px;" id="tabata-round-info">Interval 1 of 8</div>

        <!-- Controls -->
        <div style="display: flex; gap: 10px; justify-content: center; margin-bottom: 14px;">
          <button class="btn btn-accent" id="btn-tabata-play" onclick="toggleTabataPlay()" style="padding: 10px 24px; font-size: 15px;">▶️ Start</button>
          <button class="btn btn-secondary" onclick="nextTabataExercise()">⏭️ Next Drill</button>
          <button class="btn btn-secondary" onclick="resetTabataTimer()">🔄 Reset</button>
          <button class="btn btn-secondary" id="btn-tabata-sound" onclick="toggleTabataSound()">🔊</button>
        </div>
      </div>
    </div>
  </div>

  <!-- HEART RATE ANALYSIS MODAL -->
  <div class="modal-overlay" id="hr-modal">
    <div class="modal">
      <div class="modal-header">
        <h3 id="modal-hr-title">📊 Heart Rate Workout Analysis</h3>
        <button class="close-btn" onclick="closeHrModal()">✕</button>
      </div>
      <div id="hr-analysis-body"></div>
    </div>
  </div>

  <!-- Toast -->
  <div id="toast"></div>

  <script>
    // -------------------------------------------------------------
    // LOCALIZATION & BILINGUAL STATE
    // -------------------------------------------------------------
    let currentLang = "en";
    let activeTab = "workout";

    // Three Strictly Independent Plan States
    let currentStrengthPlan = []; // 5 days
    let selectedDayIndex = 0;     // 0..4
    let currentMobilityPlan = null;
    let currentRehabPlan = null;
    let userProfile = {};

    // Multi-select filters
    let selectedMobZones = [];
    let selectedRehabDepts = ["pelvic_floor_diastasis"];
    let selectedFocusAreas = ["glutes", "waist"];
    let onbInjuries = [];
    let onbMeds = [];
    let onbGear = [
      "adjustable dumbbells", "TRX", "short/mini resistance bands",
      "long resistance bands", "towels/sliders", "couch/bench support",
      "small fitness ball", "yoga blocks"
    ];

    // Equipment Ukrainian Translation Dictionary
    const EQUIPMENT_UA = {
      "adjustable dumbbells": "розбірні гантелі",
      "dumbbells": "гантелі",
      "dumbbell": "гантелі",
      "TRX": "петлі TRX",
      "short/mini resistance bands": "короткі міні-резинки",
      "mini-band": "міні-резинка",
      "long resistance bands": "довгі гумові петлі",
      "resistance band": "гумова петля",
      "towels/sliders": "рушники / слайдери",
      "sliders": "слайдери",
      "towel": "рушник",
      "couch/bench support": "опора на диван / лаву",
      "bench": "лавка",
      "couch": "диван",
      "small fitness ball": "малий фітбол",
      "yoga blocks": "йога-блоки",
      "bodyweight": "власна вага",
      "none": "без обладнання",
      "cable tower": "блочна рама / кросовер",
      "barbell": "штанга",
      "leg curl machine": "тренажер згинання ніг",
      "leg extension machine": "тренажер розгинання ніг",
      "lat pulldown machine": "тяга верхнього блоку",
      "seated abduction machine": "тренажер розведення ніг",
      "door anchor": "дверний якір",
      "pull-up bar": "турнік"
    };

    function translateEquip(name) {
      if (currentLang === "en") return name;
      const key = name.toLowerCase().trim();
      return EQUIPMENT_UA[key] || name;
    }

    const I18N = {
      en: {
        app_title: "AI Fitness Coach",
        app_sub: "Intelligent Split & Restoration Programming",
        tab_workout: "Strength & Formats",
        tab_mob: "Dynamic Mobility",
        tab_rehab: "Rehabilitation",
        tab_prog: "Progress & History",
        tab_lib: "Exercise Library",
        settings: "Settings",
        regen: "Regenerate",
        focus_btn: "Focus Workout",
        tabata_btn: "Tabata Timer",
        guide_btn: "Exercise Form Guide",
        guide_setup: "SETUP: ",
        guide_exec: "EXECUTION: ",
        guide_tip: "TRAINER TIP: ",
        mark_done: "Mark Done",
        marked_done: "✓ Completed",
        weight: "Weight",
        reps_done: "Reps",
        diff: "RPE",
        skip: "Skip",
        next_day_prefix: "Next Day (Day ",
        start_cycle: "🎉 Start Next 5-Day Cycle 🚀",
        toast_cycle_started: "🎉 New 5-Day Cycle Generated! Fresh exercises loaded.",
        toast_saved: "✓ Workout session saved successfully!",
        // Onboarding Modal
        onb_title: "📋 Athlete Profile & Biomechanics Setup",
        onb_mode: "TRAINING PROFILE MODE:",
        onb_female_btn: "👩 Female Sculpt (Glutes, Hips, Waist, Adductors)",
        onb_male_btn: "👨 Male Hypertrophy (Chest, Back, Arms, Legs)",
        onb_age: "Age",
        onb_goal: "Primary Goal",
        onb_goal_mg: "Muscle Gain / Hypertrophy",
        onb_goal_ton: "Toning & Sculpt",
        onb_goal_wl: "Weight Loss / Fat Burn",
        onb_goal_str: "Maximum Strength",
        onb_cw: "Current Weight (kg)",
        onb_tw: "Target Weight (kg)",
        onb_loc: "Primary Location",
        onb_loc_home: "Home",
        onb_loc_gym: "Commercial Gym",
        onb_trx: "TRX Mounting Point",
        onb_trx_door: "Door Anchor (Strict Zero-Overhead)",
        onb_trx_bar: "Pull-Up Bar / 360° Mount",
        onb_gear: "AVAILABLE GEAR (HOME INVENTORY):",
        onb_cat_a: "CATEGORY A: JOINT, SPINE & BIOMECHANICAL ISOLATION (Strict Zero-Load):",
        onb_cat_b: "CATEGORY B: FEMALE HEALTH & POSTURE:",
        onb_cat_c: "CATEGORY C: CARDIOVASCULAR & HEMODYNAMIC:",
        onb_cat_d: "CATEGORY D: ENDOCRINE, METABOLIC & RECOVERY:",
        onb_cat_e: "CATEGORY E: RESPIRATORY & GASTROINTESTINAL:",
        onb_save_btn: "💾 Save Profile & Generate Workouts",
        // Smartwatch Hub & Completion
        sync_watch: "Sync Watch",
        live_sync: "Live Bluetooth Sync",
        complete_title: "💾 Finish & Save Workout (Smartwatch Telemetry Hub)",
        telemetry_hint: "Log your Apple Watch / Garmin / Polar telemetry or sync live via Bluetooth:",
        lbl_dur: "Duration (min)",
        lbl_min_hr: "Min HR (BPM)",
        lbl_avg_hr: "Avg HR (BPM)",
        lbl_max_hr: "Max HR (BPM)",
        lbl_active_cals: "Active Cals (kcal)",
        lbl_total_cals: "Total Cals (kcal)",
        lbl_training_load: "Watch Load (1-5)",
        lbl_recovery_hours: "Recovery (hours)",
        lbl_rpe: "RPE Difficulty (1-5)",
        lbl_zones_breakdown: "⏱️ Smartwatch HR Zones Breakdown (Minutes in each zone):",
        save_session_btn: "Complete & Analyze Telemetry"
      },
      ua: {
        app_title: "AI Fitness Coach",
        app_sub: "Програмування сплітів, мобільності та реабілітації",
        tab_workout: "Силові та формати",
        tab_mob: "Динамічна мобільність",
        tab_rehab: "Реабілітація",
        tab_prog: "Прогрес та історія",
        tab_lib: "Бібліотека вправ",
        settings: "Налаштування",
        regen: "Перегенерувати",
        focus_btn: "Фокус-тренування",
        tabata_btn: "Таймер Табата",
        guide_btn: "Техніка виконання",
        guide_setup: "НАЛАШТУВАННЯ: ",
        guide_exec: "ВИКОНАННЯ: ",
        guide_tip: "ПОРАДА ТРЕНЕРА: ",
        mark_done: "Виконано",
        marked_done: "✓ Зроблено",
        weight: "Вага",
        reps_done: "Повтори",
        diff: "Складність",
        skip: "Пропуск",
        next_day_prefix: "Наступний день (День ",
        start_cycle: "🎉 Почати новий 5-денний цикл 🚀",
        toast_cycle_started: "🎉 Новий 5-денний цикл згенеровано! Свіжі вправи завантажено.",
        toast_saved: "✓ Тренування успішно збережено в базі!",
        // Onboarding Modal
        onb_title: "📋 Профіль атлета та біомеханічні налаштування",
        onb_mode: "РЕЖИМ ПРОФІЛЮ ТРЕНУВАНЬ:",
        onb_female_btn: "👩 Жіночий силует (Сідниці, Стегна, Талія, Привідні)",
        onb_male_btn: "👨 Чоловіча гіпертрофія (Груди, Спина, Руки, Ноги)",
        onb_age: "Вік",
        onb_goal: "Основна мета",
        onb_goal_mg: "Набір м'язів / Гіпертрофія",
        onb_goal_ton: "Тонус та рельєф",
        onb_goal_wl: "Схуднення / Жироспалювання",
        onb_goal_str: "Максимальна сила",
        onb_cw: "Поточна вага (кг)",
        onb_tw: "Цільова вага (кг)",
        onb_loc: "Локація тренувань",
        onb_loc_home: "Вдома",
        onb_loc_gym: "Фітнес-клуб",
        onb_trx: "Точка кріплення TRX",
        onb_trx_door: "Дверний якір (без навантаження над головою)",
        onb_trx_bar: "Турнік / Стельове кріплення 360°",
        onb_gear: "ДОСТУПНИЙ ІНВЕНТАР (ВДОМА):",
        onb_cat_a: "КАТЕГОРІЯ A: СУГЛОБИ, ХРЕБЕТ ТА БІОМЕХАНІЧНА ІЗОЛЯЦІЯ (Без навантаження):",
        onb_cat_b: "КАТЕГОРІЯ B: ЖІНОЧЕ ЗДОРОВ'Я ТА ПОСТАВА:",
        onb_cat_c: "КАТЕГОРІЯ C: СЕРЦЕВО-СУДИННА СИСТЕМА ТА ТИСК:",
        onb_cat_d: "КАТЕГОРІЯ D: ЕНДОКРИННА СИСТЕМА ТА ВІДНОВЛЕННЯ:",
        onb_cat_e: "КАТЕГОРІЯ E: ДИХАЛЬНА ТА ТРАВНА СИСТЕМИ:",
        onb_save_btn: "💾 Зберегти профіль та створити програму",
        // Smartwatch Hub & Completion
        sync_watch: "Синхр. годинник",
        live_sync: "Bluetooth синхронізація",
        complete_title: "💾 Завершити та зберегти (Телеметрія смарт-годинника)",
        telemetry_hint: "Внесіть дані Apple Watch / Garmin / Polar або синхронізуйте по Bluetooth:",
        lbl_dur: "Тривалість (хв)",
        lbl_min_hr: "Мін Пульс (BPM)",
        lbl_avg_hr: "Сер Пульс (BPM)",
        lbl_max_hr: "Макс Пульс (BPM)",
        lbl_active_cals: "Активні ккал",
        lbl_total_cals: "Загальні ккал",
        lbl_training_load: "Навантаження (1-5)",
        lbl_recovery_hours: "Відновлення (год)",
        lbl_rpe: "Складність RPE (1-5)",
        lbl_zones_breakdown: "⏱️ Розподіл пульсових зон годинника (хвилини в кожній зоні):",
        save_session_btn: "Завершити та проаналізувати телеметрію"
      }
    };

    // -------------------------------------------------------------
    // SMARTWATCH WEB BLUETOOTH INTEGRATION
    // -------------------------------------------------------------
    let bluetoothDevice = null;
    let hrCharacteristic = null;
    let liveBpmHistory = [];

    async function connectSmartwatch() {
      if (!navigator.bluetooth) {
        alert(currentLang === "ua" ? "Web Bluetooth API не підтримується у вашому браузері. Будь ласка, використовуйте Chrome, Edge або Opera." : "Web Bluetooth API is not supported in this browser. Please use Chrome, Edge, or Opera.");
        return;
      }
      try {
        showToast(currentLang === "ua" ? "🔍 Пошук Bluetooth пульсометра / годинника..." : "🔍 Searching for Bluetooth heart rate monitor / watch...");
        const device = await navigator.bluetooth.requestDevice({
          filters: [{ services: ['heart_rate'] }]
        });
        bluetoothDevice = device;
        const server = await device.gatt.connect();
        const service = await server.getPrimaryService('heart_rate');
        hrCharacteristic = await service.getCharacteristic('heart_rate_measurement');
        await hrCharacteristic.startNotifications();
        hrCharacteristic.addEventListener('characteristicvaluechanged', handleHeartRateNotification);

        const liveHrBadge = document.getElementById("watch-live-hr");
        if (liveHrBadge) liveHrBadge.style.display = "inline-flex";

        const syncBtn = document.getElementById("btn-watch-sync");
        if (syncBtn) {
          syncBtn.classList.remove("btn-secondary");
          syncBtn.classList.add("btn-accent");
          syncBtn.innerHTML = `⌚ <span>${device.name || 'Connected'}</span>`;
        }

        const cardSyncBtn = document.getElementById("btn-card-sync");
        if (cardSyncBtn) {
          cardSyncBtn.classList.remove("btn-secondary");
          cardSyncBtn.classList.add("btn-accent");
          cardSyncBtn.innerHTML = `⌚ <span>${device.name || 'Connected'}</span>`;
        }

        showToast(currentLang === "ua" ? `✓ Підключено: ${device.name || 'Смарт-годинник'}` : `✓ Connected to: ${device.name || 'Smartwatch'}`);
      } catch (err) {
        console.error("Bluetooth connection error:", err);
        showToast(currentLang === "ua" ? "Bluetooth: " + err.message : "Bluetooth: " + err.message);
      }
    }

    function handleHeartRateNotification(event) {
      const value = event.target.value;
      const flags = value.getUint8(0);
      const is16Bit = (flags & 0x01) === 0x01;
      let bpm = 0;
      if (is16Bit) {
        bpm = value.getUint16(1, true);
      } else {
        bpm = value.getUint8(1);
      }
      if (bpm > 35 && bpm < 240) {
        liveBpmHistory.push(bpm);
        const bpmEl = document.getElementById("watch-bpm-val");
        if (bpmEl) bpmEl.textContent = bpm;

        const minVal = Math.min(...liveBpmHistory);
        const maxVal = Math.max(...liveBpmHistory);
        const avgVal = Math.round(liveBpmHistory.reduce((a, b) => a + b, 0) / liveBpmHistory.length);

        const minInput = document.getElementById("session-min-hr");
        const avgInput = document.getElementById("session-avg-hr");
        const maxInput = document.getElementById("session-max-hr");
        if (minInput && !minInput.value) minInput.value = minVal;
        else if (minInput && minVal < parseInt(minInput.value)) minInput.value = minVal;

        if (avgInput) avgInput.value = avgVal;

        if (maxInput && !maxInput.value) maxInput.value = maxVal;
        else if (maxInput && maxVal > parseInt(maxInput.value)) maxInput.value = maxVal;
      }
    }

    function setLanguage(lang) {
      currentLang = lang;
      document.getElementById("btn-lang-en").classList.toggle("active", lang === "en");
      document.getElementById("btn-lang-ua").classList.toggle("active", lang === "ua");
      const t = I18N[lang];

      document.getElementById("app-title-text").textContent = t.app_title;
      document.getElementById("app-subtitle-text").textContent = t.app_sub;
      document.getElementById("tab-workout-text").textContent = t.tab_workout;
      document.getElementById("tab-mob-text").textContent = t.tab_mob;
      document.getElementById("tab-rehab-text").textContent = t.tab_rehab;
      document.getElementById("tab-prog-text").textContent = t.tab_prog;
      document.getElementById("tab-lib-text").textContent = t.tab_lib;
      document.getElementById("btn-settings-text").textContent = t.settings;
      document.getElementById("btn-regen-text").textContent = t.regen;
      document.getElementById("btn-focus-text").textContent = t.focus_btn;

      // Smartwatch Hub & Completion Card
      const btnWatch = document.getElementById("btn-watch-text");
      if (btnWatch) btnWatch.textContent = t.sync_watch;
      const btnCardSync = document.getElementById("btn-card-sync-text");
      if (btnCardSync) btnCardSync.textContent = t.live_sync;
      const compCardTitle = document.getElementById("complete-card-title");
      if (compCardTitle) compCardTitle.textContent = t.complete_title;
      const telemHint = document.getElementById("telemetry-hint");
      if (telemHint) telemHint.textContent = t.telemetry_hint;
      const lblDur = document.getElementById("lbl-dur");
      if (lblDur) lblDur.textContent = t.lbl_dur;
      const lblMinHr = document.getElementById("lbl-min-hr");
      if (lblMinHr) lblMinHr.textContent = t.lbl_min_hr;
      const lblAvgHr = document.getElementById("lbl-avg-hr");
      if (lblAvgHr) lblAvgHr.textContent = t.lbl_avg_hr;
      const lblMaxHr = document.getElementById("lbl-max-hr");
      if (lblMaxHr) lblMaxHr.textContent = t.lbl_max_hr;
      const lblActCals = document.getElementById("lbl-active-cals");
      if (lblActCals) lblActCals.textContent = t.lbl_active_cals;
      const lblTotCals = document.getElementById("lbl-total-cals");
      if (lblTotCals) lblTotCals.textContent = t.lbl_total_cals;
      const lblTrLoad = document.getElementById("lbl-training-load");
      if (lblTrLoad) lblTrLoad.textContent = t.lbl_training_load;
      const lblRecHrs = document.getElementById("lbl-recovery-hours");
      if (lblRecHrs) lblRecHrs.textContent = t.lbl_recovery_hours;
      const lblRpe = document.getElementById("lbl-rpe");
      if (lblRpe) lblRpe.textContent = t.lbl_rpe;
      const lblZBreakdown = document.getElementById("lbl-zones-breakdown");
      if (lblZBreakdown) lblZBreakdown.textContent = t.lbl_zones_breakdown;
      const btnSaveSess = document.getElementById("btn-save-session-text");
      if (btnSaveSess) btnSaveSess.textContent = t.save_session_btn;

      // Onboarding & Profile Table Modal
      const modalOnbTitle = document.getElementById("modal-onb-title");
      if (modalOnbTitle) modalOnbTitle.textContent = t.onb_title;
      const lblOnbMode = document.getElementById("lbl-onb-mode");
      if (lblOnbMode) lblOnbMode.textContent = t.onb_mode;
      const onbSexFem = document.getElementById("onb-sex-female");
      if (onbSexFem) onbSexFem.textContent = t.onb_female_btn;
      const onbSexM = document.getElementById("onb-sex-male");
      if (onbSexM) onbSexM.textContent = t.onb_male_btn;
      const lblOnbAge = document.getElementById("lbl-onb-age");
      if (lblOnbAge) lblOnbAge.textContent = t.onb_age;
      const lblOnbGoal = document.getElementById("lbl-onb-goal");
      if (lblOnbGoal) lblOnbGoal.textContent = t.onb_goal;

      const gSelect = document.getElementById("onb-goal");
      if (gSelect && gSelect.options.length >= 4) {
        gSelect.options[0].text = t.onb_goal_mg;
        gSelect.options[1].text = t.onb_goal_ton;
        gSelect.options[2].text = t.onb_goal_wl;
        gSelect.options[3].text = t.onb_goal_str;
      }

      const lblOnbCw = document.getElementById("lbl-onb-cw");
      if (lblOnbCw) lblOnbCw.textContent = t.onb_cw;
      const lblOnbTw = document.getElementById("lbl-onb-tw");
      if (lblOnbTw) lblOnbTw.textContent = t.onb_tw;
      const lblOnbLoc = document.getElementById("lbl-onb-loc");
      if (lblOnbLoc) lblOnbLoc.textContent = t.onb_loc;

      const lSelect = document.getElementById("onb-loc");
      if (lSelect && lSelect.options.length >= 2) {
        lSelect.options[0].text = t.onb_loc_home;
        lSelect.options[1].text = t.onb_loc_gym;
      }

      const lblOnbTrx = document.getElementById("lbl-onb-trx");
      if (lblOnbTrx) lblOnbTrx.textContent = t.onb_trx;

      const trxSelect = document.getElementById("onb-trx");
      if (trxSelect && trxSelect.options.length >= 2) {
        trxSelect.options[0].text = t.onb_trx_door;
        trxSelect.options[1].text = t.onb_trx_bar;
      }

      const lblOnbGear = document.getElementById("lbl-onb-gear");
      if (lblOnbGear) lblOnbGear.textContent = t.onb_gear;
      const lblCatA = document.getElementById("lbl-onb-cat-a");
      if (lblCatA) lblCatA.textContent = t.onb_cat_a;
      const lblCatB = document.getElementById("lbl-onb-cat-b");
      if (lblCatB) lblCatB.textContent = t.onb_cat_b;
      const lblCatC = document.getElementById("lbl-onb-cat-c");
      if (lblCatC) lblCatC.textContent = t.onb_cat_c;
      const lblCatD = document.getElementById("lbl-onb-cat-d");
      if (lblCatD) lblCatD.textContent = t.onb_cat_d;
      const lblCatE = document.getElementById("lbl-onb-cat-e");
      if (lblCatE) lblCatE.textContent = t.onb_cat_e;
      const btnSaveOnb = document.getElementById("btn-save-onb-text");
      if (btnSaveOnb) btnSaveOnb.textContent = t.onb_save_btn;

      // Update chip labels
      document.querySelectorAll(".chip-label").forEach(el => {
        el.textContent = lang === "ua" ? el.getAttribute("data-ua") : el.getAttribute("data-en");
      });

      // Update Day Pills
      for (let i = 1; i <= 5; i++) {
        const p = document.getElementById(`pill-d${i}`);
        if (p) p.textContent = lang === "ua" ? `День ${i}` : `Day ${i}`;
      }

      // Re-render gear checklist with translated gear names
      renderGearChecklist();

      // Re-render current active view
      if (activeTab === "workout") renderStrengthDay();
      else if (activeTab === "mobility") renderMobilityRoutine();
      else if (activeTab === "rehab") renderRehabRoutine();
      else if (activeTab === "progress") loadProgressStats();
    }

    // -------------------------------------------------------------
    // REACTIVE HEADER TOGGLES
    // -------------------------------------------------------------
    async function setVenue(venue) {
      document.getElementById("btn-loc-home").classList.toggle("active", venue === "home");
      document.getElementById("btn-loc-gym").classList.toggle("active", venue === "gym");
      userProfile.location = venue;
      showToast(currentLang === "ua" ? `Локація: ${venue === 'home' ? 'Дім 🏠' : 'Зал 🏋️'}` : `Venue: ${venue === 'home' ? 'Home 🏠' : 'Gym 🏋️'}`);
      await fetch("/api/profile", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ location: venue })
      });
      await regenerateCurrentPlan();
    }

    async function setSex(sex) {
      document.getElementById("btn-sex-female").classList.toggle("active", sex === "female");
      document.getElementById("btn-sex-male").classList.toggle("active", sex === "male");
      userProfile.sex = sex;
      showToast(currentLang === "ua" ? `Профіль: ${sex === 'female' ? 'Жіночий 👩' : 'Чоловічий 👨'}` : `Profile: ${sex === 'female' ? 'Female 👩' : 'Male 👨'}`);
      await fetch("/api/profile", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ sex: sex })
      });
      await regenerateCurrentPlan();
    }

    async function setLevel(lvl) {
      document.getElementById("btn-lvl-int").classList.toggle("active", lvl === "intermediate");
      document.getElementById("btn-lvl-adv").classList.toggle("active", lvl === "advanced");
      userProfile.level = lvl;
      showToast(currentLang === "ua" ? `Рівень: ${lvl === 'intermediate' ? 'Середній ⚡' : 'Просунутий 🔥'}` : `Level: ${lvl === 'intermediate' ? 'Intermediate ⚡' : 'Advanced 🔥'}`);
      await fetch("/api/profile", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ level: lvl })
      });
      await regenerateCurrentPlan();
    }

    // -------------------------------------------------------------
    // NAVIGATION & VIEW SWITCHING (STRICT STATE PRESERVATION)
    // -------------------------------------------------------------
    function switchView(view) {
      activeTab = view;
      document.getElementById("view-workout").style.display = view === "workout" ? "block" : "none";
      document.getElementById("view-mobility").style.display = view === "mobility" ? "block" : "none";
      document.getElementById("view-rehab").style.display = view === "rehab" ? "block" : "none";
      document.getElementById("view-progress").style.display = view === "progress" ? "block" : "none";
      document.getElementById("view-library").style.display = view === "library" ? "block" : "none";

      document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
      if (view === "workout") {
        document.getElementById("tab-workout").classList.add("active");
        renderStrengthDay();
      } else if (view === "mobility") {
        document.getElementById("tab-mobility").classList.add("active");
        if (!currentMobilityPlan) generateMobilityFlow();
        else renderMobilityRoutine();
      } else if (view === "rehab") {
        document.getElementById("tab-rehab").classList.add("active");
        if (!currentRehabPlan) generateRehabRoutine();
        else renderRehabRoutine();
      } else if (view === "progress") {
        document.getElementById("tab-progress").classList.add("active");
        loadProgressStats();
      } else if (view === "library") {
        document.getElementById("tab-library").classList.add("active");
        loadLibrary();
      }
    }

    // -------------------------------------------------------------
    // STRENGTH DAY NAVIGATION & RENDERING
    // -------------------------------------------------------------
    function selectStrengthDay(idx) {
      selectedDayIndex = idx;
      document.querySelectorAll("#strength-day-pills .day-pill").forEach((p, i) => {
        p.classList.toggle("active", i === idx);
      });
      fetch("/api/strength/set-day", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ day_index: idx })
      }).catch(console.error);
      renderStrengthDay();
    }

    async function nextDay() {
      if (!currentStrengthPlan || currentStrengthPlan.length === 0) return;
      if (selectedDayIndex < currentStrengthPlan.length - 1) {
        selectStrengthDay(selectedDayIndex + 1);
        showToast(currentLang === 'ua' ? `Перехід до Дня ${selectedDayIndex + 1}` : `Advanced to Day ${selectedDayIndex + 1}`);
      } else {
        // Completing Day 5! Start Next 5-Day Cycle
        showToast(currentLang === 'ua' ? '🚀 Генерація нового 5-денного циклу...' : '🚀 Generating next 5-day cycle...');
        const allIds = [];
        currentStrengthPlan.forEach(d => {
          if (d.exercises) d.exercises.forEach(e => allIds.push(e.exercise_id));
        });
        try {
          const res = await fetch("/api/generate", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ force_new_cycle: true, exclude_ids: allIds })
          });
          const data = await res.json();
          if (data.status === "ok" && data.strength_plan) {
            currentStrengthPlan = data.strength_plan;
            selectStrengthDay(0);
            showToast(currentLang === 'ua' ? I18N.ua.toast_cycle_started : I18N.en.toast_cycle_started);
          }
        } catch(e) {
          showToast("Error: " + e.message);
        }
      }
    }

    async function regenerateCurrentPlan() {
      showToast(currentLang === "ua" ? "⚡ Генерація свіжого тренування..." : "⚡ Generating fresh variations...");
      try {
        const res = await fetch("/api/generate", {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({
            force_new_cycle: false,
            workout_format: document.getElementById("workout-format-select").value
          })
        });
        const data = await res.json();
        if (data.status === "ok" && data.strength_plan) {
          currentStrengthPlan = data.strength_plan;
          renderStrengthDay();
        }
      } catch(e) {
        showToast("Error: " + e.message);
      }
    }

    async function changeFormat(fmt) {
      await fetch("/api/profile", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ workout_format: fmt })
      });
      await regenerateCurrentPlan();
    }

    function renderStrengthDay() {
      if (!currentStrengthPlan || currentStrengthPlan.length === 0) return;
      const day = currentStrengthPlan[selectedDayIndex] || currentStrengthPlan[0];

      // Update banner title & desc (Pure EN or Pure UA)
      const dayTitle = currentLang === "ua" ? (day.day_label_ua || day.day_label) : day.day_label;
      const dayDesc = currentLang === "ua" ? (day.format_description_ua || day.format_description) : day.format_description;
      document.getElementById("workout-day-title").textContent = `▶️ ${dayTitle}`;
      document.getElementById("workout-day-desc").textContent = dayDesc;

      // Target HR badge
      const hrBadge = document.getElementById("hr-target-badge");
      if (day.target_hr_zone) {
        const hrName = currentLang === "ua" ? (day.target_hr_zone_ua || day.target_hr_zone) : day.target_hr_zone;
        hrBadge.textContent = `❤️ ${hrName} (${day.target_hr_bpm_range || ''})`;
        hrBadge.style.display = "inline-block";
      } else {
        hrBadge.style.display = "none";
      }

      // Format select & badge
      document.getElementById("workout-format-select").value = day.format_type || "superset";
      document.getElementById("format-badge").textContent = (day.format_type || "superset").toUpperCase();

      // Next Day Button label
      const nextBtn = document.getElementById("btn-next-day");
      if (selectedDayIndex < currentStrengthPlan.length - 1) {
        nextBtn.textContent = currentLang === "ua" ? `${I18N.ua.next_day_prefix}${selectedDayIndex + 2}) ➡️` : `${I18N.en.next_day_prefix}${selectedDayIndex + 2}) ➡️`;
        nextBtn.className = "btn btn-accent";
      } else {
        nextBtn.textContent = currentLang === "ua" ? I18N.ua.start_cycle : I18N.en.start_cycle;
        nextBtn.className = "btn btn-purple";
      }

      // Format specific triggers: Tabata, Sandwich, Circuit
      const fmt = (day.format_type || "").toLowerCase();
      document.getElementById("btn-tabata-trigger").style.display = fmt === "tabata" ? "inline-flex" : "none";
      document.getElementById("sandwich-ladder-box").style.display = fmt === "sandwich" ? "block" : "none";
      document.getElementById("circuit-tracker-box").style.display = fmt === "circuit" ? "flex" : "none";

      if (fmt === "sandwich") renderSandwichLadder();

      // Progress Tracker
      const exercises = day.exercises || [];
      const total = exercises.length;
      const completed = exercises.filter(e => e.completed).length;
      const pct = total > 0 ? Math.round((completed / total) * 100) : 0;
      document.getElementById("strength-comp-counter").textContent = `${completed} / ${total} ${currentLang === 'ua' ? 'виконано' : 'Completed'} (${pct}%)`;
      document.getElementById("strength-comp-bar").style.width = `${pct}%`;

      // Render Exercise Cards (grouped by superset or single)
      const container = document.getElementById("strength-exercise-list");
      container.innerHTML = "";

      const supersetMap = new Map();
      exercises.forEach((ex, idx) => {
        const group = ex.superset_group || `Station ${idx + 1}`;
        if (!supersetMap.has(group)) supersetMap.set(group, []);
        supersetMap.get(group).push(ex);
      });

      supersetMap.forEach((groupExs, groupName) => {
        const block = document.createElement("div");
        block.className = "superset-block";

        const header = document.createElement("div");
        header.className = "superset-header";
        const groupTitle = currentLang === "ua" ? groupName.replace("Superset", "Суперсет") : groupName;
        header.innerHTML = `
          <div class="superset-title">⚡ ${groupTitle}</div>
          <div class="superset-badge">${groupExs.length} ${currentLang === 'ua' ? 'вправи' : 'Exercises'}</div>
        `;
        block.appendChild(header);

        groupExs.forEach(ex => {
          block.appendChild(createExerciseCard(ex, "strength", selectedDayIndex));
        });

        container.appendChild(block);
      });
    }

    function createExerciseCard(ex, planType, dayIdx) {
      const card = document.createElement("div");
      card.className = `card ${ex.completed ? 'completed-card' : ''}`;

      // Pure title (suppress subtitles to eliminate 50/50 mixed language bug)
      const title = currentLang === "ua" ? (ex.name_ua || ex.name) : ex.name;
      const zoneTag = currentLang === "ua" ? (ex.zone_ua || ex.zone_en) : ex.zone_en;
      const setupText = currentLang === "ua" ? (ex.setup_ua || ex.setup) : ex.setup;
      const execText = currentLang === "ua" ? (ex.execution_ua || ex.execution) : ex.execution;
      const tipText = currentLang === "ua" ? (ex.form_tips_ua || ex.form_tips) : ex.form_tips;
      const progTip = currentLang === "ua" ? (ex.coach_progression_tip_ua || ex.coach_progression_tip) : ex.coach_progression_tip;
      const altText = currentLang === "ua" ? (ex.equipment_alternatives_ua || ex.equipment_alternatives) : ex.equipment_alternatives;

      let perfBadge = "";
      if (ex.last_weight || ex.last_reps) {
        perfBadge = `<span class="badge badge-last-perf">${currentLang === 'ua' ? 'Минулий' : 'Last'}: ${ex.last_weight || '-'} × ${ex.last_reps || '-'}</span>`;
      }

      card.innerHTML = `
        <div class="card-top">
          <div>
            <span class="ex-index">#${ex.order_index}</span>
            <span class="exercise-title">${title}</span>
          </div>
          <div style="display: flex; gap: 5px; flex-wrap: wrap;">
            ${perfBadge}
            <span class="badge badge-zone">${zoneTag}</span>
            <span class="badge">${ex.sets} × ${ex.reps}</span>
            <span class="badge">${ex.rest_seconds}s</span>
          </div>
        </div>

        ${progTip ? `<div class="badge-tip">${progTip}</div>` : ""}
        ${altText ? `<div class="badge-alt">🔄 <strong>${currentLang === 'ua' ? 'Альтернатива' : 'Alternative'}:</strong> ${altText}</div>` : ""}

        <div class="form-guide-toggle" onclick="toggleGuide('${ex.exercise_id}')">
          ${I18N[currentLang].guide_btn} ▾
        </div>
        <div id="guide-${ex.exercise_id}" class="form-guide-content">
          <div class="guide-step"><span class="guide-label">${I18N[currentLang].guide_setup}</span>${setupText || ''}</div>
          <div class="guide-step"><span class="guide-label">${I18N[currentLang].guide_exec}</span>${execText || ''}</div>
          <div class="guide-step"><span class="guide-label guide-tip-label">${I18N[currentLang].guide_tip}</span>${tipText || ''}</div>
        </div>

        <div class="exercise-inputs">
          <button class="check-btn ${ex.completed ? 'checked' : ''}" onclick="toggleExComplete('${planType}', ${dayIdx}, '${ex.exercise_id}', ${!ex.completed})">
            ${ex.completed ? I18N[currentLang].marked_done : I18N[currentLang].mark_done}
          </button>
          <div class="input-group">
            <label>${I18N[currentLang].weight}</label>
            <input type="text" id="w-${ex.exercise_id}" value="${ex.actual_weight || ex.last_weight || ''}" placeholder="e.g. 14kg" style="width: 100px;">
          </div>
          <div class="input-group">
            <label>${I18N[currentLang].reps_done}</label>
            <input type="text" id="r-${ex.exercise_id}" value="${ex.actual_reps || ex.last_reps || ex.reps}" style="width: 80px;">
          </div>
          <div class="input-group" style="margin-left: auto;">
            <label>${I18N[currentLang].skip}</label>
            <input type="checkbox" id="skip-${ex.exercise_id}" style="width: 16px; height: 16px;">
          </div>
        </div>
      `;
      return card;
    }

    function toggleGuide(id) {
      const g = document.getElementById(`guide-${id}`);
      if (g) g.classList.toggle("open");
    }

    async function toggleExComplete(planType, dayIdx, exId, completed) {
      const wInput = document.getElementById(`w-${exId}`);
      const rInput = document.getElementById(`r-${exId}`);
      const weight = wInput ? wInput.value : "";
      const reps = rInput ? rInput.value : "";

      await fetch("/api/toggle-exercise-complete", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
          plan_type: planType,
          day_index: dayIdx,
          exercise_id: exId,
          completed: completed,
          actual_reps: reps,
          actual_weight: weight
        })
      });

      // Update local state
      let list = [];
      if (planType === "strength" && currentStrengthPlan[dayIdx]) {
        list = currentStrengthPlan[dayIdx].exercises || [];
      } else if (planType === "mobility" && currentMobilityPlan) {
        list = currentMobilityPlan.exercises || [];
      } else if (planType === "rehab" && currentRehabPlan) {
        list = currentRehabPlan.exercises || [];
      }

      for (let ex of list) {
        if (ex.exercise_id === exId) {
          ex.completed = completed;
          if (weight) ex.actual_weight = weight;
          if (reps) ex.actual_reps = reps;
          break;
        }
      }

      if (planType === "strength") renderStrengthDay();
      else if (planType === "mobility") renderMobilityRoutine();
      else if (planType === "rehab") renderRehabRoutine();
    }

    // -------------------------------------------------------------
    // SANDWICH PYRAMID LADDER (INTERACTIVE ROUND CHIPS)
    // -------------------------------------------------------------
    const SANDWICH_ROUNDS = [
      { id: 1, label: "R1: Ex #1" },
      { id: 2, label: "R2: Ex #1+#2" },
      { id: 3, label: "R3: Ex #1..#3" },
      { id: 4, label: "R4: Ex #1..#4" },
      { id: 5, label: "R5: Ex #1..#5" },
      { id: 6, label: "R6: Ex #1..#6" },
      { id: 7, label: "R7: Ex #1..#7" },
      { id: 8, label: "R8: Ex #1..#8" },
      { id: 9, label: "R9: Ex #1..#9" },
      { id: 10, label: "R10: Ex #1..#10 (Peak)" },
      { id: 11, label: "R11: Ex #2..#10" },
      { id: 12, label: "R12: Ex #3..#10" },
      { id: 13, label: "R13: Ex #4..#10" },
      { id: 14, label: "R14: Ex #5..#10" },
      { id: 15, label: "R15: Ex #6..#10" },
      { id: 16, label: "R16: Ex #7..#10" },
      { id: 17, label: "R17: Ex #8..#10" },
      { id: 18, label: "R18: Ex #9..#10" },
      { id: 19, label: "R19: Ex #10 (Finish)" }
    ];

    function renderSandwichLadder() {
      const c = document.getElementById("sandwich-chips-container");
      c.innerHTML = "";
      SANDWICH_ROUNDS.forEach(r => {
        const chip = document.createElement("div");
        chip.className = "ladder-chip";
        chip.textContent = r.label;
        chip.onclick = function() {
          this.classList.toggle("checked");
        };
        c.appendChild(chip);
      });
    }

    function toggleCircuitRound(num) {
      const btn = document.getElementById(`c-round-${num}`);
      if (btn) {
        btn.classList.toggle("checked");
        btn.textContent = btn.classList.contains("checked") ? `Round ${num} [✓]` : `Round ${num} [ ]`;
      }
    }

    // -------------------------------------------------------------
    // DYNAMIC MOBILITY (10 DRILLS)
    // -------------------------------------------------------------
    function toggleMobZone(z, el) {
      if (selectedMobZones.includes(z)) {
        selectedMobZones = selectedMobZones.filter(x => x !== z);
        el.classList.remove("active-green");
      } else {
        selectedMobZones.push(z);
        el.classList.add("active-green");
      }
    }

    async function generateMobilityFlow() {
      showToast(currentLang === "ua" ? "🧘 Генерація комплексу мобільності (10 вправ)..." : "🧘 Generating mobility flow (10 drills)...");
      try {
        const res = await fetch("/api/mobility/generate", {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({ focus_zones: selectedMobZones })
        });
        const data = await res.json();
        if (data.status === "ok" && data.mobility_plan) {
          currentMobilityPlan = data.mobility_plan;
          renderMobilityRoutine();
        }
      } catch(e) {
        showToast("Error: " + e.message);
      }
    }

    function renderMobilityRoutine() {
      if (!currentMobilityPlan) return;
      const exercises = currentMobilityPlan.exercises || [];
      const total = exercises.length;
      const completed = exercises.filter(e => e.completed).length;
      const pct = total > 0 ? Math.round((completed / total) * 100) : 0;

      document.getElementById("mob-comp-counter").textContent = `${completed} / ${total} ${currentLang === 'ua' ? 'виконано' : 'Completed'} (${pct}%)`;
      document.getElementById("mob-comp-bar").style.width = `${pct}%`;

      const container = document.getElementById("mobility-exercise-list");
      container.innerHTML = "";
      exercises.forEach(ex => {
        container.appendChild(createExerciseCard(ex, "mobility", 0));
      });
    }

    async function submitMobilitySession() {
      if (!currentMobilityPlan) return;
      await submitCompletedWorkoutGeneric(currentMobilityPlan, "mobility");
      showToast(currentLang === "ua" ? "✓ Комплекс мобільності збережено!" : "✓ Mobility flow completed & saved!");
    }

    // -------------------------------------------------------------
    // REHABILITATION & RESTORATION (10 DRILLS)
    // -------------------------------------------------------------
    function toggleRehabDept(dept, el) {
      if (selectedRehabDepts.includes(dept)) {
        if (selectedRehabDepts.length > 1) {
          selectedRehabDepts = selectedRehabDepts.filter(x => x !== dept);
          el.classList.remove("active-purple");
        }
      } else {
        selectedRehabDepts.push(dept);
        el.classList.add("active-purple");
      }
      generateRehabRoutine();
    }

    async function generateRehabRoutine() {
      showToast(currentLang === "ua" ? "❤️‍🩹 Генерація реабілітації (10 вправ)..." : "❤️‍🩹 Generating rehab flow (10 drills)...");
      try {
        const res = await fetch("/api/rehab/generate", {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({ department: selectedRehabDepts })
        });
        const data = await res.json();
        if (data.status === "ok" && data.rehab_plan) {
          currentRehabPlan = data.rehab_plan;
          renderRehabRoutine();
        }
      } catch(e) {
        showToast("Error: " + e.message);
      }
    }

    function renderRehabRoutine() {
      if (!currentRehabPlan) return;
      const exercises = currentRehabPlan.exercises || [];
      const total = exercises.length;
      const completed = exercises.filter(e => e.completed).length;
      const pct = total > 0 ? Math.round((completed / total) * 100) : 0;

      document.getElementById("rehab-comp-counter").textContent = `${completed} / ${total} ${currentLang === 'ua' ? 'виконано' : 'Completed'} (${pct}%)`;
      document.getElementById("rehab-comp-bar").style.width = `${pct}%`;

      const container = document.getElementById("rehab-exercise-list");
      container.innerHTML = "";
      exercises.forEach(ex => {
        container.appendChild(createExerciseCard(ex, "rehab", 0));
      });
    }

    async function submitRehabSession() {
      if (!currentRehabPlan) return;
      await submitCompletedWorkoutGeneric(currentRehabPlan, "rehabilitation");
      showToast(currentLang === "ua" ? "✓ Реабілітаційний комплекс збережено!" : "✓ Rehabilitation flow completed & saved!");
    }

    // -------------------------------------------------------------
    // COMPLETION SUBMISSION & HEART RATE ANALYSIS
    // -------------------------------------------------------------
    async function submitStrengthSession() {
      if (!currentStrengthPlan || !currentStrengthPlan[selectedDayIndex]) return;
      const day = currentStrengthPlan[selectedDayIndex];

      const duration = parseInt(document.getElementById("session-duration").value) || 55;
      const minHr = document.getElementById("session-min-hr").value;
      const avgHr = document.getElementById("session-avg-hr").value;
      const maxHr = document.getElementById("session-max-hr").value;
      const activeCals = document.getElementById("session-active-cals") ? document.getElementById("session-active-cals").value : null;
      const totalCals = document.getElementById("session-total-cals") ? document.getElementById("session-total-cals").value : null;
      const trainingLoad = document.getElementById("session-training-load") ? document.getElementById("session-training-load").value : null;
      const recoveryHours = document.getElementById("session-recovery-hours") ? document.getElementById("session-recovery-hours").value : null;
      const z1 = document.getElementById("session-z1") ? document.getElementById("session-z1").value : null;
      const z2 = document.getElementById("session-z2") ? document.getElementById("session-z2").value : null;
      const z3 = document.getElementById("session-z3") ? document.getElementById("session-z3").value : null;
      const z4 = document.getElementById("session-z4") ? document.getElementById("session-z4").value : null;
      const z5 = document.getElementById("session-z5") ? document.getElementById("session-z5").value : null;
      const rpe = parseInt(document.getElementById("session-rpe").value) || 3;
      const notes = document.getElementById("session-notes").value;

      const exerciseLogs = (day.exercises || []).map(ex => {
        const wInput = document.getElementById(`w-${ex.exercise_id}`);
        const rInput = document.getElementById(`r-${ex.exercise_id}`);
        const sCheck = document.getElementById(`skip-${ex.exercise_id}`);
        return {
          exercise_id: ex.exercise_id,
          sets_completed: ex.sets,
          reps_completed: rInput ? rInput.value : ex.reps,
          weight_used: wInput ? wInput.value : "Bodyweight",
          skipped: sCheck ? sCheck.checked : false,
          perceived_difficulty: rpe,
          notes: ""
        };
      });

      try {
        const res = await fetch("/api/complete", {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({
            workout_id: day.workout_id,
            duration_minutes: duration,
            watch_duration_minutes: duration,
            min_heart_rate: minHr ? parseInt(minHr) : null,
            avg_heart_rate: avgHr ? parseInt(avgHr) : null,
            max_heart_rate: maxHr ? parseInt(maxHr) : null,
            active_calories: activeCals ? parseInt(activeCals) : null,
            total_calories: totalCals ? parseInt(totalCals) : null,
            training_load: trainingLoad ? parseFloat(trainingLoad) : null,
            recovery_time_hours: recoveryHours ? parseInt(recoveryHours) : null,
            zone1_mins: z1 ? parseFloat(z1) : null,
            zone2_mins: z2 ? parseFloat(z2) : null,
            zone3_mins: z3 ? parseFloat(z3) : null,
            zone4_mins: z4 ? parseFloat(z4) : null,
            zone5_mins: z5 ? parseFloat(z5) : null,
            perceived_difficulty: rpe,
            overall_rating: 4,
            overall_fatigue: rpe,
            user_notes: notes,
            exercise_logs: exerciseLogs
          })
        });
        const data = await res.json();
        if (data.status === "ok") {
          showToast(currentLang === "ua" ? I18N.ua.toast_saved : I18N.en.toast_saved);
          if (data.hr_analysis) {
            openHrModal(data.hr_analysis);
          }
        }
      } catch(e) {
        showToast("Error: " + e.message);
      }
    }

    async function submitCompletedWorkoutGeneric(planObj, formatType) {
      const exerciseLogs = (planObj.exercises || []).map(ex => ({
        exercise_id: ex.exercise_id,
        sets_completed: ex.sets,
        reps_completed: ex.actual_reps || ex.reps,
        weight_used: ex.actual_weight || "Bodyweight",
        skipped: false,
        perceived_difficulty: 2,
        notes: ""
      }));
      await fetch("/api/complete", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
          workout_id: planObj.workout_id,
          duration_minutes: planObj.target_duration_minutes || 25,
          perceived_difficulty: 2,
          overall_rating: 5,
          overall_fatigue: 2,
          user_notes: `${formatType} session completed`,
          exercise_logs: exerciseLogs
        })
      });
    }

    function openHrModal(analysis) {
      const b = document.getElementById("hr-analysis-body");
      const title = currentLang === "ua" ? (analysis.status_ua || analysis.status_en) : analysis.status_en;
      const feedback = currentLang === "ua" ? (analysis.feedback_ua || analysis.feedback_en) : analysis.feedback_en;
      const adviceTitle = currentLang === "ua" ? (analysis.physio_title_ua || analysis.physio_title_en) : analysis.physio_title_en;
      const advice = currentLang === "ua" ? (analysis.physio_advice_ua || analysis.physio_advice_en) : analysis.physio_advice_en;

      let telemetryHtml = "";
      if (analysis.caloric_burn_rate || analysis.hr_recovery_spread || analysis.zone_distribution_analysis || analysis.watch_training_load || analysis.recommended_recovery_hours) {
        telemetryHtml = `
          <div style="margin: 14px 0; background: #090d16; padding: 12px; border-radius: 8px; border: 1px solid var(--border);">
            <div style="font-size: 13px; font-weight: 800; color: #38bdf8; margin-bottom: 8px;">⌚ ${currentLang === 'ua' ? 'Біометричні показники смарт-годинника' : 'Smartwatch Biometric Telemetry'}</div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 8px; margin-bottom: 8px;">
              ${analysis.caloric_burn_rate ? `<div style="background:#1e293b; padding:8px; border-radius:6px;"><div style="font-size:11px; color:#94a3b8;">${currentLang === 'ua' ? 'Горіння калорій' : 'Burn Rate'}</div><div style="font-size:14px; font-weight:800; color:#f59e0b;">🔥 ${analysis.caloric_burn_rate} kcal/min</div></div>` : ""}
              ${analysis.hr_recovery_spread ? `<div style="background:#1e293b; padding:8px; border-radius:6px;"><div style="font-size:11px; color:#94a3b8;">${currentLang === 'ua' ? 'HR Відновлення' : 'HR Spread'}</div><div style="font-size:14px; font-weight:800; color:#10b981;">📉 ${analysis.hr_recovery_spread} BPM drop</div></div>` : ""}
              ${analysis.watch_training_load ? `<div style="background:#1e293b; padding:8px; border-radius:6px;"><div style="font-size:11px; color:#94a3b8;">${currentLang === 'ua' ? 'Навантаження' : 'Training Load'}</div><div style="font-size:14px; font-weight:800; color:#a855f7;">⚡ ${analysis.watch_training_load} / 5.0</div></div>` : ""}
              ${analysis.recommended_recovery_hours ? `<div style="background:#1e293b; padding:8px; border-radius:6px;"><div style="font-size:11px; color:#94a3b8;">${currentLang === 'ua' ? 'Відпочинок' : 'Recovery Needed'}</div><div style="font-size:14px; font-weight:800; color:#38bdf8;">⏱️ ${analysis.recommended_recovery_hours} hrs</div></div>` : ""}
            </div>
            ${analysis.calorie_density_assessment ? `<div style="font-size:12px; color:#cbd5e1; margin-bottom:4px;"><strong>${currentLang === 'ua' ? 'Оцінка калорійності:' : 'Caloric Density:'}</strong> ${analysis.calorie_density_assessment}</div>` : ""}
            ${analysis.hr_recovery_assessment ? `<div style="font-size:12px; color:#cbd5e1; margin-bottom:4px;"><strong>${currentLang === 'ua' ? 'Вагусний тонус:' : 'Vagal Tone:'}</strong> ${analysis.hr_recovery_assessment}</div>` : ""}
            ${analysis.zone_distribution_analysis ? `<div style="font-size:12px; color:#cbd5e1;"><strong>${currentLang === 'ua' ? 'Розподіл зон:' : 'Zone Distribution:'}</strong> ${analysis.zone_distribution_analysis}</div>` : ""}
          </div>
        `;
      }

      b.innerHTML = `
        <div style="font-size: 18px; font-weight: 800; color: #38bdf8; margin-bottom: 8px;">${title}</div>
        <div style="font-size: 13px; color: #cbd5e1; margin-bottom: 14px; line-height: 1.6;">${feedback}</div>
        ${telemetryHtml}
        ${advice ? `
          <div style="background: rgba(245, 158, 11, 0.1); border-left: 3px solid #f59e0b; padding: 10px 12px; border-radius: 6px;">
            <div style="font-size: 13px; font-weight: 800; color: #fde047; margin-bottom: 4px;">${adviceTitle}</div>
            <div style="font-size: 12px; color: #cbd5e1; line-height: 1.5;">${advice}</div>
          </div>
        ` : ""}
      `;
      document.getElementById("hr-modal").classList.add("open");
    }

    function closeHrModal() {
      document.getElementById("hr-modal").classList.remove("open");
    }

    // -------------------------------------------------------------
    // DYNAMIC TABATA TIMER (WITH EXERCISES & WEB SPEECH VOICE)
    // -------------------------------------------------------------
    let tabataRunning = false;
    let tabataSec = 40;
    let tabataPhase = "work"; // "work" (40s), "rest" (10s), "intermission" (60s)
    let tabataInterval = null;
    let tabataCycle = 1;      // 1..8
    let tabataExIdx = 0;      // 0..9
    let tabataSound = true;

    function openTabataModal() {
      tabataExIdx = 0;
      tabataCycle = 1;
      resetTabataTimer();
      document.getElementById("tabata-modal").classList.add("open");
      updateTabataDisplay();
    }

    function closeTabataModal() {
      clearInterval(tabataInterval);
      tabataRunning = false;
      document.getElementById("tabata-modal").classList.remove("open");
    }

    function getActiveTabataExercises() {
      if (currentStrengthPlan && currentStrengthPlan[selectedDayIndex]) {
        return currentStrengthPlan[selectedDayIndex].exercises || [];
      }
      return [];
    }

    function updateTabataDisplay() {
      const exs = getActiveTabataExercises();
      const curEx = exs[tabataExIdx] || { name: "Exercise", name_ua: "Вправа" };
      const nextEx = exs[tabataExIdx + 1] || null;

      const curName = currentLang === "ua" ? (curEx.name_ua || curEx.name) : curEx.name;
      document.getElementById("tabata-ex-counter").textContent = currentLang === "ua" ? `Вправа ${tabataExIdx + 1} з ${exs.length}` : `Exercise ${tabataExIdx + 1} of ${exs.length}`;
      document.getElementById("tabata-current-name").textContent = curName;

      if (nextEx) {
        const nextName = currentLang === "ua" ? (nextEx.name_ua || nextEx.name) : nextEx.name;
        document.getElementById("tabata-next-preview").textContent = currentLang === "ua" ? `Наступна: ${nextName}` : `Next up: ${nextName}`;
      } else {
        document.getElementById("tabata-next-preview").textContent = currentLang === "ua" ? "Фінальна вправа!" : "Final exercise!";
      }

      document.getElementById("tabata-round-info").textContent = currentLang === "ua" ? `Інтервал ${tabataCycle} з 8` : `Interval ${tabataCycle} of 8`;

      const badge = document.getElementById("tabata-phase-badge");
      const digits = document.getElementById("tabata-digits");

      if (tabataPhase === "work") {
        badge.className = "tabata-phase-pill phase-work";
        badge.textContent = currentLang === "ua" ? "РОБОТА (40с)" : "WORK (40s)";
        digits.className = "tabata-digits digits-work";
      } else if (tabataPhase === "rest") {
        badge.className = "tabata-phase-pill phase-rest";
        badge.textContent = currentLang === "ua" ? "ВІДПОЧИНОК (10с)" : "REST (10s)";
        digits.className = "tabata-digits digits-rest";
      } else {
        badge.className = "tabata-phase-pill phase-intermission";
        badge.textContent = currentLang === "ua" ? "ВІДПОЧИНОК МІЖ СЕТАМИ (60с)" : "SET REST (60s)";
        digits.className = "tabata-digits digits-intermission";
      }

      digits.textContent = tabataSec < 10 ? `0${tabataSec}` : tabataSec;
    }

    function toggleTabataPlay() {
      const btn = document.getElementById("btn-tabata-play");
      if (tabataRunning) {
        clearInterval(tabataInterval);
        tabataRunning = false;
        btn.textContent = currentLang === "ua" ? "▶️ Продовжити" : "▶️ Resume";
      } else {
        tabataRunning = true;
        btn.textContent = currentLang === "ua" ? "⏸️ Пауза" : "⏸️ Pause";
        // Speak initial work callout
        if (tabataPhase === "work" && tabataSec === 40) {
          const exs = getActiveTabataExercises();
          const name = currentLang === "ua" ? (exs[tabataExIdx]?.name_ua || "вправа") : (exs[tabataExIdx]?.name || "exercise");
          speakVoice(currentLang === "ua" ? `Робота! ${name}` : `Work! ${name}`);
        }
        tabataInterval = setInterval(tabataTick, 1000);
      }
    }

    function nextTabataExercise() {
      const exs = getActiveTabataExercises();
      if (tabataExIdx < exs.length - 1) {
        tabataExIdx++;
        tabataCycle = 1;
        tabataSec = 40;
        tabataPhase = "work";
        updateTabataDisplay();
        const curName = currentLang === "ua" ? (exs[tabataExIdx]?.name_ua || "вправа") : (exs[tabataExIdx]?.name || "exercise");
        speakVoice(currentLang === "ua" ? `Наступна вправа: ${curName}` : `Next exercise: ${curName}`);
      } else {
        showToast(currentLang === "ua" ? "🎉 Табата сесію завершено!" : "🎉 Tabata session finished!");
      }
    }

    function resetTabataTimer() {
      clearInterval(tabataInterval);
      tabataRunning = false;
      tabataSec = 40;
      tabataPhase = "work";
      tabataCycle = 1;
      const btn = document.getElementById("btn-tabata-play");
      if (btn) btn.textContent = currentLang === "ua" ? "▶️ Старт" : "▶️ Start";
      updateTabataDisplay();
    }

    function toggleTabataSound() {
      tabataSound = !tabataSound;
      document.getElementById("btn-tabata-sound").textContent = tabataSound ? "🔊" : "🔇";
    }

    function tabataTick() {
      tabataSec--;

      // Countdown voice & beeps
      if (tabataSec <= 3 && tabataSec > 0) {
        if (tabataSound) {
          playBeep(440, 0.15);
          speakVoice(String(tabataSec));
        }
      }

      if (tabataSec < 0) {
        if (tabataPhase === "work") {
          // Switch to 10s rest
          tabataPhase = "rest";
          tabataSec = 10;
          if (tabataSound) {
            playBeep(880, 0.3);
            speakVoice(currentLang === "ua" ? "Відпочинок!" : "Rest!");
          }
        } else if (tabataPhase === "rest") {
          if (tabataCycle < 8) {
            // Next 40s cycle of same exercise
            tabataCycle++;
            tabataPhase = "work";
            tabataSec = 40;
            if (tabataSound) {
              playBeep(520, 0.3);
              speakVoice(currentLang === "ua" ? `Робота! Інтервал ${tabataCycle}` : `Work! Interval ${tabataCycle}`);
            }
          } else {
            // Completed 8 cycles! Check for 60s intermission between exercises
            const exs = getActiveTabataExercises();
            if (tabataExIdx < exs.length - 1) {
              tabataPhase = "intermission";
              tabataSec = 60;
              const nextName = currentLang === "ua" ? (exs[tabataExIdx + 1]?.name_ua || "") : (exs[tabataExIdx + 1]?.name || "");
              speakVoice(currentLang === "ua" ? `Відпочинок 1 хвилина. Наступна: ${nextName}` : `One minute rest. Next up: ${nextName}`);
            } else {
              // Workout finished
              clearInterval(tabataInterval);
              tabataRunning = false;
              speakVoice(currentLang === "ua" ? "Вітаємо! Табата завершена!" : "Congratulations! Tabata complete!");
            }
          }
        } else if (tabataPhase === "intermission") {
          // Advance to next exercise
          tabataExIdx++;
          tabataCycle = 1;
          tabataPhase = "work";
          tabataSec = 40;
          const exs = getActiveTabataExercises();
          const curName = currentLang === "ua" ? (exs[tabataExIdx]?.name_ua || "") : (exs[tabataExIdx]?.name || "");
          speakVoice(currentLang === "ua" ? `Робота! ${curName}` : `Work! ${curName}`);
        }
      }

      updateTabataDisplay();
    }

    function speakVoice(text) {
      if (!tabataSound) return;
      try {
        if ("speechSynthesis" in window) {
          window.speechSynthesis.cancel();
          const u = new SpeechSynthesisUtterance(text);
          u.lang = currentLang === "ua" ? "uk-UA" : "en-US";
          u.rate = 1.05;
          window.speechSynthesis.speak(u);
        }
      } catch(e) {}
    }

    function playBeep(freq = 440, dur = 0.1) {
      try {
        const AudioCtx = window.AudioContext || window.webkitAudioContext;
        if (!AudioCtx) return;
        const ctx = new AudioCtx();
        const osc = ctx.createOscillator();
        const g = ctx.createGain();
        osc.frequency.value = freq;
        osc.connect(g);
        g.connect(ctx.destination);
        osc.start();
        g.gain.exponentialRampToValueAtTime(0.00001, ctx.currentTime + dur);
        osc.stop(ctx.currentTime + dur);
      } catch(e) {}
    }

    // -------------------------------------------------------------
    // ONBOARDING & PROFILE QUESTIONNAIRE
    // -------------------------------------------------------------
    function openOnboardingModal() {
      document.getElementById("onb-age").value = userProfile.age || 30;
      document.getElementById("onb-cw").value = userProfile.current_weight || 75.0;
      document.getElementById("onb-tw").value = userProfile.target_weight || 72.0;
      document.getElementById("onb-goal").value = userProfile.goal || "muscle_gain";
      document.getElementById("onb-loc").value = userProfile.location || "home";
      document.getElementById("onb-trx").value = userProfile.trx_anchor || "door";

      setOnboardingSex(userProfile.sex || "female");
      renderGearChecklist();

      // Initialize onbInjuries and onbMeds from profile
      onbInjuries = Array.from(userProfile.injuries_to_avoid || []);
      onbMeds = Array.from(userProfile.medical_conditions || []);

      // Synchronize visual active state of all 25 chips
      document.querySelectorAll("#onb-injury-chips .chip").forEach(el => {
        const id = el.id.replace("chip-inj-", "");
        el.classList.toggle("active", onbInjuries.includes(id));
      });

      ["onb-cat-b-chips", "onb-cat-c-chips", "onb-cat-d-chips", "onb-cat-e-chips"].forEach(catId => {
        const catContainer = document.getElementById(catId);
        if (catContainer) {
          catContainer.querySelectorAll(".chip").forEach(el => {
            const id = el.id.replace("chip-med-", "");
            el.classList.toggle("active", onbMeds.includes(id));
          });
        }
      });

      document.getElementById("onboarding-modal").classList.add("open");
    }

    function closeOnboardingModal() {
      document.getElementById("onboarding-modal").classList.remove("open");
    }

    function setOnboardingSex(sex) {
      document.getElementById("onb-sex-female").classList.toggle("active", sex === "female");
      document.getElementById("onb-sex-male").classList.toggle("active", sex === "male");
    }

    function toggleOnboardingGearDisplay(loc) {
      document.getElementById("onb-gear-container").style.display = loc === "home" ? "block" : "none";
    }

    function renderGearChecklist() {
      const c = document.getElementById("onb-gear-checklist");
      c.innerHTML = "";
      const inventory = userProfile.equipment_inventory || onbGear;
      onbGear.forEach(g => {
        const checked = inventory.includes(g);
        const div = document.createElement("label");
        div.style.display = "flex";
        div.style.alignItems = "center";
        div.style.gap = "6px";
        div.style.cursor = "pointer";
        const labelText = translateEquip(g);
        div.innerHTML = `
          <input type="checkbox" value="${g}" ${checked ? 'checked' : ''} style="width: 15px; height: 15px;">
          <span>${labelText}</span>
        `;
        c.appendChild(div);
      });
    }

    async function toggleOnbInjury(joint, el) {
      if (onbInjuries.includes(joint)) {
        onbInjuries = onbInjuries.filter(x => x !== joint);
        el.classList.remove("active");
      } else {
        onbInjuries.push(joint);
        el.classList.add("active");
      }
      userProfile.injuries_to_avoid = onbInjuries;
      try {
        await fetch("/api/profile", {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({ injuries_to_avoid: onbInjuries })
        });
        await regenerateCurrentPlan();
      } catch(e) {
        console.error("Auto-sync injury error:", e);
      }
    }

    async function toggleOnbMed(med, el) {
      if (onbMeds.includes(med)) {
        onbMeds = onbMeds.filter(x => x !== med);
        el.classList.remove("active");
      } else {
        onbMeds.push(med);
        el.classList.add("active");
      }
      userProfile.medical_conditions = onbMeds;
      try {
        await fetch("/api/profile", {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({ medical_conditions: onbMeds })
        });
        await regenerateCurrentPlan();
      } catch(e) {
        console.error("Auto-sync medical condition error:", e);
      }
    }

    async function saveOnboardingProfile() {
      const isFemale = document.getElementById("onb-sex-female").classList.contains("active");
      const sex = isFemale ? "female" : "male";
      const age = parseInt(document.getElementById("onb-age").value) || 30;
      const cw = parseFloat(document.getElementById("onb-cw").value) || 75.0;
      const tw = parseFloat(document.getElementById("onb-tw").value) || 72.0;
      const goal = document.getElementById("onb-goal").value;
      const loc = document.getElementById("onb-loc").value;
      const trx = document.getElementById("onb-trx").value;

      const checkedGear = [];
      document.querySelectorAll("#onb-gear-checklist input:checked").forEach(cb => checkedGear.push(cb.value));

      showToast(currentLang === "ua" ? "Збереження анкети та генерація 5-денного спліту..." : "Saving questionnaire & generating 5-day split...");
      try {
        const res = await fetch("/api/onboarding", {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({
            sex: sex,
            age: age,
            current_weight: cw,
            target_weight: tw,
            goal: goal,
            location: loc,
            trx_anchor: trx,
            equipment_inventory: checkedGear,
            injuries_to_avoid: onbInjuries,
            medical_conditions: onbMeds
          })
        });
        const data = await res.json();
        if (data.status === "ok") {
          userProfile = data.profile;
          currentStrengthPlan = data.strength_plan;
          selectStrengthDay(0);
          setVenue(userProfile.location || "home");
          setSex(userProfile.sex || "female");
          closeOnboardingModal();
          showToast(currentLang === "ua" ? "✓ Анкету збережено! 5 днів тренувань готові." : "✓ Profile questionnaire saved! 5-day split ready.");
        }
      } catch(e) {
        showToast("Error: " + e.message);
      }
    }

    // -------------------------------------------------------------
    // FOCUS WORKOUT BUILDER
    // -------------------------------------------------------------
    function openFocusModal() {
      document.getElementById("focus-modal").classList.add("open");
    }
    function closeFocusModal() {
      document.getElementById("focus-modal").classList.remove("open");
    }
    function toggleFocusArea(area, el) {
      if (selectedFocusAreas.includes(area)) {
        selectedFocusAreas = selectedFocusAreas.filter(a => a !== area);
        el.classList.remove("active");
      } else {
        selectedFocusAreas.push(area);
        el.classList.add("active");
      }
    }
    async function generateFocusWorkout() {
      closeFocusModal();
      showToast(currentLang === "ua" ? "🎯 Генерація фокус-тренування (10 вправ)..." : "🎯 Generating 10-exercise focus workout...");
      try {
        const res = await fetch("/api/generate-custom", {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({ focus_areas: selectedFocusAreas })
        });
        const data = await res.json();
        if (data.status === "ok" && data.strength_plan) {
          currentStrengthPlan = data.strength_plan;
          selectStrengthDay(data.day_index || 0);
          showToast(currentLang === "ua" ? "✓ Фокус-тренування згенеровано!" : "✓ Focus workout generated!");
        }
      } catch(e) {
        showToast("Error: " + e.message);
      }
    }

    // -------------------------------------------------------------
    // PROGRESS & LIBRARY
    // -------------------------------------------------------------
    async function loadProgressStats() {
      try {
        const sRes = await fetch("/api/stats");
        const sData = await sRes.json();
        if (sData.status === "ok" && sData.stats) {
          document.getElementById("stat-total-workouts").textContent = sData.stats.total_workouts || 0;
          document.getElementById("stat-total-minutes").textContent = sData.stats.total_duration_minutes || 0;
          document.getElementById("stat-streak").textContent = sData.stats.weekly_consistency_streak || 0;
        }

        const hRes = await fetch("/api/history");
        const hData = await hRes.json();
        const list = document.getElementById("history-sessions-list");
        list.innerHTML = "";
        if (hData.status === "ok" && hData.workouts && hData.workouts.length > 0) {
          hData.workouts.forEach(w => {
            const row = document.createElement("div");
            row.style.padding = "10px 0";
            row.style.borderBottom = "1px solid var(--border)";
            row.style.display = "flex";
            row.style.justifyContent = "space-between";
            row.style.alignItems = "center";
            row.innerHTML = `
              <div>
                <div style="font-weight: 700; color: #fff;">${w.date_completed} — ${w.duration_minutes} min</div>
                <div style="font-size: 12px; color: var(--muted);">${w.user_notes || 'Workout completed'}</div>
              </div>
              <div style="display: flex; gap: 5px; flex-wrap: wrap; justify-content: flex-end;">
                ${w.active_calories ? `<span class="badge" style="background:#b45309; color:#fef3c7;">🔥 ${w.active_calories} kcal</span>` : (w.total_calories ? `<span class="badge" style="background:#b45309; color:#fef3c7;">🔥 ${w.total_calories} kcal</span>` : "")}
                ${w.avg_heart_rate ? `<span class="badge" style="background:#1e3a8a; color:#bfdbfe;">❤️ ${w.avg_heart_rate} BPM</span>` : ""}
                ${w.hr_zone_achieved ? `<span class="badge" style="background:#065f46; color:#a7f3d0;">Zone ${w.hr_zone_achieved}</span>` : ""}
                ${w.training_load ? `<span class="badge" style="background:#581c87; color:#f3e8ff;">⚡ Load ${w.training_load}</span>` : ""}
                ${w.recovery_time_hours ? `<span class="badge" style="background:#0f766e; color:#ccfbf1;">⏱️ ${w.recovery_time_hours}h rec</span>` : ""}
              </div>
            `;
            list.appendChild(row);
          });
        } else {
          list.innerHTML = `<div style="font-size: 13px; color: var(--muted);">${currentLang === 'ua' ? 'Ще немає збережених тренувань.' : 'No completed workouts recorded yet.'}</div>`;
        }
      } catch(e) {}
    }

    let allExercisesCache = [];
    async function loadLibrary() {
      if (allExercisesCache.length === 0) {
        try {
          const res = await fetch("/api/exercises");
          const data = await res.json();
          if (data.status === "ok") {
            allExercisesCache = data.exercises || [];
          }
        } catch(e) {}
      }
      filterLibrary();
    }

    function filterLibrary() {
      const q = (document.getElementById("lib-search").value || "").toLowerCase().trim();
      const pattern = document.getElementById("lib-filter-pattern").value;
      const loc = document.getElementById("lib-filter-loc").value;

      const grid = document.getElementById("library-results-grid");
      grid.innerHTML = "";

      const filtered = allExercisesCache.filter(ex => {
        const name = (currentLang === "ua" ? (ex.name_ua || ex.name) : ex.name).toLowerCase();
        const muscles = (ex.primary_muscles || []).join(" ").toLowerCase();
        if (q && !name.includes(q) && !muscles.includes(q)) return false;
        if (pattern && ex.movement_pattern !== pattern) return false;
        if (loc && !ex.location.includes(loc)) return false;
        return true;
      });

      filtered.slice(0, 60).forEach(ex => {
        const item = document.createElement("div");
        item.className = "card";
        const title = currentLang === "ua" ? (ex.name_ua || ex.name) : ex.name;
        item.innerHTML = `
          <div style="font-weight: 700; color: #fff; margin-bottom: 4px;">${title}</div>
          <div style="display: flex; gap: 4px; flex-wrap: wrap; margin-bottom: 6px;">
            <span class="badge">${ex.movement_pattern}</span>
            <span class="badge">${ex.exercise_family}</span>
            <span class="badge">${(ex.location || []).join('/')}</span>
          </div>
          <div style="font-size: 12px; color: var(--muted); line-height: 1.4;">${ex.instructions || ''}</div>
        `;
        grid.appendChild(item);
      });
    }

    function showToast(msg) {
      const t = document.getElementById("toast");
      t.textContent = msg;
      t.style.display = "block";
      setTimeout(() => { t.style.display = "none"; }, 3500);
    }

    // -------------------------------------------------------------
    // INITIALIZATION ON LOAD
    // -------------------------------------------------------------
    window.onload = async () => {
      try {
        const pRes = await fetch("/api/profile");
        const pData = await pRes.json();
        if (pData.profile) {
          userProfile = pData.profile;
          document.getElementById("btn-sex-female").classList.toggle("active", userProfile.sex === "female");
          document.getElementById("btn-sex-male").classList.toggle("active", userProfile.sex === "male");
          document.getElementById("btn-loc-home").classList.toggle("active", userProfile.location === "home");
          document.getElementById("btn-loc-gym").classList.toggle("active", userProfile.location === "gym");
          document.getElementById("btn-lvl-int").classList.toggle("active", userProfile.level === "intermediate");
          document.getElementById("btn-lvl-adv").classList.toggle("active", userProfile.level === "advanced");

          // Mandatory first start questionnaire modal
          if (!userProfile.onboarding_completed) {
            openOnboardingModal();
          }
        }

        const cRes = await fetch("/api/current-plan");
        const cData = await cRes.json();
        if (cData.status === "ok") {
          currentStrengthPlan = cData.strength_plan || [];
          currentMobilityPlan = cData.mobility_plan || null;
          currentRehabPlan = cData.rehab_plan || null;
          selectedDayIndex = cData.day_index || 0;
          setLanguage(currentLang);
        }
      } catch(e) {
        console.error(e);
      }
    };
  </script>
</body>
</html>
"""


def run_server(port=DEFAULT_PORT):
    socketserver.TCPServer.allow_reuse_address = True
    current_port = port
    httpd = None
    for attempt in range(10):
        try:
            server_address = (HOST, current_port)
            httpd = socketserver.TCPServer(server_address, FitnessAppHandler)
            break
        except OSError as e:
            if getattr(e, "errno", None) == 48:
                current_port = port + attempt + 1
            else:
                raise e

    if not httpd:
        print(f"❌ Could not bind to port {port} or subsequent ports.", flush=True)
        return

    print(f"🚀 AI Fitness Coach is running at http://{HOST}:{current_port}", flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...", flush=True)
        httpd.server_close()


if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PORT
    run_server(port)

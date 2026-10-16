"""
Database access layer for AI Fitness Coach using SQLite.
Stores exercises with bilingual names and rich descriptions,
user profile settings, completed workouts, and exercise performance history.
All data is saved locally in data/fitness.db.
"""

import json
import os
import sqlite3
from typing import Dict, List, Optional
from datetime import datetime

from models import Exercise, CompletedWorkoutLog, ExerciseFeedback
from seed_data import EXERCISE_CATALOG
import translations

DB_DIR = os.path.join(os.path.dirname(__file__), "data")
DB_PATH = os.path.join(DB_DIR, "fitness.db")


def get_connection():
    """Returns a connection to the local SQLite database."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initializes tables and seeds the exercise library with bilingual descriptions."""
    conn = get_connection()
    cursor = conn.cursor()

    # Drop and recreate exercises catalog to ensure latest rich descriptions & metadata
    cursor.execute("DROP TABLE IF EXISTS exercises")

    cursor.execute("""
    CREATE TABLE exercises (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        name_ua TEXT NOT NULL,
        movement_pattern TEXT NOT NULL,
        exercise_family TEXT NOT NULL,
        primary_muscles TEXT NOT NULL,
        secondary_muscles TEXT NOT NULL,
        equipment_needed TEXT NOT NULL,
        difficulty INTEGER NOT NULL,
        stability_demand TEXT NOT NULL,
        unilateral BOOLEAN NOT NULL,
        instructions TEXT NOT NULL,
        instructions_ua TEXT NOT NULL,
        setup TEXT NOT NULL,
        execution TEXT NOT NULL,
        form_tips TEXT NOT NULL,
        setup_ua TEXT NOT NULL,
        execution_ua TEXT NOT NULL,
        form_tips_ua TEXT NOT NULL,
        default_sets INTEGER NOT NULL,
        default_reps TEXT NOT NULL,
        rest_seconds INTEGER NOT NULL,
        joint_stress TEXT NOT NULL,
        location TEXT NOT NULL,
        trx_anchor TEXT NOT NULL,
        is_compound_combo BOOLEAN NOT NULL,
        gender_priority TEXT DEFAULT '[]',
        equipment_alternatives TEXT DEFAULT '',
        equipment_alternatives_ua TEXT DEFAULT ''
    )
    """)

    # User Profile & Preferences Table (Preserved across runs)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_profile (
        id INTEGER PRIMARY KEY,
        sex TEXT DEFAULT 'female',
        level TEXT DEFAULT 'intermediate',
        location TEXT DEFAULT 'home',
        goal TEXT DEFAULT 'muscle_gain',
        current_weight REAL DEFAULT 75.0,
        target_weight REAL DEFAULT 72.0,
        weight_unit TEXT DEFAULT 'kg',
        equipment_inventory TEXT DEFAULT '[]',
        injuries_to_avoid TEXT DEFAULT '[]',
        medical_conditions TEXT DEFAULT '[]',
        workout_format TEXT DEFAULT 'superset_pairs',
        trx_anchor TEXT DEFAULT 'door',
        age INTEGER DEFAULT 30,
        max_hr INTEGER DEFAULT 0,
        rolling_split_index INTEGER DEFAULT 0,
        onboarding_completed BOOLEAN DEFAULT 0,
        updated_at TEXT
    )
    """)

    # Safe migrations for user_profile
    for col, col_def in [
        ("sex", "TEXT DEFAULT 'female'"),
        ("equipment_inventory", "TEXT DEFAULT '[]'"),
        ("medical_conditions", "TEXT DEFAULT '[]'"),
        ("rolling_split_index", "INTEGER DEFAULT 0"),
        ("onboarding_completed", "BOOLEAN DEFAULT 0"),
        ("age", "INTEGER DEFAULT 30"),
        ("max_hr", "INTEGER DEFAULT 0"),
    ]:
        try:
            cursor.execute(f"ALTER TABLE user_profile ADD COLUMN {col} {col_def}")
        except Exception:
            pass

    default_equip_json = json.dumps([
        "adjustable dumbbells", "TRX", "short/mini resistance bands",
        "long resistance bands", "towels/sliders", "couch/bench support",
        "small fitness ball", "yoga blocks"
    ])

    # Ensure default user profile exists
    cursor.execute("SELECT COUNT(*) as count FROM user_profile WHERE id = 1")
    if cursor.fetchone()["count"] == 0:
        cursor.execute("""
        INSERT INTO user_profile (
            id, sex, level, location, goal, current_weight, target_weight,
            weight_unit, equipment_inventory, injuries_to_avoid, medical_conditions,
            workout_format, trx_anchor, age, max_hr, rolling_split_index, onboarding_completed, updated_at
        ) VALUES (1, 'female', 'intermediate', 'home', 'muscle_gain', 75.0, 72.0, 'kg', ?, '[]', '[]', 'superset_pairs', 'door', 30, 0, 0, 0, ?)
        """, (default_equip_json, datetime.now().isoformat(),))

    # Workout Sessions Table (Preserved across runs)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS workout_sessions (
        workout_id TEXT PRIMARY KEY,
        date_completed TEXT NOT NULL,
        duration_minutes INTEGER NOT NULL,
        overall_rating INTEGER NOT NULL,
        overall_fatigue INTEGER NOT NULL,
        user_notes TEXT,
        min_heart_rate INTEGER,
        max_heart_rate INTEGER,
        avg_heart_rate INTEGER,
        hr_zone_achieved INTEGER DEFAULT 0,
        hr_goal_achieved BOOLEAN DEFAULT 0,
        hr_analysis_feedback TEXT DEFAULT ''
    )
    """)

    # Safe migrations for workout_sessions
    for col, col_def in [
        ("min_heart_rate", "INTEGER"),
        ("avg_heart_rate", "INTEGER"),
        ("max_heart_rate", "INTEGER"),
        ("hr_zone_achieved", "INTEGER DEFAULT 0"),
        ("hr_goal_achieved", "BOOLEAN DEFAULT 0"),
        ("hr_analysis_feedback", "TEXT DEFAULT ''"),
        ("watch_duration_minutes", "INTEGER"),
        ("active_calories", "INTEGER"),
        ("total_calories", "INTEGER"),
        ("zone1_mins", "INTEGER"),
        ("zone2_mins", "INTEGER"),
        ("zone3_mins", "INTEGER"),
        ("zone4_mins", "INTEGER"),
        ("zone5_mins", "INTEGER"),
        ("dominant_zone", "INTEGER"),
        ("training_load", "REAL"),
        ("recovery_time_hours", "INTEGER"),
        ("telemetry_analysis", "TEXT DEFAULT ''"),
    ]:
        try:
            cursor.execute(f"ALTER TABLE workout_sessions ADD COLUMN {col} {col_def}")
        except Exception:
            pass

    # Exercise Performance Logs Table (Preserved across runs)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS exercise_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        workout_id TEXT NOT NULL,
        exercise_id TEXT NOT NULL,
        sets_completed INTEGER NOT NULL,
        reps_completed TEXT NOT NULL,
        weight_used TEXT NOT NULL,
        skipped BOOLEAN NOT NULL,
        perceived_difficulty INTEGER NOT NULL,
        notes TEXT,
        date_performed TEXT NOT NULL,
        FOREIGN KEY (workout_id) REFERENCES workout_sessions (workout_id),
        FOREIGN KEY (exercise_id) REFERENCES exercises (id)
    )
    """)

    conn.commit()

    # Seed all exercises enriched with translations, form guides, and metadata
    for raw_ex in EXERCISE_CATALOG:
        ex = translations.enrich_exercise(raw_ex)
        cursor.execute("""
        INSERT INTO exercises (
            id, name, name_ua, movement_pattern, exercise_family,
            primary_muscles, secondary_muscles, equipment_needed,
            difficulty, stability_demand, unilateral, instructions, instructions_ua,
            setup, execution, form_tips, setup_ua, execution_ua, form_tips_ua,
            default_sets, default_reps, rest_seconds,
            joint_stress, location, trx_anchor, is_compound_combo,
            gender_priority, equipment_alternatives, equipment_alternatives_ua
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            ex.id,
            ex.name,
            ex.name_ua,
            ex.movement_pattern,
            ex.exercise_family,
            json.dumps(ex.primary_muscles),
            json.dumps(ex.secondary_muscles),
            json.dumps(ex.equipment_needed),
            ex.difficulty,
            ex.stability_demand,
            1 if ex.unilateral else 0,
            ex.instructions,
            ex.instructions_ua,
            ex.setup,
            ex.execution,
            ex.form_tips,
            ex.setup_ua,
            ex.execution_ua,
            ex.form_tips_ua,
            ex.default_sets,
            ex.default_reps,
            ex.rest_seconds,
            json.dumps(ex.joint_stress),
            json.dumps(ex.location),
            ex.trx_anchor,
            1 if ex.is_compound_combo else 0,
            json.dumps(getattr(ex, "gender_priority", [])),
            getattr(ex, "equipment_alternatives", "") or "",
            getattr(ex, "equipment_alternatives_ua", "") or ""
        ))
    conn.commit()
    conn.close()


def get_all_exercises() -> List[Exercise]:
    """Retrieves all exercises from the database as Exercise objects."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM exercises ORDER BY movement_pattern, name")
    rows = cursor.fetchall()
    conn.close()

    exercises = []
    for row in rows:
        exercises.append(Exercise(
            id=row["id"],
            name=row["name"],
            name_ua=row["name_ua"],
            movement_pattern=row["movement_pattern"],
            exercise_family=row["exercise_family"],
            primary_muscles=json.loads(row["primary_muscles"]),
            secondary_muscles=json.loads(row["secondary_muscles"]),
            equipment_needed=json.loads(row["equipment_needed"]),
            difficulty=row["difficulty"],
            stability_demand=row["stability_demand"],
            unilateral=bool(row["unilateral"]),
            instructions=row["instructions"],
            instructions_ua=row["instructions_ua"],
            setup=row["setup"],
            execution=row["execution"],
            form_tips=row["form_tips"],
            setup_ua=row["setup_ua"],
            execution_ua=row["execution_ua"],
            form_tips_ua=row["form_tips_ua"],
            default_sets=row["default_sets"],
            default_reps=row["default_reps"],
            rest_seconds=row["rest_seconds"],
            joint_stress=json.loads(row["joint_stress"]) if "joint_stress" in row.keys() and row["joint_stress"] else [],
            location=json.loads(row["location"]) if "location" in row.keys() and row["location"] else ["home", "gym"],
            trx_anchor=row["trx_anchor"] if "trx_anchor" in row.keys() and row["trx_anchor"] else "any",
            is_compound_combo=bool(row["is_compound_combo"]) if "is_compound_combo" in row.keys() and row["is_compound_combo"] else False,
            gender_priority=json.loads(row["gender_priority"]) if "gender_priority" in row.keys() and row["gender_priority"] else [],
            equipment_alternatives=row["equipment_alternatives"] if "equipment_alternatives" in row.keys() and row["equipment_alternatives"] else "",
            equipment_alternatives_ua=row["equipment_alternatives_ua"] if "equipment_alternatives_ua" in row.keys() and row["equipment_alternatives_ua"] else ""
        ))
    return exercises


def get_exercise_history() -> Dict[str, Dict]:
    """
    Returns a dictionary mapping exercise_id to performance statistics:
    - times_performed: int
    - last_performed_date: str or None
    - times_skipped: int
    - avg_difficulty: float
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT 
        exercise_id,
        COUNT(CASE WHEN skipped = 0 THEN 1 END) AS times_performed,
        MAX(CASE WHEN skipped = 0 THEN date_performed ELSE NULL END) AS last_performed_date,
        COUNT(CASE WHEN skipped = 1 THEN 1 END) AS times_skipped,
        AVG(CASE WHEN skipped = 0 THEN perceived_difficulty ELSE NULL END) AS avg_difficulty
    FROM exercise_logs
    GROUP BY exercise_id
    """)

    rows = cursor.fetchall()
    conn.close()

    history = {}
    for row in rows:
        history[row["exercise_id"]] = {
            "times_performed": row["times_performed"],
            "last_performed_date": row["last_performed_date"],
            "times_skipped": row["times_skipped"],
            "avg_difficulty": row["avg_difficulty"]
        }
    return history


def get_user_profile() -> Dict:
    """Retrieves user profile preferences."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_profile WHERE id = 1")
    row = cursor.fetchone()
    conn.close()

    default_equipment = [
        "adjustable dumbbells", "TRX", "short/mini resistance bands",
        "long resistance bands", "towels/sliders", "couch/bench support",
        "small fitness ball", "yoga blocks"
    ]

    if not row:
        return {
            "sex": "female",
            "level": "intermediate",
            "location": "home",
            "goal": "muscle_gain",
            "current_weight": 75.0,
            "target_weight": 72.0,
            "weight_unit": "kg",
            "equipment_inventory": default_equipment,
            "injuries_to_avoid": [],
            "medical_conditions": [],
            "workout_format": "superset_pairs",
            "trx_anchor": "door",
            "age": 30,
            "max_hr": None,
            "rolling_split_index": 0,
            "onboarding_completed": False
        }

    keys = row.keys()
    return {
        "sex": row["sex"] if "sex" in keys and row["sex"] else "female",
        "level": row["level"],
        "location": row["location"],
        "goal": row["goal"],
        "current_weight": float(row["current_weight"]),
        "target_weight": float(row["target_weight"]),
        "weight_unit": row["weight_unit"],
        "equipment_inventory": json.loads(row["equipment_inventory"]) if "equipment_inventory" in keys and row["equipment_inventory"] else default_equipment,
        "injuries_to_avoid": json.loads(row["injuries_to_avoid"]) if "injuries_to_avoid" in keys and row["injuries_to_avoid"] else [],
        "medical_conditions": json.loads(row["medical_conditions"]) if "medical_conditions" in keys and row["medical_conditions"] else [],
        "workout_format": row["workout_format"] if "workout_format" in keys and row["workout_format"] else "superset_pairs",
        "trx_anchor": row["trx_anchor"],
        "age": int(row["age"]) if "age" in keys and row["age"] else 30,
        "max_hr": int(row["max_hr"]) if "max_hr" in keys and row["max_hr"] and int(row["max_hr"]) > 0 else None,
        "rolling_split_index": int(row["rolling_split_index"]) if "rolling_split_index" in keys and row["rolling_split_index"] is not None else 0,
        "onboarding_completed": bool(row["onboarding_completed"]) if "onboarding_completed" in keys and row["onboarding_completed"] else False
    }


def save_user_profile(data: Dict) -> Dict:
    """Updates user profile preferences with safe merging to avoid clearing unspecified fields."""
    current = get_user_profile()
    merged = {**current, **data}

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE user_profile SET
        sex = ?,
        level = ?,
        location = ?,
        goal = ?,
        current_weight = ?,
        target_weight = ?,
        weight_unit = ?,
        equipment_inventory = ?,
        injuries_to_avoid = ?,
        medical_conditions = ?,
        workout_format = ?,
        trx_anchor = ?,
        age = ?,
        max_hr = ?,
        rolling_split_index = ?,
        onboarding_completed = ?,
        updated_at = ?
    WHERE id = 1
    """, (
        merged.get("sex", "female"),
        merged.get("level", "intermediate"),
        merged.get("location", "home"),
        merged.get("goal", "muscle_gain"),
        float(merged.get("current_weight", 75.0)),
        float(merged.get("target_weight", 72.0)),
        merged.get("weight_unit", "kg"),
        json.dumps(merged.get("equipment_inventory", [])),
        json.dumps(merged.get("injuries_to_avoid", [])),
        json.dumps(merged.get("medical_conditions", [])),
        merged.get("workout_format", "superset_pairs"),
        merged.get("trx_anchor", "door"),
        int(merged.get("age", 30)),
        int(merged.get("max_hr", 0)) if merged.get("max_hr") else 0,
        int(merged.get("rolling_split_index", 0)),
        1 if merged.get("onboarding_completed") else 0,
        datetime.now().isoformat()
    ))
    conn.commit()
    conn.close()
    return get_user_profile()


def advance_rolling_split_index() -> int:
    """Advances the 5-day rolling split queue to the next workout index (0-4)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT rolling_split_index FROM user_profile WHERE id = 1")
    row = cursor.fetchone()
    current_idx = int(row["rolling_split_index"]) if row and "rolling_split_index" in row.keys() and row["rolling_split_index"] is not None else 0
    next_idx = (current_idx + 1) % 5
    cursor.execute("UPDATE user_profile SET rolling_split_index = ? WHERE id = 1", (next_idx,))
    conn.commit()
    conn.close()
    return next_idx


def set_rolling_split_index(index: int) -> int:
    """Sets the rolling split index directly (0-4)."""
    conn = get_connection()
    cursor = conn.cursor()
    safe_idx = max(0, min(4, int(index)))
    cursor.execute("UPDATE user_profile SET rolling_split_index = ? WHERE id = 1", (safe_idx,))
    conn.commit()
    conn.close()
    return safe_idx


def get_last_performance_for_exercises(exercise_ids: Optional[List[str]] = None) -> Dict[str, Dict]:
    """
    Returns the most recent performance log for each exercise:
    {exercise_id: {"weight": str, "weight_used": str, "reps": str, "reps_completed": str, "perceived_difficulty": int, "date_performed": str}}
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT exercise_id, weight_used, reps_completed, perceived_difficulty, date_performed
    FROM exercise_logs
    WHERE skipped = 0
    ORDER BY date_performed ASC, id ASC
    """)
    rows = cursor.fetchall()
    conn.close()

    target_ids = set(exercise_ids) if exercise_ids else None
    last_perf = {}
    for r in rows:
        ex_id = r["exercise_id"]
        if target_ids is not None and ex_id not in target_ids:
            continue
        last_perf[ex_id] = {
            "weight": r["weight_used"],
            "weight_used": r["weight_used"],
            "reps": r["reps_completed"],
            "reps_completed": r["reps_completed"],
            "perceived_difficulty": r["perceived_difficulty"],
            "date_performed": r["date_performed"]
        }
    return last_perf


def save_completed_workout(workout_log: CompletedWorkoutLog):
    """Saves a completed workout session and its exercise logs in a single transaction."""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
        INSERT OR REPLACE INTO workout_sessions (
            workout_id, date_completed, duration_minutes,
            overall_rating, overall_fatigue, user_notes,
            min_heart_rate, max_heart_rate, avg_heart_rate,
            hr_zone_achieved, hr_goal_achieved, hr_analysis_feedback,
            watch_duration_minutes, active_calories, total_calories,
            zone1_mins, zone2_mins, zone3_mins, zone4_mins, zone5_mins,
            dominant_zone, training_load, recovery_time_hours, telemetry_analysis
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            workout_log.workout_id,
            workout_log.date_completed,
            workout_log.duration_minutes,
            workout_log.overall_rating,
            workout_log.overall_fatigue,
            workout_log.user_notes,
            workout_log.min_heart_rate,
            workout_log.max_heart_rate,
            workout_log.avg_heart_rate or workout_log.min_heart_rate,
            workout_log.hr_zone_achieved,
            1 if workout_log.hr_goal_achieved else 0,
            workout_log.hr_analysis_feedback,
            getattr(workout_log, "watch_duration_minutes", None),
            getattr(workout_log, "active_calories", None),
            getattr(workout_log, "total_calories", None),
            getattr(workout_log, "zone1_mins", None),
            getattr(workout_log, "zone2_mins", None),
            getattr(workout_log, "zone3_mins", None),
            getattr(workout_log, "zone4_mins", None),
            getattr(workout_log, "zone5_mins", None),
            getattr(workout_log, "dominant_zone", None),
            getattr(workout_log, "training_load", None),
            getattr(workout_log, "recovery_time_hours", None),
            getattr(workout_log, "telemetry_analysis", "") or ""
        ))

        for elog in workout_log.exercise_logs:
            cursor.execute("""
            INSERT INTO exercise_logs (
                workout_id, exercise_id, sets_completed, reps_completed,
                weight_used, skipped, perceived_difficulty, notes, date_performed
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                workout_log.workout_id,
                elog.exercise_id,
                elog.sets_completed,
                elog.reps_completed,
                elog.weight_used,
                1 if elog.skipped else 0,
                elog.perceived_difficulty,
                elog.notes,
                workout_log.date_completed
            ))

        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def get_recent_workouts(limit: int = 30) -> List[Dict]:
    """Retrieves the most recent completed workout sessions."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT * FROM workout_sessions 
    ORDER BY date_completed DESC 
    LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()

    return [dict(r) for r in rows]


def get_progress_stats() -> Dict:
    """Returns aggregated stats for the history & progress dashboard."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) AS total_workouts FROM workout_sessions")
    total_workouts = cursor.fetchone()["total_workouts"]

    cursor.execute("SELECT COUNT(*) AS total_exercises FROM exercise_logs WHERE skipped = 0")
    total_exercises = cursor.fetchone()["total_exercises"]

    cursor.execute("SELECT AVG(overall_rating) AS avg_rating FROM workout_sessions")
    avg_rating_row = cursor.fetchone()["avg_rating"]
    avg_rating = round(avg_rating_row, 1) if avg_rating_row is not None else 5.0

    cursor.execute("""
    SELECT DISTINCT date_completed 
    FROM workout_sessions 
    ORDER BY date_completed DESC 
    LIMIT 30
    """)
    dates = [r["date_completed"] for r in cursor.fetchall()]

    conn.close()

    return {
        "total_workouts": total_workouts,
        "total_exercises_completed": total_exercises,
        "avg_rating": avg_rating,
        "recent_dates": dates,
        "profile": get_user_profile()
    }

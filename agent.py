"""
AI Fitness Coach - Google ADK Agent Implementation.
Built using Google's Agent Development Kit (ADK) architecture with Gemini.
Exports `root_agent` for Google ADK CLI ('adk web' / 'adk run').
"""

import os
import json
from datetime import datetime
from typing import List, Optional, Dict, Any

# Ensure database is initialized
import database
import engine
import heart_rate
from models import CompletedWorkoutLog, ExerciseFeedback

database.init_db()

# ---------------------------------------------------------------------------
# Google ADK Agent Import with Compatibility Fallback
# ---------------------------------------------------------------------------
try:
    from google.adk.agents.llm_agent import Agent
    ADK_AVAILABLE = True
except ImportError:
    try:
        from google.adk.agents import Agent
        ADK_AVAILABLE = True
    except ImportError:
        try:
            from google.adk import Agent
            ADK_AVAILABLE = True
        except ImportError:
            ADK_AVAILABLE = False

            class Agent:
                """ADK-compatible Agent stub for environments where google-adk is being installed."""
                def __init__(
                    self,
                    name: str,
                    model: str = "gemini-2.0-flash",
                    description: str = "",
                    instruction: str = "",
                    tools: Optional[List[Any]] = None,
                    sub_agents: Optional[List[Any]] = None,
                ):
                    self.name = name
                    self.model = model
                    self.description = description
                    self.instruction = instruction
                    self.tools = tools or []
                    self.sub_agents = sub_agents or []

                def __repr__(self):
                    return f"<GoogleADK.Agent name='{self.name}' model='{self.model}' tools={len(self.tools)} sub_agents={len(self.sub_agents)}>"


# ---------------------------------------------------------------------------
# Tool Definitions (Standard Python Functions for Google ADK)
# ---------------------------------------------------------------------------

def generate_weekly_plan(
    level: str = "intermediate",
    location: str = "home",
    injuries_to_avoid: Optional[List[str]] = None,
    goal: str = "muscle_gain",
    workout_format: str = "standard",
    trx_anchor: str = "door"
) -> Dict[str, Any]:
    """Generates the foundation 3-day weekly workout program (10 exercises each, balanced 2 focus zones + core always).

    Args:
        level: Fitness level ('intermediate' or 'advanced' with compound combos).
        location: Training location ('home' with dumbbells/TRX/bands or 'gym' with barbells/machines).
        injuries_to_avoid: List of joints to safely isolate/exclude (e.g., ['wrist', 'knee', 'lower_back', 'shoulder', 'elbow', 'ankle']).
        goal: Training goal ('muscle_gain', 'strength', 'weight_loss', or 'toning').
        workout_format: Protocol ('standard', 'circuit', 'tabata', or 'sandwich').
        trx_anchor: TRX mounting point ('door' anchor or 'bar' pull-up mount).

    Returns:
        A dictionary with the 3 scheduled workouts and their 10 exercise stations each.
    """
    plans = engine.generate_weekly_program(
        level=level,
        location=location,
        injuries_to_avoid=injuries_to_avoid or [],
        goal=goal,
        workout_format=workout_format,
        trx_anchor=trx_anchor
    )
    db_exercises = {e.id: e for e in database.get_all_exercises()}
    result = []
    for p in plans:
        result.append({
            "workout_id": p.workout_id,
            "day_label": p.day_label,
            "day_label_ua": p.day_label_ua,
            "format_description": p.format_description,
            "location": p.location,
            "goal": p.goal,
            "exercises_count": len(p.exercises),
            "exercises": [
                {
                    "order": ex.order_index,
                    "id": ex.exercise_id,
                    "name": ex.name,
                    "name_ua": ex.name_ua,
                    "zone": ex.zone_en,
                    "sets": ex.sets,
                    "reps": ex.reps,
                    "rest_seconds": ex.rest_seconds,
                    "is_compound_combo": ex.is_compound_combo,
                    "equipment": db_exercises[ex.exercise_id].equipment_needed if ex.exercise_id in db_exercises else [],
                    "stressed_joints": ex.joint_stress,
                    "location": ex.location,
                    "trx_anchor": ex.trx_anchor,
                }
                for ex in p.exercises
            ]
        })
    return {"status": "success", "program_days": len(result), "weekly_plan": result}


def generate_rolling_workout(
    day_index: Optional[int] = None,
    level: str = "intermediate",
    location: str = "home",
    injuries_to_avoid: Optional[List[str]] = None,
    goal: str = "muscle_gain",
    workout_format: str = "standard",
    trx_anchor: str = "door"
) -> Dict[str, Any]:
    """Generates the next workout in the 5-Day Rolling Split queue (5 Supersets x 2 Exercises = 10 exercises).

    Args:
        day_index: Optional 0-4 day index (Day 1: Shoulders/Arms/Core, Day 2: Back/Chest/Core, Day 3: Abs/Waist/Deep Core, Day 4: Glutes/Hamstrings/Hip Dips, Day 5: Quads/Adductors/Calves). Defaults to current user profile queue index.
        level: Fitness level ('intermediate' or 'advanced').
        location: Training venue ('home' or 'gym').
        injuries_to_avoid: Joints to isolate (e.g. ['wrist', 'knee', 'lower_back']).
        goal: Training goal ('muscle_gain', 'weight_loss', 'strength', or 'toning').
        workout_format: Protocol ('standard', 'circuit', 'tabata', or 'sandwich').
        trx_anchor: TRX mounting point ('door' or 'bar').

    Returns:
        Structured 10-exercise workout plan grouped into 5 supersets with progression tips.
    """
    plan = engine.generate_rolling_workout(
        day_index=day_index,
        level=level,
        location=location,
        injuries_to_avoid=injuries_to_avoid or [],
        goal=goal,
        workout_format=workout_format,
        trx_anchor=trx_anchor
    )
    return {
        "status": "success",
        "workout_id": plan.workout_id,
        "day_label": plan.day_label,
        "day_label_ua": plan.day_label_ua,
        "format": plan.format_description,
        "format_ua": plan.format_description_ua,
        "exercises_count": len(plan.exercises),
        "exercises": [
            {
                "order": ex.order_index,
                "superset": ex.superset_group,
                "id": ex.exercise_id,
                "name": ex.name,
                "name_ua": ex.name_ua,
                "zone": ex.zone_en,
                "sets": ex.sets,
                "reps": ex.reps,
                "rest_seconds": ex.rest_seconds,
                "coach_progression_tip": ex.coach_progression_tip,
                "coach_progression_tip_ua": ex.coach_progression_tip_ua,
                "last_weight": ex.last_weight,
                "last_reps": ex.last_reps,
                "equipment_alternatives": ex.equipment_alternatives,
                "equipment_alternatives_ua": ex.equipment_alternatives_ua,
                "stressed_joints": ex.joint_stress,
                "location": ex.location,
                "trx_anchor": ex.trx_anchor
            }
            for ex in plan.exercises
        ]
    }


def advance_rolling_split() -> Dict[str, Any]:
    """Advances the 5-day rolling split queue to the next day (0-4) in the user's cycle.

    Returns:
        New rolling split queue index and status.
    """
    new_idx = engine.advance_rolling_split()
    return {"status": "success", "new_rolling_split_index": new_idx, "message": f"Queue advanced to Day {new_idx + 1}"}


def generate_mono_workout(
    mono_key: str = "special_13_lower_body",
    level: str = "intermediate",
    location: str = "home",
    injuries_to_avoid: Optional[List[str]] = None,
    goal: str = "muscle_gain",
    workout_format: str = "standard",
    trx_anchor: str = "door"
) -> Dict[str, Any]:
    """Generates an on-demand targeted Mono-Day workout.

    Args:
        mono_key: One of 'special_13_lower_body' (13 exercises), 'pure_back' (10 exercises), 'pure_glutes_legs' (10 exercises), 'pure_core' (10 exercises).
        level: Fitness level ('intermediate' or 'advanced').
        location: Training venue ('home' or 'gym').
        injuries_to_avoid: Joints to avoid.
        goal: Training goal.
        workout_format: Workout format.
        trx_anchor: 'door' or 'bar'.

    Returns:
        Structured mono-day workout plan.
    """
    plan = engine.generate_mono_workout(
        mono_key=mono_key,
        level=level,
        location=location,
        injuries_to_avoid=injuries_to_avoid or [],
        goal=goal,
        workout_format=workout_format,
        trx_anchor=trx_anchor
    )
    return {
        "status": "success",
        "workout_id": plan.workout_id,
        "day_label": plan.day_label,
        "day_label_ua": plan.day_label_ua,
        "format": plan.format_description,
        "exercises_count": len(plan.exercises),
        "exercises": [
            {
                "order": ex.order_index,
                "superset": ex.superset_group,
                "id": ex.exercise_id,
                "name": ex.name,
                "name_ua": ex.name_ua,
                "zone": ex.zone_en,
                "sets": ex.sets,
                "reps": ex.reps,
                "rest_seconds": ex.rest_seconds,
                "coach_progression_tip": ex.coach_progression_tip,
                "equipment_alternatives": ex.equipment_alternatives
            }
            for ex in plan.exercises
        ]
    }


def get_rehab_departments() -> Dict[str, Any]:
    """Returns the 6 specialized rehabilitation & restoration departments.

    Returns:
        List of departments with descriptions, target pathologies, and drill counts.
    """
    depts = engine.get_rehab_departments()
    return {"status": "success", "departments": depts}


def generate_rehab_routine(
    department: str = "pelvic_floor_diastasis",
    location: str = "home"
) -> Dict[str, Any]:
    """Generates an 8-exercise gentle, restorative rehabilitation routine.

    Args:
        department: One of 'pelvic_floor_diastasis', 'lower_back_lordosis', 'wrists_elbows', 'knees_hips', 'ankles_feet', 'neck_scapula'.
        location: 'home' or 'gym'.

    Returns:
        Structured restorative session with gentle form cues and pain-free execution rules.
    """
    plan = engine.generate_rehab_routine(
        department=department,
        location=location
    )
    return {
        "status": "success",
        "workout_id": plan.workout_id,
        "department": department,
        "day_label": plan.day_label,
        "day_label_ua": plan.day_label_ua,
        "format": plan.format_description,
        "exercises_count": len(plan.exercises),
        "exercises": [
            {
                "order": ex.order_index,
                "name": ex.name,
                "name_ua": ex.name_ua,
                "sets": ex.sets,
                "reps": ex.reps,
                "rest_seconds": ex.rest_seconds,
                "setup": ex.setup,
                "execution": ex.execution,
                "form_tips": ex.form_tips,
                "setup_ua": ex.setup_ua,
                "execution_ua": ex.execution_ua,
                "form_tips_ua": ex.form_tips_ua,
                "coach_progression_tip": ex.coach_progression_tip
            }
            for ex in plan.exercises
        ]
    }


def build_custom_focus_workout(
    focus_areas: List[str],
    level: str = "intermediate",
    location: str = "home",
    injuries_to_avoid: Optional[List[str]] = None,
    goal: str = "muscle_gain",
    workout_format: str = "standard",
    trx_anchor: str = "door"
) -> Dict[str, Any]:
    """Builds a custom 10-exercise workout targeting user-requested muscle focus zones plus core foundation.

    Args:
        focus_areas: Target muscle groups (e.g. ['chest', 'arms', 'shoulders', 'abs', 'back', 'quads', 'hamstrings_glutes']).
        level: Fitness level ('intermediate' or 'advanced').
        location: 'home' or 'gym'.
        injuries_to_avoid: Specific sore joints to safely bypass (e.g. ['wrist', 'knee']).
        goal: Training objective ('muscle_gain', 'weight_loss', 'strength', 'toning').
        workout_format: Method ('standard', 'circuit', 'tabata', 'sandwich').
        trx_anchor: TRX attachment point ('door' or 'bar').

    Returns:
        A dictionary containing the generated 10-exercise custom session.
    """
    plan = engine.generate_custom_workout(
        focus_areas=focus_areas,
        level=level,
        location=location,
        injuries_to_avoid=injuries_to_avoid or [],
        goal=goal,
        workout_format=workout_format,
        trx_anchor=trx_anchor
    )
    db_exercises = {e.id: e for e in database.get_all_exercises()}
    return {
        "status": "success",
        "workout_id": plan.workout_id,
        "day_label": plan.day_label,
        "format": plan.format_description,
        "exercises": [
            {
                "order": ex.order_index,
                "id": ex.exercise_id,
                "name": ex.name,
                "name_ua": ex.name_ua,
                "zone": ex.zone_en,
                "sets": ex.sets,
                "reps": ex.reps,
                "rest_seconds": ex.rest_seconds,
                "is_combo": ex.is_compound_combo,
                "equipment": db_exercises[ex.exercise_id].equipment_needed if ex.exercise_id in db_exercises else [],
                "stressed_joints": ex.joint_stress,
                "location": ex.location,
                "trx_anchor": ex.trx_anchor,
            }
            for ex in plan.exercises
        ]
    }


def generate_mobility_routine(
    focus_zones: Optional[List[str]] = None,
    location: str = "home",
    injuries_to_avoid: Optional[List[str]] = None,
    level: str = "intermediate"
) -> Dict[str, Any]:
    """Generates an intelligent 10-exercise mobility session, either general full-body or targeted zones.

    Args:
        focus_zones: Optional target mobility areas (e.g. ['hips', 'spine', 'shoulders', 'ankles', 'wrists_neck', 'hamstrings']).
                     If omitted or empty, generates an automatic general full-body routine (10 drills).
        location: Training location ('home' or 'gym').
        injuries_to_avoid: Joints to protect (e.g. ['wrist', 'knee', 'shoulder']).
        level: 'intermediate' or 'advanced'.

    Returns:
        Structured 10-drill mobility session with form cues, sets, reps, and zone allocations.
    """
    plan = engine.generate_mobility_routine(
        focus_zones=focus_zones,
        location=location,
        injuries_to_avoid=injuries_to_avoid or [],
        level=level
    )
    db_exercises = {e.id: e for e in database.get_all_exercises()}
    return {
        "status": "success",
        "workout_id": plan.workout_id,
        "day_label": plan.day_label,
        "day_label_ua": plan.day_label_ua,
        "format": plan.format_description,
        "format_ua": plan.format_description_ua,
        "exercises_count": len(plan.exercises),
        "exercises": [
            {
                "order": ex.order_index,
                "id": ex.exercise_id,
                "name": ex.name,
                "name_ua": ex.name_ua,
                "zone": ex.zone_en,
                "zone_ua": ex.zone_ua,
                "sets": ex.sets,
                "reps": ex.reps,
                "rest_seconds": ex.rest_seconds,
                "equipment": db_exercises[ex.exercise_id].equipment_needed if ex.exercise_id in db_exercises else [],
                "stressed_joints": ex.joint_stress,
                "setup": ex.setup,
                "execution": ex.execution,
                "form_tips": ex.form_tips,
                "setup_ua": ex.setup_ua,
                "execution_ua": ex.execution_ua,
                "form_tips_ua": ex.form_tips_ua,
            }
            for ex in plan.exercises
        ]
    }


def get_mobility_zones() -> Dict[str, Any]:
    """Returns the list of anatomical mobility zones available for targeted routines.

    Returns:
        Dictionary of available mobility zones with English and Ukrainian names and icons.
    """
    from mobility_data import MOBILITY_ZONES
    return {
        "status": "success",
        "zones": [
            {
                "id": k,
                "name_en": v["name_en"],
                "name_ua": v["name_ua"],
                "icon": v["icon"],
                "default_reps": v["default_reps"]
            }
            for k, v in MOBILITY_ZONES.items()
        ]
    }


def search_exercise_catalog(
    query: str = "",
    movement_pattern: str = "",
    equipment: str = "",
    joint_to_avoid: str = ""
) -> Dict[str, Any]:
    """Searches the 162-exercise library by keyword, pattern, equipment, or joint safety.

    Args:
        query: Search term (e.g. 'thruster', 'clean', 'squat', 'curl', 'trx').
        movement_pattern: Movement type ('Squat', 'Hinge', 'Push', 'Pull', 'Lunge', 'Core').
        equipment: Equipment filter (e.g. 'Dumbbells', 'TRX Suspension', 'Barbell', 'Resistance Band').
        joint_to_avoid: Exclude exercises that stress this joint (e.g. 'wrist', 'knee', 'lower_back', 'shoulder').

    Returns:
        List of matching exercises with difficulty, equipment, and combo status.
    """
    all_ex = database.get_all_exercises()
    results = []
    q = query.lower().strip()
    pat = movement_pattern.lower().strip()
    eq = equipment.lower().strip()
    avoid = joint_to_avoid.lower().strip()

    for ex in all_ex:
        if q and (q not in ex.name.lower() and q not in ex.name_ua.lower()):
            continue
        if pat and pat not in ex.movement_pattern.lower():
            continue
        if eq and not any(eq in item.lower() for item in ex.equipment_needed):
            continue
        if avoid and any(avoid in j.lower() for j in ex.joint_stress):
            continue

        results.append({
            "id": ex.id,
            "name": ex.name,
            "name_ua": ex.name_ua,
            "pattern": ex.movement_pattern,
            "equipment": ex.equipment_needed,
            "difficulty": ex.difficulty,
            "is_compound_combo": ex.is_compound_combo,
            "stressed_joints": ex.joint_stress,
            "location": ex.location,
            "trx_anchor": ex.trx_anchor,
        })

    return {"status": "success", "count": len(results), "matches": results[:25]}


def get_exercise_technique(exercise_id_or_name: str, language: str = "en") -> Dict[str, Any]:
    """Retrieves step-by-step biomechanical form cues, setup, execution, and pro tips for an exercise.

    Args:
        exercise_id_or_name: The exact exercise ID (e.g., 'combo_db_clean_and_press') or name keyword.
        language: 'en' for English or 'ua' for Ukrainian.

    Returns:
        Step-by-step stance, execution mechanics, and common trainer corrections.
    """
    all_ex = database.get_all_exercises()
    target = None
    query = exercise_id_or_name.lower().strip()

    # Exact ID match
    for ex in all_ex:
        if ex.id.lower() == query:
            target = ex
            break

    # Name match fallback
    if not target:
        for ex in all_ex:
            if query in ex.name.lower() or query in ex.name_ua.lower():
                target = ex
                break

    if not target:
        return {"status": "error", "message": f"Exercise '{exercise_id_or_name}' not found in library."}

    is_ua = language.lower() in ["ua", "uk", "ukrainian"]
    return {
        "status": "success",
        "id": target.id,
        "name": target.name_ua if is_ua else target.name,
        "alternate_name": target.name if is_ua else target.name_ua,
        "is_compound_combo": target.is_compound_combo,
        "setup_stance": target.setup_ua if is_ua else target.setup,
        "execution_steps": target.execution_ua if is_ua else target.execution,
        "pro_tips_mistakes": target.form_tips_ua if is_ua else target.form_tips,
        "primary_muscles": target.primary_muscles,
        "secondary_muscles": target.secondary_muscles,
        "equipment": target.equipment_needed,
        "joint_stress": target.joint_stress,
        "trx_anchor": target.trx_anchor,
    }


def get_tabata_protocol_settings(
    work_seconds: int = 40,
    rest_seconds: int = 10,
    cycles: int = 8,
    set_rest_seconds: int = 60,
    sets: int = 2
) -> Dict[str, Any]:
    """Returns the pacing structure, timing breakdown, and countdown voice cues for the dynamic Tabata protocol.

    Args:
        work_seconds: Work interval duration (standard: 40s).
        rest_seconds: Rest interval duration between cycles (standard: 10s).
        cycles: Number of repetitions per set (standard: 8 cycles).
        set_rest_seconds: Recovery rest between sets (standard: 60s).
        sets: Total number of sets to perform (default: 2 sets).

    Returns:
        Structured breakdown with total workout duration, cycle pacing, and countdown specifications.
    """
    one_set_sec = cycles * (work_seconds + rest_seconds) - rest_seconds
    total_sec = (sets * one_set_sec) + ((sets - 1) * set_rest_seconds)
    total_minutes = round(total_sec / 60, 1)

    return {
        "status": "success",
        "protocol": "Dynamic Tabata Protocol",
        "work_duration": f"{work_seconds} seconds of maximum effort",
        "rest_duration": f"{rest_seconds} seconds of transition rest",
        "cycles_per_set": f"{cycles} repetitions per set",
        "inter_set_recovery": f"{set_rest_seconds} seconds (1 minute) rest between sets",
        "total_sets": sets,
        "estimated_session_duration": f"{total_minutes} minutes ({total_sec} seconds total)",
        "countdown_audio_cues": "Loud ascending audio beeps from 10 seconds down to 0, with dynamic transition buzzer.",
        "voice_synthesis_cues": "Spoken exercise names called out at WORK start and upcoming movements previewed during REST.",
    }


def log_workout_progress(
    workout_id: str,
    duration_minutes: int,
    rating: int,
    fatigue: int,
    notes: str = ""
) -> Dict[str, Any]:
    """Logs a finished workout session into the database, updating exercise performance history and cooldown memory.

    Args:
        workout_id: The ID of the completed workout.
        duration_minutes: Actual duration of workout session in minutes.
        rating: Subjective workout rating from 1 (poor) to 5 (excellent).
        fatigue: Fatigue level from 1 (fresh) to 5 (exhausted).
        notes: User reflection or coach notes.

    Returns:
        Confirmation status and updated history log ID.
    """
    log = CompletedWorkoutLog(
        workout_id=workout_id,
        date_completed=datetime.now().strftime("%Y-%m-%d"),
        duration_minutes=duration_minutes,
        overall_rating=max(1, min(5, rating)),
        overall_fatigue=max(1, min(5, fatigue)),
        user_notes=notes,
        exercise_logs=[]
    )
    database.save_completed_workout(log)
    return {
        "status": "success",
        "message": f"Workout '{workout_id}' logged successfully! Exercise cooldown memory updated.",
        "logged_at": log.date_completed,
    }


def get_user_progress_metrics() -> Dict[str, Any]:
    """Retrieves all-time athletic progress metrics, total sessions completed, volume, and recent workout logs.

    Returns:
        Summary metrics including total sessions, avg ratings, and weight goal tracking.
    """
    stats = database.get_progress_stats()
    recent_workouts = database.get_recent_workouts(limit=5)
    profile = stats.get("profile", {})

    return {
        "status": "success",
        "total_workouts_completed": stats.get("total_workouts", 0),
        "total_exercises_finished": stats.get("total_exercises_completed", 0),
        "average_session_rating": stats.get("avg_rating", 5.0),
        "weight_goal": {
            "current_weight": profile.get("current_weight", 75.0),
            "target_weight": profile.get("target_weight", 72.0),
            "weight_unit": "kg",
        },
        "recent_sessions_count": len(recent_workouts),
        "recent_sessions": [
            {
                "date": w["date_completed"],
                "workout_id": w["workout_id"],
                "duration": f"{w['duration_minutes']} min",
                "rating": f"{w['overall_rating']}/5",
                "notes": w.get("user_notes", ""),
            }
            for w in recent_workouts
        ]
    }


def calculate_heart_rate_zones(age: int = 30, custom_max_hr: Optional[int] = None) -> Dict[str, Any]:
    """Calculates the 5 physiological heart rate training zones calibrated to the user's age and max HR.

    Args:
        age: User age in years (used to derive Max HR = 220 - age).
        custom_max_hr: Optional clinically measured or wearable-derived max heart rate.

    Returns:
        Dictionary with max HR and the 5 zones (BPM ranges, physiological goals, energy systems).
    """
    return heart_rate.get_heart_rate_zones(age=age, custom_max_hr=custom_max_hr)


def get_target_heart_rate_zone(
    goal: str = "muscle_gain",
    workout_format: str = "standard",
    age: int = 30,
    custom_max_hr: Optional[int] = None
) -> Dict[str, Any]:
    """Determines the prescribed target heart rate training zone and BPM boundary for a workout.

    Args:
        goal: Training goal ('weight_loss', 'muscle_gain', 'strength', 'toning').
        workout_format: Workout format ('standard', 'circuit', 'tabata', 'mobility', 'sandwich').
        age: User age in years.
        custom_max_hr: Optional custom maximum heart rate.

    Returns:
        Target zone number, target BPM range, physiological stimulus explanation, and zone boundaries.
    """
    return heart_rate.get_target_zone_for_workout(
        goal=goal,
        workout_format=workout_format,
        age=age,
        custom_max_hr=custom_max_hr
    )


def analyze_workout_heart_rate(
    avg_hr: int,
    max_hr_recorded: Optional[int] = None,
    goal: str = "muscle_gain",
    workout_format: str = "standard",
    age: int = 30,
    custom_max_hr: Optional[int] = None
) -> Dict[str, Any]:
    """Analyzes completed workout heart rate data against target zones and provides physiological coach feedback.

    Args:
        avg_hr: Average heart rate in BPM maintained across the workout.
        max_hr_recorded: Peak recorded heart rate in BPM (optional).
        goal: Session goal ('weight_loss', 'muscle_gain', 'strength', 'toning').
        workout_format: Format ('standard', 'circuit', 'tabata', 'mobility', 'sandwich').
        age: User age in years.
        custom_max_hr: Optional custom max heart rate.

    Returns:
        Evaluation of target zone achievement, energy substrate usage (fat oxidation vs glycogen), and coaching advice.
    """
    return heart_rate.analyze_workout_heart_rate(
        avg_hr=avg_hr,
        max_hr_recorded=max_hr_recorded,
        goal=goal,
        workout_format=workout_format,
        age=age,
        custom_max_hr=custom_max_hr
    )


# ---------------------------------------------------------------------------
# Google ADK Sub-Agents & Root Agent Configuration
# ---------------------------------------------------------------------------

# 1. Specialized Workout Planner Sub-Agent
workout_planner = Agent(
    name="workout_planner",
    model="gemini-2.0-flash",
    description="Specialist strength and conditioning coach that programs 5-Day Rolling Split workouts (5 supersets x 2 exercises = 10 exercises), foundation 3-day weekly plans, on-demand mono-days (13-exercise lower body sculpt, pure back, pure glutes/legs, pure core), and custom guided focus sessions.",
    instruction=(
        "You are the Master Workout Architect in the Google ADK AI Fitness Coach team.\n"
        "Your role is to build balanced, periodized, and progressive workouts.\n"
        "Rules:\n"
        "- The core program is the 5-Day Rolling Split (Day 1: Shoulders/Arms/Core, Day 2: Back/Chest/Core, Day 3: Abs/Waist/Deep Core, Day 4: Glutes/Hamstrings/Hip Dips, Day 5: Quads/Adductors/Calves).\n"
        "- Every standard workout consists of exactly 10 exercises arranged in 5 supersets (3 sets each, ~55-60 min).\n"
        "- We also offer special Mono-Days, including our 13-exercise Lower Body & Waist Sculpt.\n"
        "- NEVER mix mobility, stretching, or rehab inside strength workouts!\n"
        "- Respect physical limitations and joint injuries strictly (e.g. zero-palm rule for wrist; no kneeling for no_kneeling; zero axial load for lower back).\n"
        "- Tailor exercise selection to venue: 'home' matches user equipment inventory and TRX anchor ('door' vs 'bar'); 'gym' unlocks machines and barbells.\n"
        "- Female Mode Priority: glutes in 3 planes, gluteus medius ('hip dips'), inner thighs, calves/ankles, posture, and waist narrowing without thickening obliques."
    ),
    tools=[generate_rolling_workout, advance_rolling_split, generate_mono_workout, generate_weekly_plan, build_custom_focus_workout],
)

# 2. Specialized Biomechanics & Technique Sub-Agent
technique_coach = Agent(
    name="technique_coach",
    model="gemini-2.0-flash",
    description="Specialist biomechanics and movement coach that provides step-by-step form cues, setup instructions, and joint-safe modifications across all 230 catalog exercises.",
    instruction=(
        "You are the Biomechanics and Form Coach in the Google ADK AI Fitness Coach team.\n"
        "Your role is to teach flawless movement patterns and prevent injuries across our 230-exercise library.\n"
        "When explaining exercises:\n"
        "1. Break instructions into SETUP & STANCE, EXECUTION MECHANICS, and TRAINER PRO TIPS / COMMON MISTAKES.\n"
        "2. Detail target muscle engagement and joint shear points.\n"
        "3. Provide safe modifications when a user reports pain or movement restrictions.\n"
        "Support both English and Ukrainian fluently."
    ),
    tools=[search_exercise_catalog, get_exercise_technique],
)

# 3. Specialized Tabata & Interval Conditioning Sub-Agent
tabata_specialist = Agent(
    name="tabata_specialist",
    model="gemini-2.0-flash",
    description="Specialist interval coach for high-intensity Tabata sessions (40s work / 10s rest, 8 cycles per set, 60s rest between sets) with loud dynamic countdowns.",
    instruction=(
        "You are the Tabata Pacing and Interval Specialist in the Google ADK AI Fitness Coach team.\n"
        "Your job is to coach high-metabolic-density Tabata sessions:\n"
        "- Standard Protocol: 40 seconds of maximum effort exercise, 10 seconds of rest, repeated 8 times per set.\n"
        "- Inter-set Recovery: 1 minute (60 seconds) rest between sets.\n"
        "- Voice and Audio: Emphasize that exercise names are called out out loud, with loud ascending audio countdowns from 10 seconds to 0."
    ),
    tools=[get_tabata_protocol_settings],
)

# 4. Specialized Joint Mobility & Restoration Sub-Agent
mobility_specialist = Agent(
    name="mobility_specialist",
    model="gemini-2.0-flash",
    description="Specialist joint mobility and active restoration coach. Programs 10-drill full-body or targeted mobility routines across hips, spine, shoulders, ankles, wrists/neck, and posterior chain.",
    instruction=(
        "You are the Joint Mobility and Restoration Specialist in the Google ADK AI Fitness Coach team.\n"
        "Your mission is to structure restoring, safe, and athletic 10-drill mobility flows.\n"
        "Rules:\n"
        "- General Routine: Distribute 10 drills across the entire body (Hips 2, Thoracic Spine 2, Shoulders 2, Ankles 2, Wrists/Neck 1, Hamstrings 1).\n"
        "- Targeted Routine: When the user requests specific zones (e.g. hips, spine, shoulders, ankles), concentrate the 10 slots on those areas with complementary drills.\n"
        "- Respect physical limitations and joint injuries strictly (e.g. avoid floor-loaded wrists if wrist is injured; avoid deep squats if knee is injured).\n"
        "- Guide users with deliberate, controlled breathing and end-range isometric holds."
    ),
    tools=[generate_mobility_routine, get_mobility_zones],
)

# 5. Specialized Rehabilitation & Recovery Sub-Agent (NEW)
rehab_specialist = Agent(
    name="rehab_specialist",
    model="gemini-2.0-flash",
    description="Specialist rehabilitation and active restoration coach for 6 departments: Pelvic Floor & Diastasis Recti, Hyperlordosis & Lumbar Decompression, Wrist & Carpal Tunnel Unloading, Knee Joint & Hip Alignment, Ankle Stability & Anti-Edema Lymphatic Pump, and Cervical Spine & Scapular Stabilization.",
    instruction=(
        "You are the Rehabilitation and Restoration Specialist in the Google ADK AI Fitness Coach team.\n"
        "Your mission is to structure gentle, therapeutic, and biomechanically safe 8-exercise restoration sessions across 6 departments:\n"
        "1. Pelvic Floor & Diastasis Recti Recovery: strictly zero crunches, doming, or high intra-abdominal pressure.\n"
        "2. Hyperlordosis Correction & Lumbar Decompression: zero axial spine loading, posterior pelvic tilt focus.\n"
        "3. Wrist & Carpal Tunnel Unloading: zero palm weight-bearing, median nerve flossing and forearm gliding.\n"
        "4. Knee Joint & Hip Alignment: VMO tracking, gluteus medius pelvic leveling, zero deep shear squats.\n"
        "5. Ankle Stability & Anti-Edema Lymphatic Pump: short foot arch activation and calf venous pumps.\n"
        "6. Cervical Spine & Scapular Stabilization: chin tucks, wall angels, and thoracic extension.\n"
        "Always guide users to move gently, breathe diaphragmatically, and never push through pain."
    ),
    tools=[get_rehab_departments, generate_rehab_routine],
)

# 6. Specialized Cardiovascular Physiology Sub-Agent
cardio_physiology_coach = Agent(
    name="cardio_physiology_coach",
    model="gemini-2.0-flash",
    description="Specialist cardiovascular physiology coach. Computes 5-zone HR targets (Zone 2 fat oxidation, Zone 3-4 hypertrophy, Zone 5 Tabata) and evaluates post-workout heart rate telemetry (Min HR, Max HR, Avg HR, RPE).",
    instruction=(
        "You are the Cardiovascular Physiology Coach in the Google ADK AI Fitness Coach team.\n"
        "Your role is to ensure training stimulates the intended metabolic pathways:\n"
        "- Fat Burning / Weight Loss: Prescribe and track Zone 2 (60-70% Max HR) for maximum lipid oxidation.\n"
        "- Muscle Building / Hypertrophy: Prescribe Zone 3-4 (75-88% Max HR) balancing mechanical tension with recovery intervals.\n"
        "- Tabata Intervals: Push into Zone 4-5 (85-95% Max HR) for anaerobic capacity and EPOC afterburn.\n"
        "- Mobility & Restoration: Keep strictly in Zone 1 (50-60% Max HR) for parasympathetic joint recovery.\n"
        "After workouts, analyze user min, max, and average heart rates with RPE across 3 physiological cases:\n"
        "1. Cardio Limiting Muscles -> advice to extend rest by 20-30s.\n"
        "2. Incomplete Recovery / Thyroid / Edema Alert -> reduce volume by 15-20% and prioritize supine/seated positions.\n"
        "3. Optimal Stimulus -> progressive overload unlocked!"
    ),
    tools=[calculate_heart_rate_zones, get_target_heart_rate_zone, analyze_workout_heart_rate],
)

# 7. Root Coordinator Agent (The Head AI Fitness Coach)
root_agent = Agent(
    name="ai_fitness_coach",
    model="gemini-2.0-flash",
    description="The Head AI Fitness Coach. Manages user goals, orchestrates periodized 5-day rolling programming, mono-days, form analysis, Tabata pacing, mobility routines, 6-department rehabilitation, cardiovascular heart rate zones, and long-term athletic progression.",
    instruction=(
        "You are the Head AI Fitness Coach, an elite personal trainer powered by Google ADK.\n"
        "You provide encouraging, scientifically grounded, and injury-conscious coaching.\n\n"
        "Capabilities:\n"
        "- Program 5-Day Rolling Split workouts, mono-days, or foundation weekly plans (delegate to 'workout_planner').\n"
        "- Provide step-by-step form guides and biomechanics analysis for 230 catalog exercises (delegate to 'technique_coach').\n"
        "- Guide high-intensity 40s/10s Tabata protocols with 60s rest between sets (delegate to 'tabata_specialist').\n"
        "- Generate 10-drill joint mobility flows (delegate to 'mobility_specialist').\n"
        "- Generate specialized restorative routines for 6 rehabilitation departments (delegate to 'rehab_specialist').\n"
        "- Calculate physiological heart rate zones and cross-analyze telemetry (delegate to 'cardio_physiology_coach').\n"
        "- Track user progress, log completed sessions, and monitor weight delta trends using your built-in tools.\n\n"
        "Communication Style:\n"
        "- Concise, athletic, positive, and direct.\n"
        "- Always check for joint pain or injuries and actively filter out dangerous movements.\n"
        "- Respond in the language preferred by the user (English or Ukrainian)."
    ),
    tools=[
        get_user_progress_metrics,
        log_workout_progress,
        generate_rolling_workout,
        advance_rolling_split,
        generate_mono_workout,
        generate_mobility_routine,
        generate_rehab_routine,
        get_rehab_departments,
        calculate_heart_rate_zones,
        get_target_heart_rate_zone,
        analyze_workout_heart_rate,
    ],
    sub_agents=[
        workout_planner,
        technique_coach,
        tabata_specialist,
        mobility_specialist,
        rehab_specialist,
        cardio_physiology_coach,
    ],
)


# ---------------------------------------------------------------------------
# Interactive Command-Line Console Runner
# ---------------------------------------------------------------------------
def run_cli():
    """Runs a standalone interactive console for testing the Google ADK agent and tools."""
    print("=" * 65)
    print(" 🏋️ AI Fitness Coach - Google ADK (Agent Development Kit)")
    print(f" Root Agent: {root_agent.name} (Model: {root_agent.model})")
    print(f" Sub-Agents: {[a.name for a in root_agent.sub_agents]}")
    print(f" ADK Framework Installed: {'Yes (google-adk)' if ADK_AVAILABLE else 'No (Running in standalone mode)'}")
    print("=" * 65)
    print("Quick Commands:")
    print("  1: Generate 3-Day Weekly Plan (Intermediate, Home)")
    print("  2: Build Custom Focus Workout (Chest, Arms, Abs)")
    print("  3: Search Compound Combo Exercises")
    print("  4: Show Tabata Protocol (40s/10s, 8 cycles, 60s rest)")
    print("  5: View Progress Metrics")
    print("  6: Generate 10-Drill Mobility Routine (General or Targeted)")
    print("  7: Heart Rate Zones & Post-Workout Physiology Analysis")
    print("  8: Generate 5-Day Rolling Split Workout (10 drills, 5 supersets)")
    print("  9: Advance Rolling Split Queue")
    print(" 10: Generate Rehabilitation Routine (Restorative flow)")
    print("  q: Quit")
    print("-" * 65)

    while True:
        try:
            cmd = input("\nEnter command [1-10, q]: ").strip().lower()
            if cmd in ["q", "quit", "exit"]:
                print("Goodbye! Keep training strong! 💪")
                break
            elif cmd == "1":
                plan = generate_weekly_plan(level="intermediate", location="home")
                print(f"\n✓ Generated {plan['program_days']} workout days (10 exercises each):")
                for d in plan["weekly_plan"]:
                    print(f"  • {d['day_label']}: {d['format_description'][:45]}...")
            elif cmd == "2":
                workout = build_custom_focus_workout(["chest", "arms", "abs"], level="advanced")
                print(f"\n✓ Built Custom Workout '{workout['day_label']}':")
                for ex in workout["exercises"][:5]:
                    print(f"  #{ex['order']} {ex['name']} ({ex['zone']}) - {ex['sets']}x{ex['reps']}")
                print(f"  ... plus 5 more exercises (10 total)")
            elif cmd == "3":
                matches = search_exercise_catalog(query="", movement_pattern="")
                combos = [m for m in matches["matches"] if m.get("is_compound_combo")]
                print(f"\n✓ Found {len(combos)} compound combo hybrids:")
                for c in combos[:6]:
                    print(f"  ⚡ {c['name']} [{', '.join(c['equipment'])}]")
            elif cmd == "4":
                tab = get_tabata_protocol_settings(40, 10, 8, 60, 2)
                print(f"\n⏱️ {tab['protocol']}:")
                print(f"  • Work: {tab['work_duration']}")
                print(f"  • Rest: {tab['rest_duration']}")
                print(f"  • Structure: {tab['cycles_per_set']}, {tab['inter_set_recovery']}")
                print(f"  • Est. Duration: {tab['estimated_session_duration']}")
            elif cmd == "5":
                stats = get_user_progress_metrics()
                print(f"\n📊 Athletic Progress Metrics:")
                print(f"  • Workouts Completed: {stats['total_workouts_completed']}")
                print(f"  • Target Weight: {stats['weight_goal']['target_weight']} kg")
            elif cmd == "6":
                mob = generate_mobility_routine(focus_zones=["hips", "spine"])
                print(f"\n🧘 {mob['day_label']} (10 drills total):")
                for ex in mob["exercises"][:6]:
                    print(f"  #{ex['order']} [{ex['zone']}] {ex['name']} - {ex['reps']}")
                print(f"  ... plus 4 more mobility drills")
            elif cmd == "7":
                zones = calculate_heart_rate_zones(age=30)
                print(f"\n❤️ Heart Rate Training Zones (Age 30, Max HR: {zones['max_hr']} BPM):")
                for z in zones["zones"]:
                    print(f"  • Zone {z['zone']}: {z['name_en']} ({z['bpm_range']}) - {z['primary_focus_en'][:40]}...")
                analysis = analyze_workout_heart_rate(avg_hr=125, max_hr_recorded=140, goal="weight_loss", workout_format="standard", age=30)
                print(f"\n🔬 Sample Workout Analysis (Weight Loss @ 125 BPM):")
                print(f"  • Status: {analysis['status_title_en']}")
                print(f"  • Feedback: {analysis['feedback_en']}")
            elif cmd == "8":
                rolling = generate_rolling_workout(day_index=None, location="home", sex="female")
                print(f"\n🔄 {rolling['day_name_en']} - {rolling['name_en']}:")
                for ex in rolling["exercises"]:
                    print(f"  • [{ex['superset_group']}] {ex['name']} ({ex['sets']}x{ex['reps']}) | Tip: {ex['coach_progression_tip']}")
            elif cmd == "9":
                res = advance_rolling_split()
                print(f"\n⏭️ Split Queue Advanced: New Day Index = {res['new_day_index']} ({res['next_day_name_en']})")
            elif cmd == "10":
                rehab = generate_rehab_routine(department="pelvic_floor_diastasis", location="home")
                print(f"\n🩺 {rehab['name_en']} (8 restorative drills):")
                for ex in rehab["exercises"]:
                    print(f"  • #{ex['order']} {ex['name']} ({ex['reps']}) - {ex['execution'][:60]}...")
            else:
                print("Invalid option. Enter 1 to 10, or 'q' to quit.")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break



if __name__ == "__main__":
    run_cli()

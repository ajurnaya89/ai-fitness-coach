"""
Data models for the AI Fitness Coach.
Defines exercises, planned workouts, and workout history logs.
Supports full multi-language capabilities (English / Ukrainian)
and detailed step-by-step form execution descriptions.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Optional


@dataclass
class Exercise:
    """Represents a single exercise in the exercise library."""
    id: str                                  # Unique identifier, e.g. "db_goblet_squat"
    name: str                                # English name, e.g. "Dumbbell Goblet Squat"
    movement_pattern: str                    # Squat, Hinge, Lunge, Push, Pull, Core, Carry, Combo
    exercise_family: str                     # Sub-group, e.g. "Bilateral Knee Dominant"
    primary_muscles: List[str]               # e.g. ["Quadriceps", "Glutes"]
    secondary_muscles: List[str]             # e.g. ["Core", "Upper Back"]
    equipment_needed: List[str]              # e.g. ["adjustable dumbbells"]
    difficulty: int                          # 1 (Beginner) to 5 (Advanced)
    stability_demand: str                    # "Low", "Medium", "High"
    unilateral: bool                         # True if single-leg/single-arm
    instructions: str                        # Full English step-by-step guide
    name_ua: str = ""                        # Ukrainian name, e.g. "Гоблет-присідання з гантеллю"
    instructions_ua: str = ""                # Full Ukrainian step-by-step guide
    setup: str = ""                          # English setup & stance cues
    execution: str = ""                      # English movement execution
    form_tips: str = ""                      # English pro tip / common mistake
    setup_ua: str = ""                       # Ukrainian setup & stance cues
    execution_ua: str = ""                   # Ukrainian movement execution
    form_tips_ua: str = ""                   # Ukrainian pro tip / common mistake
    default_sets: int = 3
    default_reps: str = "10-12"
    rest_seconds: int = 60
    joint_stress: List[str] = field(default_factory=list)      # ["wrist", "knee", "shoulder", "lower_back", "elbow", "ankle"]
    location: List[str] = field(default_factory=lambda: ["home", "gym"])  # ["home", "gym"] or ["gym"]
    trx_anchor: str = "any"                 # "door", "bar", or "any"
    is_compound_combo: bool = False         # True for multi-movement hybrids (e.g. Squat + Press)
    equipment_alternatives: str = ""        # e.g. "Resistance Band / Dumbbell alternative"
    equipment_alternatives_ua: str = ""     # e.g. "Альтернатива: гумова стрічка / гантелі"
    gender_priority: List[str] = field(default_factory=lambda: ["female", "male"])

    def to_dict(self):
        return asdict(self)


@dataclass
class PlannedExercise:
    """Represents an exercise assigned to a specific planned workout."""
    exercise_id: str
    name: str
    order_index: int
    sets: int
    reps: str
    rest_seconds: int
    name_ua: str = ""
    zone_en: str = ""
    zone_ua: str = ""
    instructions: str = ""
    instructions_ua: str = ""
    setup: str = ""
    execution: str = ""
    form_tips: str = ""
    setup_ua: str = ""
    execution_ua: str = ""
    form_tips_ua: str = ""
    notes: str = ""
    completed: bool = False
    actual_reps: str = ""
    actual_weight: str = ""
    joint_stress: List[str] = field(default_factory=list)
    location: List[str] = field(default_factory=lambda: ["home", "gym"])
    trx_anchor: str = "any"
    is_compound_combo: bool = False
    equipment_alternatives: str = ""
    equipment_alternatives_ua: str = ""
    superset_group: str = ""                # e.g. "Superset 1", "A1", "A2"
    coach_progression_tip: str = ""         # Progression advice badge
    coach_progression_tip_ua: str = ""
    last_weight: str = ""                   # Last logged weight
    last_reps: str = ""                     # Last logged reps
    gender_priority: List[str] = field(default_factory=lambda: ["female", "male"])
    actual_sets: Optional[int] = None
    perceived_difficulty: Optional[int] = 3
    user_comment: str = ""
    disliked: bool = False
    replaced_badge: Optional[str] = None
    replaced_badge_ua: Optional[str] = None

    def to_dict(self):
        return asdict(self)


@dataclass
class WorkoutPlan:
    """Represents a planned workout session (~60 min)."""
    workout_id: str
    day_label: str
    target_duration_minutes: int
    day_label_ua: str = ""
    name_en: str = ""
    name_ua: str = ""
    day_name_en: str = ""
    day_name_ua: str = ""
    format_type: str = "standard"           # "standard", "circuit", "tabata", "sandwich", "superset", "antagonist", "pilates_static"
    format_description: str = ""
    format_description_ua: str = ""
    goal: str = "muscle_gain"
    location: str = "home"
    target_hr_zone: str = ""
    target_hr_zone_ua: str = ""
    target_hr_bpm_range: str = ""
    mode: str = "workout"                   # "workout", "mobility", "rehabilitation"
    rehab_department: str = ""
    exercises: List[PlannedExercise] = field(default_factory=list)

    def to_dict(self):
        return asdict(self)


@dataclass
class ExerciseFeedback:
    """Tracks feedback and performance for one exercise within a workout."""
    exercise_id: str
    sets_completed: int
    reps_completed: str
    weight_used: str
    skipped: bool = False
    perceived_difficulty: int = 3
    notes: str = ""
    user_comment: str = ""
    disliked: bool = False


@dataclass
class CompletedWorkoutLog:
    """Tracks the summary and user feedback of a completed workout."""
    workout_id: str
    date_completed: str
    duration_minutes: int
    overall_rating: int
    overall_fatigue: int
    user_notes: str = ""
    min_heart_rate: Optional[int] = None
    max_heart_rate: Optional[int] = None
    avg_heart_rate: Optional[int] = None
    hr_zone_achieved: int = 0
    hr_goal_achieved: bool = False
    hr_analysis_feedback: str = ""
    # Smartwatch Telemetry Hub fields
    watch_duration_minutes: Optional[int] = None
    active_calories: Optional[int] = None
    total_calories: Optional[int] = None
    zone1_mins: Optional[int] = None
    zone2_mins: Optional[int] = None
    zone3_mins: Optional[int] = None
    zone4_mins: Optional[int] = None
    zone5_mins: Optional[int] = None
    dominant_zone: Optional[int] = None
    training_load: Optional[float] = None
    recovery_time_hours: Optional[int] = None
    telemetry_analysis: str = ""
    exercise_logs: List[ExerciseFeedback] = field(default_factory=list)

    def to_dict(self):
        return asdict(self)

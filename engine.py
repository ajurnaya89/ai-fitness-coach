"""
Programming and Exercise Rotation Engine for AI Fitness Coach.
Rules:
- Exactly 10 exercises per standard workout (~55-60 minutes) arranged as 5 Supersets x 2 Exercises.
- 5-Day Rolling Split Architecture:
  * Day 1: Shoulders + Biceps + Triceps + Core (5 Supersets)
  * Day 2: Back + Chest + Rear Delts + Core (5 Supersets)
  * Day 3: Dedicated Abs, Deep Core, Waist & Pelvic Stabilizers (10 Exercises, zero doming/wrist strain)
  * Day 4: Glutes + Hamstrings + "Hip Dips / Ушки" (Gluteus Medius) + Core (5 Supersets)
  * Day 5: Quads + Inner Thighs (Adductors) + Calves & Ankle Pumps + Core (5 Supersets)
- Foundation 3-Day Weekly Program (for backward compatibility).
- Special Mono-Days:
  * Special 13-Exercise Lower Body & Waist Sculpt (13 exercises)
  * Pure Back & Scapular Posture (10 exercises)
  * Pure Glutes & Legs Hypertrophy (10 exercises)
  * Pure Core & Flat Stomach (10 exercises)
- Rehabilitation & Restoration (6 Dedicated Departments):
  * Pelvic Floor & Diastasis Recti Recovery
  * Hyperlordosis Correction & Lumbar Decompression
  * Wrist & Carpal Tunnel Unloading
  * Knee Joint & Hip Alignment
  * Ankle Stability & Anti-Edema Lymphatic Pump
  * Cervical Spine & Scapular Stabilization
- Dynamic Joint Mobility Flow (10 drills).
- Biomechanical & Medical Guardrails:
  * Strict zero-palm-bearing rule for wrist isolation.
  * No deep knee flexion under shear load for knee isolation.
  * Strict exclusion of quadruped/kneeling for 'no_kneeling'.
  * Zero axial load for lower back / lordosis / spinal hernia.
  * Diastasis recti safe mode (no crunches, doming, jumps).
  * Thyroid care (rest >= 60-75s, no cortisol spikes).
  * Edema care (lymphatic pump & venous return).
  * TRX Anchor: Bar vs Door isolation.
  * Equipment inventory matching.
- Closed-Loop Progression Tips and Last Performance prefill.
"""

import random
from datetime import datetime
from typing import Dict, List, Optional, Any

from models import Exercise, PlannedExercise, WorkoutPlan
import database
import heart_rate
from mobility_data import MOBILITY_ZONES, MOBILITY_EXERCISES
from rehab_data import REHAB_DEPARTMENTS, REHAB_EXERCISES


# ---------------------------------------------------------------------------
# 1. CLASSIC 3-DAY WEEKLY TEMPLATES (Cleaned: Zero Mobility inside Strength!)
# ---------------------------------------------------------------------------
WORKOUT_TEMPLATES = [
    {
        "day_label": "Day 1: Quads + Chest + Abs (10 Exercises)",
        "day_label_ua": "День 1: Квадрицепси + Груди + Прес (10 вправ)",
        "slots": [
            # --- ACCENT 1: QUADS / KNEE DOMINANT (4 exercises) ---
            {
                "zone": "Quads (Primary Compound)",
                "zone_ua": "Квадрицепси (База)",
                "patterns": ["Squat"],
                "families": ["Bilateral Knee Dominant"],
                "sets": 3, "reps": "8-12", "rest": 60, "superset": "Superset 1: A1"
            },
            {
                "zone": "Quads (Unilateral)",
                "zone_ua": "Квадрицепси (Унілатерально)",
                "patterns": ["Lunge", "Squat"],
                "families": ["Unilateral Knee Dominant"],
                "sets": 3, "reps": "8-10 each", "rest": 60, "superset": "Superset 1: A2"
            },
            {
                "zone": "Quads (Angles / Sliders / TRX)",
                "zone_ua": "Квадрицепси (Кути / Слайдери / TRX)",
                "patterns": ["Squat", "Lunge"],
                "families": ["Bilateral Knee Dominant", "Lateral Knee Dominant", "Unilateral Knee Dominant", "Compound Combo Hybrid"],
                "sets": 2, "reps": "10-12", "rest": 60, "superset": "Superset 2: B1"
            },
            {
                "zone": "Quads (Isolation / Tempo)",
                "zone_ua": "Квадрицепси (Ізоляція / Темп)",
                "patterns": ["Squat"],
                "families": ["Quad Isolation", "Bilateral Knee Dominant"],
                "sets": 2, "reps": "12-15", "rest": 45, "superset": "Superset 2: B2"
            },

            # --- ACCENT 2: CHEST / HORIZONTAL PUSH (4 exercises) ---
            {
                "zone": "Chest (Primary Press)",
                "zone_ua": "Груди (Базовий жим)",
                "patterns": ["Push"],
                "families": ["Horizontal Push Bilateral"],
                "sets": 3, "reps": "8-12", "rest": 60, "superset": "Superset 3: C1"
            },
            {
                "zone": "Chest (TRX / Suspension)",
                "zone_ua": "Груди (TRX / Підвіс)",
                "patterns": ["Push"],
                "families": ["Horizontal Push Suspension"],
                "sets": 3, "reps": "10-12", "rest": 60, "superset": "Superset 3: C2"
            },
            {
                "zone": "Chest (Push-Up / Band Resisted)",
                "zone_ua": "Груди (Віджимання / Гума)",
                "patterns": ["Push"],
                "families": ["Horizontal Push Resisted", "Horizontal Push Bodyweight", "Horizontal Push Standing"],
                "sets": 2, "reps": "10-15", "rest": 60, "superset": "Superset 4: D1"
            },
            {
                "zone": "Chest (Flye / Stretch Focus)",
                "zone_ua": "Груди (Розведення / Розтяг)",
                "patterns": ["Push"],
                "families": ["Chest Isolation", "Chest Isolation Suspension", "Horizontal Push Unilateral"],
                "sets": 2, "reps": "12-15", "rest": 45, "superset": "Superset 4: D2"
            },

            # --- ABS / CORE ALWAYS (2 exercises) ---
            {
                "zone": "Abs (Anti-Extension)",
                "zone_ua": "Прес (Анти-розгинання)",
                "patterns": ["Core"],
                "families": ["Anti-Extension Core"],
                "sets": 3, "reps": "10-12", "rest": 45, "superset": "Superset 5: E1"
            },
            {
                "zone": "Abs (Anti-Rotation / Obliques)",
                "zone_ua": "Прес (Анти-ротація / Косі)",
                "patterns": ["Core"],
                "families": ["Anti-Rotation Core", "Rotational Core", "Lateral Core & Adductor"],
                "sets": 2, "reps": "12-15 each", "rest": 45, "superset": "Superset 5: E2"
            }
        ]
    },
    {
        "day_label": "Day 2: Back + Hamstrings & Glutes + Abs (10 Exercises)",
        "day_label_ua": "День 2: Спина + Біцепс стегна та сідниці + Прес (10 вправ)",
        "slots": [
            # --- ACCENT 1: HAMSTRINGS & GLUTES / HINGE (4 exercises) ---
            {
                "zone": "Hamstrings & Glutes (Primary Hinge)",
                "zone_ua": "Біцепс стегна та сідниці (Базовий нахил)",
                "patterns": ["Hinge"],
                "families": ["Bilateral Hip Hinge"],
                "sets": 3, "reps": "8-12", "rest": 60, "superset": "Superset 1: A1"
            },
            {
                "zone": "Hamstrings & Glutes (Unilateral Hinge)",
                "zone_ua": "Біцепс стегна та сідниці (Унілатерально)",
                "patterns": ["Hinge"],
                "families": ["Unilateral Hip Hinge"],
                "sets": 3, "reps": "8-10 each", "rest": 60, "superset": "Superset 1: A2"
            },
            {
                "zone": "Hamstrings (Slider / Ball / Knee Flexion)",
                "zone_ua": "Біцепс стегна (Слайдери / М'яч / Згинання)",
                "patterns": ["Hinge"],
                "families": ["Posterior Knee Flexion"],
                "sets": 2, "reps": "10-12", "rest": 60, "superset": "Superset 2: B1"
            },
            {
                "zone": "Glutes (Bridge / Thrust / Isolation)",
                "zone_ua": "Сідниці (Міст / Тяга / Ізоляція)",
                "patterns": ["Hinge", "Squat"],
                "families": ["Glute Bridge / Thrust", "Hip Abduction / Stability", "Glute Isolation"],
                "sets": 2, "reps": "12-15", "rest": 45, "superset": "Superset 2: B2"
            },

            # --- ACCENT 2: BACK / PULL (4 exercises) ---
            {
                "zone": "Back (Horizontal Row Bilateral)",
                "zone_ua": "Спина (Горизонтальна тяга обома руками)",
                "patterns": ["Pull"],
                "families": ["Horizontal Pull Bilateral"],
                "sets": 3, "reps": "8-12", "rest": 60, "superset": "Superset 3: C1"
            },
            {
                "zone": "Back (TRX Inverted Row)",
                "zone_ua": "Спина (Тяга в петлях TRX)",
                "patterns": ["Pull"],
                "families": ["Horizontal Pull Suspension"],
                "sets": 3, "reps": "10-12", "rest": 60, "superset": "Superset 3: C2"
            },
            {
                "zone": "Back (Vertical Pulldown / Pullover)",
                "zone_ua": "Спина (Вертикальна тяга / Пуловер)",
                "patterns": ["Pull"],
                "families": ["Vertical Pull Bilateral", "Vertical Pull Unilateral", "Vertical Pull / Extension", "Vertical Pull Suspension"],
                "sets": 2, "reps": "10-12", "rest": 60, "superset": "Superset 4: D1"
            },
            {
                "zone": "Back (Rear Delts / Scapular)",
                "zone_ua": "Спина (Задня дельта / Лопатки)",
                "patterns": ["Pull"],
                "families": ["Posterior Shoulder / Scapular"],
                "sets": 2, "reps": "12-15", "rest": 45, "superset": "Superset 4: D2"
            },

            # --- ABS / CORE ALWAYS (2 exercises) ---
            {
                "zone": "Abs (Dynamic Core / Planks)",
                "zone_ua": "Прес (Динамічний кор / Планки)",
                "patterns": ["Core"],
                "families": ["Dynamic Core / Hip Flexion", "Anti-Extension Core"],
                "sets": 3, "reps": "10-15", "rest": 45, "superset": "Superset 5: E1"
            },
            {
                "zone": "Abs (Lateral Core / Rotation)",
                "zone_ua": "Прес (Боковий кор / Ротація)",
                "patterns": ["Core"],
                "families": ["Rotational Core", "Lateral Core & Hip Abduction", "Lateral Core & Adductor"],
                "sets": 2, "reps": "12-15 each", "rest": 45, "superset": "Superset 5: E2"
            }
        ]
    },
    {
        "day_label": "Day 3: Shoulders & Arms + Lunges & Glutes + Abs (10 Exercises)",
        "day_label_ua": "День 3: Плечі та руки + Випади та сідниці + Прес (10 вправ)",
        "slots": [
            # --- ACCENT 1: SHOULDERS & ARMS (4 exercises) ---
            {
                "zone": "Shoulders (Overhead Press)",
                "zone_ua": "Плечі (Жим над головою)",
                "patterns": ["Push"],
                "families": ["Vertical Push Bilateral", "Vertical Push Unilateral", "Vertical Push Bodyweight"],
                "sets": 3, "reps": "8-10", "rest": 60, "superset": "Superset 1: A1"
            },
            {
                "zone": "Shoulders (Lateral Raise / Scaption)",
                "zone_ua": "Плечі (Махи / Ізоляція дельт)",
                "patterns": ["Push"],
                "families": ["Shoulder Isolation"],
                "sets": 3, "reps": "12-15", "rest": 45, "superset": "Superset 1: A2"
            },
            {
                "zone": "Arms (Biceps)",
                "zone_ua": "Руки (Біцепс)",
                "patterns": ["Pull"],
                "families": ["Elbow Flexion", "Elbow Flexion Suspension"],
                "sets": 2, "reps": "10-12", "rest": 45, "superset": "Superset 2: B1"
            },
            {
                "zone": "Arms (Triceps)",
                "zone_ua": "Руки (Трицепс)",
                "patterns": ["Push"],
                "families": ["Elbow Extension", "Elbow Extension Suspension"],
                "sets": 2, "reps": "10-12", "rest": 45, "superset": "Superset 2: B2"
            },

            # --- ACCENT 2: LUNGES & GLUTES (4 exercises) ---
            {
                "zone": "Legs (Forward / Reverse Lunge)",
                "zone_ua": "Ноги (Випади вперед/назад)",
                "patterns": ["Lunge"],
                "families": ["Unilateral Knee Dominant", "Compound Combo Hybrid"],
                "sets": 3, "reps": "10-12 each", "rest": 60, "superset": "Superset 3: C1"
            },
            {
                "zone": "Legs (Lateral / Curtsy Lunge)",
                "zone_ua": "Ноги (Бокові / Діагональні випади)",
                "patterns": ["Lunge"],
                "families": ["Lateral Knee Dominant", "Multi-Planar Knee Dominant"],
                "sets": 2, "reps": "10-12 each", "rest": 60, "superset": "Superset 3: C2"
            },
            {
                "zone": "Glutes (Abduction / Band Stability)",
                "zone_ua": "Сідниці (Відведення з гумою)",
                "patterns": ["Hinge", "Squat"],
                "families": ["Hip Abduction / Stability", "Glute Bridge / Thrust", "Glute Isolation"],
                "sets": 2, "reps": "15-20", "rest": 45, "superset": "Superset 4: D1"
            },
            {
                "zone": "Legs & Core (Loaded Carry / Calves)",
                "zone_ua": "Ноги та Кор (Переноски / Литки)",
                "patterns": ["Carry", "Squat"],
                "families": ["Unilateral Loaded Carry", "Bilateral Loaded Carry", "Offset Loaded Carry", "Ankle Plantarflexion"],
                "sets": 2, "reps": "40 paces / 15 reps", "rest": 45, "superset": "Superset 4: D2"
            },

            # --- ABS / CORE ALWAYS (2 exercises) ---
            {
                "zone": "Abs (TRX / Slider Body Saw)",
                "zone_ua": "Прес (Планка-пила в TRX / Слайдерах)",
                "patterns": ["Core"],
                "families": ["Anti-Extension Core", "Dynamic Core & Push"],
                "sets": 3, "reps": "10-12", "rest": 45, "superset": "Superset 5: E1"
            },
            {
                "zone": "Abs (Obliques / Lateral Core)",
                "zone_ua": "Прес (Косі м'язи / Боковий кор)",
                "patterns": ["Core"],
                "families": ["Lateral Core & Adductor", "Anti-Rotation Core", "Cross-Body Posterior Stability"],
                "sets": 2, "reps": "10-12 each", "rest": 45, "superset": "Superset 5: E2"
            }
        ]
    }
]


# ---------------------------------------------------------------------------
# 2. THE 5-DAY ROLLING SPLIT QUEUE (5 Supersets x 2 Exercises = 10 Exercises)
# ---------------------------------------------------------------------------
ROLLING_SPLIT_TEMPLATES = [
    # DAY 1: Shoulders + Biceps + Triceps + Core
    {
        "day_index": 0,
        "day_label": "Day 1: Shoulders + Biceps + Triceps + Core (5 Supersets)",
        "day_label_ua": "День 1: Плечі + Біцепс + Трицепс + Прес (5 Суперсетів)",
        "description_en": "Upper body sculpt emphasizing shoulder deltoids, arm definition, and wrist-safe deep core stabilization.",
        "description_ua": "Скульптурування верхньої частини тіла: дельти плечей, рельєф рук та безпечна для зап'ясть стабілізація кору.",
        "slots": [
            # Superset 1: Shoulders (Press + Lateral Raise)
            {
                "zone": "Shoulders (Overhead Press)",
                "zone_ua": "Плечі (Жим над головою)",
                "patterns": ["Push"],
                "families": ["Vertical Push Bilateral", "Vertical Push Unilateral", "Vertical Push Bodyweight"],
                "sets": 3, "reps": "8-10", "rest": 60, "superset": "Superset 1: A1"
            },
            {
                "zone": "Shoulders (Lateral Raise / Scaption)",
                "zone_ua": "Плечі (Махи в сторони / Скапція)",
                "patterns": ["Push"],
                "families": ["Shoulder Isolation"],
                "sets": 3, "reps": "12-15", "rest": 45, "superset": "Superset 1: A2"
            },
            # Superset 2: Shoulders (Front Raise + Rear Delt / Y-Raise)
            {
                "zone": "Shoulders (Front Raise / Upright Row)",
                "zone_ua": "Плечі (Підйоми перед собою / Протяжка)",
                "patterns": ["Push", "Pull"],
                "families": ["Shoulder Isolation", "Vertical Pull Bilateral"],
                "sets": 3, "reps": "10-12", "rest": 45, "superset": "Superset 2: B1"
            },
            {
                "zone": "Shoulders (Rear Delt / Y-Raise / Face Pull)",
                "zone_ua": "Плечі (Задня дельта / Y-підйоми / Фейспул)",
                "patterns": ["Pull"],
                "families": ["Posterior Shoulder / Scapular"],
                "sets": 3, "reps": "12-15", "rest": 45, "superset": "Superset 2: B2"
            },
            # Superset 3: Biceps (2 Variations)
            {
                "zone": "Biceps (Supinated Dumbbell / TRX Curl)",
                "zone_ua": "Біцепс (Супінований згин з гантелями / TRX)",
                "patterns": ["Pull"],
                "families": ["Elbow Flexion", "Elbow Flexion Suspension"],
                "sets": 3, "reps": "10-12", "rest": 45, "superset": "Superset 3: C1"
            },
            {
                "zone": "Biceps (Hammer Curl / Neutral Grip)",
                "zone_ua": "Біцепс (Молотковий згин / Нейтральний хват)",
                "patterns": ["Pull"],
                "families": ["Elbow Flexion", "Elbow Flexion Suspension"],
                "sets": 3, "reps": "10-12", "rest": 45, "superset": "Superset 3: C2"
            },
            # Superset 4: Triceps (2 Variations)
            {
                "zone": "Triceps (TRX / Overhead Extension)",
                "zone_ua": "Трицепс (Французький жим / Розгинання в TRX)",
                "patterns": ["Push"],
                "families": ["Elbow Extension", "Elbow Extension Suspension"],
                "sets": 3, "reps": "10-12", "rest": 45, "superset": "Superset 4: D1"
            },
            {
                "zone": "Triceps (Band Pushdown / Kickback / Diamond)",
                "zone_ua": "Трицепс (Розгинання з гумою / Кикбек)",
                "patterns": ["Push"],
                "families": ["Elbow Extension", "Elbow Extension Suspension"],
                "sets": 3, "reps": "12-15", "rest": 45, "superset": "Superset 4: D2"
            },
            # Superset 5: Abs / Deep Core (wrist-safe)
            {
                "zone": "Abs (Anti-Extension / Dead Bug)",
                "zone_ua": "Прес (Анти-розгинання / Dead Bug)",
                "patterns": ["Core"],
                "families": ["Anti-Extension Core"],
                "sets": 3, "reps": "10-12", "rest": 45, "superset": "Superset 5: E1"
            },
            {
                "zone": "Abs (Anti-Rotation / Obliques)",
                "zone_ua": "Прес (Анти-ротація / Косі м'язи)",
                "patterns": ["Core"],
                "families": ["Anti-Rotation Core", "Lateral Core & Adductor", "Rotational Core"],
                "sets": 3, "reps": "12-15 each", "rest": 45, "superset": "Superset 5: E2"
            }
        ]
    },

    # DAY 2: Back + Chest + Rear Delts + Core
    {
        "day_index": 1,
        "day_label": "Day 2: Back + Chest + Rear Delts + Core (5 Supersets)",
        "day_label_ua": "День 2: Спина + Груди + Задня дельта + Прес (5 Суперсетів)",
        "description_en": "Antagonistic torso workout targeting posture, lats, scapular retraction, and chest sculpt.",
        "description_ua": "Антагоністичне тренування торсу: постава, найширші м'язи, зведення лопаток та тонус грудей.",
        "slots": [
            # Superset 1: Back (Horizontal Pull / TRX Row + Narrow Row)
            {
                "zone": "Back (TRX / Horizontal Pull)",
                "zone_ua": "Спина (Тяга в TRX / Горизонтальна тяга)",
                "patterns": ["Pull"],
                "families": ["Horizontal Pull Suspension", "Horizontal Pull Bilateral"],
                "sets": 3, "reps": "8-12", "rest": 60, "superset": "Superset 1: A1"
            },
            {
                "zone": "Back (Narrow Row Dumbbell / Band)",
                "zone_ua": "Спина (Вузька тяга гантелей / гуми)",
                "patterns": ["Pull"],
                "families": ["Horizontal Pull Bilateral", "Horizontal Pull Unilateral"],
                "sets": 3, "reps": "10-12", "rest": 60, "superset": "Superset 1: A2"
            },
            # Superset 2: Back & Rear Delts (Unilateral Row + Rear Delt Flye / Face Pull)
            {
                "zone": "Back (Unilateral Dumbbell / Band Row)",
                "zone_ua": "Спина (Одноручна тяга з упором)",
                "patterns": ["Pull"],
                "families": ["Horizontal Pull Unilateral"],
                "sets": 3, "reps": "10-12 each", "rest": 60, "superset": "Superset 2: B1"
            },
            {
                "zone": "Rear Delts (Rear Delt Flye / Band Face Pull)",
                "zone_ua": "Задня дельта (Махи в нахилі / Фейспул з гумою)",
                "patterns": ["Pull"],
                "families": ["Posterior Shoulder / Scapular"],
                "sets": 3, "reps": "12-15", "rest": 45, "superset": "Superset 2: B2"
            },
            # Superset 3: Scapular Control & Lats
            {
                "zone": "Lats (Straight-Arm Pulldown / TRX Scapular Retraction)",
                "zone_ua": "Найширші (Пуловер з прямими руками / Лопаткова тяга TRX)",
                "patterns": ["Pull"],
                "families": ["Vertical Pull / Extension", "Vertical Pull Suspension", "Posterior Shoulder / Scapular"],
                "sets": 3, "reps": "10-12", "rest": 45, "superset": "Superset 3: C1"
            },
            {
                "zone": "Upper Back (Band Star / Pullover)",
                "zone_ua": "Верх спини (Пуловер на дивані / Розведення гуми 'Зірка')",
                "patterns": ["Pull"],
                "families": ["Vertical Pull / Extension", "Posterior Shoulder / Scapular"],
                "sets": 3, "reps": "12-15", "rest": 45, "superset": "Superset 3: C2"
            },
            # Superset 4: Chest (Press + Flye / Band Press)
            {
                "zone": "Chest (Dumbbell Floor Press / Standing Band Press)",
                "zone_ua": "Груди (Жим гантелей з підлоги / Жим стоячи з гумою)",
                "patterns": ["Push"],
                "families": ["Horizontal Push Bilateral", "Horizontal Push Standing", "Horizontal Push Unilateral"],
                "sets": 3, "reps": "10-12", "rest": 60, "superset": "Superset 4: D1"
            },
            {
                "zone": "Chest (Flye / Push-Up on Couch / Incline)",
                "zone_ua": "Груди (Розведення гантелей / Віджимання від дивану)",
                "patterns": ["Push"],
                "families": ["Chest Isolation", "Horizontal Push Resisted", "Horizontal Push Bodyweight", "Chest Isolation Suspension"],
                "sets": 3, "reps": "12-15", "rest": 45, "superset": "Superset 4: D2"
            },
            # Superset 5: Abs / Core
            {
                "zone": "Abs (Anti-Extension Core / Hollow Hold)",
                "zone_ua": "Прес (Анти-розгинання / Холлоу)",
                "patterns": ["Core"],
                "families": ["Anti-Extension Core"],
                "sets": 3, "reps": "10-12", "rest": 45, "superset": "Superset 5: E1"
            },
            {
                "zone": "Abs (Side Plank on Forearms / Rotation)",
                "zone_ua": "Прес (Бокова планка на передпліччях / Ротація)",
                "patterns": ["Core"],
                "families": ["Lateral Core & Adductor", "Rotational Core", "Lateral Core & Hip Abduction"],
                "sets": 3, "reps": "10-12 each", "rest": 45, "superset": "Superset 5: E2"
            }
        ]
    },

    # DAY 3: Dedicated Abs, Deep Core, Waist & Pelvic Stabilizers (10 Exercises)
    {
        "day_index": 2,
        "day_label": "Day 3: Dedicated Abs, Deep Core, Waist & Pelvic Stabilizers (10 Exercises)",
        "day_label_ua": "День 3: Прес, Глибокий Кор, Тонка Талія та Тазове Дно (10 вправ)",
        "description_en": "Precision core architecture: transverse abdominis, waist narrowing anti-rotation, pelvic stability, strictly zero wrist loading and zero doming.",
        "description_ua": "Ювелірна робота над кором: поперечний м'яз живота, звуження талії без бічних нахилів, стабільність тазу та розвантаження зап'ясть.",
        "slots": [
            # Superset 1: Upper Rectus Abdominis + Deep Transverse Abdominis Activation
            {
                "zone": "Core (Controlled Upper Ab Curl / Reach)",
                "zone_ua": "Кор (Контрольовані скручування з тягою до стелі)",
                "patterns": ["Core"],
                "families": ["Anti-Extension Core", "Dynamic Core / Hip Flexion"],
                "sets": 3, "reps": "12-15", "rest": 45, "superset": "Superset 1: A1"
            },
            {
                "zone": "Core (Dead Bug with Glued Lumbar Spine)",
                "zone_ua": "Кор (Dead Bug з притиснутим попереком до підлоги)",
                "patterns": ["Core"],
                "families": ["Anti-Extension Core", "Cross-Body Posterior Stability"],
                "sets": 3, "reps": "10-12 each", "rest": 45, "superset": "Superset 1: A2"
            },
            # Superset 2: Anti-Rotation Core / Pallof Press + Obliques / Waist Narrowing
            {
                "zone": "Waist (Standing Band Pallof Press)",
                "zone_ua": "Талія (Стоячи: жим Паллофа з гумою - анти-ротація)",
                "patterns": ["Core"],
                "families": ["Anti-Rotation Core"],
                "sets": 3, "reps": "10-12 each", "rest": 45, "superset": "Superset 2: B1"
            },
            {
                "zone": "Waist (Standing Band Waist Pull / Towel Woodchop)",
                "zone_ua": "Талія (Тяга гуми на талію без обтяження / Дроворуб)",
                "patterns": ["Core"],
                "families": ["Anti-Rotation Core", "Rotational Core"],
                "sets": 3, "reps": "12-15 each", "rest": 45, "superset": "Superset 2: B2"
            },
            # Superset 3: Lower Rectus / Pelvic Tilt + Deep Core
            {
                "zone": "Lower Abs (Reverse Pelvic Tuck / Floor Leg Drops)",
                "zone_ua": "Низ живота (Зворотні скручування тазу / Опускання ніг)",
                "patterns": ["Core"],
                "families": ["Dynamic Core / Hip Flexion", "Anti-Extension Core"],
                "sets": 3, "reps": "10-12", "rest": 45, "superset": "Superset 3: C1"
            },
            {
                "zone": "Deep Core (Single-Leg Glute Bridge with Core Exhale)",
                "zone_ua": "Глибокий кор (Одноногий міст з видихом та втягуванням)",
                "patterns": ["Hinge", "Core"],
                "families": ["Glute Bridge / Thrust", "Cross-Body Posterior Stability"],
                "sets": 3, "reps": "10-12 each", "rest": 45, "superset": "Superset 3: C2"
            },
            # Superset 4: Lateral Core / Forearm Side Plank variations + Anti-Extension
            {
                "zone": "Lateral Core (Forearm Side Plank with Hip Lift)",
                "zone_ua": "Боковий кор (Бокова планка на передпліччі з підйомом тазу)",
                "patterns": ["Core"],
                "families": ["Lateral Core & Adductor", "Lateral Core & Hip Abduction"],
                "sets": 3, "reps": "10-12 each", "rest": 45, "superset": "Superset 4: D1"
            },
            {
                "zone": "Deep Core (Forearm Towel / Slider Body Saw)",
                "zone_ua": "Глибокий кор (Планка-пила на передпліччях з рушником)",
                "patterns": ["Core"],
                "families": ["Anti-Extension Core"],
                "sets": 3, "reps": "10-12", "rest": 45, "superset": "Superset 4: D2"
            },
            # Superset 5: Pelvic Stabilizers / Transverse Abdominis
            {
                "zone": "Pelvic Floor (Adductor Squeeze Bridge with Exhale)",
                "zone_ua": "Тазове дно (Сідничний міст зі стисканням м'яча/рушника)",
                "patterns": ["Hinge", "Squat"],
                "families": ["Glute Bridge / Thrust", "Adductor Isolation"],
                "sets": 3, "reps": "12-15", "rest": 45, "superset": "Superset 5: E1"
            },
            {
                "zone": "Core Finish (Forearm Plank Toe Taps / Sliders)",
                "zone_ua": "Фінішер кору (Торкання носками на передпліччях / Слайдери)",
                "patterns": ["Core"],
                "families": ["Anti-Extension Core", "Anti-Rotation Core"],
                "sets": 3, "reps": "12-15 each", "rest": 45, "superset": "Superset 5: E2"
            }
        ]
    },

    # DAY 4: Glutes + Hamstrings + "Hip Dips / Ушки" (Gluteus Medius) + Core
    {
        "day_index": 3,
        "day_label": "Day 4: Glutes + Hamstrings + 'Hip Dips / Ушки' + Core (5 Supersets)",
        "day_label_ua": "День 4: Сідниці + Біцепс стегна + 'Вушка' (Середній сідничний) + Кор",
        "description_en": "Targeted posterior chain hypertrophy: 3-plane glute activation, gluteus medius sculpting, hamstring curls, and pelvic stability.",
        "description_ua": "Сфокусоване тренування задньої поверхні: сідниці у 3 площинах, усунення 'вушок', згинання стегна та стабільність тазу.",
        "slots": [
            # Superset 1: Glute Bridge / Hip Thrust from Couch/Bench + Single-Leg Hip Thrust
            {
                "zone": "Glutes (Couch / Bench Hip Thrust)",
                "zone_ua": "Сідниці (Сідничний міст з опорою спини на диван)",
                "patterns": ["Hinge"],
                "families": ["Glute Bridge / Thrust"],
                "sets": 3, "reps": "10-12", "rest": 60, "superset": "Superset 1: A1"
            },
            {
                "zone": "Glutes (Single-Leg Hip Thrust / Glute Bridge)",
                "zone_ua": "Сідниці (Одноногий сідничний міст)",
                "patterns": ["Hinge"],
                "families": ["Glute Bridge / Thrust", "Unilateral Hip Hinge"],
                "sets": 3, "reps": "8-10 each", "rest": 60, "superset": "Superset 1: A2"
            },
            # Superset 2: Romanian Deadlift + Hamstring Curl (Sliders/Towel/TRX)
            {
                "zone": "Hamstrings (Romanian Deadlift with Dumbbells / Band)",
                "zone_ua": "Біцепс стегна (Румунська тяга з гантелями / гумою)",
                "patterns": ["Hinge"],
                "families": ["Bilateral Hip Hinge", "Unilateral Hip Hinge"],
                "sets": 3, "reps": "10-12", "rest": 60, "superset": "Superset 2: B1"
            },
            {
                "zone": "Hamstrings (Slider / Towel / Ball Hamstring Curls)",
                "zone_ua": "Біцепс стегна (Згинання ніг з рушником / слайдерами)",
                "patterns": ["Hinge"],
                "families": ["Posterior Knee Flexion"],
                "sets": 3, "reps": "10-12", "rest": 60, "superset": "Superset 2: B2"
            },
            # Superset 3: Reverse Lunges + Bulgarian Split Squat / TRX Assisted
            {
                "zone": "Glutes & Hamstrings (Deficit / Reverse Lunge)",
                "zone_ua": "Сідниці (Зворотні випади з нахилом корпусу)",
                "patterns": ["Lunge"],
                "families": ["Unilateral Knee Dominant", "Compound Combo Hybrid"],
                "sets": 3, "reps": "10-12 each", "rest": 60, "superset": "Superset 3: C1"
            },
            {
                "zone": "Glutes (Bulgarian Split Squat on Couch)",
                "zone_ua": "Сідниці (Болгарські випади з ногою на дивані)",
                "patterns": ["Lunge", "Squat"],
                "families": ["Unilateral Knee Dominant", "Unilateral Hip Hinge"],
                "sets": 3, "reps": "8-10 each", "rest": 60, "superset": "Superset 3: C2"
            },
            # Superset 4: Gluteus Medius & "Hip Dips" (Clamshell / Lateral Abduction / Curtsy) + Frog Pumps
            {
                "zone": "Gluteus Medius (Side-Lying Band Clamshell / Lateral Kick)",
                "zone_ua": "Середній сідничний / 'Вушка' (Клемшел з гумою / Відведення ноги)",
                "patterns": ["Squat", "Hinge"],
                "families": ["Hip Abduction / Stability", "Lateral Knee Dominant"],
                "sets": 3, "reps": "15-20 each", "rest": 45, "superset": "Superset 4: D1"
            },
            {
                "zone": "Glute Burnout (Frog Pumps with Soles Together)",
                "zone_ua": "Сідниці пампінг (Frog Pumps зі стопами разом)",
                "patterns": ["Hinge"],
                "families": ["Glute Bridge / Thrust", "Glute Isolation"],
                "sets": 3, "reps": "15-20", "rest": 45, "superset": "Superset 4: D2"
            },
            # Superset 5: Deep Core / Pelvic Floor
            {
                "zone": "Deep Core (Dead Bug / Transverse Abdominis)",
                "zone_ua": "Глибокий кор (Dead Bug з фіксацією та видихом)",
                "patterns": ["Core"],
                "families": ["Anti-Extension Core", "Cross-Body Posterior Stability"],
                "sets": 3, "reps": "10-12 each", "rest": 45, "superset": "Superset 5: E1"
            },
            {
                "zone": "Deep Core (Forearm Side Plank with Top Leg Pulse)",
                "zone_ua": "Кор (Бокова планка на передпліччі з відведенням ноги)",
                "patterns": ["Core"],
                "families": ["Lateral Core & Adductor", "Lateral Core & Hip Abduction"],
                "sets": 3, "reps": "10-12 each", "rest": 45, "superset": "Superset 5: E2"
            }
        ]
    },

    # DAY 5: Quads + Inner Thighs (Adductors) + Calves & Ankle Pumps + Core
    {
        "day_index": 4,
        "day_label": "Day 5: Quads + Inner Thighs + Calves & Ankle Pumps + Core (5 Supersets)",
        "day_label_ua": "День 5: Квадрицепси + Внутрішня поверхня стегна + Литки + Кор",
        "description_en": "Lower body balance session: quad definition, adductor firmness (inner thighs), calf venous pump for anti-edema, and core.",
        "description_ua": "Баланс ніг: тонус квадрицепсів, підтягнута внутрішня частина стегон, лімфодренаж литок та міцний кор.",
        "slots": [
            # Superset 1: Goblet Squat / Sumo Squat + Lateral / Cossack Squat
            {
                "zone": "Quads & Glutes (Goblet / Sumo Squat with Dumbbell)",
                "zone_ua": "Квадрицепси та сідниці (Кубковий / Сумо присед з гантеллю)",
                "patterns": ["Squat"],
                "families": ["Bilateral Knee Dominant"],
                "sets": 3, "reps": "10-12", "rest": 60, "superset": "Superset 1: A1"
            },
            {
                "zone": "Inner Thighs (Cossack / Lateral Slider Squat)",
                "zone_ua": "Внутрішня частина стегна (Козацький присед / Боковий слайд)",
                "patterns": ["Squat", "Lunge"],
                "families": ["Lateral Knee Dominant", "Multi-Planar Knee Dominant"],
                "sets": 3, "reps": "10-12 each", "rest": 60, "superset": "Superset 1: A2"
            },
            # Superset 2: Step-Ups (Couch/Chair) + Copenhagen Plank / Ball Squeeze
            {
                "zone": "Quads & Glutes (Step-Ups on Couch / Chair)",
                "zone_ua": "Ноги (Зашагування на диван / стілець)",
                "patterns": ["Squat", "Lunge"],
                "families": ["Unilateral Knee Dominant"],
                "sets": 3, "reps": "10-12 each", "rest": 60, "superset": "Superset 2: B1"
            },
            {
                "zone": "Inner Thighs (Copenhagen Side Plank on Forearms / Ball Squeeze)",
                "zone_ua": "Внутрішня частина стегна (Копенгагенська планка / Стискання м'яча)",
                "patterns": ["Core", "Squat"],
                "families": ["Lateral Core & Adductor", "Adductor Isolation"],
                "sets": 3, "reps": "20-30s / 15 reps", "rest": 45, "superset": "Superset 2: B2"
            },
            # Superset 3: Sissy Squat / Quad Isolation + Adductor Squeeze Bridge
            {
                "zone": "Quads (Sissy Squat Bodyweight / Wall Chair Hold)",
                "zone_ua": "Квадрицепси (Сіссі-присед біля стіни / Стільчик)",
                "patterns": ["Squat"],
                "families": ["Quad Isolation", "Bilateral Knee Dominant"],
                "sets": 3, "reps": "10-12", "rest": 45, "superset": "Superset 3: C1"
            },
            {
                "zone": "Inner Thighs (Supine Towel / Pillow Squeeze Bridge)",
                "zone_ua": "Внутрішня частина стегна (Міст зі стисканням подушки/рушника)",
                "patterns": ["Hinge", "Squat"],
                "families": ["Glute Bridge / Thrust", "Adductor Isolation"],
                "sets": 3, "reps": "12-15", "rest": 45, "superset": "Superset 3: C2"
            },
            # Superset 4: Standing Calf Raises + Seated Tibialis / Ankle Pumps
            {
                "zone": "Calves (Standing Calf Raise with Elevated Toes & 2s Pause)",
                "zone_ua": "Литки (Підйоми на носки з книги/блоку з паузою вгорі 2с)",
                "patterns": ["Squat", "Carry"],
                "families": ["Ankle Plantarflexion"],
                "sets": 3, "reps": "15-20", "rest": 45, "superset": "Superset 4: D1"
            },
            {
                "zone": "Ankles & Tibialis (Ankle Dorsiflexion Pump / Towel Scrunch)",
                "zone_ua": "Гомілкостоп (Підйоми носків сидячи / Лімфодренажна помпа)",
                "patterns": ["Squat", "Mobility"],
                "families": ["Ankle Plantarflexion", "Ankle Mobility"],
                "sets": 3, "reps": "20-25", "rest": 30, "superset": "Superset 4: D2"
            },
            # Superset 5: Abs / Anti-Extension
            {
                "zone": "Abs (Forearm Hollow Hold / Low Plank)",
                "zone_ua": "Прес (Холлоу на підлозі / Низька планка на ліктях)",
                "patterns": ["Core"],
                "families": ["Anti-Extension Core"],
                "sets": 3, "reps": "10-12", "rest": 45, "superset": "Superset 5: E1"
            },
            {
                "zone": "Abs (Towel Knee Tucks on Forearms)",
                "zone_ua": "Прес (Підтягування колін з рушником на ліктях)",
                "patterns": ["Core"],
                "families": ["Dynamic Core / Hip Flexion", "Anti-Extension Core"],
                "sets": 3, "reps": "10-12", "rest": 45, "superset": "Superset 5: E2"
            }
        ]
    }
]


# ---------------------------------------------------------------------------
# 3. SPECIAL MONO-DAYS (On-Demand Targeted Power Sessions)
# ---------------------------------------------------------------------------
MONO_DAY_TEMPLATES = {
    # Special 13-Exercise Lower Body & Waist Sculpt (Gold Standard)
    "special_13_lower_body": {
        "id": "special_13_lower_body",
        "title_en": "✨ Special 13-Exercise Lower Body & Waist Sculpt",
        "title_ua": "✨ Спеціальний комплекс 13 вправ: Сідниці, Ноги та Вузька Талія",
        "description_en": "Our gold-standard 13-exercise marathon session targeting glutes in 3 planes, hamstring curves, adductor firmness, calf lymphatic pumping, and waist cinching.",
        "description_ua": "Золотий стандарт на 13 вправ: сідниці у 3 площинах, рельєф задньої поверхні, підтягнута внутрішня частина стегон, лімфодренаж литок та тонка талія.",
        "target_duration_minutes": 65,
        "slots": [
            {"zone": "Glutes (Couch Hip Thrust)", "zone_ua": "Сідниці (Сідничний міст від дивану)", "patterns": ["Hinge"], "families": ["Glute Bridge / Thrust"], "sets": 3, "reps": "10-12", "rest": 60, "superset": "Superset 1: A1"},
            {"zone": "Glutes (Single-Leg Hip Thrust)", "zone_ua": "Сідниці (Одноногий сідничний міст)", "patterns": ["Hinge"], "families": ["Glute Bridge / Thrust", "Unilateral Hip Hinge"], "sets": 3, "reps": "8-10 each", "rest": 60, "superset": "Superset 1: A2"},
            {"zone": "Hamstrings (Banded Romanian Deadlift)", "zone_ua": "Біцепс стегна (Румунська тяга з гумою)", "patterns": ["Hinge"], "families": ["Bilateral Hip Hinge", "Unilateral Hip Hinge"], "sets": 3, "reps": "10-12", "rest": 60, "superset": "Superset 2: B1"},
            {"zone": "Hamstrings (Slider / Towel Curls)", "zone_ua": "Біцепс стегна (Згинання з рушником)", "patterns": ["Hinge"], "families": ["Posterior Knee Flexion"], "sets": 3, "reps": "10-12", "rest": 60, "superset": "Superset 2: B2"},
            {"zone": "Glutes & Quads (Bulgarian Split Squat)", "zone_ua": "Сідниці (Болгарські випади)", "patterns": ["Lunge"], "families": ["Unilateral Knee Dominant"], "sets": 3, "reps": "8-10 each", "rest": 60, "superset": "Superset 3: C1"},
            {"zone": "Gluteus Medius (Curtsy Lunge / Deficit)", "zone_ua": "Середній сідничний (Діагональні реверанс-випади)", "patterns": ["Lunge"], "families": ["Lateral Knee Dominant", "Multi-Planar Knee Dominant"], "sets": 3, "reps": "10-12 each", "rest": 60, "superset": "Superset 3: C2"},
            {"zone": "Gluteus Medius / 'Hip Dips' (Side-Lying Band Clamshell)", "zone_ua": "Середній сідничний / 'Вушка' (Клемшел з гумою)", "patterns": ["Squat", "Hinge"], "families": ["Hip Abduction / Stability"], "sets": 3, "reps": "15-20 each", "rest": 45, "superset": "Superset 4: D1"},
            {"zone": "Inner Thighs (Sumo Squat with 3s Pause)", "zone_ua": "Внутрішня частина стегна (Сумо присед з паузою 3с)", "patterns": ["Squat"], "families": ["Bilateral Knee Dominant"], "sets": 3, "reps": "10-12", "rest": 60, "superset": "Superset 4: D2"},
            {"zone": "Inner Thighs (Adductor Ball/Towel Squeeze Bridge)", "zone_ua": "Внутрішня частина стегна (Міст зі стисканням м'яча)", "patterns": ["Hinge", "Squat"], "families": ["Glute Bridge / Thrust", "Adductor Isolation"], "sets": 3, "reps": "12-15", "rest": 45, "superset": "Superset 5: E1"},
            {"zone": "Calves & Lymph (Standing Calf Raise on Block)", "zone_ua": "Литки та лімфодренаж (Підйоми на носок з блоку)", "patterns": ["Squat"], "families": ["Ankle Plantarflexion"], "sets": 3, "reps": "15-20", "rest": 45, "superset": "Superset 5: E2"},
            {"zone": "Deep Core (Dead Bug Glued Lower Back)", "zone_ua": "Глибокий кор (Dead Bug з притиснутим попереком)", "patterns": ["Core"], "families": ["Anti-Extension Core"], "sets": 3, "reps": "10-12 each", "rest": 45, "superset": "Finisher: F1"},
            {"zone": "Waist (Forearm Side Plank with Hip Lift)", "zone_ua": "Талія (Бокова планка на передпліччі)", "patterns": ["Core"], "families": ["Lateral Core & Adductor", "Lateral Core & Hip Abduction"], "sets": 3, "reps": "10-12 each", "rest": 45, "superset": "Finisher: F2"},
            {"zone": "Waist Narrowing (Standing Band Waist Pallof Pull)", "zone_ua": "Звуження талії (Тяга гуми на талію стоячи)", "patterns": ["Core"], "families": ["Anti-Rotation Core"], "sets": 3, "reps": "12-15 each", "rest": 45, "superset": "Finisher: F3"}
        ]
    },

    # Pure Back & Scapular Posture (10 Exercises)
    "pure_back": {
        "id": "pure_back",
        "title_en": "🦅 Pure Back & Scapular Posture",
        "title_ua": "🦅 Королівська Спина та Розкриття Плечей (10 вправ)",
        "description_en": "Dedicated posterior torso training: scapular stabilization, lat development, rear deltoids, and deep postural anti-extension core.",
        "description_ua": "Акцент на спину та поставу: стабілізація лопаток, розвиток найширших, задня дельта та міцний кор.",
        "target_duration_minutes": 55,
        "slots": [
            {"zone": "Back (TRX Inverted Row)", "zone_ua": "Спина (Тяга в TRX)", "patterns": ["Pull"], "families": ["Horizontal Pull Suspension", "Horizontal Pull Bilateral"], "sets": 3, "reps": "10-12", "rest": 60, "superset": "Superset 1: A1"},
            {"zone": "Back (Dumbbell Dual Row)", "zone_ua": "Спина (Тяга двох гантелей до поясу)", "patterns": ["Pull"], "families": ["Horizontal Pull Bilateral"], "sets": 3, "reps": "10-12", "rest": 60, "superset": "Superset 1: A2"},
            {"zone": "Back (Unilateral Dumbbell Row with Bench)", "zone_ua": "Спина (Одноручна тяга з упором на лаву)", "patterns": ["Pull"], "families": ["Horizontal Pull Unilateral"], "sets": 3, "reps": "10-12 each", "rest": 60, "superset": "Superset 2: B1"},
            {"zone": "Scapular (Band Face Pull with External Rotation)", "zone_ua": "Лопатки (Фейспул з гумою та розворотом)", "patterns": ["Pull"], "families": ["Posterior Shoulder / Scapular"], "sets": 3, "reps": "12-15", "rest": 45, "superset": "Superset 2: B2"},
            {"zone": "Lats (Straight-Arm Pulldown with Band)", "zone_ua": "Найширші (Тяга прямими руками вниз з гумою)", "patterns": ["Pull"], "families": ["Vertical Pull / Extension"], "sets": 3, "reps": "10-12", "rest": 45, "superset": "Superset 3: C1"},
            {"zone": "Lats (Couch Pullover with Dumbbell)", "zone_ua": "Найширші (Пуловер з гантеллю через диван)", "patterns": ["Pull"], "families": ["Vertical Pull / Extension"], "sets": 3, "reps": "10-12", "rest": 45, "superset": "Superset 3: C2"},
            {"zone": "Rear Delts (Prone Rear Delt Raise / Y-Raise)", "zone_ua": "Задня дельта (Підйоми Y лежачи / Махи)", "patterns": ["Pull"], "families": ["Posterior Shoulder / Scapular"], "sets": 3, "reps": "12-15", "rest": 45, "superset": "Superset 4: D1"},
            {"zone": "Upper Back (Band Pull-Apart with 2s Squeeze)", "zone_ua": "Верх спини (Розведення гуми з паузою 2с)", "patterns": ["Pull"], "families": ["Posterior Shoulder / Scapular"], "sets": 3, "reps": "15-20", "rest": 45, "superset": "Superset 4: D2"},
            {"zone": "Core Posture (Dead Bug Anti-Extension)", "zone_ua": "Кор (Dead Bug для фіксації постави)", "patterns": ["Core"], "families": ["Anti-Extension Core"], "sets": 3, "reps": "10-12 each", "rest": 45, "superset": "Superset 5: E1"},
            {"zone": "Core Posture (Forearm Side Plank Posture Hold)", "zone_ua": "Кор (Бокова планка на передпліччі)", "patterns": ["Core"], "families": ["Lateral Core & Adductor"], "sets": 3, "reps": "10-12 each", "rest": 45, "superset": "Superset 5: E2"}
        ]
    },

    # Pure Glutes & Legs Hypertrophy (10 Exercises)
    "pure_glutes_legs": {
        "id": "pure_glutes_legs",
        "title_en": "🍑 Pure Glutes & Legs Hypertrophy",
        "title_ua": "🍑 Максимальна Гіпертрофія Сідниць та Ніг (10 вправ)",
        "description_en": "Intense lower body session targeting maximum glute roundness, hamstring sweeps, quad power, and calf definition.",
        "description_ua": "Інтенсивне тренування низу тіла: максимальний об'єм сідниць, рельєф стегон та литок.",
        "target_duration_minutes": 55,
        "slots": [
            {"zone": "Glutes (Heavy Couch Hip Thrust)", "zone_ua": "Сідниці (Важкий сідничний міст від дивану)", "patterns": ["Hinge"], "families": ["Glute Bridge / Thrust"], "sets": 4, "reps": "8-10", "rest": 60, "superset": "Superset 1: A1"},
            {"zone": "Glutes (Single-Leg Elevated Glute Bridge)", "zone_ua": "Сідниці (Одноногий міст з піднятою ногою)", "patterns": ["Hinge"], "families": ["Glute Bridge / Thrust", "Unilateral Hip Hinge"], "sets": 3, "reps": "8-10 each", "rest": 60, "superset": "Superset 1: A2"},
            {"zone": "Hamstrings (Romanian Deadlift)", "zone_ua": "Біцепс стегна (Румунська тяга)", "patterns": ["Hinge"], "families": ["Bilateral Hip Hinge"], "sets": 3, "reps": "8-12", "rest": 60, "superset": "Superset 2: B1"},
            {"zone": "Hamstrings (Slider / Towel Knee Flexion)", "zone_ua": "Біцепс стегна (Згинання ніг з рушником)", "patterns": ["Hinge"], "families": ["Posterior Knee Flexion"], "sets": 3, "reps": "10-12", "rest": 60, "superset": "Superset 2: B2"},
            {"zone": "Quads & Glutes (Bulgarian Split Squat)", "zone_ua": "Сідниці (Болгарські випади)", "patterns": ["Lunge"], "families": ["Unilateral Knee Dominant"], "sets": 3, "reps": "8-10 each", "rest": 60, "superset": "Superset 3: C1"},
            {"zone": "Quads (Goblet Squat with Slow Tempo)", "zone_ua": "Квадрицепси (Кубковий присед з повільним темпом)", "patterns": ["Squat"], "families": ["Bilateral Knee Dominant"], "sets": 3, "reps": "10-12", "rest": 60, "superset": "Superset 3: C2"},
            {"zone": "Gluteus Medius (Side-Lying Band Abduction)", "zone_ua": "Середній сідничний (Відведення ноги лежачи з гумою)", "patterns": ["Squat", "Hinge"], "families": ["Hip Abduction / Stability"], "sets": 3, "reps": "15-20 each", "rest": 45, "superset": "Superset 4: D1"},
            {"zone": "Glute Burnout (Frog Pumps)", "zone_ua": "Сідниці (Frog Pumps)", "patterns": ["Hinge"], "families": ["Glute Bridge / Thrust", "Glute Isolation"], "sets": 3, "reps": "15-20", "rest": 45, "superset": "Superset 4: D2"},
            {"zone": "Calves (Standing Calf Raise on Block)", "zone_ua": "Литки (Підйоми на носок з блоку)", "patterns": ["Squat"], "families": ["Ankle Plantarflexion"], "sets": 3, "reps": "15-20", "rest": 45, "superset": "Superset 5: E1"},
            {"zone": "Core Stability (Dead Bug with Exhale)", "zone_ua": "Кор (Dead Bug з фіксацією та видихом)", "patterns": ["Core"], "families": ["Anti-Extension Core"], "sets": 3, "reps": "10-12 each", "rest": 45, "superset": "Superset 5: E2"}
        ]
    },

    # Pure Core & Flat Stomach (10 Exercises)
    "pure_core": {
        "id": "pure_core",
        "title_en": "🧘 Pure Core, Flat Stomach & Waist",
        "title_ua": "🧘 Плоский Живіт, Тонка Талія та Глибокий Кор (10 вправ)",
        "description_en": "Zero-doming flat stomach sequence targeting the transverse abdominis, vacuum activation, pelvic stabilizers, and oblique contouring.",
        "description_ua": "Комплекс для плоского живота без домінгу та білої лінії: поперечний м'яз, вакуум, стабілізатори та контур талії.",
        "target_duration_minutes": 45,
        "slots": [
            {"zone": "Deep Core (Dead Bug Glued Spine)", "zone_ua": "Глибокий кор (Dead Bug з притиснутим попереком)", "patterns": ["Core"], "families": ["Anti-Extension Core"], "sets": 3, "reps": "10-12 each", "rest": 45, "superset": "Superset 1: A1"},
            {"zone": "Core (Controlled Upper Abdominal Curl)", "zone_ua": "Кор (Контрольовані скручування вгору)", "patterns": ["Core"], "families": ["Anti-Extension Core"], "sets": 3, "reps": "12-15", "rest": 45, "superset": "Superset 1: A2"},
            {"zone": "Waist (Standing Band Pallof Press)", "zone_ua": "Талія (Жим Паллофа стоячи з гумою)", "patterns": ["Core"], "families": ["Anti-Rotation Core"], "sets": 3, "reps": "10-12 each", "rest": 45, "superset": "Superset 2: B1"},
            {"zone": "Waist (Standing Band Waist Rotation Pull)", "zone_ua": "Талія (Тяга гуми на талію стоячи)", "patterns": ["Core"], "families": ["Anti-Rotation Core", "Rotational Core"], "sets": 3, "reps": "12-15 each", "rest": 45, "superset": "Superset 2: B2"},
            {"zone": "Lower Abs (Reverse Pelvic Curl on Floor)", "zone_ua": "Низ живота (Зворотні скручування тазу)", "patterns": ["Core"], "families": ["Dynamic Core / Hip Flexion"], "sets": 3, "reps": "10-12", "rest": 45, "superset": "Superset 3: C1"},
            {"zone": "Deep Core (Single-Leg Glute Bridge Exhale)", "zone_ua": "Глибокий кор (Одноногий міст з видихом)", "patterns": ["Hinge", "Core"], "families": ["Glute Bridge / Thrust"], "sets": 3, "reps": "10-12 each", "rest": 45, "superset": "Superset 3: C2"},
            {"zone": "Lateral Core (Forearm Side Plank with Hip Lift)", "zone_ua": "Боковий кор (Бокова планка на передпліччі)", "patterns": ["Core"], "families": ["Lateral Core & Adductor"], "sets": 3, "reps": "10-12 each", "rest": 45, "superset": "Superset 4: D1"},
            {"zone": "Deep Core (Forearm Towel / Slider Body Saw)", "zone_ua": "Глибокий кор (Планка-пила на передпліччях)", "patterns": ["Core"], "families": ["Anti-Extension Core"], "sets": 3, "reps": "10-12", "rest": 45, "superset": "Superset 4: D2"},
            {"zone": "Pelvic Floor (Adductor Squeeze Bridge)", "zone_ua": "Тазове дно (Сідничний міст зі стисканням м'яча)", "patterns": ["Hinge"], "families": ["Glute Bridge / Thrust", "Adductor Isolation"], "sets": 3, "reps": "12-15", "rest": 45, "superset": "Superset 5: E1"},
            {"zone": "Core Finish (Forearm Plank Toe Taps)", "zone_ua": "Фінішер (Торкання носками на передпліччях)", "patterns": ["Core"], "families": ["Anti-Extension Core", "Anti-Rotation Core"], "sets": 3, "reps": "12-15 each", "rest": 45, "superset": "Superset 5: E2"}
        ]
    }
}



# ---------------------------------------------------------------------------
# 3. MALE HYPERTROPHY 5-DAY ROLLING SPLIT QUEUE (5 Supersets x 2 Exercises = 10 Exercises)
# ---------------------------------------------------------------------------
MALE_SPLIT_TEMPLATES = [
    # DAY 1: Chest + Triceps + Core (5 Supersets / 10 Exercises)
    {
        "day_index": 0,
        "day_label": "Day 1: Chest + Triceps + Core (5 Supersets)",
        "day_label_ua": "День 1: Груди + Трицепс + Прес (5 Суперсетів)",
        "day_name_en": "Chest & Triceps Hypertrophy",
        "day_name_ua": "Гіпертрофія грудей та трицепса",
        "description_en": "Upper body push hypertrophy focusing on pectorals, triceps extension strength, and anti-extension core.",
        "description_ua": "Тренування жимових м'язів верху тіла: грудні, сила трицепса та анти-розгинання кору.",
        "slots": [
            {
                "zone": "Chest (Primary Flat Press)",
                "zone_ua": "Груди (Базовий горизонтальний жим)",
                "patterns": ["Push"],
                "families": ["Horizontal Push Bilateral", "Horizontal Push Unilateral"],
                "sets": 3, "reps": "8-10", "rest": 60, "superset": "Superset 1: A1"
            },
            {
                "zone": "Chest (Incline Press / Incline Flye)",
                "zone_ua": "Груди (Похилий жим / Розведення на верх грудей)",
                "patterns": ["Push"],
                "families": ["Horizontal Push Incline", "Chest Isolation", "Horizontal Push Bilateral"],
                "sets": 3, "reps": "10-12", "rest": 60, "superset": "Superset 1: A2"
            },
            {
                "zone": "Chest (Dips / Suspension Press)",
                "zone_ua": "Груди (Бруси / Віджимання в TRX)",
                "patterns": ["Push"],
                "families": ["Horizontal Push Suspension", "Horizontal Push Bodyweight", "Horizontal Push Resisted"],
                "sets": 3, "reps": "10-12", "rest": 60, "superset": "Superset 2: B1"
            },
            {
                "zone": "Chest (Cable / Band Flye)",
                "zone_ua": "Груди (Зведення в кросовері / з гумою)",
                "patterns": ["Push"],
                "families": ["Chest Isolation", "Chest Isolation Suspension"],
                "sets": 3, "reps": "12-15", "rest": 45, "superset": "Superset 2: B2"
            },
            {
                "zone": "Triceps (Close-Grip Press / Skull Crusher)",
                "zone_ua": "Трицепс (Французький жим / Вузький жим)",
                "patterns": ["Push"],
                "families": ["Elbow Extension", "Elbow Extension Suspension"],
                "sets": 3, "reps": "8-10", "rest": 60, "superset": "Superset 3: C1"
            },
            {
                "zone": "Triceps (Overhead Rope / Dumbbell Extension)",
                "zone_ua": "Трицепс (Французький жим з-за голови)",
                "patterns": ["Push"],
                "families": ["Elbow Extension", "Elbow Extension Suspension"],
                "sets": 3, "reps": "10-12", "rest": 45, "superset": "Superset 3: C2"
            },
            {
                "zone": "Triceps (Cable / Band Pushdown)",
                "zone_ua": "Трицепс (Розгинання на блоці / з гумою)",
                "patterns": ["Push"],
                "families": ["Elbow Extension", "Elbow Extension Suspension"],
                "sets": 3, "reps": "12-15", "rest": 45, "superset": "Superset 4: D1"
            },
            {
                "zone": "Triceps (Bench Dips / Kickbacks)",
                "zone_ua": "Трицепс (Зворотні віджимання від лави / Кикбеки)",
                "patterns": ["Push"],
                "families": ["Elbow Extension", "Elbow Extension Suspension"],
                "sets": 3, "reps": "12-15", "rest": 45, "superset": "Superset 4: D2"
            },
            {
                "zone": "Core (Anti-Extension / Hanging Knee Raise)",
                "zone_ua": "Прес (Підйоми колін у висі / Слайдер-пила)",
                "patterns": ["Core"],
                "families": ["Anti-Extension Core", "Dynamic Core / Hip Flexion"],
                "sets": 3, "reps": "10-12", "rest": 45, "superset": "Superset 5: E1"
            },
            {
                "zone": "Core (Anti-Rotation / Pallof Press)",
                "zone_ua": "Прес (Жим Паллофа / Ротації з гумою)",
                "patterns": ["Core"],
                "families": ["Anti-Rotation Core", "Rotational Core"],
                "sets": 3, "reps": "12-15 each", "rest": 45, "superset": "Superset 5: E2"
            }
        ]
    },

    # DAY 2: Back + Biceps + Core (5 Supersets / 10 Exercises)
    {
        "day_index": 1,
        "day_label": "Day 2: Back + Biceps + Core (5 Supersets)",
        "day_label_ua": "День 2: Спина + Біцепс + Прес (5 Суперсетів)",
        "day_name_en": "Back Width & Biceps Peak",
        "day_name_ua": "Ширина спини та пік біцепса",
        "description_en": "Posterior upper body hypertrophy: lats, rhomboids, rear delts, heavy elbow flexion, and deep core stability.",
        "description_ua": "Гіпертрофія спини та біцепса: найширші, ромбоподібні, задні дельти та стабілізація кору.",
        "slots": [
            {
                "zone": "Back (Heavy Horizontal Row)",
                "zone_ua": "Спина (Базова горизонтальна тяга штанги/гантелей)",
                "patterns": ["Pull"],
                "families": ["Horizontal Pull Bilateral", "Horizontal Pull Suspension"],
                "sets": 3, "reps": "8-10", "rest": 60, "superset": "Superset 1: A1"
            },
            {
                "zone": "Back (Unilateral Dumbbell Row)",
                "zone_ua": "Спина (Тяга гантелі однією рукою в нахилі)",
                "patterns": ["Pull"],
                "families": ["Horizontal Pull Unilateral"],
                "sets": 3, "reps": "8-10 each", "rest": 60, "superset": "Superset 1: A2"
            },
            {
                "zone": "Back (Vertical Lat Pulldown / Pull-Up)",
                "zone_ua": "Спина (Тяга верхнього блоку / Підтягування)",
                "patterns": ["Pull"],
                "families": ["Vertical Pull / Extension", "Vertical Pull Suspension", "Vertical Pull Bilateral"],
                "sets": 3, "reps": "8-12", "rest": 60, "superset": "Superset 2: B1"
            },
            {
                "zone": "Back & Scapula (Straight-Arm Pulldown / Pullover)",
                "zone_ua": "Спина (Пуловер прямими руками / Лопаткова тяга)",
                "patterns": ["Pull"],
                "families": ["Vertical Pull / Extension", "Posterior Shoulder / Scapular"],
                "sets": 3, "reps": "10-12", "rest": 45, "superset": "Superset 2: B2"
            },
            {
                "zone": "Rear Delts (Face Pull / Rear Delt Flye)",
                "zone_ua": "Задні дельти (Фейспул на блоці / Махи в нахилі)",
                "patterns": ["Pull"],
                "families": ["Posterior Shoulder / Scapular"],
                "sets": 3, "reps": "12-15", "rest": 45, "superset": "Superset 3: C1"
            },
            {
                "zone": "Biceps (Heavy Standing Barbell / Dumbbell Curl)",
                "zone_ua": "Біцепс (Підйом штанги/гантелей на біцепс стоячи)",
                "patterns": ["Pull"],
                "families": ["Elbow Flexion", "Elbow Flexion Suspension"],
                "sets": 3, "reps": "8-10", "rest": 60, "superset": "Superset 3: C2"
            },
            {
                "zone": "Biceps (Incline / Concentration Curl)",
                "zone_ua": "Біцепс (Згинання на похилій лаві / Концентрований згин)",
                "patterns": ["Pull"],
                "families": ["Elbow Flexion", "Elbow Flexion Suspension"],
                "sets": 3, "reps": "10-12", "rest": 45, "superset": "Superset 4: D1"
            },
            {
                "zone": "Biceps (Hammer Neutral Grip Curl)",
                "zone_ua": "Біцепс (Молоткові згинання / Хват молот)",
                "patterns": ["Pull"],
                "families": ["Elbow Flexion", "Elbow Flexion Suspension"],
                "sets": 3, "reps": "10-12", "rest": 45, "superset": "Superset 4: D2"
            },
            {
                "zone": "Core (Anti-Extension / Dead Bug / Wheel Rollout)",
                "zone_ua": "Прес (Дед Баг з натягом / Ролик для преса)",
                "patterns": ["Core"],
                "families": ["Anti-Extension Core"],
                "sets": 3, "reps": "10-12", "rest": 45, "superset": "Superset 5: E1"
            },
            {
                "zone": "Core & Grip (Loaded Carry / Oblique Hold)",
                "zone_ua": "Кор та хват (Прогулянка фермера / Бокова планка)",
                "patterns": ["Carry", "Core"],
                "families": ["Unilateral Loaded Carry", "Bilateral Loaded Carry", "Lateral Core & Hip Abduction"],
                "sets": 3, "reps": "40s walk / 12 reps", "rest": 45, "superset": "Superset 5: E2"
            }
        ]
    },

    # DAY 3: Legs (Quads + Hamstrings + Calves + Core) (5 Supersets / 10 Exercises)
    {
        "day_index": 2,
        "day_label": "Day 3: Legs & Calves (5 Supersets)",
        "day_label_ua": "День 3: Ноги та литки (5 Суперсетів)",
        "day_name_en": "Lower Body Power & Mass",
        "day_name_ua": "Сила та маса нижньої частини тіла",
        "description_en": "Comprehensive leg hypertrophy combining quad drive, posterior chain hinges, and ankle/calf loading.",
        "description_ua": "Комплексне тренування ніг: квадрицепси, задня поверхня стегна, сідниці та литки.",
        "slots": [
            {
                "zone": "Quads (Primary Heavy Squat)",
                "zone_ua": "Квадрицепси (Базовий присед зі штангою / гантелями)",
                "patterns": ["Squat"],
                "families": ["Bilateral Knee Dominant"],
                "sets": 3, "reps": "8-10", "rest": 75, "superset": "Superset 1: A1"
            },
            {
                "zone": "Quads (Leg Extension Machine / Sissy Squat)",
                "zone_ua": "Квадрицепси (Розгинання ніг у тренажері / Сіссі)",
                "patterns": ["Squat"],
                "families": ["Quad Isolation", "Bilateral Knee Dominant"],
                "sets": 3, "reps": "10-12", "rest": 60, "superset": "Superset 1: A2"
            },
            {
                "zone": "Quads & Glutes (Bulgarian Split Squat / Walking Lunge)",
                "zone_ua": "Квадрицепси та сідниці (Болгарський спліт-присед / Випади)",
                "patterns": ["Lunge", "Squat"],
                "families": ["Unilateral Knee Dominant", "Compound Combo Hybrid"],
                "sets": 3, "reps": "8-10 each", "rest": 60, "superset": "Superset 2: B1"
            },
            {
                "zone": "Hamstrings (Romanian Deadlift)",
                "zone_ua": "Біцепс стегна (Румунська тяга зі штангою/гантелями)",
                "patterns": ["Hinge"],
                "families": ["Bilateral Hip Hinge", "Unilateral Hip Hinge"],
                "sets": 3, "reps": "8-10", "rest": 60, "superset": "Superset 2: B2"
            },
            {
                "zone": "Hamstrings (Leg Curl Machine / Slider Curl)",
                "zone_ua": "Біцепс стегна (Згинання ніг лежачи/сидячи)",
                "patterns": ["Hinge"],
                "families": ["Posterior Knee Flexion"],
                "sets": 3, "reps": "10-12", "rest": 60, "superset": "Superset 3: C1"
            },
            {
                "zone": "Glutes (Barbell / Dumbbell Hip Thrust)",
                "zone_ua": "Сідниці (Сідничний міст зі штангою / гантеллю)",
                "patterns": ["Hinge"],
                "families": ["Glute Bridge / Thrust"],
                "sets": 3, "reps": "8-10", "rest": 60, "superset": "Superset 3: C2"
            },
            {
                "zone": "Calves (Standing Calf Raise)",
                "zone_ua": "Литки (Підйоми на носки стоячи зі штангою/гантелями)",
                "patterns": ["Squat"],
                "families": ["Ankle Plantarflexion"],
                "sets": 3, "reps": "12-15", "rest": 45, "superset": "Superset 4: D1"
            },
            {
                "zone": "Calves & Tibialis (Seated Calf Raise / Tibialis Pulses)",
                "zone_ua": "Литки та гомілка (Підйоми на носки сидячи / Тібіаліс)",
                "patterns": ["Squat"],
                "families": ["Ankle Plantarflexion"],
                "sets": 3, "reps": "15-20", "rest": 45, "superset": "Superset 4: D2"
            },
            {
                "zone": "Core (Abdominal Cable Crunch / Hanging Leg Raise)",
                "zone_ua": "Прес (Скручування на блоці / Підйом ніг)",
                "patterns": ["Core"],
                "families": ["Dynamic Core / Hip Flexion", "Anti-Extension Core"],
                "sets": 3, "reps": "10-12", "rest": 45, "superset": "Superset 5: E1"
            },
            {
                "zone": "Core (Forearm Plank Saw / Side Plank Hold)",
                "zone_ua": "Кор (Планка-пила на передпліччях / Бокова планка)",
                "patterns": ["Core"],
                "families": ["Anti-Extension Core", "Lateral Core & Hip Abduction"],
                "sets": 3, "reps": "45s hold / 12 reps", "rest": 45, "superset": "Superset 5: E2"
            }
        ]
    },

    # DAY 4: Shoulders & Traps + Upper Core (5 Supersets / 10 Exercises)
    {
        "day_index": 3,
        "day_label": "Day 4: Shoulders & Traps + Upper Core (5 Supersets)",
        "day_label_ua": "День 4: Плечі та трапеції + Кор (5 Суперсетів)",
        "day_name_en": "3D Shoulders & Traps",
        "day_name_ua": "3D Дельти та трапеції",
        "description_en": "Deltoid boulder development across anterior, lateral, and posterior heads plus trapezius thickness.",
        "description_ua": "Розвиток дельтоподібних м'язів у всіх трьох пучках плюс товщина трапецій та кор.",
        "slots": [
            {
                "zone": "Shoulders (Heavy Overhead Press)",
                "zone_ua": "Плечі (Армійський жим стоячи / Жим гантелей сидячи)",
                "patterns": ["Push"],
                "families": ["Vertical Push Bilateral", "Vertical Push Unilateral"],
                "sets": 3, "reps": "8-10", "rest": 60, "superset": "Superset 1: A1"
            },
            {
                "zone": "Shoulders (Dumbbell / Cable Lateral Raise)",
                "zone_ua": "Плечі (Махи гантелями в сторони / Кросовер)",
                "patterns": ["Push"],
                "families": ["Shoulder Isolation"],
                "sets": 3, "reps": "12-15", "rest": 45, "superset": "Superset 1: A2"
            },
            {
                "zone": "Shoulders (Arnold Press / Seated DB Press)",
                "zone_ua": "Плечі (Жим Арнольда / Жим гантелей з поворотом)",
                "patterns": ["Push"],
                "families": ["Vertical Push Bilateral", "Vertical Push Unilateral"],
                "sets": 3, "reps": "10-12", "rest": 60, "superset": "Superset 2: B1"
            },
            {
                "zone": "Shoulders (Upright Row / Cable Lateral)",
                "zone_ua": "Плечі (Тяга штанги до підборіддя / Протяжка)",
                "patterns": ["Pull", "Push"],
                "families": ["Vertical Pull Bilateral", "Shoulder Isolation"],
                "sets": 3, "reps": "10-12", "rest": 45, "superset": "Superset 2: B2"
            },
            {
                "zone": "Rear Delts (Incline Rear Flye / Band Pull-Apart)",
                "zone_ua": "Задні дельти (Махи в нахилі на лаві / Розтягування гуми)",
                "patterns": ["Pull"],
                "families": ["Posterior Shoulder / Scapular"],
                "sets": 3, "reps": "12-15", "rest": 45, "superset": "Superset 3: C1"
            },
            {
                "zone": "Rear Delts (Face Pull with High Elbows)",
                "zone_ua": "Задні дельти (Фейспул з канатом та розведенням)",
                "patterns": ["Pull"],
                "families": ["Posterior Shoulder / Scapular"],
                "sets": 3, "reps": "12-15", "rest": 45, "superset": "Superset 3: C2"
            },
            {
                "zone": "Traps (Heavy Dumbbell / Barbell Shrugs)",
                "zone_ua": "Трапеції (Шраги з гантелями / штангою)",
                "patterns": ["Pull"],
                "families": ["Vertical Pull Bilateral", "Posterior Shoulder / Scapular"],
                "sets": 3, "reps": "10-12", "rest": 45, "superset": "Superset 4: D1"
            },
            {
                "zone": "Shoulders (Front Plate / Dumbbell Raise)",
                "zone_ua": "Плечі (Підйоми перед собою з диском/гантелями)",
                "patterns": ["Push"],
                "families": ["Shoulder Isolation"],
                "sets": 3, "reps": "12-15", "rest": 45, "superset": "Superset 4: D2"
            },
            {
                "zone": "Core (Rotational Cable Chop / Woodchop)",
                "zone_ua": "Прес (Дроворуб на блоці / Ротація корпусу)",
                "patterns": ["Core"],
                "families": ["Rotational Core", "Anti-Rotation Core"],
                "sets": 3, "reps": "10-12 each", "rest": 45, "superset": "Superset 5: E1"
            },
            {
                "zone": "Core (Forearm Plank Hold with Knee Taps)",
                "zone_ua": "Прес (Планка на передпліччях з торканням колінами)",
                "patterns": ["Core"],
                "families": ["Anti-Extension Core"],
                "sets": 3, "reps": "12-15 each", "rest": 45, "superset": "Superset 5: E2"
            }
        ]
    },

    # DAY 5: Full Upper Body & Arms Hypertrophy / Athletic Conditioning (5 Supersets / 10 Exercises)
    {
        "day_index": 4,
        "day_label": "Day 5: Upper Body Hypertrophy & Arms (5 Supersets)",
        "day_label_ua": "День 5: Верх тіла та руки (5 Суперсетів)",
        "day_name_en": "Upper Body & Arms Volume",
        "day_name_ua": "Об'єм верху тіла та рук",
        "description_en": "Antagonistic supersets for chest, back, biceps, triceps, and athletic core finish.",
        "description_ua": "Антагоністичні суперсети на груди, спину, біцепс, трицепс та атлетичний фінішер кору.",
        "slots": [
            {
                "zone": "Chest (Incline Dumbbell Press)",
                "zone_ua": "Груди (Похилий жим гантелей)",
                "patterns": ["Push"],
                "families": ["Horizontal Push Incline", "Horizontal Push Bilateral"],
                "sets": 3, "reps": "8-10", "rest": 60, "superset": "Superset 1: A1"
            },
            {
                "zone": "Back (Chest-Supported Dumbbell Row)",
                "zone_ua": "Спина (Тяга гантелей з упором грудьми в лаву)",
                "patterns": ["Pull"],
                "families": ["Horizontal Pull Bilateral", "Horizontal Pull Unilateral"],
                "sets": 3, "reps": "8-10", "rest": 60, "superset": "Superset 1: A2"
            },
            {
                "zone": "Shoulders (Seated Dumbbell OHP)",
                "zone_ua": "Плечі (Жим гантелей сидячи над головою)",
                "patterns": ["Push"],
                "families": ["Vertical Push Bilateral", "Vertical Push Unilateral"],
                "sets": 3, "reps": "8-10", "rest": 60, "superset": "Superset 2: B1"
            },
            {
                "zone": "Back (Lat Pulldown / Wide Neutral Row)",
                "zone_ua": "Спина (Тяга вертикального блоку широким хватом)",
                "patterns": ["Pull"],
                "families": ["Vertical Pull / Extension", "Horizontal Pull Bilateral"],
                "sets": 3, "reps": "10-12", "rest": 60, "superset": "Superset 2: B2"
            },
            {
                "zone": "Arms - Biceps (Barbell / EZ-Bar Curl)",
                "zone_ua": "Біцепс (Підйом EZ-штанги або гантелей на біцепс)",
                "patterns": ["Pull"],
                "families": ["Elbow Flexion", "Elbow Flexion Suspension"],
                "sets": 3, "reps": "10-12", "rest": 45, "superset": "Superset 3: C1"
            },
            {
                "zone": "Arms - Triceps (Overhead Rope Extension / Skull Crusher)",
                "zone_ua": "Трицепс (Французький жим з канатом з нижнього блоку)",
                "patterns": ["Push"],
                "families": ["Elbow Extension", "Elbow Extension Suspension"],
                "sets": 3, "reps": "10-12", "rest": 45, "superset": "Superset 3: C2"
            },
            {
                "zone": "Arms - Biceps (Incline Hammer Curl)",
                "zone_ua": "Біцепс (Молоткові згинання на похилій лаві)",
                "patterns": ["Pull"],
                "families": ["Elbow Flexion", "Elbow Flexion Suspension"],
                "sets": 3, "reps": "10-12", "rest": 45, "superset": "Superset 4: D1"
            },
            {
                "zone": "Arms - Triceps (Cable Straight-Bar / Band Pushdown)",
                "zone_ua": "Трицепс (Розгинання на блоці з прямою рукояткою)",
                "patterns": ["Push"],
                "families": ["Elbow Extension", "Elbow Extension Suspension"],
                "sets": 3, "reps": "12-15", "rest": 45, "superset": "Superset 4: D2"
            },
            {
                "zone": "Core (Hanging Knee Raise / Floor Leg Drops)",
                "zone_ua": "Прес (Підйом ніг або колін у висі / з підлоги)",
                "patterns": ["Core"],
                "families": ["Dynamic Core / Hip Flexion", "Anti-Extension Core"],
                "sets": 3, "reps": "10-12", "rest": 45, "superset": "Superset 5: E1"
            },
            {
                "zone": "Core & Full Body Finish (Farmer's Walk / Loaded Carry)",
                "zone_ua": "Кор та атлетизм (Прогулянка фермера з важкими гантелями)",
                "patterns": ["Carry", "Core"],
                "families": ["Bilateral Loaded Carry", "Unilateral Loaded Carry", "Anti-Rotation Core"],
                "sets": 3, "reps": "45s walk", "rest": 45, "superset": "Superset 5: E2"
            }
        ]
    }
]
# ---------------------------------------------------------------------------
# 5. FOCUS AREA DEFINITIONS FOR CUSTOM BUILDER
# ---------------------------------------------------------------------------
FOCUS_DEFINITIONS = {
    "chest": {
        "name_en": "Chest",
        "name_ua": "Груди",
        "patterns": ["Push", "Combo"],
        "families": ["Horizontal Push Bilateral", "Horizontal Push Suspension", "Horizontal Push Resisted", "Horizontal Push Bodyweight", "Horizontal Push Standing", "Chest Isolation", "Chest Isolation Suspension", "Horizontal Push Unilateral", "Compound Combo Hybrid"],
        "default_reps": "8-12",
        "default_rest": 60
    },
    "back": {
        "name_en": "Back",
        "name_ua": "Спина",
        "patterns": ["Pull", "Combo"],
        "families": ["Horizontal Pull Bilateral", "Horizontal Pull Unilateral", "Horizontal Pull Suspension", "Vertical Pull Bilateral", "Vertical Pull Unilateral", "Vertical Pull / Extension", "Vertical Pull Suspension", "Posterior Shoulder / Scapular", "Compound Combo Hybrid"],
        "default_reps": "8-12",
        "default_rest": 60
    },
    "shoulders": {
        "name_en": "Shoulders",
        "name_ua": "Плечі",
        "patterns": ["Push", "Pull", "Combo"],
        "families": ["Vertical Push Bilateral", "Vertical Push Unilateral", "Vertical Push Bodyweight", "Shoulder Isolation", "Posterior Shoulder / Scapular", "Compound Combo Hybrid"],
        "default_reps": "10-12",
        "default_rest": 45
    },
    "arms": {
        "name_en": "Arms",
        "name_ua": "Руки",
        "patterns": ["Pull", "Push", "Combo"],
        "families": ["Elbow Flexion", "Elbow Flexion Suspension", "Elbow Extension", "Elbow Extension Suspension", "Compound Combo Hybrid"],
        "default_reps": "10-12",
        "default_rest": 45
    },
    "quads": {
        "name_en": "Quads",
        "name_ua": "Квадрицепси",
        "patterns": ["Squat", "Lunge", "Combo"],
        "families": ["Bilateral Knee Dominant", "Unilateral Knee Dominant", "Lateral Knee Dominant", "Quad Isolation", "Compound Combo Hybrid"],
        "default_reps": "8-12",
        "default_rest": 60
    },
    "hamstrings_glutes": {
        "name_en": "Hamstrings & Glutes",
        "name_ua": "Сідниці та задня ланцюг",
        "patterns": ["Hinge", "Combo"],
        "families": ["Bilateral Hip Hinge", "Unilateral Hip Hinge", "Posterior Knee Flexion", "Glute Bridge / Thrust", "Hip Abduction / Stability", "Glute Isolation", "Compound Combo Hybrid"],
        "default_reps": "10-12",
        "default_rest": 60
    },
    "abs": {
        "name_en": "Abs & Core",
        "name_ua": "Прес та Кор",
        "patterns": ["Core"],
        "families": ["Anti-Extension Core", "Anti-Rotation Core", "Rotational Core", "Dynamic Core / Hip Flexion", "Lateral Core & Hip Abduction", "Lateral Core & Adductor", "Cross-Body Posterior Stability", "Dynamic Core & Push"],
        "default_reps": "10-12",
        "default_rest": 45
    },
    "waist": {
        "name_en": "Waist Narrowing & Pelvis",
        "name_ua": "Звуження талії та таз",
        "patterns": ["Core", "Hinge"],
        "families": ["Anti-Rotation Core", "Lateral Core & Adductor", "Glute Bridge / Thrust", "Rotational Core"],
        "default_reps": "12-15",
        "default_rest": 45
    },
    "adductors": {
        "name_en": "Inner Thighs (Adductors)",
        "name_ua": "Внутрішня частина стегна",
        "patterns": ["Squat", "Lunge", "Core"],
        "families": ["Adductor Isolation", "Lateral Knee Dominant", "Lateral Core & Adductor"],
        "default_reps": "12-15",
        "default_rest": 45
    },
    "calves": {
        "name_en": "Calves & Ankle Pumps",
        "name_ua": "Литки та лімфодренаж",
        "patterns": ["Squat", "Carry"],
        "families": ["Ankle Plantarflexion"],
        "default_reps": "15-20",
        "default_rest": 30
    }
}


# ---------------------------------------------------------------------------
# 6. BIOMECHANICAL & INVENTORY FILTERING ENGINE
# ---------------------------------------------------------------------------
def filter_exercises(
    exercises: List[Exercise],
    location: str = "home",
    injuries_to_avoid: Optional[List[str]] = None,
    trx_anchor: str = "door",
    equipment_inventory: Optional[List[str]] = None,
    medical_conditions: Optional[List[str]] = None,
    sex: str = "female"
) -> List[Exercise]:
    """Filters exercises according to venue, equipment inventory, joint isolation, and medical restrictions."""
    avoid_set = set(i.lower().strip() for i in (injuries_to_avoid or []))
    med_set = set(m.lower().strip() for m in (medical_conditions or []))
    loc = location.lower().strip()
    anchor = trx_anchor.lower().strip()

    # Pre-parse user inventory keywords for home
    inv_set = set(item.lower().strip() for item in (equipment_inventory or []))
    has_inv = bool(equipment_inventory and loc == "home")

    filtered = []
    for ex in exercises:
        # Never pick mobility movements in strength routines (unless routine is specifically mobility/rehab)
        # Note: mobility routines filter their own pool directly

        # Location filter
        if loc == "home" and "home" not in ex.location:
            continue

        # TRX anchor filter (Strict: if door anchor, strictly exclude all bar-only exercises)
        if "trx" in ex.id.lower() or "trx" in ex.equipment_needed:
            if anchor == "door" and ex.trx_anchor == "bar":
                continue

        # Equipment inventory filter for home workouts
        if has_inv:
            needed = [eq.lower().strip() for eq in ex.equipment_needed]
            can_do = True
            for req in needed:
                if req in ["bodyweight", "none"]:
                    continue
                if "dumbbell" in req:
                    if not any("dumbbell" in i for i in inv_set):
                        can_do = False
                elif "trx" in req:
                    if not any("trx" in i for i in inv_set):
                        can_do = False
                elif "short/mini" in req or "mini-band" in req or "mini band" in req:
                    if not any("short" in i or "mini" in i for i in inv_set):
                        can_do = False
                elif "band" in req:
                    if not any("band" in i for i in inv_set):
                        can_do = False
                elif "slider" in req or "towel" in req:
                    if not any("towel" in i or "slider" in i for i in inv_set):
                        can_do = False
                elif "bench" in req or "couch" in req or "chair" in req:
                    if not any("bench" in i or "couch" in i or "chair" in i for i in inv_set):
                        can_do = False
                elif "ball" in req:
                    if not any("ball" in i for i in inv_set):
                        can_do = False
                elif "block" in req or "book" in req:
                    if not any("block" in i or "book" in i for i in inv_set):
                        can_do = False
            if not can_do and not ex.equipment_alternatives:
                continue

        # 1. Joint & Injury Contraindications
        ex_joints = set(j.lower().strip() for j in ex.joint_stress)

        # WRIST: Strict zero-palm-bearing rule
        if "wrist" in avoid_set:
            if "wrist" in ex_joints:
                continue
            # Also exclude exercises that require supporting bodyweight on palms
            name_lower = (ex.name + " " + ex.id).lower()
            if any(term in name_lower for term in [
                "pushup", "push_up", "push-up", "bear_crawl", "hand_plank", "burpee"
            ]) and "forearm" not in name_lower and "couch" not in name_lower:
                continue

        # KNEE: Exclude deep shear load
        if "knee" in avoid_set:
            if "knee" in ex_joints:
                continue
            name_lower = ex.id.lower()
            if any(term in name_lower for term in ["sissy_squat", "jump_squat", "pistol_squat"]):
                continue

        # NO_KNEELING: Exclude quadruped, kneeling, and half-kneeling drills
        if "no_kneeling" in avoid_set:
            name_lower = (ex.name + " " + ex.id).lower()
            if any(term in name_lower for term in ["kneeling", "quadruped", "all_fours", "all-fours", "bird_dog"]):
                continue

        # LOWER BACK / HYPERLORDOSIS / SPINAL HERNIA: Zero axial spine loading
        if any(b in avoid_set for b in ["lower_back", "hyperlordosis", "spinal_hernia", "back"]):
            if "lower_back" in ex_joints or "spine" in ex_joints:
                continue
            name_lower = ex.id.lower()
            if any(term in name_lower for term in ["good_morning", "bb_back_squat", "deadlift_straight_leg"]):
                continue

        # Standard check for other avoided joints (hip, shoulder, elbow, ankle)
        if any(joint in avoid_set for joint in ex_joints):
            continue

        # 2. Medical & Endocrine Conditions
        # DIASTASIS RECTI & PELVIC FLOOR SAFE MODE
        if "diastasis_pelvic_floor" in med_set:
            name_lower = (ex.name + " " + ex.id).lower()
            # Strictly forbid crunches, sit-ups, V-ups, hanging leg raises, jumping jacks
            if any(term in name_lower for term in [
                "crunch", "situp", "sit_up", "v_up", "v-up", "hanging_leg", "jump", "burpee"
            ]) and "reverse" not in name_lower:
                continue

        # FEMALE MODE: Avoid heavy weighted lateral side bends that thicken the waist
        if sex == "female":
            name_lower = ex.id.lower()
            if "side_bend" in name_lower or "db_side_bend" in name_lower:
                continue

        filtered.append(ex)

    # Safety fallback: ensure candidates exist
    return filtered if filtered else exercises


def adjust_reps_and_rest(
    base_reps: str,
    base_rest: int,
    base_sets: int,
    goal: str = "muscle_gain",
    workout_format: str = "standard",
    current_weight: float = 75.0,
    target_weight: float = 72.0,
    medical_conditions: Optional[List[str]] = None
):
    """Calibrates sets, reps, and rest based on training goal, format, weight delta, and medical safety."""
    reps = base_reps
    rest = base_rest
    sets = base_sets
    meds = set(m.lower().strip() for m in (medical_conditions or []))

    if goal == "strength":
        reps = "5-8"
        rest = max(base_rest, 75)
    elif goal == "weight_loss":
        reps = "12-15"
        rest = min(base_rest, 45)
        if target_weight < current_weight:
            rest = min(rest, 30)  # heightened metabolic pacing
    elif goal == "toning":
        reps = "15-20"
        rest = 30
    else:  # muscle_gain (hypertrophy)
        reps = "8-12"
        rest = 60

    if workout_format == "circuit":
        rest = 15
        reps = "10-12"
    elif workout_format == "tabata":
        reps = "40s Work / 10s Rest (8 cycles/set)"
        rest = 10
    elif workout_format == "sandwich":
        reps = "10 reps"
        rest = 30

    # THYROID / HYPOTHYROIDISM CARE: Prevent cortisol spikes, enforce minimum 60-75s rest
    if "thyroid" in meds:
        rest = max(rest, 65)

    return reps, rest, sets


def get_format_descriptions(workout_format: str):
    """Returns bilingual protocol descriptions for workout formats."""
    fmt = workout_format.lower().strip()
    if fmt == "circuit":
        return (
            "🔁 Circuit Training: Perform 1 set of exercises 1 to 10 consecutively with 15s transition. Rest 2 mins after round 10. Repeat for 2-3 rounds.",
            "🔁 Кругове тренування: Виконуйте по 1 підходу вправ з 1 по 10 поспіль (15 сек перехід). Відпочинок 2 хв після 10-ї вправи. Повторіть 2-3 кола."
        )
    elif fmt == "tabata":
        return (
            "⏱️ Tabata Protocol: 40 seconds maximum effort work / 10 seconds rest intervals, repeated 8 times per set with 60s rest between sets.",
            "⏱️ Протокол Табата: 40 секунд максимальної роботи / 10 секунд відпочинку, повторюється 8 разів на сет з 60с відпочинком між сетами."
        )
    elif fmt == "sandwich":
        return (
            "🥪 'Sandwich' Method (Pyramid Ladder): Ex 1 -> Ex 1+2 -> Ex 1+2+3 ... up to 1..10! Then descend down: 2..10, 3..10 ... to Ex 10 alone.",
            "🥪 Метод 'Сендвіч' (Сходинки-піраміда): Вправа 1 -> 1+2 -> 1+2+3 ... до 1..10! Потім спадання: 2..10, 3..10 ... до вправи 10 окремо."
        )
    return (
        "⚡ 5 Supersets x 2 Exercises (3 sets each, ~55-60 min). Complete paired exercises back-to-back, rest 45-60s, then repeat for 3 sets.",
        "⚡ 5 Суперсетів x 2 Вправи (по 3 підходи, ~55-60 хв). Виконуйте спарені вправи поспіль, відпочинок 45-60 сек, потім повторіть на 3 підходи."
    )


def score_exercise_candidate(
    exercise: Exercise,
    history: Dict[str, Dict],
    used_exercise_ids_this_week: set,
    used_families_this_week: set,
    current_date: Optional[datetime] = None,
    level: str = "intermediate",
    location: str = "home",
    sex: str = "female",
    exclude_ids: Optional[set] = None
) -> float:
    """Scores an exercise candidate based on freshness, cooldown, diversity, level demand, gym boost, and gender priorities."""
    if current_date is None:
        current_date = datetime.now()

    if exercise.id in used_exercise_ids_this_week:
        return -9999.0

    if exclude_ids and exercise.id in exclude_ids:
        return -9999.0

    score = 100.0

    if exercise.exercise_family in used_families_this_week and not exercise.is_compound_combo:
        score -= 20.0

    # Level scoring
    if level == "advanced":
        if exercise.difficulty >= 4:
            score += 25.0
        elif exercise.difficulty == 3:
            score += 15.0
        elif exercise.difficulty <= 1:
            score -= 30.0
        if exercise.stability_demand == "High":
            score += 15.0
        if exercise.is_compound_combo:
            score += 35.0
    else:  # intermediate
        if exercise.difficulty in [2, 3]:
            score += 20.0
        elif exercise.difficulty >= 5:
            score -= 35.0
        elif exercise.difficulty == 1:
            score += 5.0
        if exercise.is_compound_combo and exercise.difficulty <= 3:
            score += 20.0

    # Commercial Gym Equipment Boost (+200)
    if location.lower().strip() == "gym":
        gym_keywords = ["cable", "machine", "barbell", "smith", "pulldown", "rack", "seated abduction", "leg extension", "leg curl", "incline dumbbell bench"]
        eq_text = " ".join(exercise.equipment_needed).lower() + " " + exercise.id.lower()
        if any(k in eq_text for k in gym_keywords) or "gym" in exercise.location:
            score += 200.0

    # Gender Priority Boost (+150)
    gender_pri = getattr(exercise, "gender_priority", []) or []
    if sex.lower().strip() == "female" and "female" in gender_pri:
        score += 150.0
    elif sex.lower().strip() == "male" and "male" in gender_pri:
        score += 150.0

    # Freshness cooldown based on history
    hist = history.get(exercise.id)
    if not hist or not hist.get("last_performed_date"):
        score += 50.0
    else:
        try:
            last_date = datetime.strptime(hist["last_performed_date"], "%Y-%m-%d")
            days_ago = (current_date - last_date).days

            if days_ago < 7:
                score -= 150.0
            elif days_ago < 14:
                score -= 40.0
            elif days_ago >= 21:
                score += 35.0
        except Exception:
            pass

        times_done = hist.get("times_performed", 0)
        score -= min(times_done * 4.0, 25.0)

        times_skipped = hist.get("times_skipped", 0)
        score -= times_skipped * 20.0

    # Significant random perturbation (0-50) for variation on every regeneration
    score += random.uniform(0.0, 50.0)
    return score


def _build_planned_exercise(
    slot: Dict,
    selected_ex: Exercise,
    slot_index: int,
    goal: str,
    workout_format: str,
    current_weight: float,
    target_weight: float,
    level: str,
    perf_data: Optional[Dict] = None,
    medical_conditions: Optional[List[str]] = None
) -> PlannedExercise:
    """Helper to assemble a PlannedExercise with closed-loop progression tips, last performance, and superset grouping."""
    prescribed_sets = slot.get("sets", 3)
    if level == "advanced" and prescribed_sets < 4 and slot_index <= 4:
        prescribed_sets = 4

    adj_reps, adj_rest, adj_sets = adjust_reps_and_rest(
        slot.get("reps", "10-12"),
        slot.get("rest", 60),
        prescribed_sets,
        goal=goal,
        workout_format=workout_format,
        current_weight=current_weight,
        target_weight=target_weight,
        medical_conditions=medical_conditions
    )

    # Dumbbell per-hand clarification
    is_db = any("dumbbell" in req.lower() for req in selected_ex.equipment_needed)
    db_note_en = " [Weight is PER 1 DUMBBELL in hand]" if is_db else ""
    db_note_ua = " [Вага зазначена ДЛЯ 1 ГАНТЕЛІ в руці]" if is_db else ""

    # Unilateral per-side clarification
    if any(term in selected_ex.exercise_family.lower() or term in selected_ex.name.lower() for term in ["unilateral", "single-leg", "single leg", "clamshell", "lunge"]):
        if "each" not in adj_reps.lower() and "по" not in adj_reps.lower():
            adj_reps = f"{adj_reps} each side"

    anchor_tag = f" [Anchor: {selected_ex.trx_anchor.capitalize()}]" if "trx" in selected_ex.id.lower() else ""

    # Last performance & Closed-Loop progression tip
    last_weight = ""
    last_reps = ""
    coach_tip_en = "🎯 Base set: choose weight that leaves 2 reps in reserve (RPE 7-8)."
    coach_tip_ua = "🎯 Базовий підхід: оберіть вагу, з якою залишається 2 повторення в запасі (RPE 7-8)."

    if perf_data:
        last_weight = perf_data.get("weight", "")
        last_reps = perf_data.get("reps", "")
        rpe = perf_data.get("perceived_difficulty")
        if rpe is not None:
            if rpe <= 2:
                coach_tip_en = f"🚀 Last session felt easy (RPE {rpe}). Increase weight by +1-2 kg or use heavier band!"
                coach_tip_ua = f"🚀 Минулого разу було легко (RPE {rpe}). Додайте +1-2 кг або візьміть тугішу гуму!"
            elif rpe >= 4:
                coach_tip_en = f"🛡️ High exertion last time (RPE {rpe}). Keep weight, focus on strict form and tempo."
                coach_tip_ua = f"🛡️ Високе навантаження (RPE {rpe}). Збережіть вагу, зосередьтеся на чистій техніці."
            else:
                coach_tip_en = f"⚖️ Optimal stimulus (RPE {rpe}). Aim for +1 extra rep with crisp technique."
                coach_tip_ua = f"⚖️ Оптимальний стимул (RPE {rpe}). Спробуйте зробити на +1 повторення більше з чіткою технікою."

    superset_tag = slot.get("superset", f"Superset {(slot_index + 1) // 2}: {'A' if slot_index % 2 == 1 else 'B'}")

    return PlannedExercise(
        exercise_id=selected_ex.id,
        name=selected_ex.name,
        name_ua=selected_ex.name_ua,
        zone_en=slot["zone"],
        zone_ua=slot["zone_ua"],
        order_index=slot_index,
        sets=adj_sets,
        reps=adj_reps,
        rest_seconds=adj_rest,
        instructions=selected_ex.instructions,
        instructions_ua=selected_ex.instructions_ua,
        setup=selected_ex.setup,
        execution=selected_ex.execution,
        form_tips=selected_ex.form_tips,
        setup_ua=selected_ex.setup_ua,
        execution_ua=selected_ex.execution_ua,
        form_tips_ua=selected_ex.form_tips_ua,
        notes=f"[{slot['zone']}]{anchor_tag}{db_note_en} — {selected_ex.setup}",
        completed=False,
        actual_reps="",
        actual_weight="",
        joint_stress=selected_ex.joint_stress,
        location=selected_ex.location,
        trx_anchor=selected_ex.trx_anchor,
        is_compound_combo=selected_ex.is_compound_combo,
        equipment_alternatives=selected_ex.equipment_alternatives,
        equipment_alternatives_ua=selected_ex.equipment_alternatives_ua,
        superset_group=superset_tag,
        coach_progression_tip=coach_tip_en,
        coach_progression_tip_ua=coach_tip_ua,
        last_weight=last_weight,
        last_reps=last_reps
    )


# ---------------------------------------------------------------------------
# 7. THE 5-DAY ROLLING SPLIT GENERATOR
# ---------------------------------------------------------------------------
def generate_rolling_workout(
    day_index: Optional[int] = None,
    level: str = "intermediate",
    location: str = "home",
    injuries_to_avoid: Optional[List[str]] = None,
    goal: str = "muscle_gain",
    current_weight: float = 75.0,
    target_weight: float = 72.0,
    workout_format: str = "standard",
    trx_anchor: str = "door",
    target_date: Optional[datetime] = None,
    age: int = 30,
    custom_max_hr: Optional[int] = None,
    sex: str = "female",
    equipment_inventory: Optional[List[str]] = None,
    medical_conditions: Optional[List[str]] = None
) -> WorkoutPlan:
    """Generates the next workout in the 5-Day Rolling Split queue (5 Supersets x 2 Exercises = 10 exercises)."""
    if target_date is None:
        target_date = datetime.now()

    profile = database.get_user_profile()
    if day_index is None:
        day_index = profile.get("rolling_split_index", 0)

    templates = MALE_SPLIT_TEMPLATES if str(sex).lower() == "male" else ROLLING_SPLIT_TEMPLATES
    day_index = day_index % len(templates)
    template = templates[day_index]

    all_exercises = database.get_all_exercises()
    history = database.get_exercise_history()

    # Filter exercises (strict non-mobility for strength workouts)
    strength_pool = [e for e in all_exercises if e.movement_pattern != "Mobility"]
    exercises = filter_exercises(
        strength_pool,
        location=location,
        injuries_to_avoid=injuries_to_avoid,
        trx_anchor=trx_anchor,
        equipment_inventory=equipment_inventory or profile.get("equipment_inventory"),
        medical_conditions=medical_conditions or profile.get("medical_conditions"),
        sex=sex
    )

    # Fetch last performance dictionary for all candidates
    perf_map = database.get_last_performance_for_exercises([e.id for e in exercises])

    workout_id = f"roll_{target_date.strftime('%Y%m%d')}_d{day_index + 1}"
    planned_exercises: List[PlannedExercise] = []
    used_exercise_ids = set()
    used_families = set()

    for slot_index, slot in enumerate(template["slots"], start=1):
        family_candidates = [
            ex for ex in exercises if ex.exercise_family in slot["families"] and ex.id not in used_exercise_ids
        ]
        if not family_candidates:
            family_candidates = [
                ex for ex in exercises if ex.movement_pattern in slot["patterns"] and ex.id not in used_exercise_ids
            ]

        if not family_candidates:
            family_candidates = [ex for ex in exercises if ex.id not in used_exercise_ids]

        if not family_candidates:
            family_candidates = exercises[:]

        scored_candidates = []
        for cand in family_candidates:
            score = score_exercise_candidate(
                cand,
                history,
                used_exercise_ids,
                used_families,
                target_date,
                level=level,
                location=location,
                sex=sex
            )
            scored_candidates.append((score, cand))

        scored_candidates.sort(key=lambda x: x[0], reverse=True)
        selected_ex = scored_candidates[0][1]

        used_exercise_ids.add(selected_ex.id)
        used_families.add(selected_ex.exercise_family)

        planned_ex = _build_planned_exercise(
            slot=slot,
            selected_ex=selected_ex,
            slot_index=slot_index,
            goal=goal,
            workout_format=workout_format,
            current_weight=current_weight,
            target_weight=target_weight,
            level=level,
            perf_data=perf_map.get(selected_ex.id),
            medical_conditions=medical_conditions or profile.get("medical_conditions")
        )
        planned_exercises.append(planned_ex)

    fmt_desc_en, fmt_desc_ua = get_format_descriptions(workout_format)
    target_hr = heart_rate.get_target_zone_for_workout(
        goal=goal,
        workout_format=workout_format,
        age=age,
        custom_max_hr=custom_max_hr
    )

    return WorkoutPlan(
        workout_id=workout_id,
        day_label=template["day_label"],
        day_label_ua=template["day_label_ua"],
        target_duration_minutes=60,
        format_type=workout_format,
        format_description=fmt_desc_en,
        format_description_ua=fmt_desc_ua,
        goal=goal,
        location=location,
        target_hr_zone=target_hr["target_zone_name_en"],
        target_hr_zone_ua=target_hr["target_zone_name_ua"],
        target_hr_bpm_range=target_hr["target_bpm_range"],
        exercises=planned_exercises,
        mode="workout"
    )


def generate_5day_program(
    force_new_cycle: bool = False,
    exclude_ids: Optional[List[str]] = None,
    sex: str = "female",
    level: str = "intermediate",
    location: str = "home",
    injuries_to_avoid: Optional[List[str]] = None,
    goal: str = "muscle_gain",
    current_weight: float = 75.0,
    target_weight: float = 72.0,
    workout_format: str = "superset",
    trx_anchor: str = "door",
    target_date: Optional[datetime] = None,
    age: int = 30,
    custom_max_hr: Optional[int] = None,
    equipment_inventory: Optional[List[str]] = None,
    medical_conditions: Optional[List[str]] = None
) -> List[WorkoutPlan]:
    """Generates all 5 days of the rolling split program with guaranteed non-overlapping exercises across all 5 days,
    honoring gender split (Female Sculpt vs Male Hypertrophy), venue boost/exclusion, and cycle-to-cycle freshness."""
    if target_date is None:
        target_date = datetime.now()

    profile = database.get_user_profile()
    if equipment_inventory is None:
        equipment_inventory = profile.get("equipment_inventory")
    if medical_conditions is None:
        medical_conditions = profile.get("medical_conditions")

    templates = MALE_SPLIT_TEMPLATES if str(sex).lower() == "male" else ROLLING_SPLIT_TEMPLATES

    all_exercises = database.get_all_exercises()
    history = database.get_exercise_history()

    strength_pool = [e for e in all_exercises if e.movement_pattern != "Mobility"]
    filtered_exercises = filter_exercises(
        strength_pool,
        location=location,
        injuries_to_avoid=injuries_to_avoid,
        trx_anchor=trx_anchor,
        equipment_inventory=equipment_inventory,
        medical_conditions=medical_conditions,
        sex=sex
    )

    perf_map = database.get_last_performance_for_exercises([e.id for e in filtered_exercises])

    cycle_used_ids = set(exclude_ids or []) if force_new_cycle else set()
    program_days: List[WorkoutPlan] = []

    for day_idx in range(5):
        template = templates[day_idx]
        day_used_ids = set()
        day_used_families = set()
        day_planned_exercises: List[PlannedExercise] = []

        for slot_index, slot in enumerate(template["slots"], start=1):
            candidates = [
                ex for ex in filtered_exercises
                if ex.exercise_family in slot["families"] and ex.id not in day_used_ids and ex.id not in cycle_used_ids
            ]
            if not candidates:
                candidates = [
                    ex for ex in filtered_exercises
                    if ex.movement_pattern in slot["patterns"] and ex.id not in day_used_ids and ex.id not in cycle_used_ids
                ]
            if not candidates:
                candidates = [
                    ex for ex in filtered_exercises
                    if ex.id not in day_used_ids and ex.id not in cycle_used_ids
                ]
            if not candidates:
                candidates = [
                    ex for ex in filtered_exercises
                    if ex.exercise_family in slot["families"] and ex.id not in day_used_ids
                ]
            if not candidates:
                candidates = [
                    ex for ex in filtered_exercises
                    if ex.movement_pattern in slot["patterns"] and ex.id not in day_used_ids
                ]
            if not candidates:
                candidates = [ex for ex in filtered_exercises if ex.id not in day_used_ids]
            if not candidates:
                candidates = filtered_exercises[:]

            scored_candidates = []
            for cand in candidates:
                score = score_exercise_candidate(
                    cand,
                    history,
                    day_used_ids,
                    day_used_families,
                    target_date,
                    level=level,
                    location=location,
                    sex=sex,
                    exclude_ids=cycle_used_ids
                )
                scored_candidates.append((score, cand))

            scored_candidates.sort(key=lambda x: x[0], reverse=True)
            selected_ex = scored_candidates[0][1]

            day_used_ids.add(selected_ex.id)
            cycle_used_ids.add(selected_ex.id)
            day_used_families.add(selected_ex.exercise_family)

            planned_ex = _build_planned_exercise(
                slot=slot,
                selected_ex=selected_ex,
                slot_index=slot_index,
                goal=goal,
                workout_format=workout_format,
                current_weight=current_weight,
                target_weight=target_weight,
                level=level,
                perf_data=perf_map.get(selected_ex.id),
                medical_conditions=medical_conditions
            )
            day_planned_exercises.append(planned_ex)

        fmt_desc_en, fmt_desc_ua = get_format_descriptions(workout_format)
        target_hr = heart_rate.get_target_zone_for_workout(
            goal=goal,
            workout_format=workout_format,
            age=age,
            custom_max_hr=custom_max_hr
        )

        workout_id = f"prog_{target_date.strftime('%Y%m%d')}_d{day_idx + 1}"
        program_days.append(WorkoutPlan(
            workout_id=workout_id,
            day_label=template["day_label"],
            day_label_ua=template["day_label_ua"],
            target_duration_minutes=60,
            format_type=workout_format,
            format_description=fmt_desc_en,
            format_description_ua=fmt_desc_ua,
            goal=goal,
            location=location,
            target_hr_zone=target_hr["target_zone_name_en"],
            target_hr_zone_ua=target_hr["target_zone_name_ua"],
            target_hr_bpm_range=target_hr["target_bpm_range"],
            exercises=day_planned_exercises,
            mode="workout",
            day_name_en=template.get("day_name_en", template["day_label"]),
            day_name_ua=template.get("day_name_ua", template["day_label_ua"])
        ))

    return program_days


# ---------------------------------------------------------------------------
# 8. SPECIAL MONO-DAY GENERATOR (13-Exercise Lower Body, Pure Back, etc.)
# ---------------------------------------------------------------------------
def generate_mono_workout(
    mono_key: str = "special_13_lower_body",
    level: str = "intermediate",
    location: str = "home",
    injuries_to_avoid: Optional[List[str]] = None,
    goal: str = "muscle_gain",
    current_weight: float = 75.0,
    target_weight: float = 72.0,
    workout_format: str = "standard",
    trx_anchor: str = "door",
    target_date: Optional[datetime] = None,
    age: int = 30,
    custom_max_hr: Optional[int] = None,
    sex: str = "female",
    equipment_inventory: Optional[List[str]] = None,
    medical_conditions: Optional[List[str]] = None
) -> WorkoutPlan:
    """Generates an on-demand targeted Mono-Day workout (e.g. 13-exercise lower body sculpt)."""
    if target_date is None:
        target_date = datetime.now()

    template = MONO_DAY_TEMPLATES.get(mono_key, MONO_DAY_TEMPLATES["special_13_lower_body"])

    all_exercises = database.get_all_exercises()
    history = database.get_exercise_history()
    profile = database.get_user_profile()

    strength_pool = [e for e in all_exercises if e.movement_pattern != "Mobility"]
    exercises = filter_exercises(
        strength_pool,
        location=location,
        injuries_to_avoid=injuries_to_avoid,
        trx_anchor=trx_anchor,
        equipment_inventory=equipment_inventory or profile.get("equipment_inventory"),
        medical_conditions=medical_conditions or profile.get("medical_conditions"),
        sex=sex
    )

    perf_map = database.get_last_performance_for_exercises([e.id for e in exercises])

    workout_id = f"mono_{mono_key}_{target_date.strftime('%Y%m%d_%H%M%S')}"
    planned_exercises: List[PlannedExercise] = []
    used_exercise_ids = set()
    used_families = set()

    for slot_index, slot in enumerate(template["slots"], start=1):
        family_candidates = [
            ex for ex in exercises if ex.exercise_family in slot["families"] and ex.id not in used_exercise_ids
        ]
        if not family_candidates:
            family_candidates = [
                ex for ex in exercises if ex.movement_pattern in slot["patterns"] and ex.id not in used_exercise_ids
            ]

        if not family_candidates:
            family_candidates = [ex for ex in exercises if ex.id not in used_exercise_ids]

        if not family_candidates:
            family_candidates = exercises[:]

        scored_candidates = []
        for cand in family_candidates:
            score = score_exercise_candidate(
                cand,
                history,
                used_exercise_ids,
                used_families,
                target_date,
                level=level,
                location=location,
                sex=sex
            )
            scored_candidates.append((score, cand))

        scored_candidates.sort(key=lambda x: x[0], reverse=True)
        selected_ex = scored_candidates[0][1]

        used_exercise_ids.add(selected_ex.id)
        used_families.add(selected_ex.exercise_family)

        planned_ex = _build_planned_exercise(
            slot=slot,
            selected_ex=selected_ex,
            slot_index=slot_index,
            goal=goal,
            workout_format=workout_format,
            current_weight=current_weight,
            target_weight=target_weight,
            level=level,
            perf_data=perf_map.get(selected_ex.id),
            medical_conditions=medical_conditions or profile.get("medical_conditions")
        )
        planned_exercises.append(planned_ex)

    fmt_desc_en, fmt_desc_ua = get_format_descriptions(workout_format)
    target_hr = heart_rate.get_target_zone_for_workout(
        goal=goal,
        workout_format=workout_format,
        age=age,
        custom_max_hr=custom_max_hr
    )

    return WorkoutPlan(
        workout_id=workout_id,
        day_label=template["title_en"],
        day_label_ua=template["title_ua"],
        target_duration_minutes=template.get("target_duration_minutes", 60),
        format_type=workout_format,
        format_description=fmt_desc_en,
        format_description_ua=fmt_desc_ua,
        goal=goal,
        location=location,
        target_hr_zone=target_hr["target_zone_name_en"],
        target_hr_zone_ua=target_hr["target_zone_name_ua"],
        target_hr_bpm_range=target_hr["target_bpm_range"],
        exercises=planned_exercises,
        mode="workout"
    )


# ---------------------------------------------------------------------------
# 9. REHABILITATION & RESTORATION ROUTINE GENERATOR
# ---------------------------------------------------------------------------
def get_rehab_departments() -> List[Dict[str, Any]]:
    """Returns the list of 6 available rehabilitation departments with bilingual metadata."""
    return [
        {
            "id": k,
            "name_en": v["name_en"],
            "name_ua": v["name_ua"],
            "icon": v["icon"],
            "description_en": v["description_en"],
            "description_ua": v["description_ua"],
            "drills_count": len(v["drills"])
        }
        for k, v in REHAB_DEPARTMENTS.items()
    ]


def generate_rehab_routine(
    department: Any = "pelvic_floor_diastasis",
    location: str = "home",
    injuries_to_avoid: Optional[List[str]] = None,
    level: str = "intermediate",
    target_date: Optional[datetime] = None,
    age: int = 30,
    custom_max_hr: Optional[int] = None,
    exclude_ids: Optional[List[str]] = None
) -> WorkoutPlan:
    """Generates an intelligent 10-drill restorative rehabilitation session from REHAB_EXERCISES."""
    if target_date is None:
        target_date = datetime.now()

    if isinstance(department, list):
        dept_keys = [str(d).lower().strip() for d in department if str(d).lower().strip() in REHAB_DEPARTMENTS]
    elif isinstance(department, str) and "," in department:
        dept_keys = [d.lower().strip() for d in department.split(",") if d.lower().strip() in REHAB_DEPARTMENTS]
    elif isinstance(department, str) and department.lower().strip() in REHAB_DEPARTMENTS:
        dept_keys = [department.lower().strip()]
    else:
        dept_keys = []

    available_rehab = REHAB_EXERCISES[:]
    if dept_keys:
        primary_pool = [
            e for e in available_rehab
            if any(dk in e.exercise_family.lower() or dk in e.id.lower() for dk in dept_keys)
        ]
        if not primary_pool:
            primary_pool = [e for e in available_rehab if any(dk in e.id for dk in dept_keys)]
    else:
        primary_pool = available_rehab[:]

    safe_pool = filter_exercises(primary_pool if primary_pool else available_rehab, location=location, injuries_to_avoid=injuries_to_avoid)
    if not safe_pool:
        safe_pool = available_rehab[:]

    excluded = set(exclude_ids or [])
    pool = [e for e in safe_pool if e.id not in excluded]
    if len(pool) < 10:
        pool = safe_pool[:]

    random.shuffle(pool)

    selected_drills = []
    used_ids = set()
    for ex in pool:
        if ex.id not in used_ids:
            selected_drills.append(ex)
            used_ids.add(ex.id)
            if len(selected_drills) == 10:
                break

    if len(selected_drills) < 10:
        other_safe = filter_exercises(available_rehab, location=location, injuries_to_avoid=injuries_to_avoid)
        random.shuffle(other_safe)
        for ex in other_safe:
            if ex.id not in used_ids:
                selected_drills.append(ex)
                used_ids.add(ex.id)
                if len(selected_drills) == 10:
                    break

    planned_exercises: List[PlannedExercise] = []
    for idx, ex in enumerate(selected_drills, start=1):
        planned_exercises.append(PlannedExercise(
            exercise_id=ex.id,
            name=ex.name,
            name_ua=ex.name_ua or ex.name,
            zone_en=f"Rehab #{idx}",
            zone_ua=f"Реабілітація #{idx}",
            order_index=idx,
            sets=2,
            reps=ex.default_reps or "10-12 reps",
            rest_seconds=ex.rest_seconds or 30,
            instructions=ex.instructions,
            instructions_ua=ex.instructions_ua or ex.instructions,
            setup=ex.setup,
            execution=ex.execution,
            form_tips=ex.form_tips,
            setup_ua=ex.setup_ua or ex.setup,
            execution_ua=ex.execution_ua or ex.execution,
            form_tips_ua=ex.form_tips_ua or ex.form_tips,
            notes=f"[{ex.exercise_family}] — {ex.setup}",
            completed=False,
            actual_reps="",
            actual_weight="",
            joint_stress=ex.joint_stress,
            location=ex.location,
            trx_anchor=ex.trx_anchor,
            is_compound_combo=False,
            equipment_alternatives=getattr(ex, "equipment_alternatives", "") or "",
            equipment_alternatives_ua=getattr(ex, "equipment_alternatives_ua", "") or "",
            superset_group=f"Rehab Station {idx}",
            coach_progression_tip="🌱 Restorative pace: prioritize alignment and mind-muscle reconnection over fatigue.",
            coach_progression_tip_ua="🌱 Відновлювальний темп: пріоритет на поставу та нейром'язовий зв'язок без втоми.",
            last_weight="",
            last_reps=""
        ))

    if dept_keys and len(dept_keys) == 1:
        dept_meta = REHAB_DEPARTMENTS.get(dept_keys[0], {})
        day_label = dept_meta.get("name_en", "Rehabilitation Session (10 Exercises)")
        day_label_ua = dept_meta.get("name_ua", "Реабілітаційний комплекс (10 вправ)")
        desc_en = dept_meta.get("description_en", "")
        desc_ua = dept_meta.get("description_ua", "")
    elif dept_keys:
        names_en = [REHAB_DEPARTMENTS[k]["name_en"] for k in dept_keys if k in REHAB_DEPARTMENTS]
        names_ua = [REHAB_DEPARTMENTS[k]["name_ua"] for k in dept_keys if k in REHAB_DEPARTMENTS]
        day_label = f"Rehab: {', '.join(names_en)} (10 Exercises)"
        day_label_ua = f"Реабілітація: {', '.join(names_ua)} (10 вправ)"
        desc_en = "Targeted restorative flow for selected departments."
        desc_ua = "Цільовий відновлювальний комплекс для обраних зон."
    else:
        day_label = "Comprehensive Full-Body Rehabilitation (10 Exercises)"
        day_label_ua = "Комплексна реабілітація всього тіла (10 вправ)"
        desc_en = "Full-body joint decompression and pelvic-lumbar restoration."
        desc_ua = "Загальна декомпресія суглобів та відновлення тазово-поперекової зони."

    target_hr = heart_rate.get_target_zone_for_workout(
        goal="rehabilitation",
        workout_format="rehabilitation",
        age=age,
        custom_max_hr=custom_max_hr
    )

    fmt_desc_en = f"🩺 Rehabilitation Protocol: {desc_en} 2 sets of deliberate repetitions with relaxed parasympathetic breathing."
    fmt_desc_ua = f"🩺 Реабілітаційний протокол: {desc_ua} 2 підходи плавних повторень зі спокійним діафрагмальним диханням."

    dept_id = dept_keys[0] if len(dept_keys) == 1 else "combined"

    return WorkoutPlan(
        workout_id=f"rehab_{target_date.strftime('%Y%m%d_%H%M%S')}",
        day_label=day_label,
        day_label_ua=day_label_ua,
        target_duration_minutes=25,
        format_type="rehabilitation",
        format_description=fmt_desc_en,
        format_description_ua=fmt_desc_ua,
        goal="rehabilitation",
        location=location,
        target_hr_zone=target_hr["target_zone_name_en"],
        target_hr_zone_ua=target_hr["target_zone_name_ua"],
        target_hr_bpm_range=target_hr["target_bpm_range"],
        exercises=planned_exercises,
        mode="rehabilitation",
        rehab_department=dept_id,
        day_name_en=day_label,
        day_name_ua=day_label_ua
    )

# ---------------------------------------------------------------------------
# 10. ADVANCE ROLLING SPLIT HELPER
# ---------------------------------------------------------------------------
def advance_rolling_split() -> int:
    """Advances user profile rolling_split_index to the next day in the 5-day cycle."""
    return database.advance_rolling_split_index()


# ---------------------------------------------------------------------------
# 11. FOUNDATION 3-DAY WEEKLY PROGRAM GENERATOR (Backward Compatible)
# ---------------------------------------------------------------------------
def generate_weekly_program(
    target_date: Optional[datetime] = None,
    available_equipment: Optional[List[str]] = None,
    level: str = "intermediate",
    location: str = "home",
    injuries_to_avoid: Optional[List[str]] = None,
    goal: str = "muscle_gain",
    current_weight: float = 75.0,
    target_weight: float = 72.0,
    workout_format: str = "standard",
    trx_anchor: str = "door",
    age: int = 30,
    custom_max_hr: Optional[int] = None,
    sex: str = "female",
    equipment_inventory: Optional[List[str]] = None,
    medical_conditions: Optional[List[str]] = None
) -> List[WorkoutPlan]:
    """Generates the foundation 3-day weekly workout program (10 exercises each, ~60 min)."""
    if target_date is None:
        target_date = datetime.now()

    all_exercises = database.get_all_exercises()
    history = database.get_exercise_history()
    profile = database.get_user_profile()

    strength_pool = [e for e in all_exercises if e.movement_pattern != "Mobility"]
    exercises = filter_exercises(
        strength_pool,
        location=location,
        injuries_to_avoid=injuries_to_avoid,
        trx_anchor=trx_anchor,
        equipment_inventory=equipment_inventory or profile.get("equipment_inventory"),
        medical_conditions=medical_conditions or profile.get("medical_conditions"),
        sex=sex
    )

    if available_equipment:
        avail_set = set(e.lower() for e in available_equipment)
        exercises = [
            ex for ex in exercises
            if all(any(req.lower() in avail_item for avail_item in avail_set) for req in ex.equipment_needed)
        ]

    perf_map = database.get_last_performance_for_exercises([e.id for e in exercises])

    weekly_plan: List[WorkoutPlan] = []
    used_exercise_ids_this_week = set()
    used_families_this_week = set()

    fmt_desc_en, fmt_desc_ua = get_format_descriptions(workout_format)
    target_hr = heart_rate.get_target_zone_for_workout(
        goal=goal,
        workout_format=workout_format,
        age=age,
        custom_max_hr=custom_max_hr
    )

    for day_index, template in enumerate(WORKOUT_TEMPLATES, start=1):
        workout_id = f"w_{target_date.strftime('%Y%W')}_d{day_index}"
        planned_exercises: List[PlannedExercise] = []

        for slot_index, slot in enumerate(template["slots"], start=1):
            family_candidates = [
                ex for ex in exercises if ex.exercise_family in slot["families"] and ex.id not in used_exercise_ids_this_week
            ]
            if not family_candidates:
                family_candidates = [
                    ex for ex in exercises if ex.movement_pattern in slot["patterns"] and ex.id not in used_exercise_ids_this_week
                ]

            if not family_candidates:
                family_candidates = [ex for ex in exercises if ex.id not in used_exercise_ids_this_week]

            if not family_candidates:
                family_candidates = exercises[:]

            scored_candidates = []
            for cand in family_candidates:
                cand_score = score_exercise_candidate(
                    cand,
                    history,
                    used_exercise_ids_this_week,
                    used_families_this_week,
                    target_date,
                    level=level
                )
                scored_candidates.append((cand_score, cand))

            scored_candidates.sort(key=lambda x: x[0], reverse=True)
            selected_ex = scored_candidates[0][1]

            used_exercise_ids_this_week.add(selected_ex.id)
            used_families_this_week.add(selected_ex.exercise_family)

            planned_ex = _build_planned_exercise(
                slot=slot,
                selected_ex=selected_ex,
                slot_index=slot_index,
                goal=goal,
                workout_format=workout_format,
                current_weight=current_weight,
                target_weight=target_weight,
                level=level,
                perf_data=perf_map.get(selected_ex.id),
                medical_conditions=medical_conditions or profile.get("medical_conditions")
            )
            planned_exercises.append(planned_ex)

        weekly_plan.append(WorkoutPlan(
            workout_id=workout_id,
            day_label=template["day_label"],
            day_label_ua=template["day_label_ua"],
            target_duration_minutes=60,
            format_type=workout_format,
            format_description=fmt_desc_en,
            format_description_ua=fmt_desc_ua,
            goal=goal,
            location=location,
            target_hr_zone=target_hr["target_zone_name_en"],
            target_hr_zone_ua=target_hr["target_zone_name_ua"],
            target_hr_bpm_range=target_hr["target_bpm_range"],
            exercises=planned_exercises,
            mode="workout"
        ))

    return weekly_plan


# ---------------------------------------------------------------------------
# 12. CUSTOM GUIDED FOCUS WORKOUT BUILDER
# ---------------------------------------------------------------------------
def build_custom_slots(focus_areas: List[str], level: str = "intermediate") -> List[Dict]:
    """Dynamically balances exactly 10 exercise slots based on user-requested focus areas."""
    valid_keys = [k.lower().strip() for k in focus_areas if k.lower().strip() in FOCUS_DEFINITIONS]
    if not valid_keys:
        valid_keys = ["chest", "arms", "shoulders", "abs"]

    has_abs = "abs" in valid_keys
    non_abs = [k for k in valid_keys if k != "abs"]

    if has_abs:
        abs_count = 3 if len(non_abs) <= 3 else 2
    else:
        abs_count = 2

    remaining_slots = 10 - abs_count
    slot_assignments = []
    if not non_abs:
        slot_assignments = ["abs", "abs", "abs", "abs", "quads", "quads", "chest", "chest", "back", "back"]
        abs_count = 0
    else:
        idx = 0
        while len(slot_assignments) < remaining_slots:
            slot_assignments.append(non_abs[idx % len(non_abs)])
            idx += 1
        slot_assignments.extend(["abs"] * abs_count)

    slots = []
    area_counts = {}
    for slot_idx, f_key in enumerate(slot_assignments, start=1):
        area_counts[f_key] = area_counts.get(f_key, 0) + 1
        count_for_this = area_counts[f_key]
        def_info = FOCUS_DEFINITIONS[f_key]

        if level == "advanced":
            sets = 4 if count_for_this <= 2 and f_key != "abs" else 3
        else:
            sets = 3 if count_for_this <= 2 else 2

        zone_label_en = f"{def_info['name_en']} #{count_for_this}"
        zone_label_ua = f"{def_info['name_ua']} #{count_for_this}"
        superset_tag = f"Superset {(slot_idx + 1) // 2}: {'A' if slot_idx % 2 == 1 else 'B'}"

        slots.append({
            "zone": zone_label_en,
            "zone_ua": zone_label_ua,
            "patterns": def_info["patterns"],
            "families": def_info["families"],
            "sets": sets,
            "reps": def_info["default_reps"],
            "rest": def_info["default_rest"],
            "superset": superset_tag
        })

    return slots


def generate_custom_workout(
    focus_areas: List[str],
    level: str = "intermediate",
    location: str = "home",
    injuries_to_avoid: Optional[List[str]] = None,
    goal: str = "muscle_gain",
    current_weight: float = 75.0,
    target_weight: float = 72.0,
    workout_format: str = "standard",
    trx_anchor: str = "door",
    target_date: Optional[datetime] = None,
    available_equipment: Optional[List[str]] = None,
    age: int = 30,
    custom_max_hr: Optional[int] = None,
    sex: str = "female",
    equipment_inventory: Optional[List[str]] = None,
    medical_conditions: Optional[List[str]] = None
) -> WorkoutPlan:
    """Builds a custom 10-exercise workout based on user-selected focus areas and preferences."""
    if target_date is None:
        target_date = datetime.now()

    all_exercises = database.get_all_exercises()
    history = database.get_exercise_history()
    profile = database.get_user_profile()

    strength_pool = [e for e in all_exercises if e.movement_pattern != "Mobility"]
    exercises = filter_exercises(
        strength_pool,
        location=location,
        injuries_to_avoid=injuries_to_avoid,
        trx_anchor=trx_anchor,
        equipment_inventory=equipment_inventory or profile.get("equipment_inventory"),
        medical_conditions=medical_conditions or profile.get("medical_conditions"),
        sex=sex
    )

    if available_equipment:
        avail_set = set(e.lower() for e in available_equipment)
        exercises = [
            ex for ex in exercises
            if all(any(req.lower() in avail_item for avail_item in avail_set) for req in ex.equipment_needed)
        ]

    perf_map = database.get_last_performance_for_exercises([e.id for e in exercises])
    slots = build_custom_slots(focus_areas, level=level)

    workout_id = f"custom_{target_date.strftime('%Y%m%d_%H%M%S')}"
    planned_exercises: List[PlannedExercise] = []
    used_exercise_ids = set()
    used_families = set()

    excluded = set(exclude_ids or [])
    for slot_index, slot in enumerate(slots, start=1):
        family_candidates = [
            ex for ex in exercises if ex.exercise_family in slot["families"] and ex.id not in used_exercise_ids and ex.id not in excluded
        ]
        if not family_candidates:
            family_candidates = [
                ex for ex in exercises if ex.exercise_family in slot["families"] and ex.id not in used_exercise_ids
            ]
        if not family_candidates:
            family_candidates = [
                ex for ex in exercises if ex.movement_pattern in slot["patterns"] and ex.id not in used_exercise_ids
            ]

        if not family_candidates:
            family_candidates = [ex for ex in exercises if ex.id not in used_exercise_ids]

        if not family_candidates:
            family_candidates = exercises[:]

        scored_candidates = []
        for cand in family_candidates:
            score = score_exercise_candidate(
                cand,
                history,
                used_exercise_ids,
                used_families,
                target_date,
                level=level,
                location=location,
                sex=sex
            )
            scored_candidates.append((score, cand))

        scored_candidates.sort(key=lambda x: x[0], reverse=True)
        selected_ex = scored_candidates[0][1]

        used_exercise_ids.add(selected_ex.id)
        used_families.add(selected_ex.exercise_family)

        planned_ex = _build_planned_exercise(
            slot=slot,
            selected_ex=selected_ex,
            slot_index=slot_index,
            goal=goal,
            workout_format=workout_format,
            current_weight=current_weight,
            target_weight=target_weight,
            level=level,
            perf_data=perf_map.get(selected_ex.id),
            medical_conditions=medical_conditions or profile.get("medical_conditions")
        )
        planned_exercises.append(planned_ex)

    area_names_en = [FOCUS_DEFINITIONS[f]["name_en"] for f in focus_areas if f in FOCUS_DEFINITIONS]
    area_names_ua = [FOCUS_DEFINITIONS[f]["name_ua"] for f in focus_areas if f in FOCUS_DEFINITIONS]
    if not area_names_en:
        area_names_en = ["Custom Focus"]
        area_names_ua = ["Персональний фокус"]

    day_label = f"Focus Workout: {', '.join(area_names_en)} (10 Exercises)"
    day_label_ua = f"Фокус-тренування: {', '.join(area_names_ua)} (10 вправ)"

    fmt_desc_en, fmt_desc_ua = get_format_descriptions(workout_format)
    target_hr = heart_rate.get_target_zone_for_workout(
        goal=goal,
        workout_format=workout_format,
        age=age,
        custom_max_hr=custom_max_hr
    )

    return WorkoutPlan(
        workout_id=workout_id,
        day_label=day_label,
        day_label_ua=day_label_ua,
        target_duration_minutes=60,
        format_type=workout_format,
        format_description=fmt_desc_en,
        format_description_ua=fmt_desc_ua,
        goal=goal,
        location=location,
        target_hr_zone=target_hr["target_zone_name_en"],
        target_hr_zone_ua=target_hr["target_zone_name_ua"],
        target_hr_bpm_range=target_hr["target_bpm_range"],
        exercises=planned_exercises,
        mode="workout"
    )


# ---------------------------------------------------------------------------
# 13. DYNAMIC JOINT MOBILITY ROUTINE GENERATOR (10 Drills)
# ---------------------------------------------------------------------------
def build_mobility_slots(focus_zones: Optional[List[str]] = None) -> List[Dict]:
    """Builds exactly 10 slots for a dynamic mobility session."""
    valid = [z.lower().strip() for z in (focus_zones or []) if z.lower().strip() in MOBILITY_ZONES]

    slots = []
    if not valid:
        distribution = [
            ("hips", 2),
            ("spine", 2),
            ("shoulders", 2),
            ("ankles", 2),
            ("wrists_neck", 1),
            ("hamstrings", 1)
        ]
        for zone_key, count in distribution:
            z_meta = MOBILITY_ZONES[zone_key]
            for _ in range(count):
                slots.append({
                    "zone_key": zone_key,
                    "zone": z_meta["name_en"],
                    "zone_ua": z_meta["name_ua"],
                    "families": z_meta["families"],
                    "reps": z_meta["default_reps"],
                    "sets": 2,
                    "rest": 25
                })
    else:
        n = len(valid)
        counts = {}
        if n == 1:
            counts[valid[0]] = 6
            other_zones = [z for z in MOBILITY_ZONES if z not in valid]
            for oz in other_zones[:4]:
                counts[oz] = 1
        elif n == 2:
            counts[valid[0]] = 4
            counts[valid[1]] = 4
            other_zones = [z for z in MOBILITY_ZONES if z not in valid]
            for oz in other_zones[:2]:
                counts[oz] = 1
        elif n == 3:
            counts[valid[0]] = 3
            counts[valid[1]] = 3
            counts[valid[2]] = 3
            other_zones = [z for z in MOBILITY_ZONES if z not in valid]
            if other_zones:
                counts[other_zones[0]] = 1
        else:
            remaining = 10
            for idx, z in enumerate(valid):
                if remaining <= 0:
                    break
                share = min(remaining, 2 if idx < 4 else 1)
                counts[z] = counts.get(z, 0) + share
                remaining -= share
            while sum(counts.values()) < 10:
                for z in valid:
                    if sum(counts.values()) >= 10:
                        break
                    counts[z] = counts.get(z, 0) + 1

        for zone_key, count in counts.items():
            z_meta = MOBILITY_ZONES[zone_key]
            for _ in range(count):
                slots.append({
                    "zone_key": zone_key,
                    "zone": z_meta["name_en"],
                    "zone_ua": z_meta["name_ua"],
                    "families": z_meta["families"],
                    "reps": z_meta["default_reps"],
                    "sets": 2,
                    "rest": 25
                })

    return slots[:10]


def generate_mobility_routine(
    focus_zones: Optional[List[str]] = None,
    location: str = "home",
    injuries_to_avoid: Optional[List[str]] = None,
    level: str = "intermediate",
    target_date: Optional[datetime] = None,
    age: int = 30,
    custom_max_hr: Optional[int] = None,
    sex: str = "female",
    exclude_ids: Optional[List[str]] = None
) -> WorkoutPlan:
    """Generates an intelligent 10-exercise dynamic mobility routine."""
    if target_date is None:
        target_date = datetime.now()

    all_exercises = database.get_all_exercises()
    history = database.get_exercise_history()

    # Filter mobility pool
    mobility_pool = [ex for ex in all_exercises if ex.movement_pattern == "Mobility"]
    exercises = filter_exercises(
        mobility_pool,
        location=location,
        injuries_to_avoid=injuries_to_avoid
    )
    if not exercises:
        exercises = mobility_pool[:]

    slots = build_mobility_slots(focus_zones)

    workout_id = f"mob_{target_date.strftime('%Y%m%d_%H%M%S')}"
    planned_exercises: List[PlannedExercise] = []
    used_exercise_ids = set()
    used_families = set()

    for slot_index, slot in enumerate(slots, start=1):
        family_candidates = [
            ex for ex in exercises if ex.exercise_family in slot["families"] and ex.id not in used_exercise_ids
        ]
        if not family_candidates:
            family_candidates = [ex for ex in exercises if ex.exercise_family in slot["families"]]

        if not family_candidates:
            family_candidates = [ex for ex in exercises if ex.id not in used_exercise_ids]

        if not family_candidates:
            family_candidates = exercises[:]

        scored = []
        for cand in family_candidates:
            score = score_exercise_candidate(
                cand,
                history,
                used_exercise_ids,
                used_families,
                target_date,
                level=level,
                location=location,
                sex=sex
            )
            scored.append((score, cand))

        scored.sort(key=lambda x: x[0], reverse=True)
        selected_ex = scored[0][1]

        used_exercise_ids.add(selected_ex.id)
        used_families.add(selected_ex.exercise_family)

        planned_exercises.append(PlannedExercise(
            exercise_id=selected_ex.id,
            name=selected_ex.name,
            name_ua=selected_ex.name_ua,
            zone_en=slot["zone"],
            zone_ua=slot["zone_ua"],
            order_index=slot_index,
            sets=slot["sets"],
            reps=slot["reps"],
            rest_seconds=slot["rest"],
            instructions=selected_ex.instructions,
            instructions_ua=selected_ex.instructions_ua,
            setup=selected_ex.setup,
            execution=selected_ex.execution,
            form_tips=selected_ex.form_tips,
            setup_ua=selected_ex.setup_ua,
            execution_ua=selected_ex.execution_ua,
            form_tips_ua=selected_ex.form_tips_ua,
            notes=f"[{slot['zone']}] — {selected_ex.setup}",
            completed=False,
            actual_reps="",
            actual_weight="",
            joint_stress=selected_ex.joint_stress,
            location=selected_ex.location,
            trx_anchor=selected_ex.trx_anchor,
            is_compound_combo=False,
            equipment_alternatives=selected_ex.equipment_alternatives,
            equipment_alternatives_ua=selected_ex.equipment_alternatives_ua,
            superset_group=f"Mobility Station {slot_index}",
            coach_progression_tip="🌊 Focus on fluid breathing and holding end-ranges with zero joint pain.",
            coach_progression_tip_ua="🌊 Зосередьтеся на плавному диханні та фіксації кінцевих точок без болю.",
            last_weight="",
            last_reps=""
        ))

    valid_zones = [z.lower().strip() for z in (focus_zones or []) if z.lower().strip() in MOBILITY_ZONES]
    if not valid_zones:
        day_label = "Full-Body Dynamic Mobility Flow (10 Exercises)"
        day_label_ua = "Загальний комплекс динамічної мобільності (10 вправ)"
    else:
        names_en = [MOBILITY_ZONES[z]["name_en"] for z in valid_zones]
        names_ua = [MOBILITY_ZONES[z]["name_ua"] for z in valid_zones]
        day_label = f"Targeted Mobility: {', '.join(names_en)} (10 Exercises)"
        day_label_ua = f"Цільова мобільність: {', '.join(names_ua)} (10 вправ)"

    fmt_desc_en = "🧘 Dynamic Mobility Flow: 10 targeted joint mobility drills. Perform 2 sets of 8-10 controlled reps per side with end-range pauses. Rest 20-30s between drills."
    fmt_desc_ua = "🧘 Комплекс динамічної мобільності: 10 вправ на рухливість суглобів. Виконуйте 2 підходи по 8-10 контрольованих повторень на кожну сторону з фіксацією. Відпочинок 20-30 сек."

    target_hr = heart_rate.get_target_zone_for_workout(
        goal="mobility",
        workout_format="mobility",
        age=age,
        custom_max_hr=custom_max_hr
    )

    return WorkoutPlan(
        workout_id=workout_id,
        day_label=day_label,
        day_label_ua=day_label_ua,
        target_duration_minutes=20,
        format_type="mobility",
        format_description=fmt_desc_en,
        format_description_ua=fmt_desc_ua,
        goal="mobility",
        location=location,
        target_hr_zone=target_hr["target_zone_name_en"],
        target_hr_zone_ua=target_hr["target_zone_name_ua"],
        target_hr_bpm_range=target_hr["target_bpm_range"],
        exercises=planned_exercises,
        mode="mobility"
    )

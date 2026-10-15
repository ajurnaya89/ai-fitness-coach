# AI Personal Fitness Coach

An intelligent, local personal training engine tailored for home and gym workouts with smart variety rotation, injury isolation, customizable focus builder, training level selection, and full bilingual support.

---

## Equipment Supported
- **Home Gym**: Adjustable dumbbells, TRX suspension trainer, long & mini resistance bands, towels / sliders, small fitness ball, exercise stick, yoga blocks, bodyweight.
- **Commercial Gym**: Barbells, squat racks, cable crossover towers, leg press, leg extension, lying hamstring curl, lat pulldowns, seated cable rows, smith machines, benches.

---

## Key Features

1. **Injury & Sore Area Isolation**:
   - Isolate and safely exclude exercises stressing specific joints:
     - ✋ **Wrist** (excludes floor palm push-ups/planks; provides forearm, neutral grip, or TRX alternatives).
     - 🦵 **Knee** (excludes deep squats/lunges; provides hip hinge, glute bridge, upper body, and core alternatives).
     - 🛡️ **Lower Back** (excludes heavy bent-over rows/deadlifts).
     - 💪 **Shoulder** (excludes high-shear overhead work).
     - 🦴 **Elbow** (excludes heavy tricep/bicep isolations).
     - 🦶 **Ankle** (excludes jumping/high dorsiflexion).

2. **Training Location (Home vs. Gym)**:
   - **🏠 Home**: Uses home gym gear with creative angles and variable resistance.
   - **🏋️ Gym**: Unlocks commercial gym barbells, cable machines, and isolation stations.

3. **Training Goals & Weight Targets**:
   - **⚡ Strength**: Lower rep ranges (5–8 reps) with extended rest (75–90s).
   - **🏋️ Muscle Gain**: Hypertrophy focus (8–12 reps) with 60s rest.
   - **🔥 Weight Loss**: High metabolic density (12–15 reps, 30–45s rest) with target weight delta calibration.
   - **✨ Toning & Endurance**: High volume (15–20 reps) with continuous tempo (30s rest).
   - **⚖️ Current & Target Weight Tracking**: Automatically calculates deficit/surplus focus.

4. **Workout Methods & Interactive Tabata Counter**:
   - **📋 Standard Sets**: Traditional sets with full prescribed rest.
   - **🔁 Circuit Training**: 10 exercises performed back-to-back with 15s transition; 2–3 rounds total.
   - **⏱️ Tabata Protocol & Interactive Dynamic Counter**:
     - Dedicated interval timer featuring **40 seconds of exercise** followed by **10 seconds of rest**, repeated **8 times** per set.
     - **1-minute rest between sets** (60s set recovery) with clear cycle and set counters.
     - **Loud & dynamic countdown from 10 to the end**: Punchy rising audio tones and visual pulsing heartbeat in the final 10 seconds.
     - **Voice Callouts**: Automatically speaks the name of each exercise out loud on start and previews upcoming movements during rest.
     - Controls: Start / Pause, Interval Skip / Prev, Reset, Audio Effects Toggle (🔊), and Voice Callout Toggle (🗣️).
   - **🥪 "Sandwich" Method (Pyramid Ladder)**: 10 exercises arranged in an ascending then descending pyramid:
     `Ex 1 -> Ex 1+2 -> Ex 1+2+3 ... up to 1..10! Then descend: 2..10, 3..10 ... to Ex 10 alone.`

5. **Advanced Compound Combo Hybrids (29 Combo Exercises)**:
   - Dynamic compound movements for athletic variety and metabolic density:
     - *Dumbbell Squat to Overhead Press (Thrusters)*
     - *Dumbbell Goblet Squat to Bicep Curl*
     - *Dumbbell Clean and Overhead Press*
     - *Dumbbell Step-Up to Overhead Press*
     - *Dumbbell Burpee to Overhead Press*
     - *Dumbbell Renegade Row to Push-Up*
     - *Dumbbell Romanian Deadlift to Upright Row*
     - *Dumbbell Lunge to Hammer Curl*
     - *Dumbbell Side Lunge to Overhead Press*
     - *Dumbbell Sumo Squat to High Pull*
     - *Dumbbell Push-Up to T-Spine Rotation*
     - *TRX Atomic Push-Up (Push-Up to Knee Tuck)*
     - *TRX Squat to Low Row Fluid Combo*
     - *TRX Reverse Lunge to Y-Shoulder Flye*
     - *TRX Single Leg Squat (Pistol) to High Row*
     - *Glute Bridge Hold with Dumbbell Chest Press*
     - *Slider Mountain Climber to Pike Combo*
     - *Resistance Band Squat to Overhead Press*
     - *And many more...*

6. **TRX Anchor Alignment**:
   - **🚪 Door Anchor**: Tailored for home doors (horizontal pulls, chest presses, bicep curls, door squats).
   - **🏗️ Pull-Up Bar / 360° Mount**: Unlocks vertical pull-ups, inverted hangs, and suspended pikes.

7. **Interactive Exercise Completion & Reps Tracking**:
   - Inline **`[✓ Mark Completed]`** button on each exercise card.
   - Real-time session progress bar (`X / 10 Completed`).
   - Track actual weight loads and reps done for each exercise.

8. **Progress & History Dashboard**:
   - Summary cards: Total Workouts Completed, Exercises Finished, Average Rating, Weight Goal Target.
   - History logs table with user notes, fatigue, dates, and cardiovascular telemetry (Average BPM, Zone badge, and Peak HR).

9. **Cardiovascular Heart Rate Training Zones & Physiological Analysis**:
   - **❤️ 5 Physiological Training Zones**: Automatically calibrated to user age ($HR_{max} = 220 - \text{age}$) or optional laboratory-measured $HR_{max}$:
     - **Zone 1 (50%–60% $HR_{max}$)**: Active Recovery & Joint Restoration (prescribed for mobility routines).
     - **Zone 2 (60%–70% $HR_{max}$)**: Optimal Lipid Oxidation / Fat Burning (prescribed for weight loss).
     - **Zone 3 (70%–80% $HR_{max}$)**: Aerobic Tempo & Conditioning (prescribed for circuits and toning).
     - **Zone 4 (80%–90% $HR_{max}$)**: Anaerobic Threshold / Hypertrophic Mechanical Tension (prescribed for muscle gain & strength).
     - **Zone 5 (90%–100% $HR_{max}$)**: Peak Neuromuscular Power & Maximal Effort (prescribed for Tabata intervals).
   - **🎯 Prescribed Workout Target HR**: Every generated session automatically displays its target HR zone and exact BPM range badge.
   - **📊 Post-Workout Telemetry & Physiological Feedback**:
     - Input your workout Average BPM and optional Peak BPM upon completion.
     - Interactive modal compares achieved zone vs target zone with a visual 5-zone gauge.
     - Provides instant coach evaluation in English and Ukrainian evaluating whether today's metabolic/hypertrophic goals were achieved.

10. **Dynamic Joint Mobility & Restoration (10 Drills per Routine)**:
   - **✨ General Full-Body Flow**: Balances 10 mobility drills across the body's kinetic checkpoints: Hips & Pelvis (2), Thoracic Spine & Back (2), Shoulders & Scapulae (2), Ankles & Calves (2), Wrists & Neck (1), Hamstrings & Posterior Chain (1).
   - **🎯 Targeted Focus Routines**: Select specific zones (e.g. Hips, Thoracic Spine, Shoulders, Ankles, Wrists/Neck, Hamstrings) to generate a customized 10-drill joint restoration session.
   - **Safe & Injury-Conscious**: Filters out floor-loaded wrist or knee shear movements if an injury is specified.
   - 2 sets × 8–10 controlled reps per side or 45–60s active articulation with end-range pauses and breathing cues.

11. **Expanded Library (193 Exercises including 31 Mobility Movements)**:
   - Full bilingual support (English / Ukrainian).
   - Step-by-step form guides (**Setup & Stance**, **Execution**, **Pro Tips / Common Mistakes**) for all 193 movements.

---

## How to Run the App

1. Open your **Terminal** app on your Mac.
2. Navigate to the project directory:
   ```bash
   cd "/Users/admin/AI Fitness Coach"
   ```
3. Start the application:
   ```bash
   python3 app.py
   ```
4. Open your web browser at:
   ```text
   http://localhost:8000
   ```
   *(If port 8000 is occupied, it will automatically fallback to 8080, 8081, etc., as printed in your terminal)*.
5. In the top bar:
   - Choose **Home** or **Gym**.
   - Choose **Intermediate** or **Advanced**.
   - Choose **EN** or **UA**.
   - Click **"⚙️ Goals & Settings"** to calibrate your Age, optional Max HR, isolate sore areas (wrist, knee, etc.), set your weight goals, choose your workout method (Standard, Circuit, Tabata, or Sandwich), and set your TRX anchor.
   - Click **"⚡ Generate Weekly Workouts"** for your complete 3-day foundation.
   - Click **"🎯 Focus Workout"** for custom targeted muscle splits.
   - Click **"🧘 Mobility"** to generate a general 10-drill full-body flow or target specific joints (hips, spine, shoulders, ankles, wrists, hamstrings).

---

## 🤖 Google ADK (Agent Development Kit) Architecture

The coach is engineered with Google's **Agent Development Kit (ADK)** framework (`agent.py`) powered by Gemini models (`gemini-2.0-flash`), featuring hierarchical multi-agent delegation and custom tool calling:

### 1. Hierarchical Multi-Agent Structure
- **👑 Root Coordinator (`ai_fitness_coach`)**:
  - The Head Coach orchestrating programming, form analysis, interval conditioning, mobility routines, cardiovascular physiology, and progress tracking.
- **📅 Workout Planner Sub-Agent (`workout_planner`)**:
  - Generates 10-exercise periodized weekly plans (Day A: Upper Push/Quads, Day B: Upper Pull/Hinge, Day C: Full Body) and targeted focus splits with target HR zone metadata.
- **🧘 Technique & Biomechanics Sub-Agent (`technique_coach`)**:
  - Delivers step-by-step form cues, setup/stance instructions, and joint-safe alternatives across 193 catalog exercises in English and Ukrainian.
- **⏱️ Tabata Interval Specialist Sub-Agent (`tabata_specialist`)**:
  - Guides dynamic high-intensity interval conditioning (40s work / 10s rest, 8 cycles/set, 60s recovery between sets) with vocal countdowns.
- **🤸 Mobility & Joint Restoration Sub-Agent (`mobility_specialist`)**:
  - Structures restoring 10-drill mobility flows (general full-body or targeted joint splits across hips, spine, shoulders, ankles, wrists, and hamstrings).
- **❤️ Cardio Physiology Coach Sub-Agent (`cardio_physiology_coach`)**:
  - Computes 5 physiological heart rate training zones ($HR_{max} = 220 - \text{age}$), assigns target zones for fat loss (Zone 2) and muscle building (Zone 3–4), and analyzes post-workout BPM telemetry.

### 2. Custom ADK Tools
1. `generate_weekly_plan`: Generates the foundation 3-day weekly workout program (10 exercises each, 2 focus zones + core always) with target HR metadata.
2. `build_custom_focus_workout`: Builds a tailored 10-exercise session targeting user-requested muscle focus zones with target HR metadata.
3. `generate_mobility_routine`: Builds an intelligent 10-drill mobility flow with Zone 1 active recovery HR metadata.
4. `get_mobility_zones`: Retrieves available anatomical mobility zones and descriptions.
5. `search_exercise_catalog`: Searches the 193-exercise library with filters for equipment, movement pattern, and joint safety.
6. `get_exercise_technique`: Biomechanical breakdown (Setup & Stance, Execution Steps, Pro Tips) for any exercise.
7. `get_tabata_protocol_settings`: Protocol configuration and countdown cues for 40s/10s Tabata.
8. `calculate_heart_rate_zones`: Calculates 5 heart rate training zones and exact BPM ranges based on age and optional custom $HR_{max}$.
9. `get_target_heart_rate_zone`: Prescribes optimal target HR zone and BPM bounds for specific goals and formats.
10. `analyze_workout_heart_rate`: Compares recorded average & peak BPM against target zones and returns bilingual physiological feedback.
11. `log_workout_progress`: Logs completed sessions, updates exercise performance, stores HR telemetry, and maintains cooldown memory.
12. `get_user_progress_metrics`: Retrieves lifetime stats, workout counts, and weight delta tracking.

### 3. How to Run the ADK Agent

#### Option A: Google ADK CLI (Web UI & Inspector)
```bash
pip install google-adk
adk web
# Opens the interactive Google ADK Agent Explorer
```

#### Option B: Standalone Interactive Console Runner
```bash
python3 agent.py
```
Provides an interactive terminal menu [1-7, q] to test weekly plan generation, custom workout builders, exercise search, Tabata pacing, metric tracking, and cardiovascular HR zone telemetry directly.

#### Option C: Web App Integration
The visual web app (`app.py`) exposes agent endpoints:
- `GET /api/agent/info`: Returns ADK agent metadata, sub-agents, and model configuration.
- `POST /api/agent/call`: Executes any of the 12 ADK tools dynamically with parameters.

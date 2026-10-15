"""
Heart Rate Training Zones and Workout Physiology Engine for AI Fitness Coach.
Provides:
- 5-Zone Heart Rate modeling calibrated to user age and max HR.
- Prescribed target HR zones for fat burning, hypertrophy, Tabata, and recovery.
- Post-workout heart rate analysis and personalized coaching feedback.
- Full bilingual English and Ukrainian explanations.
"""

from typing import Dict, Any, Optional, List, Tuple


def calculate_user_max_hr(age: int = 30, custom_max_hr: Optional[int] = None) -> int:
    """Calculates maximum heart rate using the standard Fox formula or user custom value."""
    if custom_max_hr and custom_max_hr > 120:
        return custom_max_hr
    age_clamped = max(15, min(95, age))
    return 220 - age_clamped


def get_heart_rate_zones(age: int = 30, custom_max_hr: Optional[int] = None) -> Dict[str, Any]:
    """
    Computes the 5 physiological heart rate training zones based on user's max HR.

    Zones:
    - Zone 1 (50-60%): Active Recovery & Warm-Up
    - Zone 2 (60-70%): Aerobic & Optimal Fat Burning (Lipid Oxidation)
    - Zone 3 (70-80%): Tempo & Aerobic Power (Cardiovascular Stamina)
    - Zone 4 (80-90%): Anaerobic Threshold & Muscle Building Density
    - Zone 5 (90-100%): Peak Neuromuscular & VO2 Max Bursts (Tabata)
    """
    max_hr = calculate_user_max_hr(age, custom_max_hr)

    z1_min = int(round(max_hr * 0.50))
    z1_max = int(round(max_hr * 0.60)) - 1

    z2_min = int(round(max_hr * 0.60))
    z2_max = int(round(max_hr * 0.70)) - 1

    z3_min = int(round(max_hr * 0.70))
    z3_max = int(round(max_hr * 0.80)) - 1

    z4_min = int(round(max_hr * 0.80))
    z4_max = int(round(max_hr * 0.90)) - 1

    z5_min = int(round(max_hr * 0.90))
    z5_max = max_hr

    zones_list = [
        {
            "zone": 1,
            "name_en": "Zone 1: Active Recovery",
            "name_ua": "Зона 1: Активне відновлення",
            "pct_range": "50%–60%",
            "min_bpm": z1_min,
            "max_bpm": z1_max,
            "bpm_range": f"{z1_min}–{z1_max} BPM",
            "primary_focus_en": "Mobility, joint restoration, warm-up, parasympathetic cool down.",
            "primary_focus_ua": "Мобільність, розминка, заминка, суглобове відновлення.",
            "color": "#38bdf8"
        },
        {
            "zone": 2,
            "name_en": "Zone 2: Fat Burning & Base",
            "name_ua": "Зона 2: Жироспалення та аеробна база",
            "pct_range": "60%–70%",
            "min_bpm": z2_min,
            "max_bpm": z2_max,
            "bpm_range": f"{z2_min}–{z2_max} BPM",
            "primary_focus_en": "Maximum lipid oxidation ('Fat Burning'), mitochondrial density, endurance foundation.",
            "primary_focus_ua": "Максимальне окиснення жирів ('Жироспалення'), мітохондріальна витривалість.",
            "color": "#10b981"
        },
        {
            "zone": 3,
            "name_en": "Zone 3: Tempo & Aerobic Power",
            "name_ua": "Зона 3: Темп та аеробна витривалість",
            "pct_range": "70%–80%",
            "min_bpm": z3_min,
            "max_bpm": z3_max,
            "bpm_range": f"{z3_min}–{z3_max} BPM",
            "primary_focus_en": "Circuits, steady resistance pacing, glycogen + fat hybrid metabolism.",
            "primary_focus_ua": "Кругові тренування, стабільний темп, змішане споживання глікогену та жирів.",
            "color": "#f59e0b"
        },
        {
            "zone": 4,
            "name_en": "Zone 4: Anaerobic / Muscle Building Density",
            "name_ua": "Зона 4: Анаеробний поріг / Набір м'язів",
            "pct_range": "80%–90%",
            "min_bpm": z4_min,
            "max_bpm": z4_max,
            "bpm_range": f"{z4_min}–{z4_max} BPM",
            "primary_focus_en": "Hypertrophic mechanical tension, lactate tolerance, heavy compound density.",
            "primary_focus_ua": "М'язова гіпертрофія, толерантність до лактату, силова щільність.",
            "color": "#f97316"
        },
        {
            "zone": 5,
            "name_en": "Zone 5: Peak Neuromuscular Burst",
            "name_ua": "Зона 5: Пікове анаеробне навантаження",
            "pct_range": "90%–100%",
            "min_bpm": z5_min,
            "max_bpm": z5_max,
            "bpm_range": f"{z5_min}–{z5_max} BPM",
            "primary_focus_en": "Tabata intervals, maximum anaerobic power, explosive output.",
            "primary_focus_ua": "Табата-інтервали, максимальна потужність, вибухова витривалість.",
            "color": "#ef4444"
        }
    ]

    return {
        "max_hr": max_hr,
        "age": age,
        "zones": zones_list
    }


def get_target_zone_for_workout(
    goal: str = "muscle_gain",
    workout_format: str = "standard",
    age: int = 30,
    custom_max_hr: Optional[int] = None
) -> Dict[str, Any]:
    """Determines the prescribed target heart rate zone and BPM range for a workout."""
    zones_data = get_heart_rate_zones(age, custom_max_hr)
    zones = zones_data["zones"]

    fmt = workout_format.lower().strip()
    g = goal.lower().strip()

    if fmt == "mobility":
        target_zone_idx = 1
        name_en = "Zone 1: Active Recovery (50%–60%)"
        name_ua = "Зона 1: Активне відновлення (50%–60%)"
        ideal_min = zones[0]["min_bpm"]
        ideal_max = zones[0]["max_bpm"]
        stimulus_en = "Parasympathetic joint restoration and gentle tissue oxygenation."
        stimulus_ua = "Суглобове відновлення та легке насичення тканин киснем."
    elif fmt == "tabata":
        target_zone_idx = 5
        name_en = "Zone 4–5: High Anaerobic Bursts (85%–95%)"
        name_ua = "Зона 4–5: Пікові анаеробні сплески (85%–95%)"
        ideal_min = int(zones_data["max_hr"] * 0.85)
        ideal_max = int(zones_data["max_hr"] * 0.95)
        stimulus_en = "Dynamic 40s intervals pushing anaerobic threshold with high EPOC afterburn."
        stimulus_ua = "Динамічні 40с інтервали з виходом на анаеробний поріг та пост-тренувальним спалюванням калорій."
    elif g == "weight_loss":
        target_zone_idx = 2
        name_en = "Zone 2: Optimal Fat Burning (60%–70%)"
        name_ua = "Зона 2: Оптимальне жироспалення (60%–70%)"
        ideal_min = zones[1]["min_bpm"]
        ideal_max = zones[1]["max_bpm"]
        stimulus_en = "Optimal lipid oxidation window where fats serve as the primary fuel source."
        stimulus_ua = "Оптимальне вікно окиснення жирів, де ліпіди є основним джерелом енергії."
    elif g in ["muscle_gain", "strength"]:
        target_zone_idx = 4
        name_en = "Zone 3–4: Hypertrophy & Muscle Building (75%–88%)"
        name_ua = "Зона 3–4: Сила та набір м'язів (75%–88%)"
        ideal_min = int(zones_data["max_hr"] * 0.75)
        ideal_max = int(zones_data["max_hr"] * 0.88)
        stimulus_en = "High mechanical tension and muscle recruitment with inter-set heart rate drops."
        stimulus_ua = "Високе механічне напруження для росту м'язів із відновленням пульсу між підходами."
    else:  # toning, circuit, standard
        target_zone_idx = 3
        name_en = "Zone 2–3: Aerobic Conditioning & Toning (65%–78%)"
        name_ua = "Зона 2–3: Тонус та аеробна витривалість (65%–78%)"
        ideal_min = int(zones_data["max_hr"] * 0.65)
        ideal_max = int(zones_data["max_hr"] * 0.78)
        stimulus_en = "Sustained athletic conditioning with balanced calorie burn and muscular endurance."
        stimulus_ua = "Збалансоване спалювання калорій та розвиток м'язової витривалості."

    return {
        "target_zone_number": target_zone_idx,
        "target_zone_name_en": name_en,
        "target_zone_name_ua": name_ua,
        "target_bpm_range": f"{ideal_min}–{ideal_max} BPM",
        "min_bpm": ideal_min,
        "max_bpm": ideal_max,
        "max_hr": zones_data["max_hr"],
        "stimulus_en": stimulus_en,
        "stimulus_ua": stimulus_ua,
        "all_zones": zones
    }


def analyze_workout_heart_rate(
    avg_hr: Optional[int] = None,
    max_hr_recorded: Optional[int] = None,
    min_hr_recorded: Optional[int] = None,
    perceived_difficulty: Optional[int] = None,
    goal: str = "muscle_gain",
    workout_format: str = "standard",
    age: int = 30,
    custom_max_hr: Optional[int] = None,
    medical_conditions: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Analyzes workout heart rate telemetry (Min HR, Max HR, Avg HR) against today's target physiological zone and RPE.
    Detects physiological adaptations:
    - Case 1: Cardio limiting muscles (High HR, high RPE from breathlessness) -> +20-30s rest, replace jumps with controlled tempo.
    - Case 2: Incomplete recovery / Thyroid / Edema alert (Elevated rest HR) -> -20% volume, prioritize supine/seated.
    - Case 3: Optimal stimulus -> Progressive overload unlocked!
    """
    target_info = get_target_zone_for_workout(goal, workout_format, age, custom_max_hr)
    user_max_hr = target_info["max_hr"]

    # Deduce missing heart rate inputs sensibly
    if not avg_hr or avg_hr <= 0:
        if min_hr_recorded and max_hr_recorded:
            avg_hr = int((min_hr_recorded + max_hr_recorded) / 2)
        elif max_hr_recorded:
            avg_hr = int(max_hr_recorded * 0.85)
        else:
            avg_hr = 120

    avg_hr_clamped = max(40, min(230, avg_hr))
    max_hr = max_hr_recorded if max_hr_recorded and max_hr_recorded > 0 else int(min(230, avg_hr_clamped * 1.15))
    min_hr = min_hr_recorded if min_hr_recorded and min_hr_recorded > 0 else int(max(40, avg_hr_clamped * 0.80))
    rpe = perceived_difficulty if perceived_difficulty else 3
    meds = set(m.lower().strip() for m in (medical_conditions or []))

    avg_pct = round((avg_hr_clamped / user_max_hr) * 100)

    # Determine which zone avg_hr landed in
    if avg_pct < 60:
        achieved_zone = 1
        achieved_name_en = "Zone 1: Active Recovery (<60%)"
        achieved_name_ua = "Зона 1: Активне відновлення (<60%)"
    elif avg_pct < 70:
        achieved_zone = 2
        achieved_name_en = "Zone 2: Aerobic / Fat Burning (60%–70%)"
        achieved_name_ua = "Зона 2: Жироспалення (60%–70%)"
    elif avg_pct < 80:
        achieved_zone = 3
        achieved_name_en = "Zone 3: Tempo / Aerobic Power (70%–80%)"
        achieved_name_ua = "Зона 3: Темп та аеробна витривалість (70%–80%)"
    elif avg_pct < 90:
        achieved_zone = 4
        achieved_name_en = "Zone 4: Anaerobic / Hypertrophy (80%–90%)"
        achieved_name_ua = "Зона 4: Анаеробна / Набір м'язів (80%–90%)"
    else:
        achieved_zone = 5
        achieved_name_en = "Zone 5: Peak Neuromuscular (>90%)"
        achieved_name_ua = "Зона 5: Пікове навантаження (>90%)"

    target_min = target_info["min_bpm"]
    target_max = target_info["max_bpm"]

    within_target = (target_min - 4) <= avg_hr_clamped <= (target_max + 6)
    fmt = workout_format.lower().strip()
    g = goal.lower().strip()

    goal_achieved = False
    status_en = ""
    status_ua = ""
    feedback_en = ""
    feedback_ua = ""

    if g == "weight_loss":
        if within_target or achieved_zone == 2:
            goal_achieved = True
            status_en = "🎯 Fat Burning Goal Achieved!"
            status_ua = "🎯 Ціль жироспалення досягнута!"
            feedback_en = (
                f"Outstanding pacing! Your average heart rate of {avg_hr_clamped} BPM ({avg_pct}% of max) "
                f"was locked in the optimal Zone 2 fat oxidation window ({target_min}–{target_max} BPM). "
                f"In this zone, fatty acids provided the dominant energy substrate without excessive muscular fatigue."
            )
            feedback_ua = (
                f"Чудовий темп! Ваш середній пульс {avg_hr_clamped} уд/хв ({avg_pct}% від макс) "
                f"знаходився чітко в зоні активного жироспалення ({target_min}–{target_max} уд/хв). "
                f"Організм використовував жирні кислоти як основне джерело палива без зайвого виснаження м'язів."
            )
        elif avg_hr_clamped > target_max:
            goal_achieved = False
            status_en = "⚡ Above Fat Burning Zone (Anaerobic Glycolysis Shift)"
            status_ua = "⚡ Вище зони жироспалення (Перехід на спалювання глікогену)"
            feedback_en = (
                f"Great intensity ({avg_hr_clamped} BPM, {avg_pct}% of max), but your body shifted from fat burning "
                f"into anaerobic carbohydrate/glycogen burning (Zone {achieved_zone}). For maximum fat oxidation next time, "
                f"allow slightly longer recovery (45–60s) or maintain a smoother rhythm to stay around {target_min}–{target_max} BPM."
            )
            feedback_ua = (
                f"Висока інтенсивність ({avg_hr_clamped} уд/хв, {avg_pct}% від макс), але організм перейшов "
                f"на спалювання вуглеводів/глікогену замість жирів (Зона {achieved_zone}). Для максимального жироспалення "
                f"наступного разу робіть трохи довший відпочинок між підходами, щоб утримувати пульс біля {target_min}–{target_max} уд/хв."
            )
        else:
            goal_achieved = False
            status_en = "⚠️ Below Target Fat Burning Intensity"
            status_ua = "⚠️ Нижче цільової зони жироспалення"
            feedback_en = (
                f"Your session was light ({avg_hr_clamped} BPM, {avg_pct}% of max), remaining in active recovery. "
                f"To trigger meaningful metabolic fat oxidation, increase your workout tempo, reduce rest to 30–45s, "
                f"or add brisk movement to reach {target_min}–{target_max} BPM."
            )
            feedback_ua = (
                f"Навантаження було занадто легким ({avg_hr_clamped} уд/хв, {avg_pct}% від макс), на рівні відновлення. "
                f"Щоб запустити жироспалення, зменшіть час відпочинку до 30-45 сек або збільшіть темп, "
                f"щоб підняти пульс до {target_min}–{target_max} уд/хв."
            )

    elif g in ["muscle_gain", "strength"]:
        if within_target or achieved_zone in [3, 4]:
            goal_achieved = True
            status_en = "💪 Hypertrophy Intensity Goal Achieved!"
            status_ua = "💪 Ціль інтенсивності для росту м'язів досягнута!"
            feedback_en = (
                f"Excellent muscle-building density! Your average heart rate of {avg_hr_clamped} BPM ({avg_pct}% of max) "
                f"demonstrated sufficient mechanical tension and motor unit recruitment (Zone {achieved_zone}) "
                f"without cardiovascular exhaustion, ensuring peak hypertrophic stimulus."
            )
            feedback_ua = (
                f"Чудова щільність для росту м'язів! Середній пульс {avg_hr_clamped} уд/хв ({avg_pct}% від макс) "
                f"забезпечив достатнє механічне напруження та залучення м'язових волокон (Зона {achieved_zone}) "
                f"із адекватним відновленням між підходами для максимальної гіпертрофії."
            )
        elif avg_hr_clamped > target_max:
            goal_achieved = True
            status_en = "🔥 High Metabolic Workload Achieved"
            status_ua = "🔥 Висока метаболічна щільність досягнута"
            feedback_en = (
                f"Very high intensity ({avg_hr_clamped} BPM, {avg_pct}% of max). You generated immense metabolic stress. "
                f"Be mindful to take full prescribed rest (60–90s) between heavy compound lifts so fatigue doesn't compromise force output."
            )
            feedback_ua = (
                f"Дуже висока інтенсивність ({avg_hr_clamped} уд/хв, {avg_pct}% від макс). Створено сильний метаболічний стрес. "
                f"Не забувайте про повноцінний відпочинок (60-90 сек) між базовими підходами, щоб втома не знижувала робочу вагу."
            )
        else:
            goal_achieved = False
            status_en = "⚠️ Low Muscular Output Intensity"
            status_ua = "⚠️ Недостатнє навантаження для росту м'язів"
            feedback_en = (
                f"Your heart rate ({avg_hr_clamped} BPM, {avg_pct}% of max) suggests the resistance load was relatively light. "
                f"To trigger muscle growth, select slightly heavier dumbbells, perform reps closer to technical failure (RPE 7-8), "
                f"and aim to elevate exertion into {target_min}–{target_max} BPM."
            )
            feedback_ua = (
                f"Пульс ({avg_hr_clamped} уд/хв, {avg_pct}% від макс) вказує на відносно легке навантаження. "
                f"Для стимуляції росту м'язів візьміть трохи більшу вагу гантелей та працюйте ближче до відмови (RPE 7-8)."
            )

    elif fmt == "tabata":
        if avg_hr_clamped >= target_min or (max_hr and max_hr >= target_min):
            goal_achieved = True
            status_en = "⏱️ Tabata Anaerobic Peak Achieved!"
            status_ua = "⏱️ Анаеробний пік Табата досягнуто!"
            feedback_en = (
                f"Phenomenal interval drive! Peak HR of {max_hr} BPM reached into high-intensity Zone {achieved_zone}. "
                f"You successfully pushed through the anaerobic threshold, triggering a massive EPOC calorie burn for the next 24 hours."
            )
            feedback_ua = (
                f"Феноменальна інтервальна робота! Піковий пульс {max_hr} уд/хв досяг Зони {achieved_zone}. "
                f"Ви подолали анаеробний поріг, що активує потужне пост-тренувальне спалювання калорій на наступні 24 години."
            )
        else:
            goal_achieved = False
            status_en = "⚠️ Tabata Peak Not Reached"
            status_ua = "⚠️ Пік Табата не досягнуто"
            feedback_en = (
                f"Tabata demands maximum output during the 40s work intervals. Your peak heart rate was {max_hr} BPM. "
                f"Try moving more explosively during the work phases to elevate intensity toward {target_min}+ BPM."
            )
            feedback_ua = (
                f"Протокол Табата вимагає максимальної викладки впродовж 40 сек роботи. Піковий пульс склав {max_hr} уд/хв. "
                f"Працюйте більш вибухово у робочих фазах, щоб підняти пульс до {target_min}+ уд/хв."
            )

    elif fmt in ["mobility", "rehabilitation"]:
        if achieved_zone in [1, 2]:
            goal_achieved = True
            status_en = "🧘 Parasympathetic Recovery Achieved!"
            status_ua = "🧘 Відновлення нервової системи досягнуто!"
            feedback_en = (
                f"Perfect recovery pace ({avg_hr_clamped} BPM, {avg_pct}% of max). Your heart rate stayed low in Zone {achieved_zone}, "
                f"allowing deep joint lubrication, myofascial release, and parasympathetic nervous system down-regulation."
            )
            feedback_ua = (
                f"Ідеальний відновлювальний темп ({avg_hr_clamped} уд/хв, {avg_pct}% від макс). Пульс залишався у Зоні {achieved_zone}, "
                f"забезпечуючи розвантаження суглобів, зняття спазмів та перемикання нервової системи на відновлення."
            )
        else:
            goal_achieved = False
            status_en = "⚡ Pace Was Elevated"
            status_ua = "⚡ Пульс на відновленні був зависокий"
            feedback_en = (
                f"Your heart rate was {avg_hr_clamped} BPM (Zone {achieved_zone}). Restorative work should be relaxing. "
                f"Focus on slow nasal breathing and gentle end-range holds without bracing too intensely."
            )
            feedback_ua = (
                f"Пульс становив {avg_hr_clamped} уд/хв (Зона {achieved_zone}). Відновлювальна робота має розслабляти. "
                f"Зосередьтеся на повільному диханні носом без надмірного напруження."
            )

    else:
        if within_target or achieved_zone in [2, 3]:
            goal_achieved = True
            status_en = "✨ Toning & Endurance Goal Hit!"
            status_ua = "✨ Ціль тонусу та витривалості досягнута!"
            feedback_en = (
                f"Spot-on cardiovascular conditioning! Average heart rate of {avg_hr_clamped} BPM ({avg_pct}% of max) "
                f"provided continuous aerobic stimulation and muscular endurance."
            )
            feedback_ua = (
                f"Відмінна аеробна форма! Середній пульс {avg_hr_clamped} уд/хв ({avg_pct}% від макс) "
                f"забезпечив безперервну роботу серцево-судинної системи та витривалість."
            )
        else:
            goal_achieved = avg_hr_clamped > target_min
            status_en = "🎯 Workout Complete"
            status_ua = "🎯 Тренування завершено"
            feedback_en = f"Workout completed with an average heart rate of {avg_hr_clamped} BPM ({avg_pct}% of max)."
            feedback_ua = f"Тренування завершено із середнім пульсом {avg_hr_clamped} уд/хв ({avg_pct}% від макс)."

    # ---------------------------------------------------------------------------
    # Cross-Analysis with Min HR, Max HR, and RPE (3 Physiological Cases)
    # ---------------------------------------------------------------------------
    min_hr_pct = (min_hr / user_max_hr) * 100

    # Case 2: Incomplete Recovery / High Sympathetic Strain / Thyroid / Edema Alert
    if min_hr_pct > 65 or (min_hr > 120 and rpe >= 4) or ("thyroid" in meds and min_hr_pct > 60):
        physiological_case = "incomplete_recovery"
        physio_title_en = "⚠️ Incomplete Recovery & Sympathetic Strain Alert"
        physio_title_ua = "⚠️ Сигнал неповного відновлення та симпатичного напруження"
        physio_advice_en = (
            f"Your heart rate between sets remained elevated (Min HR: {min_hr} BPM, {round(min_hr_pct)}% of max), "
            f"indicating high accumulated cardiovascular or sympathetic fatigue. For your next session: reduce volume by 15–20%, "
            f"extend rest between sets to 75–90s, prioritize supine/seated positions to lower cardiac preload, "
            f"and avoid high-cortisol exhaustion."
        )
        physio_advice_ua = (
            f"Ваш пульс між підходами залишався зависоким (Мін. пульс: {min_hr} уд/хв, {round(min_hr_pct)}% від макс), "
            f"що свідчить про накопичену втому та перевантаження симпатичної нервової системи. На наступному тренуванні: "
            f"зменшіть об'єм на 15–20%, збільшіть відпочинок до 75–90 сек, надавайте перевагу вправам лежачи/сидячи "
            f"для кращого венозного відтоку та уникайте сплесків кортизолу."
        )

    # Case 1: Cardio Limiting Muscle Output
    elif (max_hr / user_max_hr >= 0.88 and rpe >= 4 and g in ["muscle_gain", "strength"]):
        physiological_case = "cardio_limiting"
        physio_title_en = "⚡ Cardiovascular System Limiting Muscular Output"
        physio_title_ua = "⚡ Серцево-судинна система обмежує м'язове зусилля"
        physio_advice_en = (
            f"Your peak heart rate reached {max_hr} BPM with high exertion (RPE {rpe}). "
            f"Cardiovascular breathlessness became the limiting factor before target muscles reached true mechanical tension. "
            f"Next time: add +20–30s rest before heavy sets, eliminate jumps or rushing, and breathe deeply through the mouth on exertion "
            f"to allow full ATP-CP replenishment so muscle fibers can be trained to true technical failure."
        )
        physio_advice_ua = (
            f"Ваш піковий пульс сягнув {max_hr} уд/хв при високому напруженні (RPE {rpe}). "
            f"Задишка та пульс стали обмежувальним фактором раніше, ніж м'язи отримали повноцінне силове навантаження. "
            f"Наступного разу: додайте +20–30 сек відпочинку перед важкими підходами, приберіть поспіх і глибоко видихайте на зусиллі, "
            f"щоб відновити фосфагенну систему (АТФ) для максимального росту м'язів."
        )

    # Case 3: Optimal Physiological Stimulus
    else:
        physiological_case = "optimal_stimulus"
        physio_title_en = "🎯 Optimal Physiological Adaptation & Progression Unlocked!"
        physio_title_ua = "🎯 Оптимальна фізіологічна адаптація: Прогресія розблокована!"
        physio_advice_en = (
            f"Superb cardiovascular contrast! Strong mechanical drive during work (Max HR: {max_hr} BPM) "
            f"followed by efficient parasympathetic recovery between sets (Min HR: {min_hr} BPM, drop of {max_hr - min_hr} BPM). "
            f"Your neuromuscular and circulatory systems adapted flawlessly. Progressive overload is unlocked for next time: "
            f"aim for +1–2 kg on primary exercises or +1 extra rep with clean form!"
        )
        physio_advice_ua = (
            f"Відмінний фізіологічний контраст! Потужне робоче навантаження (Макс. пульс: {max_hr} уд/хв) "
            f"та ефективне відновлення між підходами (Мін. пульс: {min_hr} уд/хв, зниження на {max_hr - min_hr} уд/хв). "
            f"Організм адаптувався ідеально. Прогресивне перевантаження розблоковано: на наступному тренуванні "
            f"можна сміливо додати +1–2 кг або +1 повторення з чистою технікою!"
        )

    return {
        "status": "success",
        "avg_heart_rate": avg_hr_clamped,
        "max_heart_rate_recorded": max_hr,
        "min_heart_rate_recorded": min_hr,
        "perceived_difficulty": rpe,
        "user_max_hr": user_max_hr,
        "avg_hr_pct": avg_pct,
        "achieved_zone": achieved_zone,
        "achieved_zone_name_en": achieved_name_en,
        "achieved_zone_name_ua": achieved_name_ua,
        "target_zone": target_info["target_zone_number"],
        "target_zone_name_en": target_info["target_zone_name_en"],
        "target_zone_name_ua": target_info["target_zone_name_ua"],
        "target_bpm_range": target_info["target_bpm_range"],
        "goal_achieved": goal_achieved,
        "status_title_en": status_en,
        "status_title_ua": status_ua,
        "feedback_en": feedback_en,
        "feedback_ua": feedback_ua,
        "physiological_case": physiological_case,
        "physio_title_en": physio_title_en,
        "physio_title_ua": physio_title_ua,
        "physio_advice_en": physio_advice_en,
        "physio_advice_ua": physio_advice_ua,
        "all_zones": target_info["all_zones"]
    }

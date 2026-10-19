"""
Dedicated Mobility Exercise Catalog and Translations for AI Fitness Coach.
Defines 31 biomechanically vetted mobility movements across 6 key anatomical zones:
- Hips & Pelvis
- Thoracic Spine & Back
- Shoulders & Scapulae
- Ankles & Calves
- Wrists, Forearms & Neck
- Hamstrings & Posterior Chain
"""

from models import Exercise

MOBILITY_ZONES = {
    "hips": {
        "id": "hips",
        "name_en": "Hips & Pelvis",
        "name_ua": "Стегна та таз",
        "icon": "🦵",
        "families": ["Hip Mobility"],
        "default_reps": "8-10 reps per side / 45s active"
    },
    "spine": {
        "id": "spine",
        "name_en": "Thoracic Spine & Back",
        "name_ua": "Грудний відділ та хребет",
        "icon": "🛡️",
        "families": ["Spinal Mobility"],
        "default_reps": "8-10 smooth pulses / 45s"
    },
    "shoulders": {
        "id": "shoulders",
        "name_en": "Shoulders & Scapulae",
        "name_ua": "Плечі та лопатки",
        "icon": "💪",
        "families": ["Shoulder Mobility"],
        "default_reps": "10 controlled reps / 45s"
    },
    "ankles": {
        "id": "ankles",
        "name_en": "Ankles, Feet & Toes",
        "name_ua": "Гомілкостоп, стопи та пальці ніг",
        "icon": "🦶",
        "families": ["Ankle Mobility", "Foot & Ankle Mobility", "Podiatric Mobility"],
        "default_reps": "10-12 pulses / 40s per leg"
    },
    "wrists_neck": {
        "id": "wrists_neck",
        "name_en": "Wrists & Neck",
        "name_ua": "Зап'ястя та шия",
        "icon": "✋",
        "families": ["Wrist & Neck Mobility"],
        "default_reps": "8-10 fluid cycles / 40s"
    },
    "hamstrings": {
        "id": "hamstrings",
        "name_en": "Hamstrings & Posterior Chain",
        "name_ua": "Задня поверхня стегна",
        "icon": "🏃",
        "families": ["Posterior Chain Mobility", "Hinge Mobility / Technique"],
        "default_reps": "10 waves / 45s"
    },
    "desk_posture": {
        "id": "desk_posture",
        "name_en": "Desk Posture: Open Shoulders & Anti-Hump",
        "name_ua": "💻 Анти-офіс: Розкриття плечей та від холки",
        "icon": "💻",
        "families": ["Desk Posture", "Anti-Hump", "Thoracic Extension", "Pectoral Release"],
        "default_reps": "10-12 reps / 45s"
    }
}

MOBILITY_EXERCISES = [
    # =========================================================================
    # ZONE 1: HIPS & PELVIS
    # =========================================================================
    Exercise(
        id="mob_90_90_hip_flow",
        name="90/90 Hip Internal & External Rotation Flow",
        movement_pattern="Mobility",
        exercise_family="Hip Mobility",
        primary_muscles=["Hip Rotators", "Glutes", "Adductors"],
        secondary_muscles=["Core", "Lower Back"],
        equipment_needed=["yoga mat"],
        difficulty=2,
        stability_demand="Low",
        unilateral=True,
        instructions="Sit with front and back legs at 90 degrees. Hinge forward over front knee, then switch legs smoothly without hands.",
        default_sets=2, default_reps="8-10 each / 45s", rest_seconds=25,
        joint_stress=[], location=["home", "gym"], trx_anchor="any", is_compound_combo=False
    ),
    Exercise(
        id="mob_frog_stretch_rocks",
        name="Frog Stretch with Pelvic Rocking",
        movement_pattern="Mobility",
        exercise_family="Hip Mobility",
        primary_muscles=["Adductors", "Groin", "Hip Joint Capsule"],
        secondary_muscles=["Pelvic Floor", "Core"],
        equipment_needed=["yoga mat"],
        difficulty=2,
        stability_demand="Low",
        unilateral=False,
        instructions="On all fours with knees wide and inner feet flat. Rock hips back gently toward heels to mobilize inner hips.",
        default_sets=2, default_reps="10-12 pulses / 45s", rest_seconds=25,
        joint_stress=["knee"], location=["home", "gym"], trx_anchor="any", is_compound_combo=False
    ),
    Exercise(
        id="mob_worlds_greatest_stretch",
        name="World's Greatest Stretch (Lunge & T-Spine Rotation)",
        movement_pattern="Mobility",
        exercise_family="Hip Mobility",
        primary_muscles=["Hip Flexors", "Hamstrings", "Thoracic Spine"],
        secondary_muscles=["Glutes", "Shoulders"],
        equipment_needed=["yoga mat"],
        difficulty=2,
        stability_demand="Medium",
        unilateral=True,
        instructions="Deep runner lunge with hands inside front foot. Drop inside elbow toward ankle, then rotate torso open reaching arm high.",
        default_sets=2, default_reps="8 each / 45s", rest_seconds=30,
        joint_stress=[], location=["home", "gym"], trx_anchor="any", is_compound_combo=False
    ),
    Exercise(
        id="mob_half_kneeling_psoas_wave",
        name="Half-Kneeling Psoas Wave with Overhead Reach",
        movement_pattern="Mobility",
        exercise_family="Hip Mobility",
        primary_muscles=["Psoas", "Hip Flexors", "Quadriceps"],
        secondary_muscles=["Core", "Lats"],
        equipment_needed=["yoga mat"],
        difficulty=1,
        stability_demand="Low",
        unilateral=True,
        instructions="Half-kneeling stance. Tuck tailbone under, glide hips forward 2 inches, and reach same-side arm overhead with a gentle side bend.",
        default_sets=2, default_reps="8-10 each / 45s", rest_seconds=25,
        joint_stress=[], location=["home", "gym"], trx_anchor="any", is_compound_combo=False
    ),
    Exercise(
        id="mob_active_pigeon_stretch",
        name="Active Pigeon Stretch with Gentle Torso Sweeps",
        movement_pattern="Mobility",
        exercise_family="Hip Mobility",
        primary_muscles=["Gluteus Medius", "Piriformis", "Hip Capsule"],
        secondary_muscles=["Hamstrings", "Lower Back"],
        equipment_needed=["yoga mat"],
        difficulty=2,
        stability_demand="Low",
        unilateral=True,
        instructions="Shin across body in pigeon pose. Slowly sweep torso forward toward floor with flat spine, then inhale to elevate chest.",
        default_sets=2, default_reps="8 each / 45s", rest_seconds=25,
        joint_stress=["knee"], location=["home", "gym"], trx_anchor="any", is_compound_combo=False
    ),
    Exercise(
        id="mob_cossack_mobility_flow",
        name="Cossack Squat Lateral Mobility Flow",
        movement_pattern="Mobility",
        exercise_family="Hip Mobility",
        primary_muscles=["Adductors", "Hamstrings", "Ankles"],
        secondary_muscles=["Glutes", "Quadriceps"],
        equipment_needed=["bodyweight"],
        difficulty=3,
        stability_demand="Medium",
        unilateral=True,
        instructions="Wide stance. Shift into deep side squat with opposite leg extended and toes up. Stay low and glide across to opposite heel.",
        default_sets=2, default_reps="8 each / 45s", rest_seconds=30,
        joint_stress=["knee"], location=["home", "gym"], trx_anchor="any", is_compound_combo=False
    ),
    Exercise(
        id="mob_quadruped_hip_cars",
        name="Quadruped Hip CARs (Controlled Articular Rotations)",
        movement_pattern="Mobility",
        exercise_family="Hip Mobility",
        primary_muscles=["Hip Rotators", "Glutes", "Core"],
        secondary_muscles=["Hip Joint Capsule"],
        equipment_needed=["yoga mat"],
        difficulty=2,
        stability_demand="Medium",
        unilateral=True,
        instructions="Hands and knees. Draw largest circle possible with knee: flex to chest, abduct out to side, rotate into extension, and sweep down.",
        default_sets=2, default_reps="6 each direction / 40s", rest_seconds=25,
        joint_stress=[], location=["home", "gym"], trx_anchor="any", is_compound_combo=False
    ),

    # =========================================================================
    # ZONE 2: THORACIC SPINE & BACK
    # =========================================================================
    Exercise(
        id="mob_segmental_cat_cow",
        name="Segmental Cat-Cow with Wave Articulation",
        movement_pattern="Mobility",
        exercise_family="Spinal Mobility",
        primary_muscles=["Spinal Erectors", "Multifidus", "Core"],
        secondary_muscles=["Shoulders", "Neck"],
        equipment_needed=["yoga mat"],
        difficulty=1,
        stability_demand="Low",
        unilateral=False,
        instructions="All fours. Initiate flexion vertebra by vertebra strictly from tailbone to head, then reverse into extension starting at tailbone.",
        default_sets=2, default_reps="8-10 slow waves / 45s", rest_seconds=20,
        joint_stress=[], location=["home", "gym"], trx_anchor="any", is_compound_combo=False
    ),
    Exercise(
        id="mob_thread_the_needle",
        name="Quadruped Thread-the-Needle T-Spine Rotation",
        movement_pattern="Mobility",
        exercise_family="Spinal Mobility",
        primary_muscles=["Thoracic Spine", "Rhomboids", "Posterior Shoulder"],
        secondary_muscles=["Lats", "Core"],
        equipment_needed=["yoga mat"],
        difficulty=1,
        stability_demand="Low",
        unilateral=True,
        instructions="On all fours with hips sitting back. Slide one arm palm-up under chest to floor, then rotate open reaching high to ceiling.",
        default_sets=2, default_reps="8 each / 45s", rest_seconds=25,
        joint_stress=[], location=["home", "gym"], trx_anchor="any", is_compound_combo=False
    ),
    Exercise(
        id="mob_side_lying_open_book",
        name="Side-Lying Open Book Thoracic Rotation",
        movement_pattern="Mobility",
        exercise_family="Spinal Mobility",
        primary_muscles=["Thoracic Spine", "Pectorals", "Ribcage"],
        secondary_muscles=["Shoulders", "Neck"],
        equipment_needed=["yoga mat", "yoga block"],
        difficulty=1,
        stability_demand="Low",
        unilateral=True,
        instructions="Lie on side with knees bent at 90 deg resting on block. Rotate top arm open across chest toward floor behind you, eyes tracking hand.",
        default_sets=2, default_reps="8-10 each / 45s", rest_seconds=25,
        joint_stress=[], location=["home", "gym"], trx_anchor="any", is_compound_combo=False
    ),
    Exercise(
        id="mob_prone_cobra_extension",
        name="Prone Cobra Thoracic Extension with Scapular Squeeze",
        movement_pattern="Mobility",
        exercise_family="Spinal Mobility",
        primary_muscles=["Thoracic Erectors", "Lower Trapezius", "Rhomboids"],
        secondary_muscles=["Glutes", "Hamstrings"],
        equipment_needed=["yoga mat"],
        difficulty=1,
        stability_demand="Low",
        unilateral=False,
        instructions="Lie face down with arms by sides, thumbs up. Lift chest off mat using mid-back, rotating shoulders open and pinching blades.",
        default_sets=2, default_reps="10 reps with 3s hold / 45s", rest_seconds=25,
        joint_stress=[], location=["home", "gym"], trx_anchor="any", is_compound_combo=False
    ),
    Exercise(
        id="mob_foam_roller_thoracic_arch",
        name="Foam Roller Thoracic Extension with Overhead Reach",
        movement_pattern="Mobility",
        exercise_family="Spinal Mobility",
        primary_muscles=["Thoracic Spine", "Lats", "Intercostals"],
        secondary_muscles=["Pectorals", "Shoulders"],
        equipment_needed=["foam roller", "yoga mat"],
        difficulty=2,
        stability_demand="Low",
        unilateral=False,
        instructions="Roller under mid-back, hands supporting head, hips on floor. Inhale and gently extend upper back over roller across 3 spinal segments.",
        default_sets=2, default_reps="8-10 extensions / 45s", rest_seconds=25,
        joint_stress=[], location=["home", "gym"], trx_anchor="any", is_compound_combo=False
    ),
    Exercise(
        id="mob_childs_pose_side_reach",
        name="Child's Pose with Lat & QL Diagonal Side Reach",
        movement_pattern="Mobility",
        exercise_family="Spinal Mobility",
        primary_muscles=["Latissimus Dorsi", "Quadratus Lumborum", "Thoracolumbar Fascia"],
        secondary_muscles=["Shoulders", "Hips"],
        equipment_needed=["yoga mat"],
        difficulty=1,
        stability_demand="Low",
        unilateral=True,
        instructions="Kneel with hips on heels. Walk hands diagonally to right side and sink left hip back feeling lateral ribcage stretch. Switch sides.",
        default_sets=2, default_reps="5 deep breath cycles each / 45s", rest_seconds=20,
        joint_stress=[], location=["home", "gym"], trx_anchor="any", is_compound_combo=False
    ),

    # =========================================================================
    # ZONE 3: SHOULDERS & SCAPULAE
    # =========================================================================
    Exercise(
        id="mob_prone_ytw_scapular_cars",
        name="Prone Y-T-W Scapular Mobility Flow",
        movement_pattern="Mobility",
        exercise_family="Shoulder Mobility",
        primary_muscles=["Lower Traps", "Middle Traps", "Rotator Cuff"],
        secondary_muscles=["Posterior Deltoids"],
        equipment_needed=["yoga mat"],
        difficulty=2,
        stability_demand="Low",
        unilateral=False,
        instructions="Lie face down. Raise arms into 'Y' (45 deg) with thumbs up, then 'T' (90 deg), then 'W' squeezing shoulder blades down and back.",
        default_sets=2, default_reps="8 rounds of Y-T-W / 45s", rest_seconds=25,
        joint_stress=[], location=["home", "gym"], trx_anchor="any", is_compound_combo=False
    ),
    Exercise(
        id="mob_stick_shoulder_dislocates",
        name="Exercise Stick Shoulder Dislocates (Over-and-Backs)",
        movement_pattern="Mobility",
        exercise_family="Shoulder Mobility",
        primary_muscles=["Pectoralis Major", "Anterior Deltoid", "Rotator Cuff"],
        secondary_muscles=["Upper Traps"],
        equipment_needed=["exercise stick"],
        difficulty=2,
        stability_demand="Low",
        unilateral=False,
        instructions="Wide grip on stick. Keeping elbows straight, lift stick up overhead and rotate shoulders smoothly behind back to touch glutes.",
        default_sets=2, default_reps="10 smooth passes / 40s", rest_seconds=25,
        joint_stress=["shoulder"], location=["home", "gym"], trx_anchor="any", is_compound_combo=False
    ),
    Exercise(
        id="mob_wall_angels",
        name="Standing Wall Angels with Thoracic Flattening",
        movement_pattern="Mobility",
        exercise_family="Shoulder Mobility",
        primary_muscles=["Rotator Cuff", "Scapular Stabilizers", "Thoracic Spine"],
        secondary_muscles=["Shoulders", "Upper Back"],
        equipment_needed=["wall"],
        difficulty=2,
        stability_demand="Low",
        unilateral=False,
        instructions="Back, head, elbows, and wrists against wall. Slide arms vertically overhead like snow angels while keeping wrists in contact with wall.",
        default_sets=2, default_reps="10-12 reps / 45s", rest_seconds=25,
        joint_stress=[], location=["home", "gym"], trx_anchor="any", is_compound_combo=False
    ),
    Exercise(
        id="mob_sleeper_stretch_rotator",
        name="Side-Lying Sleeper Stretch for Posterior Capsule",
        movement_pattern="Mobility",
        exercise_family="Shoulder Mobility",
        primary_muscles=["Infraspinatus", "Teres Minor", "Posterior Capsule"],
        secondary_muscles=["Rotator Cuff"],
        equipment_needed=["yoga mat"],
        difficulty=2,
        stability_demand="Low",
        unilateral=True,
        instructions="Lie on side with bottom elbow bent at 90 deg. Use opposite hand to gently guide wrist down toward floor into internal rotation.",
        default_sets=2, default_reps="8 gentle pulses / 40s each", rest_seconds=25,
        joint_stress=["shoulder"], location=["home", "gym"], trx_anchor="any", is_compound_combo=False
    ),
    Exercise(
        id="mob_banded_shoulder_dislocate",
        name="Resistance Band Overhead Pass-Through & Lat Opener",
        movement_pattern="Mobility",
        exercise_family="Shoulder Mobility",
        primary_muscles=["Pectorals", "Anterior Deltoids", "Lats"],
        secondary_muscles=["Rotator Cuff"],
        equipment_needed=["long resistance band"],
        difficulty=1,
        stability_demand="Low",
        unilateral=False,
        instructions="Hold long resistance band wide with slight stretch. Pass band overhead and back in fluid circles, pausing at tight chest angles.",
        default_sets=2, default_reps="10 smooth passes / 40s", rest_seconds=20,
        joint_stress=[], location=["home", "gym"], trx_anchor="any", is_compound_combo=False
    ),

    # =========================================================================
    # ZONE 4: ANKLES & CALVES
    # =========================================================================
    Exercise(
        id="mob_half_kneeling_ankle_rock",
        name="Half-Kneeling Ankle Dorsiflexion Wall Rock",
        movement_pattern="Mobility",
        exercise_family="Ankle Mobility",
        primary_muscles=["Soleus", "Achilles Tendon", "Talocrural Joint"],
        secondary_muscles=["Gastrocnemius", "Tibialis Anterior"],
        equipment_needed=["yoga mat", "wall"],
        difficulty=1,
        stability_demand="Low",
        unilateral=True,
        instructions="Half-kneeling, front toes 2 inches from wall. Drive knee over 2nd toe until it touches wall without heel lifting off floor.",
        default_sets=2, default_reps="10-12 pulses / 45s each", rest_seconds=25,
        joint_stress=[], location=["home", "gym"], trx_anchor="any", is_compound_combo=False
    ),
    Exercise(
        id="mob_banded_ankle_distraction",
        name="Banded Ankle Joint Talus Distraction Mobilization",
        movement_pattern="Mobility",
        exercise_family="Ankle Mobility",
        primary_muscles=["Talocrural Joint Capsule", "Dorsiflexors"],
        secondary_muscles=["Calves"],
        equipment_needed=["long resistance band", "yoga mat"],
        difficulty=2,
        stability_demand="Low",
        unilateral=True,
        instructions="Thick band anchored low behind, looped across front of ankle crease. Drive knee forward into dorsiflexion under elastic tension.",
        default_sets=2, default_reps="10 reps / 45s each", rest_seconds=25,
        joint_stress=[], location=["home", "gym"], trx_anchor="any", is_compound_combo=False
    ),
    Exercise(
        id="mob_elevated_calf_stretch",
        name="Elevated Deficit Calf & Plantar Fascia Stretch",
        movement_pattern="Mobility",
        exercise_family="Ankle Mobility",
        primary_muscles=["Gastrocnemius", "Soleus", "Plantar Fascia"],
        secondary_muscles=["Achilles Tendon"],
        equipment_needed=["yoga block"],
        difficulty=1,
        stability_demand="Low",
        unilateral=True,
        instructions="Ball of foot on yoga block, heel hanging off. Lower heel down with straight knee for 20s, then with bent knee for 20s.",
        default_sets=2, default_reps="40s per leg", rest_seconds=20,
        joint_stress=["ankle"], location=["home", "gym"], trx_anchor="any", is_compound_combo=False
    ),
    Exercise(
        id="mob_ankle_cars_standing",
        name="Controlled Articular Rotations (Ankle CARs)",
        movement_pattern="Mobility",
        exercise_family="Ankle Mobility",
        primary_muscles=["Tibialis Anterior", "Peroneals", "Ankle Capsule"],
        secondary_muscles=["Foot Intrinsics"],
        equipment_needed=["bodyweight"],
        difficulty=1,
        stability_demand="Low",
        unilateral=True,
        instructions="Seated or standing, lift foot and trace largest possible circle with big toe at a slow 5-second tempo without twisting knee.",
        default_sets=2, default_reps="6 circles each direction / 40s", rest_seconds=20,
        joint_stress=[], location=["home", "gym"], trx_anchor="any", is_compound_combo=False
    ),
    Exercise(
        id="mob_seated_foot_arch_mobilization",
        name="Seated Foot Arch & Toe Flexor Wave",
        movement_pattern="Mobility",
        exercise_family="Ankle Mobility",
        primary_muscles=["Plantar Fascia", "Intrinsic Foot Muscles", "Toes"],
        secondary_muscles=["Calves"],
        equipment_needed=["yoga mat"],
        difficulty=2,
        stability_demand="Low",
        unilateral=False,
        instructions="Kneel with toes tucked under, sitting hips onto heels for 30s. Transition to flat feet and lift knees gently to stretch anterior ankles.",
        default_sets=2, default_reps="40s active cycle", rest_seconds=25,
        joint_stress=[], location=["home", "gym"], trx_anchor="any", is_compound_combo=False
    ),

    # =========================================================================
    # ZONE 5: WRISTS, FOREARMS & NECK
    # =========================================================================
    Exercise(
        id="mob_quadruped_wrist_rocks",
        name="Quadruped Multi-Angle Wrist Rocks",
        movement_pattern="Mobility",
        exercise_family="Wrist & Neck Mobility",
        primary_muscles=["Wrist Flexors", "Wrist Extensors", "Carpal Tunnel"],
        secondary_muscles=["Forearms"],
        equipment_needed=["yoga mat"],
        difficulty=1,
        stability_demand="Low",
        unilateral=False,
        instructions="On all fours. Lean shoulders past fingertips with fingers forward, then side to side with fingers out, then back with fingers toward knees.",
        default_sets=2, default_reps="10 pulses each angle / 45s", rest_seconds=20,
        joint_stress=["wrist"], location=["home", "gym"], trx_anchor="any", is_compound_combo=False
    ),
    Exercise(
        id="mob_reverse_wrist_flexor_lean",
        name="Reverse Palm Wrist Extensor & Fist Flexion Stretch",
        movement_pattern="Mobility",
        exercise_family="Wrist & Neck Mobility",
        primary_muscles=["Wrist Extensors", "Dorsal Ligaments"],
        secondary_muscles=["Forearms"],
        equipment_needed=["yoga mat"],
        difficulty=2,
        stability_demand="Low",
        unilateral=False,
        instructions="Place backs of hands flat on mat with fingers pointing toward each other. Gently lean hips back while closing fingers into loose fists.",
        default_sets=2, default_reps="8-10 pulses / 40s", rest_seconds=20,
        joint_stress=["wrist"], location=["home", "gym"], trx_anchor="any", is_compound_combo=False
    ),
    Exercise(
        id="mob_wrist_prayer_waves",
        name="Standing Prayer & Reverse Prayer Dynamic Wrist Waves",
        movement_pattern="Mobility",
        exercise_family="Wrist & Neck Mobility",
        primary_muscles=["Wrist Joints", "Forearms"],
        secondary_muscles=["Palmaris Longus"],
        equipment_needed=["bodyweight"],
        difficulty=1,
        stability_demand="Low",
        unilateral=False,
        instructions="Press palms together in front of sternum, lowering palms while keeping heels together. Reverse with backs of hands pressed, rolling fluid figure-8 waves.",
        default_sets=2, default_reps="10 wave cycles / 40s", rest_seconds=20,
        joint_stress=[], location=["home", "gym"], trx_anchor="any", is_compound_combo=False
    ),
    Exercise(
        id="mob_cervical_neck_cars",
        name="Controlled Articular Rotations for Cervical Spine (Neck CARs)",
        movement_pattern="Mobility",
        exercise_family="Wrist & Neck Mobility",
        primary_muscles=["Sternocleidomastoid", "Splenius", "Suboccipitals"],
        secondary_muscles=["Upper Trapezius"],
        equipment_needed=["bodyweight"],
        difficulty=1,
        stability_demand="Low",
        unilateral=False,
        instructions="Sit tall with shoulders down. Drop chin to chest, scrape collarbone right, tilt ear to shoulder, gaze upward, and trace smoothly across to left.",
        default_sets=2, default_reps="5 slow circles each direction / 45s", rest_seconds=20,
        joint_stress=[], location=["home", "gym"], trx_anchor="any", is_compound_combo=False
    ),
    Exercise(
        id="mob_levator_scapulae_release",
        name="Active Levator Scapulae & Upper Trapezius Release",
        movement_pattern="Mobility",
        exercise_family="Wrist & Neck Mobility",
        primary_muscles=["Levator Scapulae", "Upper Trapezius"],
        secondary_muscles=["Neck Extensors"],
        equipment_needed=["bodyweight"],
        difficulty=1,
        stability_demand="Low",
        unilateral=True,
        instructions="Sit on one hand to pin shoulder down. Turn head 45 deg away and look down toward armpit. Apply light traction with opposite fingertips for 5 deep breaths.",
        default_sets=2, default_reps="5 breath cycles each / 40s", rest_seconds=20,
        joint_stress=[], location=["home", "gym"], trx_anchor="any", is_compound_combo=False
    ),

    # =========================================================================
    # ZONE 6: HAMSTRINGS & POSTERIOR CHAIN
    # =========================================================================
    Exercise(
        id="mob_elephant_walk_hamstrings",
        name="Standing Elephant Walk Alternating Hamstring Floss",
        movement_pattern="Mobility",
        exercise_family="Posterior Chain Mobility",
        primary_muscles=["Hamstrings", "Sciatic Nerve", "Calves", "Lower Back"],
        secondary_muscles=["Glutes"],
        equipment_needed=["yoga mat", "yoga block"],
        difficulty=1,
        stability_demand="Low",
        unilateral=True,
        instructions="Fold forward with hands on blocks or floor, knees bent. Slowly straighten one leg fully while keeping other bent, alternating like an elephant walking.",
        default_sets=2, default_reps="16 alternating pedals / 45s", rest_seconds=25,
        joint_stress=[], location=["home", "gym"], trx_anchor="any", is_compound_combo=False
    ),
    Exercise(
        id="mob_downward_dog_cobra_wave",
        name="Downward-Facing Dog to Upward Dog / Cobra Flow",
        movement_pattern="Mobility",
        exercise_family="Posterior Chain Mobility",
        primary_muscles=["Hamstrings", "Calves", "Spine", "Shoulders", "Anterior Chain"],
        secondary_muscles=["Core", "Glutes"],
        equipment_needed=["yoga mat"],
        difficulty=2,
        stability_demand="Medium",
        unilateral=False,
        instructions="From downward dog with heels sinking, roll forward like a wave through spine into high plank, lowering hips into cobra with proud chest. Ripple back.",
        default_sets=2, default_reps="8-10 fluid waves / 45s", rest_seconds=30,
        joint_stress=[], location=["home", "gym"], trx_anchor="any", is_compound_combo=False
    ),
    Exercise(
        id="mob_supine_hamstring_nerve_floss",
        name="Supine Active Hamstring Floss & Ankle Pump",
        movement_pattern="Mobility",
        exercise_family="Posterior Chain Mobility",
        primary_muscles=["Hamstrings", "Sciatic Nerve Path"],
        secondary_muscles=["Calves"],
        equipment_needed=["yoga mat"],
        difficulty=1,
        stability_demand="Low",
        unilateral=True,
        instructions="Lie on back holding thigh at 90 deg. Extend lower leg toward ceiling until light stretch, flex toes toward shin, point toes, and bend knee back down.",
        default_sets=2, default_reps="10 reps each / 40s", rest_seconds=20,
        joint_stress=[], location=["home", "gym"], trx_anchor="any", is_compound_combo=False
    ),

    # --- EXPANDED MOBILITY DRILLS (HIPS, SPINE, SHOULDERS, ANKLES, WRISTS, HAMSTRINGS) ---
    Exercise(
        id="mob_couch_quad_hip_flexor",
        name="Couch Quad & Psoas Dynamic Wave",
        movement_pattern="Mobility",
        exercise_family="Hip Mobility",
        primary_muscles=["Quadriceps", "Psoas", "Hip Flexors"],
        secondary_muscles=["Core", "Glutes"],
        equipment_needed=["couch/bench support", "yoga mat"],
        difficulty=2, stability_demand="Low", unilateral=True,
        instructions="Place back knee near couch base with shin vertical against couch cushion. Step front foot forward into lunge. Squeeze trailing glute and pulse hips forward.",
        default_sets=2, default_reps="8-10 pulses each / 45s", rest_seconds=25,
        joint_stress=["knee"], location=["home", "gym"], trx_anchor="any", is_compound_combo=False
    ),
    Exercise(
        id="mob_butterfly_adductor_pulse",
        name="Seated Butterfly Groin & Adductor Active Flutters",
        movement_pattern="Mobility",
        exercise_family="Hip Mobility",
        primary_muscles=["Adductors", "Groin", "Hip Joint Capsule"],
        secondary_muscles=["Pelvic Floor"],
        equipment_needed=["yoga mat"],
        difficulty=1, stability_demand="Low", unilateral=False,
        instructions="Sit tall with soles of feet together, knees dropping wide. Gently pulse knees toward floor with breath, then hinge chest forward over feet for 15s.",
        default_sets=2, default_reps="15 pulses + 15s hold", rest_seconds=20,
        joint_stress=[], location=["home", "gym"], trx_anchor="any", is_compound_combo=False
    ),
    Exercise(
        id="mob_standing_gate_swings",
        name="Standing Hurdle Gate Openers & Closers",
        movement_pattern="Mobility",
        exercise_family="Hip Mobility",
        primary_muscles=["Gluteus Medius", "Hip Rotators", "Groin"],
        secondary_muscles=["Balance Stabilizers"],
        equipment_needed=["bodyweight"],
        difficulty=1, stability_demand="Medium", unilateral=True,
        instructions="Stand tall. Lift right knee to chest height, rotate knee out wide over an imaginary hurdle (open gate), tap floor, then reverse direction (close gate).",
        default_sets=2, default_reps="8 each leg / 40s", rest_seconds=20,
        joint_stress=[], location=["home", "gym"], trx_anchor="any", is_compound_combo=False
    ),
    Exercise(
        id="mob_thoracic_rotations_bench",
        name="Quadruped Thoracic Rotations (Hand on Neck)",
        movement_pattern="Mobility",
        exercise_family="Spinal Mobility",
        primary_muscles=["Thoracic Spine", "Rhomboids"],
        secondary_muscles=["Core", "Neck"],
        equipment_needed=["yoga mat"],
        difficulty=1, stability_demand="Low", unilateral=True,
        instructions="On all fours (or forearms on bench for zero wrist pressure). Place hand behind head. Rotate elbow down to touch opposite forearm, then rotate elbow high to ceiling.",
        default_sets=2, default_reps="8-10 reps each / 40s", rest_seconds=20,
        joint_stress=["wrist"], location=["home", "gym"], trx_anchor="any", is_compound_combo=False
    ),
    Exercise(
        id="mob_open_book_thoracic_reach",
        name="Side-Lying Open Book Thoracic Expansion",
        movement_pattern="Mobility",
        exercise_family="Spinal Mobility",
        primary_muscles=["Thoracic Spine", "Pectorals"],
        secondary_muscles=["Shoulders", "Neck"],
        equipment_needed=["yoga mat"],
        difficulty=1, stability_demand="Low", unilateral=True,
        instructions="Lie on side with knees bent at 90 degrees. Arms extended forward together. Inhale, sweep top arm up and across body, following hand with eyes until upper back opens.",
        default_sets=2, default_reps="8 slow reaches each side", rest_seconds=25,
        joint_stress=[], location=["home", "gym"], trx_anchor="any", is_compound_combo=False
    ),
    Exercise(
        id="mob_prone_scorpions",
        name="Prone Scorpion Dynamic Spinal Rotations",
        movement_pattern="Mobility",
        exercise_family="Spinal Mobility",
        primary_muscles=["Hip Flexors", "Lower Back", "Chest"],
        secondary_muscles=["Glutes"],
        equipment_needed=["yoga mat"],
        difficulty=2, stability_demand="Low", unilateral=True,
        instructions="Lie face down with arms outstretched like a T. Lift right leg and reach right heel across body toward left hand behind back. Alternate sides slowly.",
        default_sets=2, default_reps="6-8 each side / 45s", rest_seconds=25,
        joint_stress=[], location=["home", "gym"], trx_anchor="any", is_compound_combo=False
    ),
    Exercise(
        id="mob_sleeper_rotator_cuff_stretch",
        name="Side-Lying Sleeper Rotator Cuff Stretch",
        movement_pattern="Mobility",
        exercise_family="Shoulder Mobility",
        primary_muscles=["Infraspinatus", "Teres Minor", "Posterior Capsule"],
        secondary_muscles=["Rear Deltoid"],
        equipment_needed=["yoga mat"],
        difficulty=2, stability_demand="Low", unilateral=True,
        instructions="Lie on side with shoulder and elbow at 90 degrees. Use top hand to gently guide wrist down toward floor without pain, holding gentle internal rotation.",
        default_sets=2, default_reps="30s each shoulder", rest_seconds=20,
        joint_stress=["shoulder"], location=["home", "gym"], trx_anchor="any", is_compound_combo=False
    ),
    Exercise(
        id="mob_doorframe_pec_minor_stretch",
        name="Doorframe High-Elbow Pec Minor Opener",
        movement_pattern="Mobility",
        exercise_family="Shoulder Mobility",
        primary_muscles=["Pectoralis Minor", "Anterior Deltoid"],
        secondary_muscles=["Biceps Tendon"],
        equipment_needed=["wall"],
        difficulty=1, stability_demand="Low", unilateral=True,
        instructions="Stand in doorway with elbow bent at 120 degrees resting on doorframe above head height. Step forward through doorway gently expanding chest and shoulder.",
        default_sets=2, default_reps="30s each side", rest_seconds=20,
        joint_stress=["shoulder"], location=["home", "gym"], trx_anchor="any", is_compound_combo=False
    ),
    Exercise(
        id="mob_stick_dislocates_gentle",
        name="Gentle Stick / Towel Shoulder Overhead Dislocates",
        movement_pattern="Mobility",
        exercise_family="Shoulder Mobility",
        primary_muscles=["Shoulders", "Chest", "Scapulae"],
        secondary_muscles=["Lats"],
        equipment_needed=["exercise stick"],
        difficulty=1, stability_demand="Low", unilateral=False,
        instructions="Hold stick or towel with wide grip in front of hips. Keeping arms straight and ribs flat, sweep stick overhead and down behind back in fluid arc. Reverse.",
        default_sets=2, default_reps="10-12 smooth passes", rest_seconds=20,
        joint_stress=["shoulder"], location=["home", "gym"], trx_anchor="any", is_compound_combo=False
    ),
    Exercise(
        id="mob_kneeling_tibialis_anterior_stretch",
        name="Kneeling Shin & Tibialis Anterior Ground Glide",
        movement_pattern="Mobility",
        exercise_family="Ankle Mobility",
        primary_muscles=["Tibialis Anterior", "Anterior Ankle Joint"],
        secondary_muscles=["Peroneals"],
        equipment_needed=["yoga mat"],
        difficulty=1, stability_demand="Low", unilateral=False,
        instructions="Kneel with tops of feet flat on floor. Sit back onto heels gently. Lean hands back slightly to lift knees 1 inch off mat, stretching front of shins and ankles.",
        default_sets=2, default_reps="5 slow knee lifts / 30s", rest_seconds=20,
        joint_stress=["knee"], location=["home", "gym"], trx_anchor="any", is_compound_combo=False
    ),
    Exercise(
        id="mob_standing_slant_board_calf",
        name="Wall Slant Board / Block Dorsiflexion Pulse",
        movement_pattern="Mobility",
        exercise_family="Ankle Mobility",
        primary_muscles=["Gastrocnemius", "Soleus", "Talocrural Joint"],
        secondary_muscles=["Achilles Tendon"],
        equipment_needed=["yoga blocks", "wall"],
        difficulty=1, stability_demand="Low", unilateral=True,
        instructions="Place ball of foot on yoga block or wedge with heel firmly on floor. Lean hips and chest toward wall, gently pulsing knee forward over middle toe.",
        default_sets=2, default_reps="10-12 pulses each / 40s", rest_seconds=20,
        joint_stress=[], location=["home", "gym"], trx_anchor="any", is_compound_combo=False
    ),
    Exercise(
        id="mob_curtsy_ankle_eversion_rock",
        name="Lateral Ankle & Peroneal Rocking Matrix",
        movement_pattern="Mobility",
        exercise_family="Ankle Mobility",
        primary_muscles=["Peroneus Longus", "Lateral Ligaments"],
        secondary_muscles=["Subtalar Joint"],
        equipment_needed=["bodyweight"],
        difficulty=1, stability_demand="Low", unilateral=False,
        instructions="Standing tall with light support. Rock ankles smoothly between outer borders and inner borders, feeling lateral ligaments and foot arches mobilize.",
        default_sets=2, default_reps="15 slow cycles", rest_seconds=20,
        joint_stress=[], location=["home", "gym"], trx_anchor="any", is_compound_combo=False
    ),
    Exercise(
        id="mob_scalene_side_neck_tilt",
        name="Scalene & First-Rib Lateral Neck Release",
        movement_pattern="Mobility",
        exercise_family="Wrist & Neck Mobility",
        primary_muscles=["Scalenes", "Sternocleidomastoid"],
        secondary_muscles=["Upper Trapezius"],
        equipment_needed=["bodyweight"],
        difficulty=1, stability_demand="Low", unilateral=True,
        instructions="Place right hand on left collarbone to anchor first rib. Tilt head right and rotate chin slightly up toward ceiling. Hold breathing deep into upper chest.",
        default_sets=2, default_reps="30s each side", rest_seconds=20,
        joint_stress=[], location=["home", "gym"], trx_anchor="any", is_compound_combo=False
    ),
    Exercise(
        id="mob_wrist_roller_flexion_extension",
        name="Free-Air Wrist Wave Flexion-Extension Rolling",
        movement_pattern="Mobility",
        exercise_family="Wrist & Neck Mobility",
        primary_muscles=["Wrist Flexors", "Wrist Extensors"],
        secondary_muscles=["Forearm Muscles"],
        equipment_needed=["bodyweight"],
        difficulty=1, stability_demand="Low", unilateral=False,
        instructions="Extend arms forward. Open hands wide, flex wrists up 90 deg, then roll fingers down into tight fist and curl knuckles toward forearm. Fluid rolling waves.",
        default_sets=2, default_reps="15-20 fluid waves", rest_seconds=20,
        joint_stress=[], location=["home", "gym"], trx_anchor="any", is_compound_combo=False
    ),
    Exercise(
        id="mob_standing_single_leg_rdl_flow",
        name="Standing Single-Leg Hinge Airplane Flow",
        movement_pattern="Mobility",
        exercise_family="Posterior Chain Mobility",
        primary_muscles=["Hamstrings", "Gluteus Medius"],
        secondary_muscles=["Spinal Erectors"],
        equipment_needed=["bodyweight"],
        difficulty=2, stability_demand="Medium", unilateral=True,
        instructions="Balance on standing leg with soft knee. Hinge forward from hips extending rear leg behind until body is parallel to floor. Hold 2s, squeeze glute to stand.",
        default_sets=2, default_reps="6-8 each leg / 40s", rest_seconds=25,
        joint_stress=[], location=["home", "gym"], trx_anchor="any", is_compound_combo=False
    ),
    Exercise(
        id="mob_inchworm_to_downward_dog",
        name="Inchworm Walkout to Dynamic Downward Dog",
        movement_pattern="Mobility",
        exercise_family="Posterior Chain Mobility",
        primary_muscles=["Hamstrings", "Calves", "Shoulders", "Core"],
        secondary_muscles=["Spine"],
        equipment_needed=["yoga mat"],
        difficulty=2, stability_demand="Medium", unilateral=False,
        instructions="Stand tall. Hinge at hips, place hands on mat and walk hands forward into high plank, then push hips high into downward dog sinking heels. Walk hands back.",
        default_sets=2, default_reps="6-8 walkouts / 45s", rest_seconds=30,
        joint_stress=["wrist"], location=["home", "gym"], trx_anchor="any", is_compound_combo=False
    ),

    # =========================================================================
    # ZONE 7: DESK POSTURE & ANTI-DOWAGER'S HUMP
    # =========================================================================
    Exercise(
        id="posture_chin_tuck_wall_angel",
        name="Cervical Chin-Tuck + Wall Angel Slide (Anti-Hump C7-T1 Correction)",
        movement_pattern="Mobility",
        exercise_family="Desk Posture",
        primary_muscles=["Deep Cervical Flexors", "Lower Trapezius", "Rhomboids"],
        secondary_muscles=["Posterior Deltoids", "Thoracic Spine"],
        equipment_needed=["bodyweight"],
        difficulty=2, stability_demand="Low", unilateral=False,
        instructions="Stand with head, back and elbows against wall. Gently retract chin into double chin to align C7-T1. Slide forearms up wall into 'Y', hold 2s, slide down smoothly.",
        default_sets=3, default_reps="10-12 slides / 45s", rest_seconds=25,
        joint_stress=[], location=["home", "gym"], trx_anchor="any", is_compound_combo=False
    ),
    Exercise(
        id="posture_roller_chest_opener",
        name="Longitudinal Foam Roller Chest & Anterior Shoulder Opener (Snow Angels on Roller)",
        movement_pattern="Mobility",
        exercise_family="Desk Posture",
        primary_muscles=["Pectoralis Major & Minor", "Anterior Deltoids"],
        secondary_muscles=["Thoracic Spine", "Diaphragm"],
        equipment_needed=["foam roller", "yoga mat"],
        difficulty=1, stability_demand="Low", unilateral=False,
        instructions="Lie lengthwise along foam roller supporting head and tailbone. Open arms wide and sweep slowly like snow angels, breathing deeply into ribs and collarbones.",
        default_sets=2, default_reps="10-12 slow sweeps / 60s", rest_seconds=20,
        joint_stress=[], location=["home", "gym"], trx_anchor="any", is_compound_combo=False
    ),
    Exercise(
        id="posture_band_w_external_rotation",
        name="Standing Band 'W' External Shoulder Rotation & Scapular Depression",
        movement_pattern="Mobility",
        exercise_family="Desk Posture",
        primary_muscles=["Infraspinatus", "Teres Minor", "Rhomboids"],
        secondary_muscles=["Lower Trapezius", "Posterior Deltoids"],
        equipment_needed=["short/mini resistance bands"],
        difficulty=1, stability_demand="Low", unilateral=False,
        instructions="Elbows bent 90 deg and pinned to ribs. Rotate forearms out into 'W' shape against mini-band, squeezing lower shoulder blades down and back. Hold 2s, return.",
        default_sets=3, default_reps="12-15 reps / 45s", rest_seconds=25,
        joint_stress=[], location=["home", "gym"], trx_anchor="any", is_compound_combo=False
    ),
    Exercise(
        id="posture_prone_diamond_press",
        name="Prone Diamond Scapular Press & C7 Extension (Anti-Hump Lower Trap Activator)",
        movement_pattern="Mobility",
        exercise_family="Desk Posture",
        primary_muscles=["Lower Trapezius", "Serratus Anterior", "Spinal Erectors"],
        secondary_muscles=["Posterior Deltoids", "Deep Neck Extensors"],
        equipment_needed=["yoga mat"],
        difficulty=2, stability_demand="Low", unilateral=False,
        instructions="Prone on mat, hands overhead in diamond shape. Gently retract chin and hover forearms, elbows, and chest 2 inches off floor. Squeeze lower traps below hump. Hold 3s, lower.",
        default_sets=3, default_reps="10-12 reps / 45s", rest_seconds=30,
        joint_stress=[], location=["home", "gym"], trx_anchor="any", is_compound_combo=False
    ),
    Exercise(
        id="posture_cervical_isometric_band",
        name="Gentle Banded Cervical Retraction (Deep Neck Flexor & C7 Alignment)",
        movement_pattern="Mobility",
        exercise_family="Desk Posture",
        primary_muscles=["Deep Cervical Flexors", "Splenius Capitis"],
        secondary_muscles=["Upper Thoracic Erectors"],
        equipment_needed=["short/mini resistance bands", "towels/sliders"],
        difficulty=1, stability_demand="Low", unilateral=False,
        instructions="Loop light band behind base of skull, hold ends in front. Slide head directly backward against light resistance into cervical retraction without tilting chin. Hold 5s, release.",
        default_sets=3, default_reps="8-10 holds (5s each)", rest_seconds=25,
        joint_stress=[], location=["home", "gym"], trx_anchor="any", is_compound_combo=False
    ),
    Exercise(
        id="posture_doorway_pec_minor_release",
        name="Active Pec Minor & Anterior Deltoid Doorway Release",
        movement_pattern="Mobility",
        exercise_family="Desk Posture",
        primary_muscles=["Pectoralis Minor", "Anterior Deltoid"],
        secondary_muscles=["Biceps Short Head", "Subclavius"],
        equipment_needed=["bodyweight"],
        difficulty=1, stability_demand="Low", unilateral=True,
        instructions="Forearm vertically on doorframe at shoulder height. Step forward gently and rotate chest away to feel targeted stretch under collarbone. Hold 25-30s each side.",
        default_sets=2, default_reps="30s each side", rest_seconds=20,
        joint_stress=[], location=["home", "gym"], trx_anchor="any", is_compound_combo=False
    ),

    # =========================================================================
    # ZONE 4 (EXPANDED): PODIATRIC, FOOT & TOES INTRINSIC MOBILITY
    # =========================================================================
    Exercise(
        id="foot_toe_yoga_dissociation",
        name="Toe Yoga: Big Toe Lift vs. 4 Toes Lift Dissociation",
        movement_pattern="Mobility",
        exercise_family="Ankle Mobility",
        primary_muscles=["Extensor Hallucis Longus", "Extensor Digitorum", "Foot Intrinsics"],
        secondary_muscles=["Tibialis Anterior", "Plantar Fascia"],
        equipment_needed=["bodyweight"],
        difficulty=1, stability_demand="Low", unilateral=False,
        instructions="Stand barefoot. Pin 4 small toes down while lifting only big toe up. Pause 2s, lower. Then pin big toe down while lifting 4 small toes fan-like. Alternate fluidly.",
        default_sets=3, default_reps="10-12 alternating cycles / 45s", rest_seconds=20,
        joint_stress=[], location=["home", "gym"], trx_anchor="any", is_compound_combo=False
    ),
    Exercise(
        id="foot_short_foot_arch_doming",
        name="'Short Foot' Intrinsic Arch Doming Hold (Flat Feet & Valgus Correction)",
        movement_pattern="Mobility",
        exercise_family="Ankle Mobility",
        primary_muscles=["Abductor Hallucis", "Plantar Intrinsics", "Tibialis Posterior"],
        secondary_muscles=["Peroneals", "Soleus"],
        equipment_needed=["bodyweight"],
        difficulty=2, stability_demand="Low", unilateral=True,
        instructions="Stand barefoot on tripod foot (heel, big toe base, little toe base). Without curling toes, draw ball of big toe toward heel, doming medial arch. Hold 6s, release.",
        default_sets=3, default_reps="8-10 holds (6s each)", rest_seconds=25,
        joint_stress=[], location=["home", "gym"], trx_anchor="any", is_compound_combo=False
    ),
    Exercise(
        id="foot_ball_plantar_release",
        name="Myofascial Plantar Fascia Roll with Small Ball (Heel to Metatarsals)",
        movement_pattern="Mobility",
        exercise_family="Ankle Mobility",
        primary_muscles=["Plantar Fascia", "Flexor Digitorum Brevis"],
        secondary_muscles=["Achilles Tendon", "Calf Complex"],
        equipment_needed=["small fitness ball"],
        difficulty=1, stability_demand="Low", unilateral=True,
        instructions="Stand or sit with small ball under bare foot. Apply comfortable bodyweight pressure, rolling slowly from heel to metatarsal heads. Pause on tight spots for 5-10s.",
        default_sets=2, default_reps="60s per foot", rest_seconds=20,
        joint_stress=[], location=["home", "gym"], trx_anchor="any", is_compound_combo=False
    ),
    Exercise(
        id="foot_towel_scrunches_spread",
        name="Toe Towel Scrunches & Wide Toe Splay",
        movement_pattern="Mobility",
        exercise_family="Ankle Mobility",
        primary_muscles=["Flexor Hallucis Brevis", "Lumbricals", "Interossei"],
        secondary_muscles=["Plantar Fascia"],
        equipment_needed=["towels/sliders"],
        difficulty=1, stability_demand="Low", unilateral=True,
        instructions="Seated with bare foot on flat towel, heel pinned. Use toes to grab and gather towel toward heel. Spread toes wide into fan, push towel away, repeat.",
        default_sets=2, default_reps="3 towel gathers each foot", rest_seconds=25,
        joint_stress=[], location=["home", "gym"], trx_anchor="any", is_compound_combo=False
    ),
    Exercise(
        id="foot_heel_toe_supination_rock",
        name="Controlled Heel-to-Toe Waves & Outer/Inner Edge Ankle Control",
        movement_pattern="Mobility",
        exercise_family="Ankle Mobility",
        primary_muscles=["Tibialis Anterior", "Gastrocnemius", "Soleus"],
        secondary_muscles=["Peroneals", "Plantar Flexors"],
        equipment_needed=["bodyweight"],
        difficulty=1, stability_demand="Medium", unilateral=False,
        instructions="Stand barefoot, feet parallel. Roll onto balls of feet lifting heels high, then lower heels smoothly and shift weight to heels lifting toes up toward shins. Wave fluidly.",
        default_sets=3, default_reps="12-15 waves / 45s", rest_seconds=20,
        joint_stress=["ankle"], location=["home", "gym"], trx_anchor="any", is_compound_combo=False
    ),
    Exercise(
        id="foot_single_leg_clock_reach",
        name="Single-Leg Barefoot Balance & Tripod Foot Stabilization",
        movement_pattern="Mobility",
        exercise_family="Ankle Mobility",
        primary_muscles=["Tibialis Posterior", "Peroneus Longus", "Foot Intrinsics"],
        secondary_muscles=["Gluteus Medius", "Calf Complex"],
        equipment_needed=["bodyweight"],
        difficulty=2, stability_demand="High", unilateral=True,
        instructions="Barefoot on one leg, knee soft. Reach opposite foot to tap 12 o'clock, 3 o'clock, and 6 o'clock on floor while standing foot roots through tripod with lifted arch.",
        default_sets=3, default_reps="4-5 clock rounds each leg", rest_seconds=30,
        joint_stress=["ankle"], location=["home", "gym"], trx_anchor="any", is_compound_combo=False
    )
]

MOBILITY_TRANSLATIONS = {
    "mob_90_90_hip_flow": [
        "Динамічний перехід 90/90 для кульшових суглобів",
        "Сядьте на підлогу, передня нога зігнута під 90° перед вами, задня під 90° збоку. Спина вертикальна.",
        "Нахиліться вперед над переднім стегном із рівною спиною (пауза 3 сек). Сядьте рівно і плавно переведіть коліна на інший бік без допомоги рук.",
        "Тримайте сідничні кістки максимально притиснутими до підлоги; не округлюйте грудний відділ."
    ],
    "mob_frog_stretch_rocks": [
        "Розтяжка 'жабка' з похитуванням тазу",
        "Встаньте рачки на килимок, розведіть коліна максимально широко, стопи розгорнуті назовні. Передпліччя на підлозі.",
        "На вдиху м'яко подайте таз назад до п'ят, відчуваючи розтягування паху. На видиху поверніться вперед. Зробіть 10 плавних пульсацій.",
        "Тримайте поперек у нейтральному положенні, уникайте надмірного прогину."
    ],
    "mob_worlds_greatest_stretch": [
        "Комплексний випад з ротацією грудного відділу (World's Greatest Stretch)",
        "Глибокий випад уперед, задня нога пряма або з м'яким коліном. Обидві долоні на підлозі біля внутрішнього боку передньої стопи.",
        "Опустіть внутрішній лікоть до передньої щиколотки, потім плавно розверніть корпус і витягніть руку вертикально до стелі. Пауза 2 сек, змініть сторону.",
        "Напружуйте сідницю задньої ноги для розкриття передньої поверхні стегна."
    ],
    "mob_half_kneeling_psoas_wave": [
        "Хвиля для клубово-поперекового м'яза з коліна з витягуванням руки",
        "Позиція на одному коліні (90/90). Підкрутіть таз під себе (задній нахил таза), стисніть сідницю опорної ноги.",
        "Подайте таз уперед на 5-7 см без прогину в попереку. Підніміть однойменну руку вгору та злегка нахиліться вбік. Утримайте 3 сек.",
        "Не прогинайтеся в попереку; натяг має виникати за рахунок підкручування таза та сідниці."
    ],
    "mob_active_pigeon_stretch": [
        "Активна поза голуба з хвилеподібними нахилами",
        "Передня гомілка лежить упоперек килимка, задня нога витягнута назад. Корпус утримується на кінчиках пальців.",
        "Плавно нахиляйте груди до гомілки з прямою спиною. На вдиху піднімайтеся вгору за рахунок м'язів стегна. 8 активних хвиль.",
        "Якщо в коліні є дискомфорт, підкладіть під передню сідницю йога-блок або згорнутий рушник."
    ],
    "mob_cossack_mobility_flow": [
        "Бічні перекати козацьким присідом для рухливості",
        "Надширока стійка, носки злегка розгорнуті назовні.",
        "Опустіться в глибокий бічний присід на одну ногу, пряма нога розвертається носком до стелі. Плавно перекотіться низом на іншу ногу.",
        "П'ята опорної ноги повинна щільно стояти на підлозі. За потреби допомагайте собі пальцями рук."
    ],
    "mob_quadruped_hip_cars": [
        "Кругові обертання стегном рачки (Hip CARs)",
        "Позиція рачки, долоні під плечима, прес напружений.",
        "Підтягніть коліно до грудей, відведіть убік (поза собачки), обертайте стегно назад у розгинання і проведіть униз. Зробіть у зворотному напрямку.",
        "Рухається виключно кульшовий суглоб; таз і спина залишаються абсолютно нерухомими."
    ],
    "mob_segmental_cat_cow": [
        "Сегментарна кішка-корова з поетапною хвилею",
        "Позиція на чотирьох. Нейтральний хребет.",
        "Починайте рух суворо від куприка: підкрутіть таз, округлюйте поперек, потім грудний відділ і нарешті опустіть голову. Повертайтеся в прогин також від куприка.",
        "Рухайтеся хребець за хребцем, ніби пускаєте хвилю вздовж усього тіла."
    ],
    "mob_thread_the_needle": [
        "Протягування нитки в голку рачки (Thread-the-Needle)",
        "Рачки, коліна широко, таз злегка зміщений назад до п'ят.",
        "Просуньте одну руку долонею вгору під грудьми до торкання плечем підлоги. На вдиху відштовхніться та розкрийтеся рукою високо до стелі.",
        "Таз зафіксований на місці; ротація відбувається виключно в грудному відділі."
    ],
    "mob_side_lying_open_book": [
        "Розкриття грудного відділу лежачи на боці ('Відкрита книга')",
        "Лежачи на боці, коліна зігнуті під 90° на йога-блоці. Руки витягнуті вперед перед собою.",
        "На вдиху підніміть верхню руку і розкрийте корпус у протилежний бік до підлоги, погляд за рукою. Видих, пауза 2 сек, плавне повернення.",
        "Щільно притискайте коліна до блоку, щоб виключити скручування в попереку."
    ],
    "mob_prone_cobra_extension": [
        "Поза кобри на животі з ретракцією лопаток",
        "Лежачи на животі, руки вздовж тіла, великі пальці дивляться вгору, лоб над килимком.",
        "Силою м'язів спини підніміть груди, розвертаючи плечі назовні та зводячи лопатки назад і вниз. Пауза 3 сек, плавно опустіться.",
        "Підборіддя притиснуте до шиї; не закидайте голову назад."
    ],
    "mob_foam_roller_thoracic_arch": [
        "Розгинання грудного відділу на пінополіуретановому валику",
        "Сядьте на килимок, валик під серединою спини (нижче лопаток). Долоні підтримують потилицю, таз на підлозі.",
        "На вдиху м'яко прогніться назад через валик, не відриваючи таз. На видиху поверніться. Пересуньте валик на 3 см вище та повторіть.",
        "Не розширюйте ребра і не прогинайтеся в попереку; рух лише у верхній частині спини."
    ],
    "mob_childs_pose_side_reach": [
        "Поза дитини з діагональним витягуванням найширших м'язів",
        "Коліна широко, великі пальці ніг разом. Опустіть таз на п'яти, руки витягнуті вперед.",
        "Переставте обидві руки по діагоналі вправо, потягніться лівим стегном назад у п'яту, розтягуючи лівий бік. Зробіть 5 глибоких вдихів, змініть бік.",
        "Дихайте глибоко в ребра, розширюючи міжреберний простір."
    ],
    "mob_prone_ytw_scapular_cars": [
        "Комплекс Y-T-W лежачи на животі для лопаток",
        "Лежачи на животі, лоб на рушнику. Великі пальці дивляться вгору.",
        "Підніміть руки у формі літери 'Y' (45°), пауза 2 сек; опустіть, підніміть у 'T' (90°), пауза 2 сек; зігніть лікті у 'W' зводячи лопатки.",
        "Ініціюйте рух відведенням лопаток, не напружуючи трапецію біля вух."
    ],
    "mob_stick_shoulder_dislocates": [
        "Кругові переведення гімнастичної палиці через голову",
        "Широкий хват за палицю перед стегнами, прямі руки.",
        "Тримаючи лікті прямими, підніміть палицю через голову та плавно переведіть її за спину до торкання сідниць. Поверніть назад.",
        "Не піднімайте плечі до вух і не прогинайте поперек. Розширте хват, якщо лікті згинаються."
    ],
    "mob_wall_angels": [
        "Стінні янголи для мобільності лопаток та постави",
        "Притисніть потилицю, верх спини та крижі до стіни. Лікті та зап'ястя зігнуті під 90° біля стіни.",
        "Повільно ковзайте руками вгору вздовж стіни, не відриваючи зап'ясть та ребер від стіни. Опустіть лікті вниз, стискаючи лопатки.",
        "Постійний контакт зап'ясть зі стіною — головний показник якісної мобільності плеча."
    ],
    "mob_sleeper_stretch_rotator": [
        "Сліпер-стретч для задньої капсули плеча лежачи на боці",
        "Лежачи на боці, нижнє плече та лікоть під кутом 90°, передпліччя вгору.",
        "Протилежною рукою м'яко спрямовуйте зап'ястя вниз до підлоги у внутрішню ротацію до відчуття приємного натягу. Пауза 5 сек.",
        "Уникайте різкого болю; притискайте плече до килимка, щоб воно не піднімалося вгору."
    ],
    "mob_banded_shoulder_dislocate": [
        "Кругові переведення гумової петлі над головою",
        "Тримайте довгу гумову петлю з легким натягом перед собою.",
        "Розводячи гуму в боки, проведіть руки над головою за спину. Затримайтеся в зоні максимального розкриття грудей на 3 вдихи, потім поверніться.",
        "Еластичність гуми дозволяє безпечно адаптувати траєкторію без перевантаження суглоба."
    ],
    "mob_half_kneeling_ankle_rock": [
        "Похитування в стінку на одне коліно для тильного згинання гомілкостопа",
        "Позиція на одному коліні, носок передньої ноги за 5-7 см від стіни. П'ята щільно притиснута до підлоги.",
        "Подавайте коліно вперед над другим пальцем ноги до торкання стіни без відриву п'яти. Пауза 2 сек, поверніться.",
        "Слідкуйте, щоб склепіння стопи не завалювалося всередину під час згинання."
    ],
    "mob_banded_ankle_distraction": [
        "Мобілізація таранної кістки гомілкостопа з гумовою петлею",
        "Товста гума закріплена позаду біля підлоги та накинута на складку гомілкостопа під кісточками. Крок уперед для натягу.",
        "Згинайте гомілкостоп, подаючи коліно вперед, поки гума тягне таранну кістку назад-униз. 10 плавних повторень на кожну ногу.",
        "Тяга гуми знімає переднє защемлення та суттєво збільшує амплітуду згинання."
    ],
    "mob_elevated_calf_stretch": [
        "Глибоке розтягування литкового м'яза та стопи з підвищення",
        "Подушечка стопи на йога-блоці або сходинці, п'ята вільно звисає вниз.",
        "Опустіть п'яту вниз із прямою ногою на 20 сек (литковий м'яз), потім злегка зігніть коліно на 20 сек (камбалоподібний м'яз).",
        "Тримайтеся за стіну або стійку для стабільності та безпеки."
    ],
    "mob_ankle_cars_standing": [
        "Контрольовані ізольовані кругові обертання стопою (Ankle CARs)",
        "Сидячи або стоячи, підніміть стопу над підлогою.",
        "Великим пальцем ноги повільно малюйте максимально широке коло за 5 секунд: повне витягування, поворот усередину, на себе, назовні.",
        "Гомілка залишається абсолютно нерухомою; не обертайте коліном або стегном."
    ],
    "mob_seated_foot_arch_mobilization": [
        "Мобілізація склепіння стопи та пальців ніг",
        "Опустіться на коліна, підігнувши пальці ніг під себе, сядьте тазом на п'яти на 30 сек.",
        "Дихайте спокійно. Потім перейдіть на підйом стопи та злегка відірвіть коліна від килимка, розтягуючи передню поверхню гомілкостопа.",
        "Якщо натяг занадто інтенсивний, спирайтеся руками на підлогу перед собою."
    ],
    "mob_quadruped_wrist_rocks": [
        "Похитування на чотирьох для зап'ясть у різних кутах",
        "Позиція рачки, пальці вперед.",
        "Подайте плечі вперед за кінчики пальців, потім розверніть пальці в боки і похитайтеся вліво-вправо, потім пальці до колін — похитування назад.",
        "Долоні та основа пальців мають бути повністю притиснуті до килимка."
    ],
    "mob_reverse_wrist_flexor_lean": [
        "Розтяжка тильного боку зап'ястя з кулаками",
        "Покладіть тильний бік долонь на килимок пальцями один до одного.",
        "М'яко подайтеся тазом назад, злегка стискаючи пальці в нещільні кулаки. Відчуйте натяг по тильній поверхні передпліччя.",
        "Дійте дуже делікатно, не застосовуйте надмірну силу."
    ],
    "mob_wrist_prayer_waves": [
        "Динамічні хвилі зап'ясть у позі молитви",
        "З'єднайте долоні перед грудьми в молитовній позі, лікті широко.",
        "Опускайте долоні до талії, утримуючи основи кистей разом. Потім з'єднайте тильні боки долонь і пустіть плавні хвилі у формі вісімки.",
        "Ідеальна безконтактна вправа для тих, у кого є дискомфорт при опорі на долоні."
    ],
    "mob_cervical_neck_cars": [
        "Контрольовані плавні обертання шиєю (Neck CARs)",
        "Сядьте або встаньте прямо, плечі опущені вниз.",
        "Притисніть підборіддя до грудей, проведіть ним уздовж правої ключиці, нахиліть праве вухо до плеча, плавно погляньте вгору та переведіть коло вліво.",
        "Не заламуйте шию назад; відчувайте витягування верхівки голови вгору."
    ],
    "mob_levator_scapulae_release": [
        "Активне зняття напруги з м'яза-підіймача лопатки та трапецій",
        "Сядьте на одну долоню, щоб зафіксувати плече внизу. Поверніть голову на 45° в інший бік і подивіться вниз у пахву.",
        "Протилежною рукою створіть легкий спрямовуючий тиск на потилицю на 5 глибоких циклів дихання. Змініть бік.",
        "Тиск має бути мінімальним (вага руки); ніколи не тягніть шию силою."
    ],
    "mob_elephant_walk_hamstrings": [
        "Динамічний 'слоник' з почерговим випрямленням колін для задньої поверхні",
        "Нахиліться вперед з м'якими колінами, долоні на підлозі або йога-блоках.",
        "Живіт притиснутий до стегон. Повільно випрямляйте одне коліно, тримаючи інше зігнутим. Потім плавно чергуйте ноги, як кроки слона.",
        "Контакт живота зі стегнами захищає поперек і фокусує натяг строго на підколінних сухожиллях."
    ],
    "mob_downward_dog_cobra_wave": [
        "Динамічна хвиля: собака мордою вниз — собака мордою вгору",
        "Позиція собаки мордою вниз: таз угору, п'яти тягнуться до підлоги, груди до стегон.",
        "Підніміться на носки та пустіть хвилю хребтом уперед у планку, потім опустіть таз у собаку мордою вгору або кобру з розкритими грудьми. Відкотіться назад.",
        "Рухайтеся плавно, синхронізуючи хвилю хребта з глибоким диханням."
    ],
    "mob_supine_hamstring_nerve_floss": [
        "Мобілізація сідничного нерва та задньої поверхні стегна лежачи на спині",
        "Лежачи на спині, тримайте стегно обома руками під кутом 90°.",
        "Розгинайте ногу вгору до легкого натягу. У верхній точці натягніть носок на себе, потім витягніть від себе і зігніть коліно. 10 повторень.",
        "Вправа м'яко ковзає нервовим стовбуром без перевантаження зв'язок."
    ],
    "mob_couch_quad_hip_flexor": [
        "Розтяжка квадрицепса та стегна на дивані",
        "Коліно біля основи дивана, гомілка вертикально вгору на подушці дивана. Інша нога у випаді попереду.",
        "Стисніть сідницю ззаду, підкрутіть таз і подайтеся вперед до глибокого розтягу передньої поверхні стегна. Пульсуйте плавно.",
        "Не прогинайтеся в попереку; натяг має бути суворо в квадрицепсі та паху."
    ],
    "mob_butterfly_adductor_pulse": [
        "Метелик з активними помахами для паху",
        "Сидячи прямо, стопи з'єднані разом, коліна широко розведені в боки.",
        "М'яко пульсуйте колінами до підлоги, дихаючи вільно. Потім з рівною спиною нахиліться вперед на 15 сек.",
        "Не округлюйте спину; тягніться грудьми вперед до стоп."
    ],
    "mob_standing_gate_swings": [
        "Відкриття та закриття 'воріт' стоячи для тазу",
        "Стоячи прямо, тримайтеся рукою за стіну для балансу.",
        "Підніміть коліно до грудей, переведіть його по дузі назовні через уявний бар'єр, торкніться підлоги, потім поверніть назад.",
        "Утримуйте таз рівним, рух відбувається в кульшовому суглобі."
    ],
    "mob_thoracic_rotations_bench": [
        "Ротації грудного відділу на чотирьох з рукою на шиї",
        "Позиція рачки або передпліччя на лаві (для розвантаження зап'ясть). Одна рука за головою.",
        "Опустіть лікоть до протилежного передпліччя, потім розкрийтеся грудьми до стелі, проводячи лікоть вгору.",
        "Поперек і таз зафіксовані; обертається лише середня частина спини."
    ],
    "mob_open_book_thoracic_reach": [
        "Відкрита книга лежачи на боці для грудного відділу",
        "Лежачи на боці, коліна під кутом 90° притиснуті до килимка, руки витягнуті вперед.",
        "На вдиху розкрийте верхню руку по дузі назад, проводячи поглядом кисть до торкання лопатки підлоги. На видиху поверніться.",
        "Коліна залишаються склеєними на підлозі."
    ],
    "mob_prone_scorpions": [
        "Скорпіон лежачи на животі для хребта та стегна",
        "Лежачи на животі, руки розведені в боки літерою Т, лоб на килимку.",
        "Підніміть праву ногу і потягніться п'ятою по діагоналі назад до лівої кисті. Плавно поверніться і повторіть в інший бік.",
        "Плечі намагайтеся тримати близько до підлоги."
    ],
    "mob_sleeper_rotator_cuff_stretch": [
        "Сліпер-стретч на боці для ротаторної манжети плеча",
        "Лежачи на боці, плече та лікоть зігнуті під 90° на підлозі.",
        "Верхньою рукою плавно спрямовуйте кисть вниз до підлоги до відчуття м'якого натягу в задній частині плеча. Без болю.",
        "Не тисніть різко; рух має бути дуже делікатним."
    ],
    "mob_doorframe_pec_minor_stretch": [
        "Розкриття малих грудних м'язів у дверному отворі",
        "Стоячи в дверях, лікоть зігнутий під 120° і спирається на одвірок вище голови.",
        "Зробіть крок уперед крізь двері, розкриваючи плече та верхню частину грудей на 30 сек. Змініть бік.",
        "Не випинайте ребра; натяг фокусується у грудному м'язі."
    ],
    "mob_stick_dislocates_gentle": [
        "Плавні прокручування плечей із палицею або рушником",
        "Широкий хват палиці або рушника перед стегнами, руки прямі.",
        "Зберігаючи прямі руки та плоский живіт, переведіть палицю через голову за спину і плавно поверніть вперед.",
        "Якщо руки згинаються, візьміться ширше."
    ],
    "mob_kneeling_tibialis_anterior_stretch": [
        "Мобілізація передньої поверхні гомілки сидячи на п'ятах",
        "Сядьте тазом на п'яти, підйоми стоп плоскі на підлозі.",
        "Обіпріться руками позаду і злегка підніміть коліна на 3-5 см від килимка, розтягуючи передню поверхню гомілкостопа.",
        "Тримайте рух під контролем без різких рухів."
    ],
    "mob_standing_slant_board_calf": [
        "Активні пульсації для гомілкостопу біля стіни",
        "Пальці ноги на йога-блоці або підвищенні, п'ята на підлозі.",
        "Подавайте коліно вперед над другим пальцем стопи в м'яких пульсаціях, розтягуючи ахілл і литковий м'яз.",
        "П'ята не відривається від підлоги."
    ],
    "mob_curtsy_ankle_eversion_rock": [
        "Бічні перекати стопи для зміцнення зв'язок",
        "Стоячи прямо з опорою на стіну або стілець для рівноваги.",
        "Плавно перекочуйте стопи з зовнішнього ребра на внутрішнє, мобілізуючи гомілковостопний суглоб.",
        "Рухайтеся повільно, контролюючи відчуття в суглобах."
    ],
    "mob_scalene_side_neck_tilt": [
        "Зняття напруги з драбинчастих м'язів шиї",
        "Покладіть праву руку на ліву ключицю для фіксації першого ребра.",
        "М'яко нахиліть голову вправо і злегка розверніть підборіддя вгору до стелі на 30 сек. Подихайте в ключицю.",
        "Тягніть делікатно без різких ривків."
    ],
    "mob_wrist_roller_flexion_extension": [
        "Хвильові обертання та розгинання зап'ясть у повітрі",
        "Руки витягнуті вперед перед грудьми, пальці широко розведені.",
        "Підніміть кисті на себе на 90°, потім стисніть у кулаки і зігніть донизу. Плавні хвилеподібні рухи.",
        "Повністю безконтактна розминка передпліч."
    ],
    "mob_standing_single_leg_rdl_flow": [
        "Літачок на одній нозі з витягуванням задньої поверхні",
        "Баланс на одній нозі, опорне коліно м'яке.",
        "Нахиліть прямий корпус уперед, витягуючи задню ногу назад до паралелі з підлогою. Затримайтеся на 2 сек і встаньте.",
        "Таз не розвертайте убік; обидві клубові кістки дивляться вниз."
    ],
    "mob_inchworm_to_downward_dog": [
        "Гусениця з переходом у собаку мордою вниз",
        "Стоячи прямо, нахиліться вперед і поставте долоні на підлогу.",
        "Пройдіть руками вперед у планку, потім виштовхніть таз угору в собаку мордою вниз, потягнувши п'яти до підлоги. Поверніться руками назад.",
        "Коліна можна злегка підігнути при кроках руками."
    ],
    "posture_chin_tuck_wall_angel": [
        "Ретракція шиї (від холки) + ковзання рук по стіні «Янгол»",
        "Станьте спиною, крижами та потилицею до рівної стіни. М'яко втягніть підборіддя назад у подвійне підборіддя.",
        "Притисніть передпліччя до стіни у позицію 'W'. Ковзайте руками вгору в 'Y' без відриву потилиці та ліктів від стіни на 10-12 повторень.",
        "Цей рух прицільно розвантажує перехід шиї в грудний відділ C7-T1, де утворюється холка."
    ],
    "posture_roller_chest_opener": [
        "Поздовжнє розкриття грудного відділу та плечей лежачи вздовж ролу",
        "Ляжте вздовж довгого ролу, куприк та потилиця на ролі, ноги зігнуті на підлозі.",
        "Розкрийте руки широко в сторони долонями до стелі. Повільно ковзайте руками по підлозі у формі 'снігового янгола', дихаючи в ключиці.",
        "Гравітація м'яко розкриває затиснуті грудні м'язи та відновлює правильну поставу."
    ],
    "posture_band_w_external_rotation": [
        "Розведення рук із резинкою у позицію «W» для розвороту плечей назад та проти сутулості",
        "Стоячи рівно, резинка на зап'ястях, лікті 90° притиснуті до боків корпусу.",
        "Не відриваючи ліктів від ребер, розведіть передпліччя назовні у форму 'W'. Зведіть лопатки до центру та вниз на 2 сек паузи.",
        "Плечі опущені вниз від вух. Прицільно усуває загорнуті вперед плечі."
    ],
    "posture_prone_diamond_press": [
        "Підйом передпліч «Діамант» лежачи на животі — прицільна вправа від холки та для постави",
        "Ляжте на живіт, руки над головою у формі 'діаманта' (великі та вказівні пальці торкаються), чоло на рушнику.",
        "М'яко втягніть підборіддя. На видимоху підніміть передпліччя та груди на 5 см від підлоги, утримуючи 3 сек напруження під холкою.",
        "Не прогинайтеся в попереку; напружуйте нижню порцію трапеції та зону між лопатками."
    ],
    "posture_cervical_isometric_band": [
        "М'яка ізометрична ретракція голови назад для усунення холки",
        "Сядьте рівно, стрічка або рушник на потилиці (основа черепа), кінці тримайте руками попереду.",
        "Створіть руками легкий опір і повільно зсувайте голову строго назад по горизонталі. Утримайте 5 сек, плавно відпустіть.",
        "Не закидайте підборіддя вгору; зміцнює глибокі згиначі шиї та усуває основу для холки."
    ],
    "posture_doorway_pec_minor_release": [
        "Активне розкриття малих грудних м'язів та загорнутих плечей у дверному отворі",
        "У дверному отворі покладіть передпліччя вертикально на одвірок на рівні плеча.",
        "Зробіть плавний крок вперед і розверніть корпус у протилежний бік, розтягуючи зону під ключицею 25-30 сек на кожну сторону.",
        "Лопатка опущена вниз. Знімає спазм з малого грудного м'яза."
    ],
    "foot_toe_yoga_dissociation": [
        "«Йога для пальців стоп»: почерговий підйом великого пальця та 4 пальців окремо",
        "Сядьте або станьте босоніж на рівну підлогу.",
        "Притисніть 4 маленьких пальці до підлоги та підніміть тільки великий палець вгору (пауза 2 сек). Потім навпаки: великий палець притиснутий, 4 пальці віялом угору.",
        "Відновлює точний нейром'язовий контроль поздовжнього склепіння стопи."
    ],
    "foot_short_foot_arch_doming": [
        "Вправа «Коротка стопа» — формування та утримання склепіння стопи без підгинання пальців",
        "Станьте босоніж на три точки опори: п'ята, основа великого пальця та основа мізинця.",
        "Не підгинаючи пальці, підтягніть подушечку під великим пальцем до п'яти, піднімаючи внутрішнє склепіння стопи 'будиночком'. Тримайте 6 сек.",
        "Пальці лежать рівно на підлозі, скорочуються саме внутрішні м'язи стопи проти плоскостопості."
    ],
    "foot_ball_plantar_release": [
        "Прокатка стопи та підошовної фасції малим м'ячем від п'яти до пальців",
        "Покладіть тенісний або масажний м'яч під підошву босої стопи.",
        "Створіть комфортний тиск і повільно прокатуйте м'яч уздовж стопи від п'яти до подушечок пальців протягом 60 сек.",
        "На тригерних чутливих точках затримайтеся на 5-10 сек з глибоким диханням."
    ],
    "foot_towel_scrunches_spread": [
        "Збирання рушника пальцями стоп та широке віялове розведення пальців",
        "Сядьте на стілець, рушник розправлений перед босою стопою, п'ята на краю.",
        "Пальцями стопи збирайте та зминайте рушник під себе у напрямку п'яти. Зібравши, розчепірте пальці широко віялом, розправте і повторіть.",
        "П'ята щільно притиснута до підлоги; працюють згиначі пальців."
    ],
    "foot_heel_toe_supination_rock": [
        "Плавні перекати п'ята-носок з контролем завалювання стопи",
        "Станьте босоніж, стопи паралельні на ширині стегон.",
        "Плавно перекочуйтеся вперед на носки з високим підйомом п'ят, потім плавно на п'яти з підйомом носків до гомілок.",
        "Контролюйте, щоб гомілкостоп не завалювався всередину або назовні."
    ],
    "foot_single_leg_clock_reach": [
        "Баланс босоніж на «трикутнику стопи» для стабілізації гомілкостопа",
        "Станьте босоніж на одну ногу, опорне коліно м'яке.",
        "Вільною ногою по черзі торкайтеся умовного циферблату на підлозі на 12, 3 та 6 годин, утримуючи арку опорної стопи піднятою.",
        "Запобігає вальгусному завалюванню стопи та зміцнює зв'язки гомілкостопа."
    ]
}

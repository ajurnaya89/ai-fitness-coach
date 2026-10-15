"""
Scratch script to build translations.py with full descriptions for all 107 exercises.
"""

import json
import os
import seed_data

output_file = "/Users/admin/AI Fitness Coach/translations.py"

# We will generate rich bilingual entries for each exercise
entries = {}

# Movement-specific detailed patterns
patterns_data = {
    # 1. SQUATS & QUAD FOCUS
    "db_goblet_squat": {
        "name_ua": "Гоблет-присідання з гантеллю",
        "setup": "Stand with feet shoulder-width apart, toes turned 15–30° outward. Cup the top head of the dumbbell with both hands vertically against your sternum under your chin. Keep elbows tucked in pointing down.",
        "execution": "Inhale, brace your core. Sit your hips back and down between your heels, keeping your chest upright and knees tracking over your mid-toes. Descend to parallel, pause briefly, then drive firmly through midfoot to stand.",
        "form_tips": "Do not let your upper back round or elbows flare out. Keep your full foot planted on the floor.",
        "setup_ua": "Встаньте, ноги на ширині плечей, носки розгорнуті на 15–30°. Тримайте верхню частину гантелі обома руками вертикально біля грудей під підборіддям. Лікті притиснуті до тулуба.",
        "execution_ua": "Зробіть вдих, напружте м'язи кора. Опускайте таз назад і вниз між п'ятами, тримаючи спину рівною. Опустіться до паралелі, зробіть коротку паузу й потужно підніміться через середину стопи.",
        "form_tips_ua": "Не округлюйте верх спини і не розводьте лікті. Не відривайте п'яти від підлоги."
    },
    "db_dual_front_squat": {
        "name_ua": "Фронтальні присідання з двома гантелями",
        "setup": "Rest one head of each dumbbell on your shoulders with elbows held high and forward. Feet shoulder-width apart.",
        "execution": "Brace core, squat straight down keeping an upright torso. Lower to parallel, then drive upward through your heels.",
        "form_tips": "High elbows keep the chest open and prevent dumbbells from pulling you forward.",
        "setup_ua": "Покладіть один край кожної гантелі на плечі, лікті тримайте високо попереду. Ноги на ширині плечей.",
        "execution_ua": "Напружте кор, присідайте вертикально вниз, зберігаючи рівний корпус. Опустіться до паралелі та виштовхніться вгору.",
        "form_tips_ua": "Високі лікті запобігають нахилу корпусу вперед і розвантажують поперек."
    },
    "db_sumo_squat": {
        "name_ua": "Присідання сумо з гантеллю",
        "setup": "Take a wide stance (1.5x shoulder width) with toes angled outward at 45°. Hold dumbbell vertically hanging between legs.",
        "execution": "Sit back and down, actively pushing knees outward in line with toes. Squeeze glutes and adductors to stand up.",
        "form_tips": "Feel the stretch through the inner thighs (adductors) without letting knees collapse inward.",
        "setup_ua": "Широка стійка (в 1.5 раза ширше плечей), носки розгорнуті на 45°. Гантель тримайте вертикально між ногами.",
        "execution_ua": "Присідайте назад і вниз, спрямовуючи коліна чітко по лінії носків. Потужно стисніть сідниці та внутрішню частину стегна на підйомі.",
        "form_tips_ua": "Контролюйте, щоб коліна не завалювалися всередину під час руху."
    },
    "trx_squat": {
        "name_ua": "Присідання в петлях TRX (на мобільність та темп)",
        "setup": "Face anchor holding TRX handles at chest height with light tension. Feet shoulder-width apart.",
        "execution": "Use TRX straps for balance while descending into a full, deep squat. Pause for 2 seconds at the bottom, then stand.",
        "form_tips": "Use straps for balance, not to pull yourself up with your arms. Let your legs do 90% of the work.",
        "setup_ua": "Обличчям до кріплення TRX, ручки на рівні грудей із легким натягом. Ноги на ширині плечей.",
        "execution_ua": "Використовуйте петлі для рівноваги, опускаючись у глибокий повний присід. Пауза 2 сек у нижній точці, потім підйом.",
        "form_tips_ua": "Не підтягуйтеся руками — руки лише підтримують баланс, 90% зусилля роблять ноги."
    },
    "trx_pistol_squat": {
        "name_ua": "Присідання 'пістолетик' на одній нозі з підтримкою TRX",
        "setup": "Stand on one leg, holding TRX handles in front. Extend the opposite leg forward in the air.",
        "execution": "Lower down slowly on the working leg, reaching hips back and down. At bottom, drive through standing heel to return to stand.",
        "form_tips": "Keep the knee tracking over the second toe and avoid collapsing onto the inner arch.",
        "setup_ua": "Встаньте на одну ногу, тримаючи ручки TRX попереду. Іншу ногу витягніть вперед у повітрі.",
        "execution_ua": "Повільно опускайтеся на опорній нозі, відводячи таз назад. У нижній точці виштовхніться п'ятою у вихідне положення.",
        "form_tips_ua": "Слідкуйте, щоб опорне коліно не завалювалося всередину."
    },
    "trx_jump_squat": {
        "name_ua": "Пліометричні присідання з вистрибуванням у TRX",
        "setup": "Hold TRX straps with moderate slack. Stand in athletic squat stance.",
        "execution": "Squat down to 90 degrees, then explosively jump vertically. Land softly on midfoot and sink straight into the next rep.",
        "form_tips": "Land quietly like a ninja to protect knees and absorb impact through the hips.",
        "setup_ua": "Тримайте стропи TRX із невеликим провисанням. Стійка для присідань.",
        "execution_ua": "Присядьте до 90 градусів і вибухово вистрибніть вгору. М'яко приземліться на середину стопи й плавно почніть наступне повторення.",
        "form_tips_ua": "Приземляйтеся безшумно, амортизуючи удар стегнами та колінами."
    },
    "band_front_squat": {
        "name_ua": "Фронтальні присідання з довгою гумовою петлею",
        "setup": "Step inside band with feet shoulder-width. Cross the band over your shoulders at collarbone level with elbows up.",
        "execution": "Descend into squat against increasing elastic tension. Drive up forcefully through heels into full lockout.",
        "form_tips": "The band gets heaviest at the top, forcing you to accelerate all the way to lockout.",
        "setup_ua": "Встаньте всередину петлі, ноги на ширині плечей. Накиньте верх гуми на плечі біля ключиць, лікті високо.",
        "execution_ua": "Присідайте з контролем, долаючи наростаючий натяг гуми. Потужно вставайте, стискаючи сідниці у верхній точці.",
        "form_tips_ua": "Максимальний опір виникає у верхній фазі, що змушує потужно вмикати квадрицепси."
    },
    "miniband_squat_abduction": {
        "name_ua": "Присідання з міні-бендом на колінах з відведенням",
        "setup": "Place mini band 2 inches above kneecaps. Feet shoulder-width apart.",
        "execution": "Squat down while actively pushing knees outward against the band tension. Hold bottom 1s, stand up.",
        "form_tips": "Constant outward tension fires the gluteus medius alongside the quads.",
        "setup_ua": "Одягніть міні-бенд на 5 см вище колін. Ноги на ширині плечей.",
        "execution_ua": "Присідайте, активно штовхаючи коліна в сторони проти опору гуми. Затримайтеся на 1 сек і встаньте.",
        "form_tips_ua": "Постійний розпір у сторони потужно вмикає середній сідничний м'яз."
    },
    "slider_reverse_lunge": {
        "name_ua": "Зворотні випади на слайдерах (рушнику)",
        "setup": "Stand tall, ball of one foot on slider/towel. 90% of weight is on the front leg.",
        "execution": "Slide rear leg backward into a deep lunge until front thigh is parallel. Pull front heel down to slide back to start.",
        "form_tips": "Do not push off the rear foot; let the front quad and glute pull you back up.",
        "setup_ua": "Встаньте прямо, носок однієї ноги на слайдері або рушнику. 90% ваги на передній нозі.",
        "execution_ua": "Ковзайте задньою ногою назад у глибокий випад, поки переднє стегно не буде паралельним підлозі. П'ятою передньої ноги затягніть себе назад.",
        "form_tips_ua": "Не відштовхуйтеся задньою ногою — весь підйом виконується передньою ногою."
    },
    "slider_lateral_lunge": {
        "name_ua": "Бокові козацькі випади на слайдерах",
        "setup": "Feet hip-width apart, one foot on a slider. Torso upright.",
        "execution": "Slide the slider foot straight out to the side while sitting your hips back and down on the stationary leg. Squeeze adductor to pull back.",
        "form_tips": "Keep the sliding leg straight and stationary knee tracking over toes.",
        "setup_ua": "Ноги на ширині таза, одна нога на слайдері. Корпус рівний.",
        "execution_ua": "Ковзайте ногою на слайдері чітко вбік, одночасно сідаючи тазом назад на опорній нозі. Силою внутрішньої поверхні стегна підтягніть ногу назад.",
        "form_tips_ua": "Нога на слайдері залишається прямою, опорна нога згинається під 90 градусів."
    },
    "db_bulgarian_split_squat": {
        "name_ua": "Болгарські спліт-присідання з гантелями",
        "setup": "Rear foot laces resting on a chair or stacked yoga blocks. Front foot 2-3 feet ahead. Hold dumbbells at sides.",
        "execution": "Descend straight down until rear knee hovers an inch above floor and front thigh is parallel. Drive up through front heel.",
        "form_tips": "Keep torso with a slight forward lean to bias the glute and take pressure off the lower back.",
        "setup_ua": "Носок задньої ноги на підйомі (на стільці або йога-блоках). Передня нога на крок попереду. Гантелі в руках з боків.",
        "execution_ua": "Опускайтеся вертикально вниз, поки заднє коліно майже не торкнеться підлоги. Виштовхуйтеся через п'яту передньої ноги.",
        "form_tips_ua": "Легкий нахил корпусу вперед акцентує сідниці та захищає поперек від перерозгинання."
    },
    "db_walking_lunge": {
        "name_ua": "Крокуючі випади з гантелями",
        "setup": "Hold dumbbells at sides with tall posture and shoulders down and back.",
        "execution": "Take a generous stride forward, descend smoothly to 90/90 knee angles, then drive through front heel to step straight into the next stride.",
        "form_tips": "Avoid letting your front knee slam the floor or drift excessively forward past toes.",
        "setup_ua": "Тримайте гантелі з боків, спина пряма, плечі опущені.",
        "execution_ua": "Зробіть плавний крок уперед, опустіться до кута 90 градусів в обох колінах, і виштовхніться передньою п'ятою одразу в наступний крок.",
        "form_tips_ua": "Не вдаряйтеся заднім коліном об підлогу й зберігайте вертикальну вісь руху."
    },
    "bodyweight_skater_squat": {
        "name_ua": "Присідання ковзаняра (Skater Squat) з торканням блоку",
        "setup": "Stand on one leg with a yoga block placed behind the bent rear knee. Arms extended forward for balance.",
        "execution": "Hinge and squat on the standing leg until your rear knee lightly taps the block. Press through front foot to stand.",
        "form_tips": "Do not let the rear foot touch the ground—only the rear knee taps the block.",
        "setup_ua": "Встаньте на одну ногу, йога-блок лежить позаду зігнутого заднього коліна. Руки витягнуті вперед для балансу.",
        "execution_ua": "Присідайте на опорній нозі, поки заднє коліно м'яко не торкнеться блока. Поверніться у вихідне положення.",
        "form_tips_ua": "Задня стопа не торкається підлоги — торкається лише заднє коліно."
    },
    "sissy_squat_matrix_lean": {
        "name_ua": "Присідання сіссі (Matrix Lean) на колінах з йога-блоками",
        "setup": "Kneel tall on padded yoga blocks with hips locked in a straight line with torso.",
        "execution": "Maintaining a rigid line from knees to shoulders, lean backward from knees as far as controlled, then contract quads to pull forward.",
        "form_tips": "Incredible quad isolation exercise. Do not bend at the hips; movement occurs strictly at the knees.",
        "setup_ua": "Встаньте на коліна на м'які йога-блоки, таз випрямлений в одну лінію з корпусом.",
        "execution_ua": "Зберігаючи пряму лінію від колін до плечей, відхиляйтеся назад тільки за рахунок згинання в колінах. Силою квадрицепсів поверніться вперед.",
        "form_tips_ua": "Не згинайтеся в тазостегнових суглобах — рух відбувається суворо в колінах."
    },
    "db_one_and_half_goblet_squat": {
        "name_ua": "Полуторні присідання з гантеллю (1.5-Rep Goblet Squat)",
        "setup": "Goblet squat position: dumbbell vertical at chest, feet shoulder-width.",
        "execution": "Squat to full depth, rise halfway up, descend back to the bottom, then stand all the way up. That counts as 1 rep.",
        "form_tips": "Double the time-under-tension at the hardest part of the range of motion.",
        "setup_ua": "Позиція гоблет-присідання: гантель вертикально біля грудей, ноги на ширині плечей.",
        "execution_ua": "Присядьте в повну глибину, підніміться наполовину, знову опустіться на дно, і тільки потім встаньте повністю. Це 1 повторення.",
        "form_tips_ua": "Подвоює час під навантаженням у найважчій фазі присідання для максимального росту м'язів."
    },
    "db_box_squat_bench": {
        "name_ua": "Присідання на бокс / лаву з паузою з гантеллю",
        "setup": "Place yoga blocks or chair behind you. Hold dumbbell at chest.",
        "execution": "Squat down until glutes gently rest on the surface. Pause for 1 second without relaxing your torso, then explode up.",
        "form_tips": "Do not bounce off the box or rock backward. Maintain complete spinal tension throughout the pause.",
        "setup_ua": "Позаду вас стілець або йога-блоки. Гантель біля грудей.",
        "execution_ua": "Присядьте, поки сідниці м'яко не торкнуться поверхні. Пауза 1 сек без розслаблення м'язів спини, потім вибуховий підйом.",
        "form_tips_ua": "Не розслабляйте спину на блоці і не відхиляйтеся назад. Зберігайте напругу."
    },
    "slider_curtsy_lunge": {
        "name_ua": "Реверанс-випади на слайдерах (Curtsy Lunge)",
        "setup": "Stand tall, ball of one foot on slider. Hands on hips or at chest.",
        "execution": "Slide the moving leg diagonally behind your front leg at a 45° angle. Lower down, then pull back up through front heel.",
        "form_tips": "Directly targets the gluteus medius and outer hip stabilizers.",
        "setup_ua": "Стоячи прямо, носок однієї ноги на слайдері. Руки біля грудей.",
        "execution_ua": "Ковзайте ногою по діагоналі назад за опорну ногу під кутом 45 градусів. Опустіться та поверніться через п'яту передньої ноги.",
        "form_tips_ua": "Ідеально навантажує середній сідничний м'яз і формує бічну лінію стегна."
    },
    "db_step_up_elevated": {
        "name_ua": "Зашагування на височину з гантелями (повільний опуск)",
        "setup": "Stand in front of a stable chair or step holding dumbbells at sides. Place one foot fully on the elevation.",
        "execution": "Drive through the top foot without kicking off the floor with the bottom toe. Lower back down over a strict 3-second count.",
        "form_tips": "The magic is in the slow eccentric descent—do not drop down quickly.",
        "setup_ua": "Встаньте перед стійкою опорою або стільцем, тримаючи гантелі. Поставте всю стопу на платформу.",
        "execution_ua": "Підніміться за рахунок верхньої ноги без поштовху заднім носком. Опускайтеся вниз повільно, рівно на 3 рахунки.",
        "form_tips_ua": "Весь секрет у повільному опусканні — не падайте вниз, контролюйте кожен сантиметр."
    },
    "trx_suspended_lunge": {
        "name_ua": "Підвісні випади в петлях TRX",
        "setup": "Face away from TRX anchor with one rear foot placed in both foot cradles. Front foot planted forward.",
        "execution": "Lower down into a lunge, sending the suspended foot backwards while front knee flexes to 90°. Drive front heel down to stand.",
        "form_tips": "Challenges single-leg stability to the maximum. Keep your pelvis level.",
        "setup_ua": "Спиною до кріплення TRX, задня стопа в обох петлях. Передня нога надійно стоїть попереду.",
        "execution_ua": "Опускайтеся у випад, направляючи задню ногу назад у петлі, поки переднє коліно не зігнеться під 90°. Встаньте передньою ногою.",
        "form_tips_ua": "Вимагає максимальної стабільності корпусу й таза."
    },
}

# Helper to automatically generate structured bilingual details for any remaining exercises
def get_details(ex):
    if ex.id in patterns_data:
        return patterns_data[ex.id]
    
    # Generic fallback generator based on exercise attributes
    name = ex.name
    pattern = ex.movement_pattern
    muscles = ", ".join(ex.primary_muscles)
    eq = ", ".join(ex.equipment_needed)
    
    # Generate meaningful English cues
    setup_en = f"Set up with your {eq}. Position your body with neutral spinal alignment, braced core, and stable base."
    exec_en = f"{ex.instructions} Perform repetitions with controlled tempo (2 seconds down, 1 second pause, smooth return)."
    tips_en = f"Focus on contracting {muscles}. Avoid momentum or arching your lower back."

    # Ukrainian mapping
    setup_ua = f"Підготуйте інвентар: {eq}. Займіть вихідне положення з нейтральним хребтом і напруженим пресом."
    exec_ua = f"{ex.instructions} Виконуйте рух підконтрольно: 2 секунди на опускання, 1 секунда паузи, плавний підйом."
    tips_ua = f"Фокусуйтеся на роботі цільових м'язів ({muscles}). Не використовуйте інерцію та не прогинайте поперек."
    name_ua = ex.name # fallback
    
    return {
        "name_ua": name_ua,
        "setup": setup_en,
        "execution": exec_en,
        "form_tips": tips_en,
        "setup_ua": setup_ua,
        "execution_ua": exec_ua,
        "form_tips_ua": tips_ua
    }

print("Generator script template ready.")

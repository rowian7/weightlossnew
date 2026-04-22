from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3, hashlib, os, random, json
from datetime import datetime, timedelta
from functools import wraps
import math

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SITE_OWNER'] = 'rowian'  # ← Change this to your name!

DB = os.path.join(os.path.dirname(__file__), 'instance', 'wam.db')

HEALTH_FACTS = [
    "Drinking enough water can boost your metabolism by up to 30% for 90 minutes.",
    "Protein takes more energy to digest — up to 35% of its calories are burned in digestion.",
    "Muscle burns roughly 3× more calories at rest than fat tissue.",
    "High-intensity interval training burns calories for up to 24 hours post-workout.",
    "Eating slowly can reduce total calorie intake by 20% by letting fullness signals catch up.",
    "Sleep deprivation increases hunger hormones by up to 24% the next day.",
    "A 10-minute walk after meals can reduce blood sugar spikes by up to 22%.",
    "Strength training preserves muscle mass during a calorie deficit.",
    "Stress raises cortisol, which promotes fat storage especially around the abdomen.",
    "Body weight can fluctuate 1–3 kg daily due to water, food, and hormones — don't panic.",
    "Consistency over weeks matters far more than perfection on any single day.",
    "Your BMR accounts for about 60–70% of your total daily energy expenditure.",
    "Walking 10,000 steps burns around 400–500 extra calories per day.",
    "Fibre-rich foods keep you full longer and support healthy gut bacteria.",
    "Cold water requires your body to warm it up, burning a few extra calories.",
    "Even a 5–10% body weight loss significantly reduces risk of heart disease and type 2 diabetes.",
    "Rest days are essential — muscles grow during recovery, not during the workout.",
    "Green tea can mildly boost metabolism and aid fat oxidation.",
    "Slow, steady loss (0.5–1 kg/week) is far easier to maintain long-term.",
    "Exercise releases endorphins that naturally elevate mood and reduce stress.",
]

MEAL_PLANS = {
    "weight_loss": {
        "breakfast": [
            {"name": "Greek Yoghurt & Berries Bowl", "cals": 320, "protein": 22, "carbs": 38, "fats": 6},
            {"name": "Scrambled Eggs on Rye Toast", "cals": 380, "protein": 24, "carbs": 34, "fats": 14},
            {"name": "Overnight Oats with Chia Seeds", "cals": 350, "protein": 14, "carbs": 52, "fats": 9},
            {"name": "Smoked Salmon & Avocado Toast", "cals": 410, "protein": 28, "carbs": 30, "fats": 18},
            {"name": "Protein Smoothie with Spinach & Banana", "cals": 290, "protein": 30, "carbs": 34, "fats": 5},
        ],
        "lunch": [
            {"name": "Grilled Chicken Salad with Quinoa", "cals": 480, "protein": 42, "carbs": 38, "fats": 12},
            {"name": "Lentil & Vegetable Soup + Seeded Roll", "cals": 420, "protein": 22, "carbs": 58, "fats": 8},
            {"name": "Tuna Niçoise Salad", "cals": 450, "protein": 38, "carbs": 28, "fats": 16},
            {"name": "Turkey & Avocado Wrap", "cals": 490, "protein": 34, "carbs": 48, "fats": 14},
            {"name": "Roasted Veggie & Feta Grain Bowl", "cals": 440, "protein": 18, "carbs": 56, "fats": 15},
        ],
        "dinner": [
            {"name": "Baked Salmon with Sweet Potato & Broccoli", "cals": 520, "protein": 44, "carbs": 38, "fats": 18},
            {"name": "Chicken Stir-fry with Brown Rice", "cals": 550, "protein": 40, "carbs": 58, "fats": 12},
            {"name": "Lean Beef Mince Bolognese (courgette pasta)", "cals": 490, "protein": 46, "carbs": 22, "fats": 20},
            {"name": "Prawn & Vegetable Thai Curry (cauliflower rice)", "cals": 430, "protein": 36, "carbs": 24, "fats": 14},
            {"name": "Turkey Meatballs with Tomato Sauce & Veg", "cals": 500, "protein": 42, "carbs": 32, "fats": 16},
        ],
        "snack": [
            {"name": "Apple & Almond Butter", "cals": 190, "protein": 4, "carbs": 24, "fats": 9},
            {"name": "Rice Cakes with Cottage Cheese", "cals": 130, "protein": 12, "carbs": 16, "fats": 2},
            {"name": "Handful of Mixed Nuts", "cals": 170, "protein": 5, "carbs": 6, "fats": 15},
            {"name": "Protein Bar (low sugar)", "cals": 200, "protein": 20, "carbs": 18, "fats": 7},
            {"name": "Celery & Hummus", "cals": 120, "protein": 5, "carbs": 12, "fats": 6},
        ],
    },
    "muscle": {
        "breakfast": [
            {"name": "4-Egg Omelette with Cheese & Veg", "cals": 520, "protein": 38, "carbs": 8, "fats": 36},
            {"name": "Oats with Whey Protein & Banana", "cals": 580, "protein": 42, "carbs": 72, "fats": 10},
            {"name": "Whole Milk Smoothie with Oats & Peanut Butter", "cals": 620, "protein": 36, "carbs": 66, "fats": 22},
            {"name": "Chicken & Rice Breakfast Bowl", "cals": 590, "protein": 48, "carbs": 62, "fats": 12},
            {"name": "Smashed Avocado + 3 Eggs + Toast x2", "cals": 560, "protein": 30, "carbs": 44, "fats": 28},
        ],
        "lunch": [
            {"name": "Double Chicken Breast with Rice & Veg", "cals": 720, "protein": 68, "carbs": 72, "fats": 14},
            {"name": "Tuna Pasta Bake", "cals": 680, "protein": 56, "carbs": 76, "fats": 14},
            {"name": "Beef Burrito Bowl with Beans & Rice", "cals": 750, "protein": 52, "carbs": 82, "fats": 18},
            {"name": "Salmon Fillet, Quinoa & Edamame", "cals": 690, "protein": 58, "carbs": 60, "fats": 22},
            {"name": "Ground Turkey Rice Bowl", "cals": 700, "protein": 60, "carbs": 70, "fats": 16},
        ],
        "dinner": [
            {"name": "Sirloin Steak with Sweet Potato & Spinach", "cals": 780, "protein": 64, "carbs": 54, "fats": 28},
            {"name": "Slow-cooked Chicken Thighs with Rice", "cals": 740, "protein": 58, "carbs": 70, "fats": 22},
            {"name": "Pork Tenderloin, Roast Potatoes & Greens", "cals": 760, "protein": 56, "carbs": 68, "fats": 20},
            {"name": "Salmon & Prawn Pasta", "cals": 800, "protein": 62, "carbs": 78, "fats": 24},
            {"name": "Lamb Mince with Lentils & Flatbread", "cals": 820, "protein": 60, "carbs": 76, "fats": 26},
        ],
        "snack": [
            {"name": "Cottage Cheese with Pineapple", "cals": 220, "protein": 26, "carbs": 20, "fats": 4},
            {"name": "Mass Gainer Shake", "cals": 400, "protein": 30, "carbs": 60, "fats": 6},
            {"name": "Peanut Butter on Rice Cakes x3", "cals": 300, "protein": 10, "carbs": 34, "fats": 14},
            {"name": "Hard Boiled Eggs x3 + Toast", "cals": 320, "protein": 24, "carbs": 22, "fats": 16},
            {"name": "Greek Yoghurt with Granola & Honey", "cals": 340, "protein": 18, "carbs": 46, "fats": 8},
        ],
    },
}

EXERCISES = [
    {"name": "Running (6 mph)", "met": 9.8, "icon": "🏃"},
    {"name": "Cycling (moderate)", "met": 7.5, "icon": "🚴"},
    {"name": "Swimming (freestyle)", "met": 8.0, "icon": "🏊"},
    {"name": "Weight Training", "met": 5.0, "icon": "🏋️"},
    {"name": "HIIT", "met": 10.0, "icon": "⚡"},
    {"name": "Walking (brisk)", "met": 3.8, "icon": "🚶"},
    {"name": "Yoga", "met": 2.5, "icon": "🧘"},
    {"name": "Jump Rope", "met": 11.0, "icon": "🪢"},
    {"name": "Rowing Machine", "met": 7.0, "icon": "🚣"},
    {"name": "Elliptical", "met": 5.0, "icon": "🔄"},
    {"name": "Dancing", "met": 4.8, "icon": "💃"},
    {"name": "Boxing", "met": 9.0, "icon": "🥊"},
    {"name": "Football / Soccer", "met": 7.0, "icon": "⚽"},
    {"name": "Tennis", "met": 7.3, "icon": "🎾"},
    {"name": "Hiking", "met": 6.0, "icon": "🥾"},
]


# ── DB helpers ────────────────────────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs(os.path.dirname(DB), exist_ok=True)
    with get_db() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS calculations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            created_at TEXT DEFAULT (datetime('now')),
            age INTEGER,
            weight_kg REAL,
            height_cm REAL,
            gender TEXT,
            activity_level REAL,
            weight_loss_goal_kg REAL,
            weeks_goal INTEGER,
            bmr REAL,
            tdee REAL,
            calorie_intake INTEGER,
            unit_system TEXT DEFAULT 'metric',
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        """)

def hash_pw(pw): return hashlib.sha256(pw.encode()).hexdigest()

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access that page.', 'info')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def current_user():
    if 'user_id' not in session: return None
    with get_db() as db:
        return db.execute('SELECT * FROM users WHERE id=?', (session['user_id'],)).fetchone()

# ── Calculation helpers ───────────────────────────────────────────────────────
def calc_bmr(age, weight_kg, height_cm, gender):
    if gender == 'male':
        return 88.362 + (13.397 * weight_kg) + (4.799 * height_cm) - (5.677 * age)
    return 447.593 + (9.247 * weight_kg) + (3.098 * height_cm) - (4.330 * age)

def calc_bmi(weight_kg, height_cm):
    h = height_cm / 100
    bmi = weight_kg / (h * h)
    if bmi < 18.5: cat = "Underweight"
    elif bmi < 25: cat = "Healthy Weight"
    elif bmi < 30: cat = "Overweight"
    else: cat = "Obese"
    return round(bmi, 1), cat

def calc_body_fat(bmi, age, gender):
    # Deurenberg formula
    sex = 1 if gender == 'male' else 0
    bf = (1.20 * bmi) + (0.23 * age) - (10.8 * sex) - 5.4
    return max(3, round(bf, 1))

def water_intake(weight_kg, activity_level):
    base = weight_kg * 0.033
    if activity_level >= 1.55: base += 0.5
    if activity_level >= 1.725: base += 0.5
    return round(base, 1)

def parse_form_to_kg(form):
    unit_system = form.get('unit_system', 'metric')
    if unit_system == 'imperial':
        weight_kg = float(form['weight_lbs']) * 0.453592
        height_cm = (float(form['height_ft']) * 12 + float(form['height_in'])) * 2.54
        wl_kg = float(form.get('weight_loss_goal_lbs', 0)) * 0.453592
        display_weight = f"{form['weight_lbs']} lbs"
        display_height = f"{form['height_ft']}ft {form['height_in']}in"
        display_loss = f"{form.get('weight_loss_goal_lbs','0')} lbs"
    else:
        weight_kg = float(form['weight_kg'])
        height_cm = float(form['height_cm'])
        wl_kg = float(form.get('weight_loss_goal_kg', 0))
        display_weight = f"{weight_kg} kg"
        display_height = f"{height_cm} cm"
        display_loss = f"{wl_kg} kg"
    return weight_kg, height_cm, wl_kg, display_weight, display_height, display_loss, unit_system


# ── Routes ────────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    user = current_user()
    fact = random.choice(HEALTH_FACTS)
    history = []
    if user:
        with get_db() as db:
            history = db.execute(
                'SELECT * FROM calculations WHERE user_id=? ORDER BY created_at DESC LIMIT 3',
                (user['id'],)
            ).fetchall()
    return render_template('index.html', user=user, fact=fact, history=history)

@app.route('/calculate', methods=['GET', 'POST'])
def calculate():
    user = current_user()
    if request.method == 'POST':
        age = int(request.form['age'])
        gender = request.form['gender']
        activity_level = float(request.form['activity_level'])
        weeks_goal = int(request.form['weeks_goal'])
        weight_kg, height_cm, wl_kg, dw, dh, dl, unit_system = parse_form_to_kg(request.form)

        bmr = calc_bmr(age, weight_kg, height_cm, gender)
        tdee = bmr * activity_level
        deficit_per_day = (wl_kg * 7700) / (weeks_goal * 7)
        calorie_intake = max(600, int(round(tdee - deficit_per_day)))

        bmi, bmi_cat = calc_bmi(weight_kg, height_cm)
        body_fat = calc_body_fat(bmi, age, gender)
        water_l = water_intake(weight_kg, activity_level)

        muscle_calories = int(round(tdee * 1.10))
        protein_grams = round(weight_kg * 2.0)
        fats_kcal = 0.25 * muscle_calories
        fats_grams = round(fats_kcal / 9)
        protein_kcal = protein_grams * 4
        carbs_grams = round(max(0, muscle_calories - protein_kcal - fats_kcal) / 4)
        protein_pct = min(100, round((protein_kcal / muscle_calories) * 100))
        carbs_pct = min(100, round(((carbs_grams * 4) / muscle_calories) * 100))

        calorie_intake_1kg = max(600, int(round(tdee - 7700 / (weeks_goal * 7))))
        calorie_intake_2kg = max(600, int(round(tdee - (2 * 7700) / (weeks_goal * 7))))
        calorie_intake_5kg = max(600, int(round(tdee - (5 * 7700) / (weeks_goal * 7))))

        # Pick meal plan
        goal_type = 'muscle' if calorie_intake > tdee else 'weight_loss'
        plan = {meal: random.choice(MEAL_PLANS[goal_type][meal]) for meal in ['breakfast', 'lunch', 'dinner', 'snack']}
        total_meal_cals = sum(plan[m]['cals'] for m in plan)

        if user:
            with get_db() as db:
                db.execute("""
                    INSERT INTO calculations
                    (user_id,age,weight_kg,height_cm,gender,activity_level,weight_loss_goal_kg,
                     weeks_goal,bmr,tdee,calorie_intake,unit_system)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
                """, (user['id'], age, weight_kg, height_cm, gender, activity_level,
                      wl_kg, weeks_goal, bmr, tdee, calorie_intake, unit_system))
                db.commit()

        return render_template('result.html',
            user=user,
            calorie_intake=calorie_intake,
            calorie_intake_1kg=calorie_intake_1kg,
            calorie_intake_2kg=calorie_intake_2kg,
            calorie_intake_5kg=calorie_intake_5kg,
            display_loss=dl,
            display_weight=dw,
            display_height=dh,
            tdee=int(round(tdee)),
            bmr=int(round(bmr)),
            deficit=int(round(deficit_per_day)),
            muscle_calories=muscle_calories,
            protein_grams=protein_grams,
            carbs_grams=carbs_grams,
            fats_grams=fats_grams,
            protein_pct=protein_pct,
            carbs_pct=carbs_pct,
            bmi=bmi,
            bmi_cat=bmi_cat,
            body_fat=body_fat,
            water_l=water_l,
            weeks_goal=weeks_goal,
            age=age,
            weight_kg=weight_kg,
            gender=gender,
            plan=plan,
            total_meal_cals=total_meal_cals,
            goal_type=goal_type,
            fact=random.choice(HEALTH_FACTS),
            exercises=EXERCISES,
        )
    return render_template('calculate.html', user=user, fact=random.choice(HEALTH_FACTS))

@app.route('/exercise')
def exercise():
    user = current_user()
    return render_template('exercise.html', user=user, exercises=EXERCISES)

@app.route('/dashboard')
@login_required
def dashboard():
    user = current_user()
    with get_db() as db:
        history = db.execute(
            'SELECT * FROM calculations WHERE user_id=? ORDER BY created_at DESC LIMIT 20',
            (user['id'],)
        ).fetchall()
    return render_template('dashboard.html', user=user, history=history)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session: return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip().lower()
        pw = request.form['password']
        if len(pw) < 6:
            flash('Password must be at least 6 characters.', 'error')
            return render_template('register.html')
        try:
            with get_db() as db:
                db.execute('INSERT INTO users (username, email, password) VALUES (?,?,?)',
                           (username, email, hash_pw(pw)))
                db.commit()
                user = db.execute('SELECT * FROM users WHERE email=?', (email,)).fetchone()
                session['user_id'] = user['id']
                session['username'] = user['username']
            flash(f'Welcome, {username}! Your account is ready.', 'success')
            return redirect(url_for('calculate'))
        except sqlite3.IntegrityError:
            flash('That username or email is already taken.', 'error')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session: return redirect(url_for('index'))
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        pw = request.form['password']
        with get_db() as db:
            user = db.execute('SELECT * FROM users WHERE email=? AND password=?',
                              (email, hash_pw(pw))).fetchone()
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash(f'Welcome back, {user["username"]}!', 'success')
            return redirect(url_for('dashboard'))
        flash('Incorrect email or password.', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/api/exercise-burn', methods=['POST'])
def exercise_burn():
    data = request.json
    weight_kg = float(data.get('weight_kg', 70))
    minutes = float(data.get('minutes', 30))
    met = float(data.get('met', 5.0))
    calories = round((met * 3.5 * weight_kg / 200) * minutes)
    return jsonify({'calories': calories})

if __name__ == '__main__':
    init_db()
    app.run(port=5002, debug=True)

# Weight a Minute — Full App

## Setup

```bash
pip install flask
python app.py
```

Visit: http://localhost:5002

## Personalise

In `app.py`, change line:
```python
app.config['SITE_OWNER'] = 'Your Name'  # ← Put your name here
```
This shows your credit in the footer of every page.

## Features

- ✅ User accounts (register / login / logout)
- ✅ Calculation history saved per user
- ✅ Dashboard with full history table
- ✅ kg/cm ↔ lbs/ft·in unit toggle
- ✅ BMR & TDEE calculator (Mifflin-St Jeor)
- ✅ BMI + estimated body fat (Deurenberg)
- ✅ Daily water intake recommendation
- ✅ Draggable macro split customiser
- ✅ Meal plan suggestions (weight loss & muscle)
- ✅ Fat loss presets (gentle → max)
- ✅ Timeline adjuster (change weeks live)
- ✅ Exercise calorie burn calculator (15 activities)
- ✅ Print / Save PDF button
- ✅ Flash messages & auth protection

## File Structure

```
wam/
├── app.py              # Main Flask app + all routes
├── instance/
│   └── wam.db          # SQLite database (auto-created)
└── templates/
    ├── base.html       # Nav, footer, shared styles
    ├── index.html      # Homepage
    ├── calculate.html  # Calculator form
    ├── result.html     # Results page
    ├── exercise.html   # Exercise burn calculator
    ├── dashboard.html  # User history
    ├── login.html
    └── register.html
```

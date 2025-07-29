from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
db = SQLAlchemy(app)

class Habit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

class Completion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    habit_id = db.Column(db.Integer, db.ForeignKey('habit.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    habit = db.relationship('Habit')

@app.route('/')
def index():
    habits = Habit.query.all()
    habit_data = []
    for habit in habits:
        completions = Completion.query.filter_by(habit_id=habit.id).order_by(Completion.date.desc()).all()
        streak = calculate_streak(completions)
        habit_data.append({
            'id': habit.id,
            'name': habit.name,
            'streak': streak
        })
    return render_template('index.html', habits=habit_data)

@app.route('/add_habit', methods=['POST'])
def add_habit():
    name = request.form['name']
    if name:
        habit = Habit(name=name)
        db.session.add(habit)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/complete/<int:habit_id>', methods=['POST'])
def complete_habit(habit_id):
    today = datetime.utcnow().date()
    existing = Completion.query.filter_by(habit_id=habit_id, date=today).first()
    if not existing:
        completion = Completion(habit_id=habit_id, date=today)
        db.session.add(completion)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/api/habit_data/<int:habit_id>')
def habit_data(habit_id):
    completions = Completion.query.filter_by(habit_id=habit_id).order_by(Completion.date).all()
    dates = [c.date.strftime('%Y-%m-%d') for c in completions]
    return jsonify({
        'dates': dates,
        'count': len(dates)
    })

def calculate_streak(completions):
    if not completions:
        return 0
    streak = 1
    today = datetime.utcnow().date()
    last_date = completions[0].date
    
    if last_date != today:
        return 0
    
    for i in range(1, len(completions)):
        if (last_date - completions[i].date).days == 1:
            streak += 1
            last_date = completions[i].date
        else:
            break
    return streak

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
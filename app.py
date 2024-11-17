from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Model
class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, default=datetime.date.today)
    sleep_hours = db.Column(db.Float, nullable=False)
    calories = db.Column(db.Integer, nullable=False)
    hydration = db.Column(db.Float, nullable=False)  # Liters
    running_mileage = db.Column(db.Float, nullable=False)
    notes = db.Column(db.String, nullable=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add', methods=['GET', 'POST'])
def add_entry():
    if request.method == 'POST':
        # Convert date string to a datetime.date object
        date_str = request.form.get('date', datetime.date.today().isoformat())
        date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        
        sleep_hours = float(request.form.get('sleep_hours'))
        calories = int(request.form.get('calories'))
        hydration = float(request.form.get('hydration'))
        running_mileage = float(request.form.get('running_mileage'))
        notes = request.form.get('notes')

        # Check if an entry for this date already exists
        existing_entry = Entry.query.filter_by(date=date).first()
        if existing_entry:
            return render_template('add_entry.html', error="An entry for this date already exists.")

        # Add a new entry
        new_entry = Entry(
            date=date,
            sleep_hours=sleep_hours,
            calories=calories,
            hydration=hydration,
            running_mileage=running_mileage,
            notes=notes
        )
        db.session.add(new_entry)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_entry.html')


@app.route('/data')
def view_data():
    entries = Entry.query.order_by(Entry.date).all()
    return render_template('view_data.html', entries=entries)

@app.route('/charts')
def view_charts():
    # Query all entries
    entries = Entry.query.order_by(Entry.date).all()

    # Extract data for Chart.js
    chart_data = {
        "dates": [entry.date.strftime('%Y-%m-%d') for entry in entries],
        "sleep_hours": [entry.sleep_hours for entry in entries],
        "calories": [entry.calories for entry in entries],
        "hydration": [entry.hydration for entry in entries],
        "running_mileage": [entry.running_mileage for entry in entries],
    }

    return render_template('view_charts.html', chart_data=chart_data)


if __name__ == "__main__":
    # Ensure the database tables are created inside the application context
    with app.app_context():
        db.create_all()
    app.run(debug=True)

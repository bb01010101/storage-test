
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

@app.route('/edit/<int:entry_id>', methods=['GET', 'POST'])
def edit_entry(entry_id):
    entry = Entry.query.get_or_404(entry_id)
    
    if request.method == 'POST':
        entry.date = datetime.datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        entry.sleep_hours = float(request.form['sleep_hours'])
        entry.calories = int(request.form['calories'])
        entry.hydration = float(request.form['hydration'])
        entry.running_mileage = float(request.form['running_mileage'])
        entry.notes = request.form['notes']
        
        db.session.commit()  # Save the changes
        return redirect(url_for('view_data'))

    return render_template('edit_entry.html', entry=entry)

@app.route('/delete/<int:entry_id>', methods=['GET'])
def delete_entry(entry_id):
    entry = Entry.query.get_or_404(entry_id)
    db.session.delete(entry)
    db.session.commit()  # Commit deletion
    return redirect(url_for('view_data'))


@app.route('/data')
def view_data():
    entries = Entry.query.order_by(Entry.date).all()

    return render_template('view_data.html', entries=entries)

@app.route('/charts')
def view_charts():
    entries = Entry.query.order_by(Entry.date).all()
        # Aggregate data
    daily_data = aggregate_data(entries, "day")
    weekly_data = aggregate_data(entries, "week")
    monthly_data = aggregate_data(entries, "month")
    yearly_data = aggregate_data(entries, "year")

    chart_data = {
        "daily": daily_data,
        "weekly": weekly_data,
        "monthly": monthly_data,
        "yearly": yearly_data,
    }

    return render_template('view_charts.html', chart_data=chart_data)

    # Helper functions for aggregation
def aggregate_data(entries, group_by):
    from collections import defaultdict
    aggregated = defaultdict(lambda: {"sleep_hours": 0, "calories": 0, "hydration": 0, "running_mileage": 0, "count": 0})

    for entry in entries:
        if group_by == "day":
            key = entry.date.strftime('%Y-%m-%d')  # Convert to string
        elif group_by == "week":
            key = entry.date.strftime('%Y-W%U')  # Year and week number as string
        elif group_by == "month":
            key = entry.date.strftime('%Y-%m')  # Year and month as string
        elif group_by == "year":
            key = str(entry.date.year)  # Year as string
        else:
            raise ValueError("Invalid group_by value")

        aggregated[key]["sleep_hours"] += entry.sleep_hours
        aggregated[key]["calories"] += entry.calories
        aggregated[key]["hydration"] += entry.hydration
        aggregated[key]["running_mileage"] += entry.running_mileage
        aggregated[key]["count"] += 1

    # Calculate averages where necessary
    for key, value in aggregated.items():
        value["sleep_hours"] /= value["count"]
        value["calories"] /= value["count"]
        value["hydration"] /= value["count"]
        value["running_mileage"] /= value["count"]

    return dict(aggregated)




if __name__ == "__main__":
    # Ensure the database tables are created inside the application context
    with app.app_context():
        db.create_all()
    app.run(debug=True)
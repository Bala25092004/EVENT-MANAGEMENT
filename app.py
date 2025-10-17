import os
import io
import base64
import csv
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
import qrcode
from flask import Response
from flask_mail import Mail, Message


app = Flask(__name__)
app.config['SECRET_KEY'] = 'a_very_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)


app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER', 'j.balakrishnsn2005@gmail.com')
app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASS', 'hwsw legf xtgc pkhf')
app.config['MAIL_DEFAULT_SENDER'] = app.config['MAIL_USERNAME']

mail = Mail(app)


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    image_url = db.Column(db.String(200), nullable=True)
    attendees = db.relationship('Attendee', backref='event', lazy=True, cascade="all, delete-orphan")

    @property
    def tickets_sold(self):
        return len(self.attendees)

    @property
    def tickets_available(self):
        return self.capacity - self.tickets_sold

class Attendee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)


def generate_qr_code(data):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{img_str}"


@app.route('/')
def dashboard():
    total_events = Event.query.count()
    total_attendees = Attendee.query.count()
    total_revenue = total_attendees * 10
    upcoming_events = Event.query.filter(
        Event.date >= datetime.combine(date.today(), datetime.min.time())
    ).order_by(Event.date.asc()).limit(5).all()
    recent_attendees = Attendee.query.order_by(Attendee.id.desc()).limit(5).all()
    return render_template(
        'dashboard.html', 
        total_events=total_events, 
        total_attendees=total_attendees, 
        total_revenue=total_revenue,
        upcoming_events=upcoming_events,
        recent_attendees=recent_attendees
    )


@app.route('/events')
def list_events():
    events = Event.query.order_by(Event.date.desc()).all()
    return render_template('events.html', events=events)

@app.route('/event/new', methods=['POST'])
def create_event():
    try:
        data = request.get_json()
        new_event = Event(
            title=data['title'], description=data['description'],
            date=datetime.strptime(data['date'], '%Y-%m-%d'),
            location=data['location'], capacity=int(data['capacity']),
            image_url=data.get('image_url')
        )
        db.session.add(new_event)
        db.session.commit()
        event_url = url_for('list_attendees', event_id=new_event.id, _external=True)
        qr_code_img = generate_qr_code(event_url)
        return jsonify({
            'success': True, 'message': 'Event created successfully!',
            'event_url': event_url, 'qr_code': qr_code_img,
            'event_title': new_event.title
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/event/<int:event_id>')
def get_event_data(event_id):
    event = Event.query.get_or_404(event_id)
    return jsonify({
        'id': event.id, 'title': event.title,
        'description': event.description, 'date': event.date.strftime('%Y-%m-%d'),
        'location': event.location, 'capacity': event.capacity,
        'image_url': event.image_url
    })

@app.route('/event/update/<int:event_id>', methods=['POST'])
def update_event(event_id):
    event = Event.query.get_or_404(event_id)
    try:
        data = request.get_json()
        event.title = data['title']
        event.description = data['description']
        event.date = datetime.strptime(data['date'], '%Y-%m-%d')
        event.location = data['location']
        event.capacity = int(data['capacity'])
        event.image_url = data.get('image_url')
        db.session.commit()
        return jsonify({'success': True, 'message': 'Event updated successfully!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/event/delete/<int:event_id>', methods=['POST'])
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    flash('Event deleted successfully!', 'success')
    return redirect(url_for('list_events'))


@app.route('/event/<int:event_id>/attendees')
def list_attendees(event_id):
    event = Event.query.get_or_404(event_id)
    return render_template('attendees.html', event=event)

@app.route('/attendee/new/<int:event_id>', methods=['POST'])
def add_attendee(event_id):
    event = Event.query.get_or_404(event_id)
    if event.tickets_available <= 0:
        flash('Sorry, this event is sold out!', 'error')
        return redirect(url_for('list_attendees', event_id=event_id))
    
    name = request.form['name']
    email = request.form['email']

    
    existing_attendee = Attendee.query.filter_by(email=email, event_id=event_id).first()
    if existing_attendee:
        flash(f'{email} is already registered for this event.', 'error')
        return redirect(url_for('list_attendees', event_id=event_id))

    new_attendee = Attendee(name=name, email=email, event_id=event_id)
    db.session.add(new_attendee)
    db.session.commit()

    try:
        
        ticket_data = f"EVENT_ID:{event.id},ATTENDEE_ID:{new_attendee.id},NAME:{new_attendee.name}"
        qr_code_img = generate_qr_code(ticket_data)

    
        msg_title = f"Your Ticket for {event.title}"
        msg = Message(msg_title, recipients=[email])
        msg.html = render_template(
            'ticket_email.html', 
            attendee=new_attendee, 
            event=event, 
            qr_code=qr_code_img
        )
        mail.send(msg)
        
        flash('Attendee registered successfully! A confirmation ticket has been sent.', 'success')
    except Exception as e:
        flash('Attendee registered, but failed to send confirmation email. Please check your mail settings.', 'warning')
        
        print(e)
        
    return redirect(url_for('list_attendees', event_id=event_id))

@app.route('/reports')
def reports():
    return render_template('reports.html')

@app.route('/api/reports-data')
def reports_data():
    events = Event.query.all()
    total_attendees = Attendee.query.count()
    ticket_price = 10
    total_revenue = total_attendees * ticket_price
    avg_ticket_price = total_revenue / total_attendees if total_attendees > 0 else 0
    total_events = len(events)
    today_datetime = datetime.combine(date.today(), datetime.min.time())
    upcoming_count = sum(1 for event in events if event.date >= today_datetime)
    past_count = total_events - upcoming_count
    top_events = sorted(events, key=lambda e: e.tickets_sold * ticket_price, reverse=True)
    
    return jsonify({
        'total_revenue': total_revenue,
        'avg_ticket_price': avg_ticket_price,
        'total_events': total_events,
        'total_attendees': total_attendees,
        'revenue_by_event': {
            'labels': [e.title for e in events], 'data': [e.tickets_sold * ticket_price for e in events]
        },
        'event_status': {'upcoming': upcoming_count, 'past': past_count},
        'top_events': [{'title': e.title, 'tickets': e.tickets_sold, 'price': ticket_price, 'revenue': e.tickets_sold * ticket_price} for e in top_events],
        'event_performance': [{'title': e.title, 'sold': e.tickets_sold, 'capacity': e.capacity, 'occupancy': (e.tickets_sold / e.capacity * 100) if e.capacity > 0 else 0} for e in events]
    })

@app.route('/api/event/share/<int:event_id>')
def share_event(event_id):
    event = Event.query.get_or_404(event_id)
    event_url = url_for('list_attendees', event_id=event.id, _external=True)
    qr_code_img = generate_qr_code(event_url)
    return jsonify({
        'success': True, 'event_url': event_url,
        'qr_code': qr_code_img, 'event_title': event.title
    })

@app.route('/download-report')
def download_report():
    events = Event.query.all()
    total_attendees = Attendee.query.count()
    ticket_price = 10
    total_revenue = total_attendees * ticket_price
    report_data = {
        'total_revenue': total_revenue,
        'total_events': len(events),
        'total_attendees': total_attendees,
        'top_events': sorted(
            [{'title': e.title, 'tickets': e.tickets_sold, 'price': ticket_price, 'revenue': e.tickets_sold * ticket_price} for e in events],
            key=lambda x: x['revenue'], reverse=True
        ),
        'event_performance': [{'title': e.title, 'sold': e.tickets_sold, 'capacity': e.capacity, 'occupancy': (e.tickets_sold / e.capacity * 100) if e.capacity > 0 else 0} for e in events]
    }
    html_string = render_template(
        'report_pdf.html', data=report_data, 
        generated_date=date.today().strftime('%B %d, %Y')
    )
    pdf = HTML(string=html_string).write_pdf()
    return Response(
        pdf, mimetype='application/pdf',
        headers={'Content-Disposition': 'attachment;filename=EventPro_Report.pdf'}
    )
    
@app.route('/import', methods=['GET', 'POST'])
def import_csv():
    
    return render_template('import.html')

@app.route('/attendee/delete/<int:attendee_id>', methods=['POST'])
def delete_attendee(attendee_id):
    attendee_to_delete = Attendee.query.get_or_404(attendee_id)
    
    event_id = attendee_to_delete.event.id
    
    db.session.delete(attendee_to_delete)
    db.session.commit()
    
    flash('Attendee deleted successfully!', 'success')
    
    return redirect(url_for('list_attendees', event_id=event_id))
@app.route('/all-attendees')
def all_attendees():
    attendees = Attendee.query.order_by(Attendee.id.desc()).all()
    return render_template('all_attendees.html', attendees=attendees)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
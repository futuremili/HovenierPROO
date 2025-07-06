#!/usr/bin/env python3
"""
Test data creation script for HovenierPro application
"""

from app import app, db
from models import User, Task, TimeEntry, Message, LeaveRequest
from datetime import datetime, date, timedelta

def create_test_data():
    with app.app_context():
        # Create a test user (if not exists)
        test_user = User.query.filter_by(email='test@example.com').first()
        if not test_user:
            test_user = User()
            test_user.id = 'test_user_123'
            test_user.email = 'test@example.com'
            test_user.first_name = 'Jan'
            test_user.last_name = 'de Hovenier'
            test_user.role = 'worker'
            test_user.phone = '+31612345678'
            test_user.hire_date = date(2024, 1, 15)
            test_user.active = True
            db.session.add(test_user)
            db.session.commit()
            print("Created test user")

        # Create some test tasks
        if Task.query.count() == 0:
            tasks = [
                {
                    'title': 'Gazon maaien bij Villa de Heuvel',
                    'description': 'Complete gazononderhoud inclusief kantjes bijwerken',
                    'status': 'pending',
                    'priority': 'medium',
                    'location': 'Heuvellaan 45, Amsterdam',
                    'estimated_hours': 3.0,
                    'due_date': date.today(),
                    'assigned_to': test_user.id,
                    'created_by': test_user.id
                },
                {
                    'title': 'Heg bijsnoeien Kantoorcomplex',
                    'description': 'Hagen rondom parkeerplaats bijsnoeien en schoonmaken',
                    'status': 'pending', 
                    'priority': 'high',
                    'location': 'Bedrijfspark Noord 12, Utrecht',
                    'estimated_hours': 4.5,
                    'due_date': date.today() + timedelta(days=1),
                    'assigned_to': test_user.id,
                    'created_by': test_user.id
                },
                {
                    'title': 'Bloembakken bijplanten winkelcentrum',
                    'description': 'Seizoensplanten vervangen en water geven',
                    'status': 'completed',
                    'priority': 'low',
                    'location': 'Winkelcentrum De Oost, Almere',
                    'estimated_hours': 2.0,
                    'due_date': date.today() - timedelta(days=1),
                    'completed_at': datetime.now() - timedelta(days=1),
                    'assigned_to': test_user.id,
                    'created_by': test_user.id
                }
            ]
            
            for task_data in tasks:
                task = Task()
                for key, value in task_data.items():
                    setattr(task, key, value)
                db.session.add(task)
            
            db.session.commit()
            print("Created test tasks")

        # Create test messages
        if Message.query.count() == 0:
            messages = [
                {
                    'sender_id': test_user.id,
                    'subject': 'Weerbericht: regen verwacht',
                    'content': 'Let op: voor morgen wordt regen verwacht. Controleer of alle gereedschappen waterdicht opgeborgen zijn.',
                    'message_type': 'announcement'
                },
                {
                    'sender_id': test_user.id,
                    'subject': 'Nieuwe veiligheidsrichtlijnen',
                    'content': 'Er zijn nieuwe veiligheidsrichtlijnen voor het werken met elektrisch gereedschap. Check de app voor details.',
                    'message_type': 'urgent'
                }
            ]
            
            for msg_data in messages:
                message = Message()
                for key, value in msg_data.items():
                    setattr(message, key, value)
                db.session.add(message)
            
            db.session.commit()
            print("Created test messages")

        print("Test data creation completed successfully!")

if __name__ == '__main__':
    create_test_data()
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("./serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://visual-attendance-system-default-rtdb.firebaseio.com/'
    })

ref = db.reference('Students')

data = {
    "21BAI10097":
        {
            'Name': 'Anurag Mishra',
            'Year': '2021',
            'totalAttendance': 8,
            'lastAttendanceTime': '2023-06-15 10:52:00'
        },

    "21BCE10898":
        {
            'Name': 'Ratan Tata',
            'Year': '2021',
            'totalAttendance': 8,
            'lastAttendanceTime': '2023-06-15 10:52:00'
        },

    "21MBA10987":
        {
            'Name': 'Mukesh Ambani',
            'Year': '2021',
            'totalAttendance': 8,
            'lastAttendanceTime': '2023-06-15 10:52:00'
        }
}

for key, val in data.items():
    ref.child(key).set(val)

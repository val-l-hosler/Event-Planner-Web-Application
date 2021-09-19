from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(24), unique=True, nullable=False)
    password = db.Column(db.String(24), nullable=False)
    pw_hash = db.Column(db.String(64), nullable=False)

    # 1:m relationship between customer and events
    customer_events = db.relationship("Event", backref="customer", lazy="dynamic")

    # M:n relationship between staff and events
    works = db.relationship("Event", secondary="works", backref=db.backref("worked_by", lazy="dynamic"), lazy="dynamic")

    def __init__(self, username, password, pw_hash):
        self.username = username
        self.password = password
        self.pw_hash = pw_hash

    def __repr__(self):
        return "<User {}>".format(self.username)


works = db.Table("works",
                 db.Column("worker_id", db.Integer, db.ForeignKey("user.user_id")),
                 db.Column("event_worked_id", db.Integer, db.ForeignKey("event.event_id"))
                 )


class Event(db.Model):
    event_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(10), unique=True, nullable=False)  # This takes in a string from <input type="date">
    number_of_staff = db.Column(db.Integer, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)

    def __init__(self, name, date, number_of_staff, customer_id):
        self.name = name
        self.date = date
        self.number_of_staff = number_of_staff
        self.customer_id = customer_id

    def __repr__(self):
        return "<Event {}>".format(self.date)

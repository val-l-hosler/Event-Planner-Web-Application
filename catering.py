import os
from flask import Flask, request, session, url_for, redirect, render_template, abort, g, flash
from werkzeug.security import check_password_hash, generate_password_hash

from models import db, User, Event

app = Flask(__name__)

PER_PAGE = 30
DEBUG = True
SECRET_KEY = os.urandom(12)

SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(app.root_path, "catering.db")

app.config.from_object(__name__)
app.config.from_envvar("CATERING_SETTINGS", silent=True)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


if __name__ == '__main__':
    app.run()


# I initialized the database locally before uploading it to pythonanywhere.com
@app.cli.command("initdb")
def initdb_command():
    db.create_all()
    print("Initialized the database.")
    owner = User(username="owner", password="pass", pw_hash=generate_password_hash("pass"))
    db.session.add(owner)
    db.session.commit()


def get_event_id(date):
    rv = Event.query.filter_by(date=date).first()
    return rv.event_id if rv else None


def get_user_id(username):
    rv = User.query.filter_by(username=username).first()
    return rv.user_id if rv else None


@app.before_request
def before_request():
    g.user = None
    if "user_id" in session:
        g.user = User.query.filter_by(user_id=session["user_id"]).first()


@app.route("/", methods=["GET", "POST"])
def login():
    if g.user:  # If a user is logged in
        if g.user.username == "owner":
            return redirect(url_for("owner"))
        elif g.user.username.__contains__("staff") is True:  # All staff usernames have to contain the string "staff"
            return redirect(url_for("staff"))
        else:
            return redirect(url_for("customer"))
    else:
        if request.method == "POST":
            user = User.query.filter_by(username=request.form["username"]).first()
            if user is None:
                flash("Invalid username")
            elif not check_password_hash(user.pw_hash, request.form["password"]):
                flash("Invalid password")
            else:
                session["user_id"] = user.user_id
                return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/cancel_event/<date>")
def cancel_event(date):
    if g.user:  # If a user is logged in
        if g.user.username == "owner" or g.user.username.__contains__(
                "staff"):  # If the user is the owner or a staff member, throw a 404 error
            abort(404)

        if date is None:
            abort(404)

        db.session.delete(
            Event.query.filter_by(date=date).first()
        )
        db.session.commit()
        flash("You successfully cancelled the event")
        return redirect(url_for("customer"))
    else:  # Else, no user is logged in so throw a 404 error
        abort(404)


@app.route("/create_staff_account", methods=["GET", "POST"])
def create_staff_account():
    if g.user:  # If a user is logged in
        if g.user.username != "owner":  # If the user is not the owner, throw a 404 error
            abort(404)

        if request.method == "POST":
            if not request.form["register-staff-username"]:
                flash("You have to enter a staff username")
            elif not request.form["register-staff-password"]:
                flash("You have to enter a staff password")
            elif get_user_id(request.form["register-staff-username"]) is not None:
                flash("The staff username is already taken")
            elif request.form["register-staff-username"].__len__() > 24:
                flash("The staff username is too long. It can only be up to 24 characters in length.")
            elif request.form["register-staff-password"].__len__() > 24:
                flash("The staff password is too long. It can only be up to 24 characters in length.")
            elif request.form["register-staff-username"].__contains__("staff") is False:
                flash("Staff usernames must contain the word staff")
            else:
                db.session.add(
                    User(request.form["register-staff-username"], request.form["register-staff-password"],
                         generate_password_hash(request.form["register-staff-password"])))
                db.session.commit()
                flash("The staff member was successfully registered")
                return redirect(url_for("owner"))
    else:  # Else, no user is logged in so throw a 404 error
        abort(404)

    return render_template("create_staff_account.html")


@app.route("/customer", methods=["GET", "POST"])
def customer():
    if g.user:  # If a user is logged in
        if g.user.username == "owner" or g.user.username.__contains__(
                "staff"):  # If the user is the owner or a staff member, throw a 404 error
            abort(404)

        if request.method == "POST":
            if not request.form["event-name"]:
                flash("You have to enter an event name")
            elif not request.form["event-date"]:
                flash("You have to enter an event date")
            elif request.form["event-name"].__len__() > 100:
                flash("The event name is too long. It can only be up to 100 characters in length.")
            elif get_event_id(request.form["event-date"]) is not None:
                flash("The company is booked on that date")
            else:
                db.session.add(
                    Event(request.form["event-name"], request.form["event-date"], 0,
                          session["user_id"]))  # The 0 indicates how many staff members are working
                db.session.commit()
                flash("You successfully requested an event")
                return redirect(url_for("customer"))
    else:  # Else, no user is logged in so throw a 404 error
        abort(404)

    customer_events = Event.query.filter_by(customer_id=session["user_id"]).order_by(Event.date.asc()).all()
    return render_template("customer.html", customer_events=customer_events)


@app.route("/logout")
def logout():
    if g.user:  # If a user is logged in
        flash("You were logged out")
        session.pop("user_id", None)
        return redirect(url_for("login"))
    else:  # Else, no user is logged in so throw a 404 error
        abort(404)


@app.route("/owner")
def owner():
    if g.user:  # If a user is logged in
        if g.user.username != "owner":  # If the user is not the owner, throw a 404 error
            abort(404)

        # A list of all the scheduled events
        # If the list is empty, the owner template handles this scenario
        scheduled_events = Event.query.order_by(Event.date.asc()).all()
        # Each index of this list holds a list of one event's staff members
        scheduled_event_staff = []

        for event in scheduled_events:
            # Gets all the staff records that are associated with a particular event
            staff = User.query.filter(User.works.any(event_id=event.event_id)).all()
            # Makes an empty list that will contain the staff
            # If the list is empty, the owner templates handles this scenario
            event_staff = []

            if not staff:  # If there are no staff records
                event_staff.append("No staff working")
            else:
                for s in staff:
                    event_staff.append(s.username)  # Appends the records to the event_staff list

            scheduled_event_staff.append(event_staff)  # Appends the list of this event's staff to the larger list
    else:  # Else, no user is logged in so throw a 404 error
        abort(404)

    return render_template("owner.html", scheduled_events=scheduled_events, scheduled_event_staff=scheduled_event_staff)


@app.route("/register", methods=["GET", "POST"])
def register():
    if g.user:  # If a user is logged in, throw a 404 error
        abort(404)
    else:  # Else, no user is logged in so they can register
        if request.method == "POST":
            if not request.form["register-username"]:
                flash("You have to enter a username")
            elif not request.form["register-password"]:
                flash("You have to enter a password")
            elif request.form["register-username"].__len__() > 24:
                flash("The username is too long. It can only be up to 24 characters in length.")
            elif request.form["register-password"].__len__() > 24:
                flash("The password is too long. It can only be up to 24 characters in length.")
            elif get_user_id(request.form["register-username"]) is not None:
                flash("The username is already taken")
            elif request.form["register-username"].__contains__(
                    "staff") is True:  # This makes sure a customer cannot create a staff username
                # I am showing this error so the user doesn't know the pattern for a staff username
                flash("The username is already taken")
            else:
                db.session.add(
                    User(request.form["register-username"], request.form["register-password"],
                         generate_password_hash(request.form["register-password"])))
                db.session.commit()
                flash("You were successfully registered and can login now")
                return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/staff")
def staff():
    if g.user:  # If a user is logged in
        if g.user.username.__contains__("staff") is False:  # If the user is not a staff member, throw a 404 error
            abort(404)

        staff = User.query.filter_by(user_id=session["user_id"]).first()

        works_ids = []

        for event in staff.works:
            works_ids.append(event.event_id)

        # Gets all the events the particular staff member is working at
        worked_events = Event.query.filter(Event.event_id.in_(works_ids)).order_by(Event.date.asc()).limit(
            PER_PAGE).all()
        # Gets all the event records that have fewer than 3 staff member working and the user is not already working the event
        available_events = Event.query.filter(
            ((Event.number_of_staff == 0) | (Event.number_of_staff == 1) | (Event.number_of_staff == 2))
            & (Event.event_id.notin_(works_ids))).order_by(Event.date.asc()).all()
    else:  # Else, a user is not logged in so throw a 404 error
        abort(404)

    return render_template("staff.html", available_events=available_events, worked_events=worked_events)


@app.route("/sign_up_event/<date>")
def sign_up_event(date):
    if g.user:  # If a user is logged in
        if g.user.username.__contains__("staff") is False:  # If the user is not a staff member, throw a 404 error
            abort(404)

        if date is None:
            abort(404)

        # This is the event associated with the link the user clicked
        event_worked = Event.query.filter_by(event_id=get_event_id(date)).first()

        # If the staff member has not already signed up for the event
        if User.query.filter_by(user_id=session["user_id"]).first().works.filter_by(
                event_id=event_worked.event_id).first() is None:
            # Appends the event object to the works junction table for the online user
            User.query.filter_by(user_id=session["user_id"]).first().works.append(event_worked)
            # Updates the amount of staff members working on a particular event
            staff_currently_working = event_worked.number_of_staff + 1
            event_worked.number_of_staff = staff_currently_working
            db.session.commit()
            flash("You successfully signed up to work the event")
        else:  # Else, they already signed up for the event and cannot sign up again
            flash("You already signed up for that event")
        return redirect(url_for("staff"))
    else:  # Else, no user is logged in so throw a 404 error
        abort(404)

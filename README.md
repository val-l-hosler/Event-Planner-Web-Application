# Event-Planner-Web-Application

This is a project from CS 1520, Programming Languages for Web Applications. I created a catering event planner web application where a customer can create an account and schedule events, a staff member can view and sign up to work said events, and the owner can view said events and create staff accounts. 

Though the project description did not require extensive styling or responsivity, I tried to make the web application as neat and user-friendly as possible with some responsive elements. **However, it is not 100% responsive, as the web application only needed to be viewable on a Google Chrome desktop browser**.

### :point_right: Visit the [following url](http://valhos2.pythonanywhere.com/) to view a live demo.

### :warning: To log into the owner's account, use the username "owner" and the password "pass".

### 🧰 Tech Stack 
1. CSS (including Flexbox)
2. Flask
3. HTML
4. Jinja
5. Python
6. SQLAlchemy

### :memo: The project had the following specifications:

1. You must build your website using Python, Flask, SQLAlchemy, and the
	Flask-SQLAlchemy extension.

2. Managing users
	* Each user (Owner, Staff, or Customer) should have a username and
		password.
	* Customers are free to register for their own account.
	* Staff accounts must be created by the Owner (it is fine for the Owner
		to set passwords for the Staff).
	* If a user is logged in, no matter what page they are on, they should
		have access to a logout link.

3. Owner
	* Should be able to login with the username `owner` and password `pass`.
	* Once logged in, the Owner should be presented with a link to create new
		staff accounts, and a list of all scheduled events.
		* For each event, the Staff members signed up to work that event should
			be listed.
		* If no events are scheduled, a message should be displayed informing
			the Owner of this explicitly.
		* If any scheduled event has no staff signed up to work, a message
			should be displayed informing the Owner of this explicitly.

4. Staff
	* Once logged in, Staff members should be presented with a list of events
		they are scheduled to work and a list of events that they can sign up to
		work.
		* For each event that a Staff member can sign up to work, they should
			be provided a link to sign up for that event.
		* No event that already has 3 Staff members signed up to work should be
			presented as a sign up option for other Staff members.

5. Customers
	* Once logged in, Customers should be presented with a form to request a
		new event, and a list of events they have already requested.
		* If a Customer requests an event on a date when another event is
			already scheduled, they should be presented with an message saying
			that the company is already booked for that date.
		* For each requested event, the Customer should be provided with a link
			to cancel that event.

6. Data management
	* To ease bootstrapping and testing of your application, hardcode the
		Owner's username and password in your app to be `owner` and `pass`.
	* All other data for your application should be stored in an SQLite
		database named `catering.db` using SQLAlchemy's ORM and the
		Flask-SQLAlchemy extension.

<em>Note: The project specifications were written by my professor, Dr. Farnan.</em>

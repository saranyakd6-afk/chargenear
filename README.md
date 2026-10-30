PROJECT HANDOFF: ChargeNear (Saranya's project)

OVERVIEW
ChargeNear is a Django web app: Smart EV Charging Station Finder and Booking System.
Users find stations on a map, see slot availability and wait time, get charging time
and cost estimates, book slots with a QR ticket, and review stations. Staff manage
stations and bookings and see analytics.
Owner: Pranav (CSE graduate). Wants short answers.

STACK
Python 3.15, Django 6.1.2, SQLite, Bootstrap 5, HTML/CSS/JS, Leaflet.js + OpenStreetMap,
Chart.js, qrcode + pillow. Windows, venv, folder: C:\Users\prana\saranya pyhton
Run: venv\Scripts\activate, then python manage.py runserver

STRUCTURE
chargenear/ (settings.py, urls.py)   core/ (models, views, forms, urls, admin, backends)
core/templates/ (all templates live here, NOT in a root templates folder)
core/templates/registration/ (login.html, register.html)
core/management/commands/seed.py (optional; demo data was added via the shell instead)

SETTINGS (settings.py)
- INSTALLED_APPS includes 'core'
- TIME_ZONE = 'Asia/Kolkata'
- LOGIN_REDIRECT_URL = 'home', LOGOUT_REDIRECT_URL = 'home'
- AUTHENTICATION_BACKENDS = ['core.backends.EmailOrUsernameBackend']
- DEFAULT_FROM_EMAIL set. Django 6.1 uses MAILERS (console backend) and the old
  EMAIL_BACKEND setting must NOT be present (it caused ImproperlyConfigured).

MODELS (core/models.py)
Vehicle(owner, name, battery_kwh, connector_type)
Station(name, address, latitude, longitude, charger_type, power_kw, price_per_kwh,
        total_slots, is_open)
Booking(user, vehicle, station, start_time, end_time, current_battery, target_battery,
        est_cost, status[booked/charging/done/cancelled])
Review(user, station, rating 1-5, comment)

URLS and VIEWS (core/urls.py -> views.py)
/ home | /register/ register (RegisterForm with email) | /accounts/login/ SmartLoginView
(login by username OR email; staff redirect to /admin/, others to home) | /accounts/ django auth urls
/stations/ station_list (search, type filter, free slots, waiting count, next-slot wait time,
  avg rating, map_data for Leaflet)
/station/<id>/ station_detail (reviews, one review per user, editable)
/vehicle/add/ add_vehicle | /book/<id>/ book_station | /my-bookings/ | /cancel/<id>/
/planner/ trip_planner + /api/plan/ plan_trip_api (JSON)
/ticket/<id>/ ticket | /booking/<id>/qr/ booking_qr (PNG) | /verify/<id>/ verify_booking (staff only,
  POST sets status to charging) | /dashboard/ dashboard (staff only)

CORE LOGIC
- Energy = battery_kwh x (target% - current%) / 100
- Charging time = energy / charger power kW ; end_time = start + time
- Cost = energy x price_per_kwh
- Slot clash: count overlapping booked/charging bookings; reject if >= total_slots
- Range (km) = battery_kwh x battery% / 100 / 0.15 x 0.9 ; road distance = haversine x 1.3
- Booking sends confirmation email (printed in terminal) inside try/except
- Nearest-first sort uses browser geolocation + haversine in JS

FORMS (core/forms.py)
RegisterForm(UserCreationForm + email), VehicleForm, BookingForm(user=...), ReviewForm

TEMPLATES
base.html: dark glass theme for inner pages, navbar with role-based buttons
home.html: standalone page, live canvas particle network background, hero, 3 feature cards
registration/login.html: standalone, "calm energy portal" rings, username-or-email field
registration/register.html: standalone, circuit-flow background, power-fill progress bar,
  helptext badges, loops over form fields
stations.html: search, filter, Leaflet map with green/red pins and legend, station cards,
  Show on map button | station_detail.html | book.html | form_page.html | my_bookings.html
ticket.html (QR) | verify.html | planner.html | dashboard.html (Chart.js: peak hours,
  bookings and revenue per station)
Theme: dark slate #0f172a, teal #06b6d4, amber #f59e0b, Inter font, glassmorphism.
Navbar: logged out = Admin, Login, Register; logged in = Stations, Trip Planner,
My Bookings; staff also = Dashboard, Admin Panel.

ADMIN (core/admin.py)
Station list_editable (price, slots, is_open), BookingInline, Booking actions
(mark charging / completed), Vehicle, Review registered; custom site header.

DEMO DATA
5 stations (Thrissur, Round South, Kochi, Guruvayur, Palakkad), demo users arjun/meera/rahul
(password demo12345), 14 bookings, reviews. Admin account: created via createsuperuser
(username and email unknown to the assistant; reset with: python manage.py changepassword USERNAME).

STATUS
Verified working (check_all.py): home, login, register, stations, station detail = HTTP 200;
arjun login OK; 5 stations, 14 bookings exist.
Not yet confirmed: My Bookings, Planner, Add Vehicle, Book, Ticket, QR, Dashboard, Verify,
admin login via email.
Past issues fixed: IndentationError in views.py, 'core' missing from INSTALLED_APPS,
EMAIL_BACKEND vs MAILERS conflict, qrcode not installed in venv, station_list missing return,
core/backends.py missing (ModuleNotFoundError), station_detail/ticket/verify templates missing.
To re-test: python manage.py shell -c "exec(open('check_all.py').read())"
(piping with < breaks on multi-line blocks).

REMAINING
1. Confirm every page returns 200 and admin email login works
2. Remove the stray {% for label, val in stat_cards %}{% endfor %} line in dashboard.html;
   add Chart.defaults.color='#94a3b8' and Chart.defaults.borderColor='rgba(255,255,255,0.08)'
3. Build the PPT or Word report (abstract, objectives, modules, formulas, limitations, future scope)
4. Optional: deploy on Render, push to GitHub with a README

LIMITATIONS (for viva)
Availability comes from bookings, not live charger hardware; fixed 0.15 kWh/km consumption;
no payment gateway.

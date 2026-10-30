# ⚡ ChargeNear

**Smart EV Charging Station Finder and Booking System**

ChargeNear is a full-stack web application built with Django. EV users can find nearby charging stations, check slot availability and waiting time, see the estimated charging time and cost, and book a slot with a QR ticket. Station administrators manage stations and bookings and view usage analytics.

## Features

**For EV users**
- Register and log in with a username or email
- Save vehicle details (battery capacity and connector type)
- Search and filter stations by name, address and charger type
- Interactive map with green (slot free) and red (full) pins, and "nearest first" using browser location
- Free slots, waiting count and estimated time until the next slot is free
- Slot booking with automatic charging time and cost estimate, and a clash check so a slot is never double booked
- QR code ticket and email confirmation for every booking
- Trip range planner: checks if a destination is reachable on the current battery and suggests charging stops
- Station reviews and ratings
- My Bookings page with cancel option

**For administrators**
- Django admin panel to manage stations (price, slots, open or closed), bookings, vehicles and reviews
- QR verification page to start a charging session
- Analytics dashboard (Chart.js): peak booking hours, bookings per station and revenue per station

## Tech stack

| Area | Technology |
|---|---|
| Backend | Python, Django |
| Database | SQLite |
| Frontend | HTML, CSS, JavaScript, Bootstrap 5 |
| Maps | Leaflet.js, OpenStreetMap |
| Charts | Chart.js |
| QR codes | `qrcode`, Pillow |

## How the calculations work

- Energy needed (kWh) = battery capacity × (target % − current %) ÷ 100
- Charging time (hours) = energy needed ÷ charger power (kW)
- Estimated cost = energy needed × price per kWh
- Range (km) = battery kWh × battery % ÷ 100 ÷ 0.15 × 0.9
- Distance uses the Haversine formula × 1.3 (approximate road distance)
- A booking is rejected if the overlapping bookings are equal to or more than the station's total slots

## Database models

`Vehicle`, `Station`, `Booking`, `Review`, plus Django's built-in `User`.

## Getting started

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/chargenear.git
cd chargenear

# 2. Create and activate a virtual environment (Windows)
python -m venv venv
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up the database
python manage.py makemigrations
python manage.py migrate

# 5. Create an admin account
python manage.py createsuperuser

# 6. Run the server
python manage.py runserver
```

Open http://127.0.0.1:8000, then log in to `/admin/` and add a few charging stations (with latitude and longitude) to see the map and bookings in action.

## Project structure

```
chargenear/        Project settings and root URLs
core/              Main app: models, views, forms, URLs, admin, login backend
core/templates/    All HTML templates
```

## Limitations

- Slot availability is based on bookings in the database, not live charger hardware
- Energy consumption is fixed at 0.15 kWh/km for range estimates
- No online payment
- Location features need the browser's location permission

## Future scope

- Payment gateway
- IoT integration for real-time charger status
- Mobile app
- Dynamic pricing
- SMS alerts
- Route-based trip planning with a maps API



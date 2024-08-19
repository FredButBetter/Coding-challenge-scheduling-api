## Overview
This is my submission to the Henry Meds coding test.

My thought process behind tradeoffs was to try to get as much of the API functionality working as possible in the time allotted, while trading-off anything that wouldn't impact performance for the sake of the time limit.

These are the main limitations as I see them:
* All storage is done with variables on server memory, instead of databases. This is obviously far from ideal, and I would prefer a Postgres database with relational tables
* No testing, I would of course prefer as close to 100% unit test coverage as possible, but ran out of time while trying to get mocking set up for tests
* No user authentication, for example providers should only be able to change their own availability with a user/pass etc.
* Lots of suboptimal searching through the fake-database dictionaries, which would be orders of magnitude slower than SQL at production scale
* Needs more fleshed out functionality, i.e. removing blocks of availability, updating more fields, more input grooming / checking, etc.
* resources.py should be split up into providers.py, clients.py, etc.
* Small edge case bug - The check to stop duplicate availability creation doesn't seem to work

## Running

1. Clone this git repo 
2. Navigate into the HenryMeds folder just cloned
3. Install required packages - pip install -r ./requirements.txt
4. Run app.py - python3 ./App/__init__.py

The Flask server will start, and you can now use the api via localhost on port 5000

## Endpoints

```
/api/providers
     GET - Lists all providers
     POST - create new provider
         Required JSON - "name" : string

 /api/providers/{provider_id}
     GET - Lists provider with matching ID
     PUT - updates name of matching provider
         Required JSON - "name" : string* 
     DELETE - deletes matching provider
     
 /api/providers/availability/{provider_id}
     GET - Lists available appointment slots for matching provider
     POST - Create new appointment slots for matching provider
         Required JSON - "start_datetime": start date string in "YYYY-MM-DD HH:MM:00" format, minutes must be on division of 15 minutes
                         "end_datetime": end date string in "YYYY-MM-DD HH:MM:00" format
                        
 /api/clients
     GET - Lists all clients
     POST - create new client
         Required JSON - "name" : string

 /api/clients/{client_id}
     GET - Lists client with matching ID
     PUT - updates name of matching client
         Required JSON - "name" : string
     DELETE - deletes matching client

 /api/appointments
     GET - returns all appointments, both reservered and available, for all providers

 /api/appointments/reserve
     GET - returns all appointments which are available for reservation
         side effect - grooms all appointments to check for unconfirmed reservation attempts

 /api/appointments/reserve/id
     POST - reserve the appointment with matching appointment id for client with matching client_id
         Required JSON - "client_id" : int
         side effect - grooms all appointments to check for unconfirmed reservation attempts

 /api/appointments/confirm/id
     POST - confirm the pending appointment with matching appointment id
         side effect - grooms all appointments to check for unconfirmed reservation attempts
```


Intended workflow for reservation - 
    1. GET /api/appointments/reserve to get all possible reservations
    2. Client chooses appropriate appointment
    3. UI uses the selected appoinment's id and current client's id in POST to /api/appoinments/reserve/id
    4. Email or follow-up screen to POST to /api/appointments/confirm/id

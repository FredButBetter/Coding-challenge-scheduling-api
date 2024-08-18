import datetime

from flask_restx import Resource, Namespace
from werkzeug.exceptions import BadRequest

from models import provider_model, client_model, appointment_model, provider_input_model, client_input_model, availability_input_model, reservation_model

ns = Namespace("api")

provider_id_counter = 1
# Provider data starts with a couple of default providers for debugging purposes
providers = [
    {'id': 0,
     'name': 'tester',
     'schedule': {}
     },
    {'id': 1,
     'name': 'Fred Etingen',
     'schedule': {"2024-08-01:10:00":'available'}
     }
]

client_id_counter = 1
clients = [
    {'id': 0,
     'name': 'test client',
     'current_appointments': {}
     },
    {'id': 1,
     'name': 'Hnery Med',
     'current_appointments': {}
     }
]

appointments_id_counter = 3
appointments = [
    {'id': 0,
     'provider': providers[0],
     'datetime': datetime.datetime(2024, 8, 1, 10, 0),
     'client': clients[0],
     'submitted': datetime.datetime(2024, 7, 1, 12, 0),
     'confirmed': True
     },
    {'id': 1,
     'provider': providers[0],
     'datetime': datetime.datetime(2024, 8, 24, 10, 0),
     'client': clients[1],
     'submitted': datetime.datetime(2024, 8, 18, 18, 30),
     'confirmed': False
     },
    {'id': 2,
     'provider': providers[0],
     'datetime': datetime.datetime(2024, 8, 24, 10, 0),
     'client': None,
     'submitted': None,
     'confirmed': False
     },
    {'id': 3,
     'provider': providers[1],
     'datetime': datetime.datetime(2024, 9, 1, 14, 30),
     'client': None,
     'submitted': None,
     'confirmed': False
     }
]

def groom_all_appointments():
    for appointment in appointments:
        if appointment["client"] is not None and appointment["confirmed"] is False:
            if datetime.datetime.now() > appointment["submitted"] + datetime.timedelta(minutes=30):
                appointment["client"] = None
                appointment["submitted"] = None
                appointment["confirmed"] = False

@ns.route("/providers")
class ProviderListAPI(Resource):
    def get_next_provider_id_number(self):
        global provider_id_counter
        provider_id_counter += 1
        return provider_id_counter

    def get(self):
        return providers

    @ns.expect(provider_input_model)
    @ns.marshal_with(provider_model)
    def post(self):
        new_provider = dict()
        new_provider["id"] = self.get_next_provider_id_number()
        new_provider["name"] = ns.payload["name"]
        providers.append(new_provider)
        return new_provider, 201


@ns.route("/providers/<int:id>")
class ProviderAPI(Resource):
    @ns.marshal_with(provider_model)
    def get(self, id):
        for provider in providers:
            if provider['id'] == id:
                return provider
        raise BadRequest("Provider {} doesn't exist".format(id))

    @ns.marshal_with(provider_model)
    def put(self, id):
        for provider in providers:
            if provider['id'] == id:
                provider['name'] = ns.payload["name"]
                return provider, 200
        raise BadRequest("Provider {} doesn't exist".format(id))

    def delete(self, id):
        for provider in providers:
            if provider['id'] == id:
                providers.remove(provider)
                return {}, 204
        raise BadRequest("Provider {} doesn't exist".format(id))


@ns.route("/providers/availability/<int:id>")
class ProviderAvailabilityAPI(Resource):
    def get_next_appointment_id_number(self):
        global appointments_id_counter
        appointments_id_counter += 1
        return appointments_id_counter

    def get_all_appointment_slots(self, start_time, end_time):
        current_time = start_time
        while current_time <= end_time:
            yield current_time
            current_time += datetime.timedelta(minutes=15)

    def does_appointment_exist(self, provider, time):
        for appointment in appointments:
            if appointment['provider']['id'] == provider and appointment["datetime"] == time:
                return True
        return False

    @ns.marshal_list_with(appointment_model)
    def get(self, id):
        result_list = []
        for appointment in appointments:
            if appointment['provider']['id'] == id:
                result_list.append(appointment)
        return result_list

    @ns.marshal_with(availability_input_model)
    def post(self, id):
        start_datetime = datetime.datetime.fromisoformat(ns.payload["start_datetime"])
        end_datetime = datetime.datetime.fromisoformat(ns.payload["end_datetime"])
        if not start_datetime < end_datetime:
            raise BadRequest("Start time must be before end time")
        if start_datetime.minute % 15 != 0:
            raise BadRequest("Start time must be multiple of 15 minutes")
        current_provider = None
        for provider in providers:
            if provider['id'] == id:
                current_provider = provider
        if current_provider is None:
            raise BadRequest("Provider {} doesn't exist".format(id))

        new_appointment_times = self.get_all_appointment_slots(start_datetime, end_datetime)
        for new_time in new_appointment_times:
            if self.does_appointment_exist(current_provider, new_time):
                continue
            new_appointment = {'id': self.get_next_appointment_id_number(),
                               'provider': current_provider,
                               'datetime': new_time,
                               'client': None,
                                "submitted": None,
                                "confirmed": False
                               }
            appointments.append(new_appointment)
        return current_provider, 200


@ns.route("/clients")
class ClientListAPI(Resource):
    def get_next_client_id_number(self):
        global client_id_counter
        client_id_counter += 1
        return client_id_counter


    def get(self):
        return clients

    @ns.expect(client_input_model)
    @ns.marshal_with(client_model)
    def post(self):
        new_client = dict()
        new_client["id"] = self.get_next_client_id_number()
        new_client["name"] = ns.payload["name"]
        clients.append(new_client)
        return new_client, 201


@ns.route("/clients/<int:id>")
class ClientAPI(Resource):
    @ns.marshal_with(client_model)
    def get(self, id):
        for client in clients:
            if client['id'] == id:
                return client
        raise BadRequest("Client {} doesn't exist".format(id))

    @ns.marshal_with(client_model)
    def put(self, id):
        for client in clients:
            if client['id'] == id:
                client['name'] = ns.payload["name"]
                return client, 200
        raise BadRequest("Client {} doesn't exist".format(id))

    def delete(self, id):
        for client in clients:
            if client['id'] == id:
                clients.remove(client)
                return {}, 204
        raise BadRequest("Provider {} doesn't exist".format(id))


@ns.route("/appointments")
class AppointmentAPI(Resource):
    @ns.marshal_list_with(appointment_model)
    def get(self):
        groom_all_appointments()
        return appointments


@ns.route("/appointments/reserve")
class AvailableAppointmentsAPI(Resource):
    @ns.marshal_list_with(appointment_model)
    def get(self):
        groom_all_appointments()
        available_appointments = []
        for appointment in appointments:
            if appointment["client"] is None and datetime.datetime.now() < appointment["datetime"] + datetime.timedelta(days=1):
                available_appointments.append(appointment)
        return available_appointments


@ns.route("/appointments/reserve/<int:id>")
class AppointmentReservationAPI(Resource):
    @ns.marshal_list_with(reservation_model)
    def post(self, id):
        res_appointment = None
        for appointment in appointments:
            if appointment['id'] == id:
                res_appointment = appointment
        if res_appointment is None:
            raise BadRequest("Appointment {} doesn't exist".format(id))
        res_client = None
        for client in clients:
            if client['id'] == ns.payload["client_id"]:
                res_client = client
        if res_client is None:
            raise BadRequest("Client {} doesn't exist".format(ns.payload["client_id"]))
        if res_appointment["client"] is not None:
            raise BadRequest("Appointment {} already has a client reservation".format(id))
        if datetime.datetime.now() < res_appointment["datetime"] + datetime.timedelta(days=1):
            raise BadRequest("Appointment {} is not at least 24 hours from now".format(id))
        res_appointment["client"] = res_client
        res_appointment["submitted"] = datetime.datetime.now()
        res_appointment["confirmed"] = False
        return res_appointment, 200

@ns.route("/appointments/confirm/<int:id>")
class AppointmentConfirmationAPI(Resource):
    @ns.marshal_with(appointment_model)
    def post(self, id):
        groom_all_appointments()
        res_appointment = None
        for appointment in appointments:
            if appointment['id'] == id:
                res_appointment = appointment
        if res_appointment is None:
            raise BadRequest("Appointment {} doesn't exist".format(id))
        if res_appointment['client'] is None:
            raise BadRequest("Appointment {} hasn't been registered to a client yet".format(id))
        res_appointment["confirmed"] = True
        return res_appointment, 200


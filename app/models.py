from flask_restx import fields

from extensions import api

client_model = api.model("Client",
                           {
                               "id": fields.Integer,
                               "name": fields.String
                           })

client_input_model = api.model("ClientInput",
                           {
                               "name": fields.String
                           })

provider_model = api.model("Provider",
                           {
                               "id": fields.Integer,
                               "name": fields.String
                           })

provider_input_model = api.model("ProviderInput",
                           {
                               "name": fields.String
                           })

appointment_model = api.model("Appointment",
                              {
                                  "id": fields.Integer,
                                  "provider": fields.Nested(provider_model),
                                  "datetime": fields.DateTime,
                                  "client": fields.List(fields.Nested(client_model)),
                                  "submitted": fields.DateTime,
                                  "confirmed": fields.Boolean
                              })

availability_input_model = api.model("AvailabilityInput",
                              {
                                  "start_datetime": fields.String,
                                  "end_datetime": fields.String
                              })

reservation_model = api.model("Reservation",
                              {
                                  "client_id": fields.Integer
                              })
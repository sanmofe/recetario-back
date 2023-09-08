import json
import hashlib
from unittest import TestCase

from faker import Faker
from faker.generator import random
from modelos import db, Usuario, Ingrediente, Roles

from app import app

class TestIngredienteAdmin(TestCase):

    def setUp(self):
        self.data_factory = Faker()
        self.client = app.test_client()

        nombre_usuario = 'test_'+ self.data_factory.name()
        contrasena = 'T1$'+ self.data_factory.word()
        contrasena_encriptada = hashlib.md5(contrasena.encode('utf-8')).hexdigest()

        #Usuario creado en la base

        usario_nuevo = Usuario(usuario = nombre_usuario, contrasena = contrasena_encriptada, rol = Roles.ADMIN)
        db.session.add(usario_nuevo)
        db.session.commit()

        usuario_login = {
            "usuario": nombre_usuario,
            "contrasena": contrasena
        }

        solicitud_login = self.client.post("/login", data= json.dumps(usuario_login), headers = {'content-type': 'application/json'})

        respuesta_login = json.loads(solicitud_login.get_data())

        self.token = respuesta_login["token"]
        self.usuario_id = respuesta_login["id"]

        self.ingredientes_creados = []

        def tearDown(self):
            for inngrediente_creado in self.ingrestes_creados:
                ingrediente = Ingrediente.query.get(inngrediente_creado.id)
                db.session.delete(ingrediente)
                db.session.commit()
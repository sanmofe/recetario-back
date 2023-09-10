import json
import hashlib
from unittest import TestCase

from faker import Faker
from faker.generator import random
from modelos import db, Usuario, Roles

from app import app

class TestChef(TestCase):

    def setUp(self):
        self.data_factory = Faker()
        self.client = app.test_client()
        
        nombre_usuario = 'test_' + self.data_factory.name()
        contrasena = 'T1$' + self.data_factory.word()
        contrasena_encriptada = hashlib.md5(contrasena.encode('utf-8')).hexdigest()
        
        # Se crea el usuario para identificarse en la aplicación
        usuario_nuevo = Usuario(usuario=nombre_usuario, contrasena=contrasena_encriptada, rol=Roles.ADMIN)
        db.session.add(usuario_nuevo)
        db.session.commit()

        
        usuario_login = {
            "usuario": nombre_usuario,
            "contrasena": contrasena
        }

        solicitud_login = self.client.post("/login",
                                                data=json.dumps(usuario_login),
                                                headers={'Content-Type': 'application/json'})

        respuesta_login = json.loads(solicitud_login.get_data())

        self.token = respuesta_login["token"]
        self.usuario_id = respuesta_login["id"]
        
        self.chefs_creados = []

    def tearDown(self):
        for chef_creado in self.chefs_creados:
            chef = Usuario.query.get(chef_creado.id)
            db.session.delete(chef)
            db.session.commit()
            
        usuario_login = Usuario.query.get(self.usuario_id)
        db.session.delete(usuario_login)
        db.session.commit()

    def test_crear_chef(self):
        nombre = self.data_factory.name()
        user = 'test_' + self.data_factory.name()
        pwd = 'T1$' + self.data_factory.word()

        jsonChef = {
            "nombre": nombre,
            "usuario":user,
            "contrasena": pwd
        }

        endpoint = "/chefs/"+str(self.usuario_id)
        headers = {'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}
        resultado = self.client.post(endpoint,
                                     data = json.dumps(jsonChef),
                                     headers = headers)
        
        response = json.loads(resultado.get_data())
        chef = Usuario.query.get(response["id"])
        self.chefs_creados.append(chef)

        self.assertEqual(resultado.status_code, 200)
    
    def test_dar_chef(self):
        contrasena = 'T1$' + self.data_factory.word()
        contrasena_encriptada = hashlib.md5(contrasena.encode('utf-8')).hexdigest()
        
        chef = Usuario(
            nombre = self.data_factory.name(),
            usuario = 'test_' + self.data_factory.name(),
            contrasena = contrasena_encriptada,
            rol = Roles.CHEF,
            parent_id = self.usuario_id
        )
        db.session.add(chef)
        db.session.commit()
        self.chefs_creados.append(chef)
        endpoint = "/chefs/"+str(self.usuario_id)
        headers = {'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}
        resultado = self.client.get(endpoint,
                                     headers = headers)
        response = json.loads(resultado.get_data())[0]
        self.assertEqual(resultado.status_code, 200)
        self.assertEqual(response["nombre"], chef.nombre)
        self.assertEqual(response["usuario"], chef.usuario)
        self.assertEqual(response["contrasena"], contrasena_encriptada)

    def test_listar_chefs(self):
        
        for i in range(10):
            contrasena = 'T1$' + self.data_factory.word()
            contrasena_encriptada = hashlib.md5(contrasena.encode('utf-8')).hexdigest()
        
            chef = Usuario(
                nombre=self.data_factory.name(),
                usuario='test_' + self.data_factory.name(),
                contrasena=contrasena_encriptada,
                rol=Roles.CHEF,
                parent_id=self.usuario_id
            )
            db.session.add(chef)
            db.session.commit()
            self.chefs_creados.append(chef)

        endpoint_chefs = "/chefs/" + str(self.usuario_id)
        headers = {'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}
        resultado_consulta_chefs = self.client.get(endpoint_chefs, headers=headers)
        datos_respuesta = json.loads(resultado_consulta_chefs.get_data())
        self.assertEqual(resultado_consulta_chefs.status_code, 200)
        
        for chef in datos_respuesta:
            for chef_creado in self.chefs_creados:
                if chef['id'] == str(chef_creado.id):
                    self.assertEqual(chef['nombre'], chef_creado.nombre)
                    self.assertEqual(chef['usuario'], chef_creado.usuario)
                    self.assertEqual(chef['contrasena'], chef_creado.contrasena)
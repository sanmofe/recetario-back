import json
import hashlib
from unittest import TestCase

from faker import Faker
from faker.generator import random
from modelos import db, Usuario, Roles, Resturante

from app import app

class TestChefRestaurante(TestCase):

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
        
        self.restaurantes_creados = []
        self.chefs_creados = []

        for i in range(2):
            nombre_nuevo_restaurante = self.data_factory.sentence()
            direccion_nuevo_restaurante = self.data_factory.sentence()
            telefono_nuevo_restaurante = self.data_factory.sentence()
            redesSociales_nuevo_restaurante = self.data_factory.sentence()
            horario_nuevo_restaurante = self.data_factory.sentence()
            tipoComida_nuevo_restaurante = self.data_factory.sentence()
            apps_nuevo_restaurante = self.data_factory.sentence()
            opciones_nuevo_restaurante = round(random.uniform(1, 3))
        
            #Crear el json con el restaurante a crear
            nuevo_restaurante = Resturante(nombre = nombre_nuevo_restaurante,
                                        direccion = direccion_nuevo_restaurante, 
                                        telefono = telefono_nuevo_restaurante,
                                        redesSociales = redesSociales_nuevo_restaurante, 
                                        horario = horario_nuevo_restaurante, 
                                        tipoComida = tipoComida_nuevo_restaurante,
                                        apps = apps_nuevo_restaurante, 
                                        opciones = opciones_nuevo_restaurante)

            db.session.add(nuevo_restaurante)
            db.session.commit()

            self.restaurantes_creados.append(nuevo_restaurante)

    def tearDown(self):
        for chef_creado in self.chefs_creados:
            chef = Usuario.query.get(chef_creado.id)
            db.session.delete(chef)
            db.session.commit()
            
        for restaurante_creado in self.restaurantes_creados:
            restaurante = Resturante.query.get(restaurante_creado.id)
            db.session.delete(restaurante)
            db.session.commit()

        usuario_login = Usuario.query.get(self.usuario_id)
        db.session.delete(usuario_login)
        db.session.commit()

    def testDiferentesRestaurantes(self):
        for i in self.restaurantes_creados:
            nombre = self.data_factory.name()
            user = 'test_' + self.data_factory.name()
            pwd = 'T1$' + self.data_factory.word()

            jsonChef = {
                "nombre": nombre,
                "usuario":user,
                "contrasena": pwd,
                "restaurante": i.id
            }
            endpoint = "/chefs/"+str(self.usuario_id)
            headers = {'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}
            resultado = self.client.post(endpoint,
                                     data = json.dumps(jsonChef),
                                     headers = headers)
        
            response = json.loads(resultado.get_data())
            chef = Usuario.query.get(response["id"])
            self.chefs_creados.append(chef)

        #Ahora agarramos los datos de los chefs de los restaurantes

        nuevo_endpoint = "/restaurante/"+str(i.id)+"/empleados"
        resultado = self.client.get(nuevo_endpoint,
                                headers = headers)
        datos_respuesta = json.loads(resultado.get_data())
        self.assertEqual(resultado.status_code, 200)
                
        self.assertEqual(len(datos_respuesta), 1)
        encontrado = datos_respuesta[0]
        self.assertEqual(encontrado['nombre'], chef.nombre)
        self.assertEqual(encontrado['usuario'], chef.usuario)


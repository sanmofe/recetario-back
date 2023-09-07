import json
import hashlib
from unittest import TestCase

from faker import Faker
from faker.generator import random
from modelos import db, Usuario, Ingrediente

from app import app


class TestIngreso(TestCase):

    def setUp(self):
        self.data_factory = Faker()
        self.client = app.test_client()

        #Se crean 2 usuarios con roles distintos
        nombre_usuario_1 = 'test_' + self.data_factory.name()
        contrasena_1 = 'T1$' + self.data_factory.word()
        contrasena_encriptada_1 = hashlib.md5(contrasena_1.encode('utf-8')).hexdigest()
        self.rol_1 = 'ADMIN'

        nombre_usuario_2 = 'test_' + self.data_factory.name()
        contrasena_2 = 'T1$' + self.data_factory.word()
        contrasena_encriptada_2 = hashlib.md5(contrasena_2.encode('utf-8')).hexdigest()
        self.rol_2 = 'CHEF'
        
        # Se crea el usuario para identificarse en la aplicación
        usuario_nuevo_1 = Usuario(usuario=nombre_usuario_1, contrasena=contrasena_encriptada_1,rol=self.rol_1)
        db.session.add(usuario_nuevo_1)
        db.session.commit()

        usuario_nuevo_2 = Usuario(usuario=nombre_usuario_2, contrasena=contrasena_encriptada_2,rol=self.rol_2)
        db.session.add(usuario_nuevo_2)
        db.session.commit()

        print("USUARIO 1: ",usuario_nuevo_1.rol)
        usuario_login_1 = {
            "usuario": nombre_usuario_1,
            "contrasena": contrasena_1
        }

        usuario_login_2 = {
            "usuario": nombre_usuario_2,
            "contrasena": contrasena_2
        }

        solicitud_login_1 = self.client.post("/login",
                                                data=json.dumps(usuario_login_1),
                                                headers={'Content-Type': 'application/json'})

        respuesta_login_1 = json.loads(solicitud_login_1.get_data())

        self.token = respuesta_login_1["token"]
        self.usuario_id = respuesta_login_1["id"]

        solicitud_login_2 = self.client.post("/login",
                                                data=json.dumps(usuario_login_2),
                                                headers={'Content-Type': 'application/json'})

        respuesta_login_2 = json.loads(solicitud_login_2.get_data())
        

        self.token_2 = respuesta_login_2["token"]
        self.usuario_id_2 = respuesta_login_2["id"]

        #Definir endpoint, encabezados y hacer el llamado


        
    def tearDown(self):
            
        usuario_login = Usuario.query.get(self.usuario_id)
        db.session.delete(usuario_login)
        db.session.commit()

    def test_roles_usuario(self):
        #Crear los datos del ingrediente
        nombre_nuevo_ingrediente = self.data_factory.sentence()
        unidad_nuevo_ingrediente = self.data_factory.sentence()

        endpoint_user = "/api/user-type"
        headers1 = {'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}
        resultado_consulta_rol_usuario1 = self.client.get(endpoint_user, headers=headers1)
        datos_respuesta_usuario1 = json.loads(resultado_consulta_rol_usuario1.get_data())

        print(datos_respuesta_usuario1['user_type'])

        endpoint_user = "/api/user-type"
        headers2 = {'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token_2)}
        resultado_consulta_rol_usuario2 = self.client.get(endpoint_user, headers=headers2)
        datos_respuesta_usuario2 = json.loads(resultado_consulta_rol_usuario2.get_data())

        print(datos_respuesta_usuario2['user_type'])


        self.assertEqual(resultado_consulta_rol_usuario1.status_code,200)
        self.assertEqual(resultado_consulta_rol_usuario2.status_code,200)
        self.assertEqual(datos_respuesta_usuario1['user_type'],self.rol_1)
        self.assertEqual(datos_respuesta_usuario2['user_type'],self.rol_2)
        
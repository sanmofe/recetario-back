import json
import hashlib
from unittest import TestCase

from faker import Faker
from faker.generator import random
from modelos import db, Usuario, Resturante

from app import app


class TestRestaurante(TestCase):

    def setUp(self):
        self.data_factory = Faker()
        self.client = app.test_client()
        
        nombre_usuario = 'test_' + self.data_factory.name()
        contrasena = 'T1$' + self.data_factory.word()
        contrasena_encriptada = hashlib.md5(contrasena.encode('utf-8')).hexdigest()
        
        # Se crea el usuario para identificarse en la aplicación
        usuario_nuevo = Usuario(usuario=nombre_usuario, contrasena=contrasena_encriptada)
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
        
    
    def tearDown(self):
        for restaurante_creado in self.restaurantes_creados:
            restaurante = Resturante.query.get(restaurante_creado.id)
            db.session.delete(restaurante)
            db.session.commit()
            
        usuario_login = Usuario.query.get(self.usuario_id)
        db.session.delete(usuario_login)
        db.session.commit()

    def test_crear_restaurante(self):
        #Crear los datos del restaurante
        nombre_nuevo_restaurante = self.data_factory.sentence()
        direccion_nuevo_restaurante = self.data_factory.sentence()
        telefono_nuevo_restaurante = self.data_factory.sentence()
        redesSociales_nuevo_restaurante = self.data_factory.sentence()
        horario_nuevo_restaurante = self.data_factory.sentence()
        tipoComida_nuevo_restaurante = self.data_factory.sentence()
        apps_nuevo_restaurante = self.data_factory.sentence()
        opciones_nuevo_restaurante = round(random.uniform(1, 3))
        
        #Crear el json con el restaurante a crear
        nuevo_restaurante = {
            "nombre": nombre_nuevo_restaurante,
            "direccion": direccion_nuevo_restaurante,
            "telefono": telefono_nuevo_restaurante,
            "redesSociales": redesSociales_nuevo_restaurante,
            "horario": horario_nuevo_restaurante,
            "tipoComida": tipoComida_nuevo_restaurante,
            "apps": apps_nuevo_restaurante,
            "opciones": opciones_nuevo_restaurante
        }
        
        #Definir endpoint, encabezados y hacer el llamado
        endpoint_restaurantes = "/restaurantes/" + str(self.usuario_id)
        headers = {'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}
        
        resultado_nuevo_restaurante = self.client.post(endpoint_restaurantes,
                                                   data=json.dumps(nuevo_restaurante),
                                                   headers=headers)
                                                   
        #Obtener los datos de respuesta y dejarlos un objeto json y en el objeto a comparar
        datos_respuesta = json.loads(resultado_nuevo_restaurante.get_data())
        restaurante = Resturante.query.get(datos_respuesta['id'])
        self.restaurantes_creados.append(restaurante)

        
                                                   
        #Verificar que el llamado fue exitoso y que el objeto recibido tiene los datos iguales a los creados
        self.assertEqual(resultado_nuevo_restaurante.status_code, 200)
        self.assertEqual(datos_respuesta['nombre'], restaurante.nombre)
        self.assertEqual(datos_respuesta['direccion'], restaurante.direccion)
        self.assertEqual(datos_respuesta['telefono'], restaurante.telefono)
        self.assertEqual(datos_respuesta['redesSociales'], restaurante.redesSociales)
        self.assertEqual(datos_respuesta['horario'], restaurante.horario)
        self.assertEqual(datos_respuesta['tipoComida'], restaurante.tipoComida)
        self.assertEqual(datos_respuesta['apps'], restaurante.apps)
        self.assertEqual(float(datos_respuesta['opciones']), float(restaurante.opciones))
        self.assertIsNotNone(datos_respuesta['id'])

    def test_dar_restaurante(self):
        #Crear los datos del restaurante
        nombre_nuevo_restaurante = self.data_factory.sentence()
        direccion_nuevo_restaurante = self.data_factory.sentence()
        telefono_nuevo_restaurante = self.data_factory.sentence()
        redesSociales_nuevo_restaurante = self.data_factory.sentence()
        horario_nuevo_restaurante = self.data_factory.sentence()
        tipoComida_nuevo_restaurante = self.data_factory.sentence()
        apps_nuevo_restaurante = self.data_factory.sentence()
        opciones_nuevo_restaurante = round(random.uniform(1, 3))

        #Crear el restaurante con los datos originales para obtener su id
        restaurante = Resturante(nombre = nombre_nuevo_restaurante,
            direccion = direccion_nuevo_restaurante,
            telefono = telefono_nuevo_restaurante,
            redesSociales = redesSociales_nuevo_restaurante,
            horario = horario_nuevo_restaurante,
            tipoComida = tipoComida_nuevo_restaurante,
            apps = apps_nuevo_restaurante,
            opciones = opciones_nuevo_restaurante
        )
        db.session.add(restaurante)
        db.session.commit()
        self.restaurantes_creados.append(restaurante)
        
        #Definir endpoint, encabezados y hacer el llamado
        endpoint_restaurantes = "/restaurante/" + str(restaurante.id)
        headers = {'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}
        
        resultado_consulta_restaurante = self.client.get(endpoint_restaurantes,
                                                   headers=headers)
                                                   
        #Obtener los datos de respuesta y dejarlos un objeto json
        datos_respuesta = json.loads(resultado_consulta_restaurante.get_data())
                                                   
        #Verificar que el llamado fue exitoso y que el objeto recibido tiene los datos iguales a los creados
        self.assertEqual(resultado_consulta_restaurante.status_code, 200)
        self.assertEqual(datos_respuesta['nombre'], nombre_nuevo_restaurante)
        self.assertEqual(datos_respuesta['direccion'], direccion_nuevo_restaurante)
        self.assertEqual(datos_respuesta['telefono'], telefono_nuevo_restaurante)
        self.assertEqual(datos_respuesta['redesSociales'], redesSociales_nuevo_restaurante)
        self.assertEqual(datos_respuesta['horario'], horario_nuevo_restaurante)
        self.assertEqual(datos_respuesta['tipoComida'], tipoComida_nuevo_restaurante)
        self.assertEqual(datos_respuesta['apps'], apps_nuevo_restaurante)
        self.assertEqual(float(datos_respuesta['opciones']), float(opciones_nuevo_restaurante))
        self.assertIsNotNone(datos_respuesta['id'])

    def test_listar_restaurantes(self):
        #Generar 10 restaurantes con datos aleatorios
        for i in range(0,10):
            #Crear los datos del restaurante
            nombre_nuevo_restaurante = self.data_factory.sentence()
            direccion_nuevo_restaurante = self.data_factory.sentence()
            telefono_nuevo_restaurante = self.data_factory.sentence()
            redesSociales_nuevo_restaurante = self.data_factory.sentence()
            horario_nuevo_restaurante = self.data_factory.sentence()
            tipoComida_nuevo_restaurante = self.data_factory.sentence()
            apps_nuevo_restaurante = self.data_factory.sentence()
            opciones_nuevo_restaurante = round(random.uniform(1, 3))

            #Crear el restaurante con los datos originales para obtener su id
            restaurante = Resturante(nombre = nombre_nuevo_restaurante,
                direccion = direccion_nuevo_restaurante,
                telefono = telefono_nuevo_restaurante,
                redesSociales = redesSociales_nuevo_restaurante,
                horario = horario_nuevo_restaurante,
                tipoComida = tipoComida_nuevo_restaurante,
                apps = apps_nuevo_restaurante,
                opciones = opciones_nuevo_restaurante
            )
            db.session.add(restaurante)
            db.session.commit()
            self.restaurantes_creados.append(restaurante)
        
        #Definir endpoint, encabezados y hacer el llamado
        endpoint_restaurantes = "/restaurantes/" + str(self.usuario_id)
        headers = {'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}
        
        resultado_consulta_restaurante = self.client.get(endpoint_restaurantes,
                                                        headers=headers)
                                                   
        #Obtener los datos de respuesta y dejarlos un objeto json
        datos_respuesta = json.loads(resultado_consulta_restaurante.get_data())
                                                   
        #Verificar que el llamado fue exitoso
        self.assertEqual(resultado_consulta_restaurante.status_code, 200)
        
        #Verificar los restaurantes creados con sus datos
        for restaurante in datos_respuesta:
            for restaurante_creado in self.restaurantes_creados:
                if restaurante['id'] == str(restaurante_creado.id):

                    self.assertEqual(restaurante['nombre'], restaurante_creado.nombre)
                    self.assertEqual(restaurante['direccion'], restaurante_creado.direccion)
                    self.assertEqual(restaurante['telefono'], restaurante_creado.telefono)
                    self.assertEqual(restaurante['redesSociales'], restaurante_creado.redesSociales)
                    self.assertEqual(restaurante['horario'], restaurante_creado.horario)
                    self.assertEqual(restaurante['tipoComida'], restaurante_creado.tipoComida)
                    self.assertEqual(restaurante['apps'], restaurante_creado.apps)
                    self.assertEqual(float(restaurante['opciones']), float(restaurante_creado.opciones))


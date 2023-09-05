from flask import request
from flask_jwt_extended import jwt_required, create_access_token
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import hashlib

from modelos import \
    db, \
    Resturante, ResturanteSchema, \
    Ingrediente, IngredienteSchema, \
    RecetaIngrediente, RecetaIngredienteSchema, \
    Receta, RecetaSchema, \
    Usuario, UsuarioSchema


ingrediente_schema = IngredienteSchema()
restaurante_schema = ResturanteSchema()
receta_ingrediente_schema = RecetaIngredienteSchema()
receta_schema = RecetaSchema()
usuario_schema = UsuarioSchema()
    
class VistaSignIn(Resource):

    def post(self):
        usuario = Usuario.query.filter(Usuario.usuario == request.json["usuario"]).first()
        if usuario is None:
            contrasena_encriptada = hashlib.md5(request.json["contrasena"].encode('utf-8')).hexdigest()
            nuevo_usuario = Usuario(usuario=request.json["usuario"], contrasena=contrasena_encriptada)
            db.session.add(nuevo_usuario)
            db.session.commit()
            token_de_acceso = create_access_token(identity=nuevo_usuario.id)
            return {"mensaje": "usuario creado exitosamente", "id": nuevo_usuario.id}
        else:
            return "El usuario ya existe", 404

    def put(self, id_usuario):
        usuario = Usuario.query.get_or_404(id_usuario)
        usuario.contrasena = request.json.get("contrasena", usuario.contrasena)
        db.session.commit()
        return usuario_schema.dump(usuario)

    def delete(self, id_usuario):
        usuario = Usuario.query.get_or_404(id_usuario)
        db.session.delete(usuario)
        db.session.commit()
        return '', 204


class VistaLogIn(Resource):

    def post(self):
        contrasena_encriptada = hashlib.md5(request.json["contrasena"].encode('utf-8')).hexdigest()
        usuario = Usuario.query.filter(Usuario.usuario == request.json["usuario"],
                                       Usuario.contrasena == contrasena_encriptada).first()
        db.session.commit()
        print(str(hashlib.md5("admin".encode('utf-8')).hexdigest()))
        if usuario is None:
            return "El usuario no existe", 404
        else:
            token_de_acceso = create_access_token(identity=usuario.id)
            return {"mensaje": "Inicio de sesión exitoso", "token": token_de_acceso, "id": usuario.id}


class VistaIngredientes(Resource):
    @jwt_required()
    def get(self):
        ingredientes = Ingrediente.query.all()
        return [ingrediente_schema.dump(ingrediente) for ingrediente in ingredientes]

    @jwt_required()
    def post(self):
        nuevo_ingrediente = Ingrediente( \
            nombre = request.json["nombre"], \
            unidad = request.json["unidad"], \
            costo = float(request.json["costo"]), \
            calorias = float(request.json["calorias"]), \
            sitio = request.json["sitio"] \
        )
        
        db.session.add(nuevo_ingrediente)
        db.session.commit()
        return ingrediente_schema.dump(nuevo_ingrediente)


class VistaIngrediente(Resource):
    @jwt_required()
    def get(self, id_ingrediente):
        return ingrediente_schema.dump(Ingrediente.query.get_or_404(id_ingrediente))
        
    @jwt_required()
    def put(self, id_ingrediente):
        ingrediente = Ingrediente.query.get_or_404(id_ingrediente)
        ingrediente.nombre = request.json["nombre"]
        ingrediente.unidad = request.json["unidad"]
        ingrediente.costo = float(request.json["costo"])
        ingrediente.calorias = float(request.json["calorias"])
        ingrediente.sitio = request.json["sitio"]
        db.session.commit()
        return ingrediente_schema.dump(ingrediente)

    @jwt_required()
    def delete(self, id_ingrediente):
        ingrediente = Ingrediente.query.get_or_404(id_ingrediente)
        recetasIngrediente = RecetaIngrediente.query.filter_by(ingrediente=id_ingrediente).all()
        if not recetasIngrediente:
            db.session.delete(ingrediente)
            db.session.commit()
            return '', 204
        else:
            return 'El ingrediente se está usando en diferentes recetas', 409

# HU: REC-4 y REC-6
# Creación de vista
class VistaRestaurantes(Resource):
    @jwt_required()
    def get(self, id_usuario):
        restaurantes = Resturante.query.filter_by(usuario=str(id_usuario)).all()
        resultados = [restaurante_schema.dump(restaurante) for restaurante in restaurantes]
        return resultados

    @jwt_required()
    def post(self, id_usuario):
        nuevo_resturante = Resturante( \
            nombre = request.json["nombre"], \
            direccion = request.json["direccion"], \
            telefono = request.json["telefono"], \
            redesSociales = request.json["redesSociales"], \
            horario = request.json["horario"], \
            tipoComida = request.json["tipoComida"], \
            apps = request.json["apps"], \
            opciones = int(request.json["opciones"]), \
            usuario = id_usuario \
        )
        try:
            db.session.add(nuevo_resturante)
            db.session.commit()
        except:
            return "El nombre del restaurante ya existe", 404
            
        return restaurante_schema.dump(nuevo_resturante)

# HU: REC-4 y REC-6
# Creación de vista
class VistaRestaurante(Resource):
    @jwt_required()
    def get(self, id_restaurante):
        restaurante = Resturante.query.get_or_404(id_restaurante)
        resultados = restaurante_schema.dump(Resturante.query.get_or_404(id_restaurante))
     
        return resultados

    @jwt_required()
    def put(self, id_restaurante):
        restaurante = Resturante.query.get_or_404(id_restaurante)
        restaurante.nombre = request.json["nombre"]
        restaurante.direccion = request.json["direccion"]
        restaurante.telefono = request.json["telefono"]
        restaurante.redesSociales = request.json["redesSociales"]
        restaurante.horario = request.json["horario"]
        restaurante.tipoComida = request.json["tipoComida"]
        restaurante.apps = request.json["apps"]
        restaurante.opciones = int(request.json["opciones"])
        
        db.session.add(restaurante)
        db.session.commit()
        return restaurante_schema.dump(restaurante)

    @jwt_required()
    def delete(self, id_restaurante):
        restaurante = Resturante.query.get_or_404(id_restaurante)
        db.session.delete(restaurante)
        db.session.commit()
        return '', 204 
        

class VistaRecetas(Resource):
    @jwt_required()
    def get(self, id_usuario):
        recetas = Receta.query.filter_by(usuario=str(id_usuario)).all()
        resultados = [receta_schema.dump(receta) for receta in recetas]
        ingredientes = Ingrediente.query.all()
        for receta in resultados:
            for receta_ingrediente in receta['ingredientes']:
                self.actualizar_ingredientes_util(receta_ingrediente, ingredientes)

        return resultados

    @jwt_required()
    def post(self, id_usuario):
        nueva_receta = Receta( \
            nombre = request.json["nombre"], \
            preparacion = request.json["preparacion"], \
            ingredientes = [], \
            usuario = id_usuario, \
            duracion = float(request.json["duracion"]), \
            porcion = float(request.json["porcion"]) \
        )
        for receta_ingrediente in request.json["ingredientes"]:
            nueva_receta_ingrediente = RecetaIngrediente( \
                cantidad = receta_ingrediente["cantidad"], \
                ingrediente = int(receta_ingrediente["idIngrediente"])
            )
            nueva_receta.ingredientes.append(nueva_receta_ingrediente)
            
        db.session.add(nueva_receta)
        db.session.commit()
        return ingrediente_schema.dump(nueva_receta)
        
    def actualizar_ingredientes_util(self, receta_ingrediente, ingredientes):
        for ingrediente in ingredientes: 
            if str(ingrediente.id)==receta_ingrediente['ingrediente']:
                receta_ingrediente['ingrediente'] = ingrediente_schema.dump(ingrediente)
                receta_ingrediente['ingrediente']['costo'] = float(receta_ingrediente['ingrediente']['costo'])
        

class VistaReceta(Resource):
    @jwt_required()
    def get(self, id_receta):
        receta = Receta.query.get_or_404(id_receta)
        ingredientes = Ingrediente.query.all()
        resultados = receta_schema.dump(Receta.query.get_or_404(id_receta))
        recetaIngredientes = resultados['ingredientes']
        for recetaIngrediente in recetaIngredientes:
            for ingrediente in ingredientes: 
                if str(ingrediente.id)==recetaIngrediente['ingrediente']:
                    recetaIngrediente['ingrediente'] = ingrediente_schema.dump(ingrediente)
                    recetaIngrediente['ingrediente']['costo'] = float(recetaIngrediente['ingrediente']['costo'])
        
        return resultados

    @jwt_required()
    def put(self, id_receta):
        receta = Receta.query.get_or_404(id_receta)
        receta.nombre = request.json["nombre"]
        receta.preparacion = request.json["preparacion"]
        receta.duracion = float(request.json["duracion"])
        receta.porcion = float(request.json["porcion"])
        
        #Verificar los ingredientes que se borraron
        for receta_ingrediente in receta.ingredientes:
            borrar = self.borrar_ingrediente_util(request.json["ingredientes"], receta_ingrediente)
                
            if borrar==True:
                db.session.delete(receta_ingrediente)
            
        db.session.commit()
        
        for receta_ingrediente_editar in request.json["ingredientes"]:
            if receta_ingrediente_editar['id']=='':
                #Es un nuevo ingrediente de la receta porque no tiene código
                nueva_receta_ingrediente = RecetaIngrediente( \
                    cantidad = receta_ingrediente_editar["cantidad"], \
                    ingrediente = int(receta_ingrediente_editar["idIngrediente"])
                    
                )
                receta.ingredientes.append(nueva_receta_ingrediente)
            else:
                #Se actualiza el ingrediente de la receta
                receta_ingrediente = self.actualizar_ingrediente_util(receta.ingredientes, receta_ingrediente_editar)
                db.session.add(receta_ingrediente)
        
        db.session.add(receta)
        db.session.commit()
        return ingrediente_schema.dump(receta)

    @jwt_required()
    def delete(self, id_receta):
        receta = Receta.query.get_or_404(id_receta)
        db.session.delete(receta)
        db.session.commit()
        return '', 204 
        
    def borrar_ingrediente_util(self, receta_ingredientes, receta_ingrediente):
        borrar = True
        for receta_ingrediente_editar in receta_ingredientes:
            if receta_ingrediente_editar['id']!='':
                if int(receta_ingrediente_editar['id']) == receta_ingrediente.id:
                    borrar = False
        
        return(borrar)

    def actualizar_ingrediente_util(self, receta_ingredientes, receta_ingrediente_editar):
        receta_ingrediente_retornar = None
        for receta_ingrediente in receta_ingredientes:
            if int(receta_ingrediente_editar['id']) == receta_ingrediente.id:
                receta_ingrediente.cantidad = receta_ingrediente_editar['cantidad']
                receta_ingrediente.ingrediente = receta_ingrediente_editar['idIngrediente']
                receta_ingrediente_retornar = receta_ingrediente
                
        return receta_ingrediente_retornar

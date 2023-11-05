from flask import request
from flask_jwt_extended import jwt_required, create_access_token, verify_jwt_in_request, get_jwt
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_
from datetime import datetime
from functools import wraps
from flask import jsonify
from sqlalchemy import func
import hashlib
import json

from modelos import \
    db, Roles, \
    Resturante, ResturanteSchema, \
    Ingrediente, IngredienteSchema, \
    RecetaIngrediente, RecetaIngredienteSchema, \
    Receta, RecetaSchema, \
    Usuario, UsuarioSchema, \
    Menu, MenuSchema, \
    MenuReceta, MenuRecetaSchema \
    


ingrediente_schema = IngredienteSchema()
restaurante_schema = ResturanteSchema()
receta_ingrediente_schema = RecetaIngredienteSchema()
receta_schema = RecetaSchema()
usuario_schema = UsuarioSchema()
menu_schema = MenuSchema()

"""
def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        if claims['rol'] == 'ADMIN':
            return fn(*args, **kwargs)
        else:
            return jsonify({"mensaje": "Acceso denegado"}), 403
    return wrapper
"""
"""
REC-8 Ingreso-al-sistema: Se utilizan parametros de los metodos de flask-jwt-extended para guardar roles.
"""
def role_required(*roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            print("ROL DEL USUARIO: ",claims)
            rol = claims['rol']
            if rol not in roles:
                return {"mensaje": "Acceso denegado"}, 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator
"""
def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            print("ROL DEL USUARIO: ",claims)
            if claims["is_admin"]:
                return fn(*args, **kwargs)
            else:
                return jsonify(msg="Admins only!"), 403

        return decorator

    return wrapper
"""

"""
REC-8 Ingreso-al-sistema: Utilización del token de acceso para guardar información los roles del usuario para poder
ser accedidos luego.
"""
class VistaSignIn(Resource):

    def post(self):
        usuario = Usuario.query.filter(Usuario.usuario == request.json["usuario"]).first()
        if usuario is None:
            contrasena_encriptada = hashlib.md5(request.json["contrasena"].encode('utf-8')).hexdigest()
            nuevo_usuario = Usuario(usuario=request.json["usuario"], contrasena=contrasena_encriptada, rol=Roles.ADMIN)
            db.session.add(nuevo_usuario)
            db.session.commit()
            additional_claims={'rol': nuevo_usuario.rol}
            token_de_acceso = create_access_token(identity=nuevo_usuario.id, additional_claims=additional_claims)
            return {"mensaje": "usuario creado exitosamente", "id": nuevo_usuario.id, "rol":nuevo_usuario.rol, "token":token_de_acceso}
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


"""
REC-8 Ingreso-al-sistema: Utilización del token de acceso para guardar información los roles del usuario para poder
ser accedidos luego.
"""
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
            additional_claims={'rol': usuario.rol}
            print(additional_claims)
            token_de_acceso = create_access_token(identity=usuario.id, additional_claims=additional_claims)
            #token_de_acceso = create_access_token(identity=usuario.id)
            return {"mensaje": "Inicio de sesión exitoso", "token": token_de_acceso, "id": usuario.id,"username":usuario.usuario,"restaurante":usuario.restaurante_id,"idParent":usuario.parent_id}

class VistaRestaurantesChefs(Resource):
    @role_required('ADMIN')
    @jwt_required()
    def get(self, id_restaurante):
        results = (Usuario.query.filter_by(restaurante_id=str(id_restaurante)).all())
        return [usuario_schema.dump(usuario) for usuario in results]        
       
class VistaUsuariosChefs(Resource):

    @role_required('ADMIN')
    @jwt_required()
    #@admin_required()
    def get(self, id_usuario):
        results = (Usuario.query.filter_by(parent_id=str(id_usuario)).all())
        return [usuario_schema.dump(usuario) for usuario in results]
    
    @role_required('ADMIN')
    @jwt_required()
    def post(self, id_usuario):
        nuevo_user = Usuario( \
            usuario = request.json["usuario"], \
            contrasena = hashlib.md5(request.json["contrasena"].encode('utf-8')).hexdigest(), \
            rol = Roles.CHEF, \
            nombre = request.json["nombre"], \
            parent_id = id_usuario, \
            restaurante_id = request.json["restaurante"]  \
        )
        db.session.add(nuevo_user)
        db.session.commit()
        return {"mensaje": "Chef creado exitosamente", "id": nuevo_user.id}

class VistaIngredientes(Resource):
    @role_required('ADMIN')
    @jwt_required()
    def get(self):
        ingredientes = Ingrediente.query.all()
        return [ingrediente_schema.dump(ingrediente) for ingrediente in ingredientes]
    @role_required('ADMIN')
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
    
class VistaIngredientesChef(Resource):
    @jwt_required()
    def get(self, parent_id):
        ingredientes = Ingrediente.query.filter_by(usuario=str(parent_id)).all()
        return [ingrediente_schema.dump(ingrediente) for ingrediente in ingredientes]

    #@role_required('ADMIN')
    @jwt_required()
    def post(self, parent_id):
        nuevo_ingrediente = Ingrediente( \
            nombre = request.json["nombre"], \
            unidad = request.json["unidad"], \
            costo = float(request.json["costo"]), \
            calorias = float(request.json["calorias"]), \
            sitio = request.json["sitio"], \
            usuario = parent_id \
        )
        db.session.add(nuevo_ingrediente)
        db.session.commit()
        return ingrediente_schema.dump(nuevo_ingrediente)

class VistaIngredientesAdmin(Resource):
    #@role_required('ADMIN')
    @jwt_required()
    def get(self, id_usuario):
        ingredientes = Ingrediente.query.filter_by(usuario=str(id_usuario)).all()
        return [ingrediente_schema.dump(ingrediente) for ingrediente in ingredientes]

    #@role_required('ADMIN')
    @jwt_required()
    def post(self, id_usuario):
        nuevo_ingrediente = Ingrediente( \
            nombre = request.json["nombre"], \
            unidad = request.json["unidad"], \
            costo = float(request.json["costo"]), \
            calorias = float(request.json["calorias"]), \
            sitio = request.json["sitio"], \
            usuario = id_usuario \
        )
        db.session.add(nuevo_ingrediente)
        db.session.commit()
        return ingrediente_schema.dump(nuevo_ingrediente)

class VistaIngrediente(Resource):
    @role_required('ADMIN')
    @jwt_required()
    def get(self, id_ingrediente):
        return ingrediente_schema.dump(Ingrediente.query.get_or_404(id_ingrediente))
    @role_required('ADMIN')    
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
        restaurante = Resturante.query.filter(
            Resturante.usuario == str(id_usuario),
            func.lower(Resturante.nombre) == func.lower(request.json["nombre"])
        ).first()
        db.session.commit()
        if restaurante is None:
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
            db.session.add(nuevo_resturante)
            db.session.commit()
            return restaurante_schema.dump(nuevo_resturante)
        else:
            return "El nombre del restaurante ya existe", 404

# HU: REC-4 y REC-6
# Creación de vista
class VistaRestaurante(Resource):
    @jwt_required()
    def get(self, id_restaurante):
        restaurante = Resturante.query.get_or_404(id_restaurante)
        resultados = restaurante_schema.dump(restaurante)
     
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
            ingredientes = [],    
            usuario = id_usuario, \
            duracion = float(request.json["duracion"]), \
            porcion = float(request.json["porcion"]) \
        )
        for receta_ingrediente in request.json["ingredientes"]:
            nueva_receta_ingrediente = RecetaIngrediente( \
                cantidad = float(receta_ingrediente["cantidad"]), \
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
        resultados = receta_schema.dump(receta)
        print("TIPO DE DATO: ",type(resultados))
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
    
"""
REC-8 Ingreso-al-sistema Lógica para obtener el tipo de usuario del back
"""
class VistaTipoUsuario(Resource):
    @jwt_required()
    def get(self):
        current_user = get_jwt()
    # Lógica para obtener el tipo de usuario del back
        user_role = current_user['rol']  
        return {"user_type":user_role}
    

class VistaMenuSemanal(Resource):
    @jwt_required()
    def post(self):
        data = request.get_json()
        fecha_inicio = data.get('fechaInicio')
        fecha_fin = data.get('fechaFin')
        menus = Menu.query.filter(Menu.fechaInicio >= fecha_inicio, Menu.fechaFin <= fecha_fin).all()
        if len(menus) >0:
            return {"existeMenu": True}
        #resultados = [menu_schema.dump(menu) for menu in menus]
        return {"existeMenu": False}


class VistaMenus(Resource):
    @jwt_required()
    def post(self, id_usuario):
        new_menu = Menu( \
            nombre = request.json["nombre"], \
            fechaInicio = datetime.strptime(request.json["fechaInicio"],"%Y-%m-%d"), \
            fechaFin = datetime.strptime(request.json["fechaFin"],"%Y-%m-%d"), \
            autor = request.json["autor"], \
            descripcion = request.json["descripcion"], \
            usuario = id_usuario, \
            recetas = [],    

        )
        for menu_receta in request.json["recetas"]:
            nuevo_menu_receta = MenuReceta( \
            num_personas = float(menu_receta["num_personas"]), \
            receta = int(menu_receta["idReceta"])
        )
            new_menu.recetas.append(nuevo_menu_receta)

        fInicio = datetime.strptime(request.json["fechaInicio"],"%Y-%m-%d")
        fFin = datetime.strptime(request.json["fechaFin"],"%Y-%m-%d")

        #menus = Menu.query.filter(and_(Menu.fechaInicio >= fInicio, Menu.fechaFin <= fFin)).all()
        menus = Menu.query.all()
        print(menus)
        exist = False
        año_fecha_I1, num_semana_fecha_I1, _ = fInicio.isocalendar()
        año_fecha_F1, num_semana_fecha_F1, _ = fFin.isocalendar()
 
        for menu in menus:
            año_fecha_I2, num_semana_fecha_I2, _ = menu.fechaInicio.isocalendar()
            año_fecha_F2, num_semana_fecha_F2, _ = menu.fechaFin.isocalendar()
            print("SEMANAS: ",num_semana_fecha_I1, num_semana_fecha_I2, num_semana_fecha_F1, num_semana_fecha_F2)
            if num_semana_fecha_I1 == num_semana_fecha_I2 or num_semana_fecha_F1 == num_semana_fecha_F2:
                exist = True
                print(exist)
                break
        #print(exist)
        #if exist:
            #return "Ya existe el menú esa semana", 404
        try:
            if exist==False:
                db.session.add(new_menu)
                db.session.commit()
        except:
            return "No se pudo crear el menú", 404
        return receta_schema.dump(new_menu)
    @jwt_required()
    def get(self, id_usuario):
        menus = Menu.query.filter_by(usuario=str(id_usuario)).all()
        #resultados = [menu_schema.dump(menu) for menu in menus]

        #recetas = Receta.query.filter_by(usuario=str(id_usuario)).all()
        #resultados = [receta_schema.dump(receta) for receta in recetas]
        print("MENUS: ",menus)
        resul = [menu_schema.dumps(menu,default=str) for menu in menus]
        #resul = menu_schema.dumps(menus,default=str)
        print("RESULTADOS: ",resul)
        resultados = []

        for r in resul:
            resultados.append(json.loads(r))

        #resultados = json.loads(resul)
        ingredientes = Ingrediente.query.all()
        #for menu in menus: 
        #    if str(menu.id)==menu['receta']:
        #        menu['receta'] = ingrediente_schema.dump(menu)
                #menu['receta']['numPersonas'] = float(menu['receta']['costo'])
        return resultados

def misma_semana(fecha1, fecha2):
    # Obtener el número de semana y el año para ambas fechas
    num_semana_fecha1, año_fecha1, _ = fecha1.isocalendar()
    num_semana_fecha2, año_fecha2, _ = fecha2.isocalendar()

    # Comprobar si ambas fechas tienen el mismo número de semana y año
    return num_semana_fecha1 == num_semana_fecha2 and año_fecha1 == año_fecha2
class VistaMenusChef(Resource):
    @jwt_required()
    def post(self, parent_id):
        new_menu = Menu( \
            nombre = request.json["nombre"], \
            fechaInicio = datetime.strptime(request.json["fechaInicio"],"%Y-%m-%d"), \
            fechaFin = datetime.strptime(request.json["fechaFin"],"%Y-%m-%d"), \
            autor = request.json["autor"], \
            descripcion = request.json["descripcion"], \
            usuario = parent_id, \
            recetas = [],    

        )
        for menu_receta in request.json["recetas"]:
            nuevo_menu_receta = MenuReceta( \
            num_personas = float(menu_receta["num_personas"]), \
            receta = int(menu_receta["idReceta"])
        )
            new_menu.recetas.append(nuevo_menu_receta)

        fInicio = datetime.strptime(request.json["fechaInicio"],"%Y-%m-%d")
        fFin = datetime.strptime(request.json["fechaFin"],"%Y-%m-%d")

        #menus = Menu.query.filter(and_(Menu.fechaInicio >= fInicio, Menu.fechaFin <= fFin)).all()
        menus = Menu.query.all()
        print(menus)
        exist = False
        año_fecha_I1, num_semana_fecha_I1, _ = fInicio.isocalendar()
        año_fecha_F1, num_semana_fecha_F1, _ = fFin.isocalendar()
 
        for menu in menus:
            año_fecha_I2, num_semana_fecha_I2, _ = menu.fechaInicio.isocalendar()
            año_fecha_F2, num_semana_fecha_F2, _ = menu.fechaFin.isocalendar()
            print("SEMANAS: ",num_semana_fecha_I1, num_semana_fecha_I2, num_semana_fecha_F1, num_semana_fecha_F2)
            if num_semana_fecha_I1 == num_semana_fecha_I2 or num_semana_fecha_F1 == num_semana_fecha_F2:
                exist = True
                print(exist)
                break
        #print(exist)
        if exist:
            return "Ya existe el menú esa semana", 404
        try:
            if exist==False:
                db.session.add(new_menu)
                db.session.commit()
        except:
            return "No se pudo crear el menú", 404
        return receta_schema.dump(new_menu)
    
    @jwt_required()
    def get(self, parent_id):
            menus = Menu.query.filter_by(usuario=str(parent_id)).all()
            print("MENUS: ",menus)
            resul = [menu_schema.dumps(menu,default=str) for menu in menus]
            print("RESULTADOS: ",resul)
            resultados = []
            for r in resul:
                resultados.append(json.loads(r))
            ingredientes = Ingrediente.query.all()
            return resultados

    
class VistaMenu(Resource):
    @jwt_required()
    def get(self, id_menu):
        menu = Menu.query.get_or_404(id_menu)
        recetas = Receta.query.all()
        resul = menu_schema.dumps(menu,default=str)
        resultados = json.loads(resul)

        for field_name, field_value in menu.__dict__.items():
            print(field_name, field_value)
            print(isinstance(field_value, int))
            if isinstance(field_value, int):
                setattr(menu, field_name, str(field_value))
                menu.__dict__[field_name] = str(field_value)

        #resultados = menu_schema.dump(menu)
        print("RESULTADOS: ",resultados)
        print(resultados['recetas'])
        menuRecetas = resultados['recetas']
        for menuReceta in menuRecetas:
            for receta in recetas: 
                if str(receta.id)==menuReceta['receta']:
                    menuReceta['receta'] = receta_schema.dump(receta)
                    print("DENTRO DEL FOR: ",menuReceta['receta'])
                    #menuReceta['receta']['recetas'][] = float(menuReceta['receta']['num_personas'])

        return resultados
    
    @jwt_required()
    def delete(self, id_menu):
        menu = Menu.query.get_or_404(id_menu)
        db.session.delete(menu)
        db.session.commit()
        return '', 204 



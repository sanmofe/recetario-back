from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_restful import Api

from modelos import db
from vistas import \
    VistaIngrediente, VistaIngredientes, \
    VistaRestaurante, VistaRestaurantes, \
    VistaReceta, VistaRecetas, \
    VistaSignIn, VistaLogIn, \
    VistaUsuariosChefs, VistaTipoUsuario, \
    VistaRestaurantesChefs, VistaMenus, \
    VistaMenusChef, VistaMenu, VistaMenuSemanal,\
    VistaIngredientesChef, VistaIngredientesAdmin \


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dbapp.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'frase-secreta'
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['SQLALCHEMY_ECHO'] = True

app_context = app.app_context()
app_context.push()

db.init_app(app)
db.create_all()

#Cómo odio los cors ptm
cors = CORS(app)

api = Api(app)
api.add_resource(VistaSignIn, '/signin')
api.add_resource(VistaLogIn, '/login')
api.add_resource(VistaIngredientes, '/ingredientes')
api.add_resource(VistaIngrediente, '/ingrediente/<int:id_ingrediente>')

# HU: REC-9
api.add_resource(VistaIngredientesChef, '/chef/ingredientes/<int:parent_id>')
api.add_resource(VistaIngredientesAdmin,'/admin/ingredientes/<int:id_usuario>')

# HU: REC-4 y REC-6
api.add_resource(VistaRestaurantes, '/restaurantes/<int:id_usuario>')
api.add_resource(VistaRestaurante, '/restaurante/<int:id_restaurante>')

api.add_resource(VistaRecetas, '/recetas/<int:id_usuario>')
api.add_resource(VistaReceta, '/receta/<int:id_receta>')
api.add_resource(VistaUsuariosChefs, '/chefs/<int:id_usuario>')
api.add_resource(VistaRestaurantesChefs, "/restaurante/<int:id_restaurante>/empleados")
api.add_resource(VistaTipoUsuario, '/api/user-type')
api.add_resource(VistaMenus, '/admin/menus/<int:id_usuario>')
api.add_resource(VistaMenusChef, '/chef/menus/<int:parent_id>')
api.add_resource(VistaMenu, '/menus/<int:id_menu>')
api.add_resource(VistaMenuSemanal, '/menus/verificar')


jwt = JWTManager(app)

from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields, Schema
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from sqlalchemy.ext.declarative import declarative_base
import enum

db = SQLAlchemy()
Base = declarative_base()

class Roles(str, enum.Enum):
    ADMIN = "ADMIN"
    CHEF = "CHEF"

# HU: REC-4 y REC-6
# Creación de objeto
class Resturante(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200))
    direccion = db.Column(db.String(200))
    telefono = db.Column(db.String(200))
    redesSociales = db.Column(db.String(500))
    horario = db.Column(db.String(500))
    tipoComida = db.Column(db.String(500))
    apps = db.Column(db.String(500))
    opciones = db.Column(db.Numeric)
    usuario = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    empleado_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    empleados = db.relationship("Usuario", foreign_keys=[empleado_id])

class Ingrediente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(128))
    unidad = db.Column(db.String(128))
    costo = db.Column(db.Numeric)
    calorias = db.Column(db.Numeric)
    sitio = db.Column(db.String(128))
    usuario = db.Column(db.Integer, db.ForeignKey('usuario.id'))

class RecetaIngrediente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cantidad = db.Column(db.Numeric)
    ingrediente = db.Column(db.Integer, db.ForeignKey('ingrediente.id'))
    receta = db.Column(db.Integer, db.ForeignKey('receta.id'))

class Receta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(128))
    duracion = db.Column(db.Numeric)
    porcion = db.Column(db.Numeric)
    preparacion = db.Column(db.String)
    ingredientes = db.relationship('RecetaIngrediente', cascade='all, delete, delete-orphan')
    usuario = db.Column(db.Integer, db.ForeignKey('usuario.id'))

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(50))
    contrasena = db.Column(db.String(50))
    nombre = db.Column(db.String(50))
    parent_id = db.Column(db.Integer, db.ForeignKey("usuario.id"))
    parent = db.relationship("Usuario", remote_side=[id])
    recetas = db.relationship('Receta', cascade='all, delete, delete-orphan')
    ingredientes = db.relationship('Ingrediente', cascade= 'all, delete, delete-orphan')
    rol = db.Column(db.Enum(Roles))
    restaurante_id = db.Column(db.Integer, db.ForeignKey("resturante.id"))

# HU: REC-4 y REC-6
# Creación de esquema
class ResturanteSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Resturante
        include_relationships = True
        include_fk = True
        load_instance = True
        
    id = fields.String()
    nombre = fields.String()
    direccion = fields.String()
    telefono = fields.String()
    redesSociales = fields.String()
    horario = fields.String()
    tipoComida = fields.String()
    apps = fields.String()
    opciones = fields.String()

class IngredienteSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Ingrediente
        load_instance = True

    id = fields.String()
    costo = fields.String()
    calorias = fields.String()



class RecetaIngredienteSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = RecetaIngrediente
        include_relationships = True
        include_fk = True
        load_instance = True
        
    id = fields.String()
    cantidad = fields.String()
    ingrediente = fields.String()

class RecetaSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Receta
        include_relationships = True
        include_fk = True
        load_instance = True
        
    id = fields.String()
    duracion = fields.String()
    porcion = fields.String()
    ingredientes = fields.List(fields.Nested(RecetaIngredienteSchema()))

class UsuarioSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Usuario
        include_relationships = True
        load_instance = True
        
    id = fields.String()


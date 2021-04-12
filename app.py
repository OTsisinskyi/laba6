from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow


DB_URI = "mysql+mysqlconnector://iotuser:iotuser@localhost/iot-test-db"

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    producer = db.Column(db.String(100))
    weight_in_grams = db.Column(db.Integer)
    price = db.Column(db.Float)

    def __init__(self, name, producer, weight_in_grams, price):
        self.name = name
        self.producer = producer
        self.weight_in_grams = weight_in_grams
        self.price = price


class ProductSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'producer', 'weight_in_grams', 'price')


product_schema = ProductSchema()
products_schema = ProductSchema(many=True)


@app.route('/product', methods=['POST'])
def add_product():
    name = request.json['name']
    producer = request.json['producer']
    weight_in_grams = request.json['weight_in_grams']
    price = request.json['price']

    new_product = Product(name, producer, weight_in_grams, price)

    db.session.add(new_product)
    db.session.commit()
    return product_schema.jsonify(new_product)


@app.route('/product', methods=['GET'])
def get_products():
    all_products = Product.query.all()
    result = products_schema.dump(all_products)
    return jsonify(result)


@app.route('/product/<id>', methods=['GET'])
def get_product(id):
    product = Product.query.get(id)
    if product is None:
        abort(404)
    return product_schema.jsonify(product)


@app.route('/product/<id>', methods=['PUT'])
def update_product(id):
    product = Product.query.get(id)
    if product is None:
        abort(404)

    name = request.json['name']
    producer = request.json['producer']
    weight_in_grams = request.json['weight_in_grams']
    price = request.json['price']

    product.name = name
    product.producer = producer
    product.weight_in_grams = weight_in_grams
    product.price = price

    db.session.commit()
    return product_schema.jsonify(product)


@app.route('/product/<id>', methods=['DELETE'])
def delete_product(id):
    product = Product.query.get(id)
    if product is None:
        abort(404)
    db.session.delete(product)
    db.session.commit()
    return product_schema.jsonify(product)


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)

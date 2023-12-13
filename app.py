from flask import Flask, jsonify, request
import json
import psycopg2
import os

app = Flask(__name__)

if 'POSTGRES_PASSWORD_FILE' in os.environ:
   with open(os.environ['POSTGRES_PASSWORD_FILE'], 'r') as f:
       password = f.read().strip()
else:
   password = os.environ['POSTGRES_PASSWORD']


class Product:
    def __init__(self, id, name, price):
        self.id = id
        self.name = name
        self.price = price

@app.route('/api/products', methods=['GET'])
def get_products():
    try:
        conn = psycopg2.connect(host="db", user="postgres", password=password)
        cur = conn.cursor() 
        
        postgreSQL_select_Query = "select * from items"
        cur.execute(postgreSQL_select_Query)
       
        item_records = cur.fetchall()
        items = {}

        for index, item in enumerate(item_records):
            item = {
                "id": item[0],
                "name": item[1],
                "price": item[2]
                }
            items.update({index: item})
        
        return jsonify(items)
    except (Exception, psycopg2.Error) as error:
        if conn:
            cur.close()
            conn.close()
        return f"Failed to fetch data from table:  {error}"

@app.route('/api/products', methods=['POST'])
def add_product():
    data = request.get_json()
    new_product = (data['id'], data['name'], data['price'])
    
    postgres_insert_query = """ INSERT INTO items(id, name, price) 
    VALUES (%s,%s,%s)"""
    try:

        conn = psycopg2.connect(host="db", user="postgres", password=password)
        cur = conn.cursor() 
       
        cur.execute(postgres_insert_query, new_product)
       
        conn.commit()
       
        cur.close()
        conn.close()
        return f"Product added successfully!!"
    except (Exception, psycopg2.Error) as error:
        if conn:
            cur.close()
            conn.close()
        return f"Failed to insert record into items table {error}"


@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = next((p for p in products if p['id'] == product_id))
    if product:
        return jsonify(product)
    return jsonify({"error": "Product not found"}), 404


@app.route('/api/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    data = request.get_json()
    product = next((p for p in products if p['id'] == product_id), None)
    if product:
        product.update(data)
        return jsonify({"message": "Product updated successfully"})
    return jsonify({"error": "Product not found"}), 404

# Delete a product by ID
@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    global products
    products = [p for p in products if p['id'] != product_id]
    return jsonify({"message": "Product deleted successfully"})

@app.route('/widgets')
def get_widgets():
    with psycopg2.connect(host="db", user="postgres", password=password, database="example") as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM widgets")
            row_headers = [x[0] for x in cur.description]
            results = cur.fetchall()
    conn.close()

    json_data = [dict(zip(row_headers, result)) for result in results]
    return json.dumps(json_data)


@app.route('/initdb')
def db_init():
    
    conn = psycopg2.connect(host="db", user="postgres", password=password)
    # conn.set_session(autocommit=True)
    
    cur = conn.cursor() 
    cur.execute("DROP TABLE IF EXISTS items")
    sql = '''CREATE TABLE items(
                id INT,
                name VARCHAR(30),
                price FLOAT

        )'''
    cur.execute(sql)
    conn.commit()
    
    conn.close()

    return "Table created successfully........"


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
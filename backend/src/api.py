import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''

@app.route('/')
def index():
    return jsonify({'message': 'hellow-world'})

db_drop_and_create_all()

## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks', methods=['GET'])
def get_drinks():
    drinks = Drink.query.all()

    drinks_list = []
    for drink in drinks:
        drinks_list.append(drink.short())
    return jsonify({
        'success' : True,
        'drinks' : drinks_list,
    }), 200

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(jwt):
    try:
        drinks = Drink.query.all()
        drinks_list = []
        for drink in drinks:
            drinks_list.append(drink.long())
        return jsonify({
            'success': True,
            'drinks': drinks_list
        }), 200
    except:
        abort(401)

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drinks(jwt):
    data = request.get_json()
    if 'title' and 'recipe' not in data:
        abort(422)
        
    title = data['title']
    recipe = data['recipe']

    recipeJSON = getJSONListFromObject(recipe)

    drink = Drink(title=title, recipe=recipeJSON)
    drink.insert()
        

    return jsonify({'success': True,
                    'drinks':drink.long()})

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drinks(jwt, id):
    drink = Drink.query.get(id)
    if drink is None:
        abort(404)
    
    data = request.get_json()
    if "title" in data:
        drink.title = data['title']

    if "recipe" in data:
        recipe = data['recipe']
        recipeJSON = getJSONListFromObject(recipe)
    
        drink.recipe = recipeJSON
    
    drink.update()
    return jsonify({'success': True,
                    'drinks':drink.long()})

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(jwt, id):
    drink = Drink.query.get(id)
    if drink is None:
        abort(404)
    
    id = drink.id
    
    drink.delete()
    return jsonify({'success': True,
                    'delete': id})


@app.route('/login-results', methods=['GET'])
def login_results():
    return (jsonify({'message': 'successful login'}))

## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False, 
        "error": 422,
        "message": "unprocessable"
    }), 422

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''

@app.errorhandler(404)
def unprocessable(error):
    return jsonify({
        "success": False, 
        "error": 404,
        "message": "resource not found"
    }), 404


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''

@app.errorhandler(AuthError)
def auth_error(auth_error):
    return jsonify({
        "success": False, 
        "error": auth_error.status_code,
        "message": auth_error.error['description']
    }), auth_error.status_code

def getJSONListFromObject(obj):
    if not isinstance(obj, list):
        obj = [obj]
    
    jsonList = json.dumps(obj)

    return jsonList
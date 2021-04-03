import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from database.models import db_drop_and_create_all, setup_db, Drink
from auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
cors = CORS(app, resources={r"/*": {"origins": "*"}})


'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route("/drinks", methods=["GET"])
def get_drinks():
    drinks_short_recipe = Drink.query.order_by(Drink.id).all()
    drinks = [drink.short() for drink in drinks_short_recipe]
    return jsonify({
        "success": True,
        "drinks": drinks
    })


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route("/drinks-detail", methods=["GET"])
@requires_auth("get:drinks-detail")
def get_drinks_details():
    drinks_detailed_recipe = Drink.query.order_by(Drink.id).all()
    drinks = [drink.long() for drink in drinks_detailed_recipe]

    return jsonify({
        "success": True, 
        "drinks": drinks
    })

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@app.route("/drinks", methods=["POST"])
@requires_auth("post:drinks")
def add_drink():
    body = request.get_json()
    try: 
        title = body.get("title")
        recipe = body.get("recipe")
        new_drink = Drink(title=title, recipe=recipe)

        try:
            new_drink.insert()
        except:
            abort(500)

        return jsonify({
            "success": True,
            "drinks": [new_drink.long()]
            })
    except:
        abort(422)

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


@app.route("/drinks/<id>", methods=["PATCH"])
@requires_auth("patch:drinks")
def edit_drink(id):
    body = request.get_json()
    try:
        title = body.get("title", None)
        recipe = body.get("recipe", None)

        drink = Drink.query.filter(Drink.id == id).one_or_none()

        if drink is None:
            abort(404)

        if title:
            drink.title = title

        if recipe:
            drink.recipe = recipe
        try:
            drink.update()
        except:
            abort(500)

        return jsonify({
            "success": True, 
            "drinks": [drink.long()]
            })
    except:
        abort(422)

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


@app.route("/drinks/<id>", methods=["DELETE"])
@requires_auth('delete:drinks')
def delete_drink(id):
    drink = Drink.query.filter_by(id=id).one_or_none()

    if drink is None:
        abort(404)
    try:
        drink.delete()
    except:
        abort(500)
    return jsonify({
        "success": True,
        "delete": id
    })


# Error Handling


@app.errorhandler(422)
def not_found(error=None):
    message = {
            'success': False,
            'error': 422,
            'message': 'unprocessable'
    }
    resp = jsonify(message)
    resp.status_code = 422

    return resp

'''
@TODO implement error handler for 404
'''


@app.errorhandler(404)
def not_found(error=None):
    message = {
            'success': False,
            'error': 404,
            'message': 'resource not found: ' + request.url
    }
    resp = jsonify(message)
    resp.status_code = 404

    return resp


@app.errorhandler(500)
def not_found(error=None):
    message = {
            'success': False,
            'error': 500,
            'message': 'internal server error'
    }
    resp = jsonify(message)
    resp.status_code = 500

    return resp


@app.errorhandler(400)
def not_found(error=None):
    message = {
            'success': False,
            'error': 400,
            'message': 'Bad request'
    }
    resp = jsonify(message)
    resp.status_code = 400

    return resp
'''
@TODO implement error handler for AuthError
'''


@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response


#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

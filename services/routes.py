"""
My Service

Describe what your service does here
"""

import os
import sys
import logging
from flask import Flask, jsonify, request, url_for, make_response, abort
from . import status  # HTTP Status Codes

# For this example we'll use SQLAlchemy, a popular ORM that supports a
# variety of backends including SQLite, MySQL, and PostgreSQL
from flask_sqlalchemy import SQLAlchemy
from services.models import Shopcart, DataValidationError

# Import Flask application
from . import app


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """ Root URL response """

    app.logger.info("Request for Root URL")
    return (
        jsonify(
            name="Shopcarts REST API Service",
            version="1.0",
            # paths=url_for("list_shopcarts", _external=True),
        ),
        status.HTTP_200_OK,
    )

######################################################################
# CREATE A NEW SHOPCART
######################################################################
@app.route("/shopcarts", methods=["POST"])

def create_shopcart():

    """
    Creates a shopcart
    """
    app.logger.info("Request to create a shopcart")
    check_content_type("application/json")
    shopcart = Shopcart()
    shopcart.deserialize(request.get_json())

    shopcart.create()
    message = shopcart.serialize()
    location_url = url_for("create_shopcart", id=shopcart.id, _external=True)
    app.logger.info("Shopcart for customer ID [%s] created.", shopcart.customer_id)

    return make_response(
        jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
    )

######################################################################
# READING A SHOPCART
######################################################################
@app.route("/shopcarts/<customer_id>", methods=["GET"])
def read_shopcart(customer_id):
    """
    Reads a shopcart
    """
    app.logger.info("Request to read a shopcart for customer " + customer_id)
    shopcarts = Shopcart.find_by_customer_id(customer_id).all()
    if not shopcarts:
        message = {"error": "Shopcart for the customer does not exist!"}
        return make_response(
        jsonify(message), status.HTTP_404_NOT_FOUND
    )
    message = [shopcart.serialize() for shopcart in shopcarts]
    location_url = url_for("read_shopcart", id=[shopcart.id for shopcart in shopcarts], customer_id=customer_id, _external=True)
    
    return make_response(
        jsonify(message), status.HTTP_200_OK, {"Location": location_url}
    )

######################################################################

# LIST ALL SHOPCARTS
######################################################################
@app.route("/shopcarts", methods=["GET"])
def list_shopcarts():
    """
    Return all of the shopcarts
    """
    app.logger.info("Request for shopcarts list")
    shopcarts=[]
    shopcarts=Shopcart.all()
    results=[shopcart.serialize() for shopcart in shopcarts]
    app.logger.info("Returning %d shopcarts", len(results))
    return make_response(jsonify(results),status.HTTP_200_OK)
    

######################################################################
# UPDATE A SHOPCART 
######################################################################
@app.route("/shopcarts/<int:shopcart_id>", methods=["PUT"])
def update_shopcarts(shopcart_id):
    """
    Update a Shopcart

    This endpoint will update a Shopcart based the body that is posted
    """
    app.logger.info("Request to update Shopcart with id: %s", id)
    check_content_type("application/json")
    shopcart = Shopcart.find_by_id(shopcart_id)
    if not shopcart:
        raise NotFound("ShopCart with id '{}' was not found.".format(shopcart_id))
    shopcart.deserialize(request.get_json())
    shopcart.id = shopcart_id
    shopcart.update()
    app.logger.info("Pet with ID [%s] updated.", shopcart.id)
    return make_response(jsonify(shopcart.serialize()), status.HTTP_200_OK)


# DELETING A SHOPCART
######################################################################
@app.route("/shopcarts/<customer_id>", methods=["DELETE"])
def delete_shopcart(customer_id):
    """
    Delete a shopcart
    """
    app.logger.info("Request to delete a shopcart for customer " + customer_id)
    shopcarts = Shopcart.find_by_customer_id(customer_id).all()

    message = [shopcart.serialize() for shopcart in shopcarts]
    
    for shopcart in shopcarts:
        shopcart.delete()
    
    location_url = url_for("delete_shopcart", id=[shopcart.id for shopcart in shopcarts], customer_id=customer_id, _external=True)
    
    return make_response(
        jsonify(message), status.HTTP_200_OK, {"Location": location_url}
    )
    



######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def init_db():
    """ Initialies the SQLAlchemy app """
    global app
    Shopcart.init_db(app)

def check_content_type(media_type):
    """Checks that the media type is correct"""
    content_type = request.headers.get("Content-Type")
    if content_type and content_type == media_type:
        return
    app.logger.error("Invalid Content-Type: %s", content_type)
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        "Content-Type must be {}".format(media_type),
    )


    
    

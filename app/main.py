from flask import Blueprint, session, render_template, abort, Response
from flask.globals import current_app, request
from flask.helpers import url_for
from flask_socketio import emit, join_room, leave_room
from werkzeug.utils import redirect
from .models import Basket, Customer, Menu, Settings
import json
from . import db

import logging

main = Blueprint('main', __name__)

@main.before_app_first_request
def newCustomer():
    if 'customer' not in session:
        customer = Customer()
        db.session.add(customer)
        db.session.commit()
        session['customer'] = str(customer.id)
        current_app.logger.info("New user id: {}".format(customer.id))

@main.before_request
def fixCustomer():
    if 'customer' in session:
        session['customer'] = session['customer']
    else:
        customer = Customer()
        db.session.add(customer)
        db.session.commit()
        session['customer'] = str(customer.id)
        current_app.logger.info("New user on fixCustomer trigger: {}".format(customer.id))

@main.route('/')
def mainpage():
    s = Settings.query.filter_by(key='status').first()
    if s.value == 1:
        kstatus = 1
        current_app.logger.info("Status: {}".format(kstatus))
    else:
        kstatus = 0
        current_app.logger.info("Status: {}".format(kstatus))
    current_app.logger.info('Real Status: {}'.format(s.value))
    menu = Menu.query.all()
    return render_template('index.html', menu=menu, status=kstatus)


@main.route('/api/getbalance', methods=['POST'])
def getbalance():
    product_id = int(request.json['product_id'])
    q = Menu.query.filter_by(id=product_id).first()
    return Response(response=json.dumps({'id': product_id, 'q': q.balance}, ensure_ascii=False), status=200, mimetype='application/json')


@main.route('/api/getbasket', methods=['POST'])
def getbasket():
    customer_id = int(session['customer'])

    db_items = Basket.query.filter_by(cust_id=customer_id).all()
    items = {}
    for id, item in enumerate(db_items):
        items[id] = {
            'name': item.item.name,
            'amount': item.amount,  
            'summ': item.item.price * item.amount
                    } 
    return Response(response=json.dumps({'status': 'good'}+items, ensure_ascii=False), status=200, mimetype='application/json')


@main.route('/api/addtobasket', methods=['POST'])
def addtobasket():
    try:
        customer_id = int(session['customer'])
        item_id = int(request.json['item_id'])
        amount = int(request.json['amount'])
    except:
        return Response(response=json.dumps({'status': "bad", 'e_desc': 'validation error'}, ensure_ascii=False), status=200, mimetype='application/json')
    
    item = Menu.query.filter_by(id=item_id).first()
    customer = Customer.query.filter_by(id=customer_id).first()
    
    if item.balance < amount: return Response(response=json.dumps({'status': 'bad', 'e_desc': 'q error'}, ensure_ascii=False), status=200, mimetype='application/json')

    if Basket.query.filter_by(cust_id=customer.id, item=item.id).first():
        b = Basket.query.filter_by(cust_id=customer.id, item=item.id).first()
        b.amount +=amount
        db.session.add(b)
        db.session.commit()
        return Response(response=json.dumps({'status':'good', 'q': amount}, ensure_ascii=False), status=200, mimetype='application/json')
    else:
        b = Basket(cust_id=customer.id, item=item.id, amount=amount)
        db.session.add(b)
        db.session.commit()
        return Response(response=json.dumps({'status':'good', 'q': amount}, ensure_ascii=False), status=200, mimetype='application/json')

        
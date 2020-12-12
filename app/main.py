from re import L
from flask import Blueprint, session, render_template, abort, Response
from flask.globals import current_app, request
from flask.helpers import url_for
from flask_migrate import history
from flask_socketio import emit, join_room, leave_room
from sqlalchemy.orm.query import Query
from werkzeug.utils import redirect
from .models import Basket, Customer, Menu, Order, Settings
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


def gethistory(customer):
    history = { 'orders': [] }
    o = Order.query.filter_by(customer_id=customer).order_by(Order.id.desc()).all()
    current_app.logger.info("log len o: {}".format(len(o)))

    for ord in o:
        current_app.logger.info("iteration {}".format(ord.id))
        ord_id = ord.id
        ord_price = ord.ord_price
        confirm = ord.confirmation_code
        status = ord.status
        items = json.loads(ord.items)
        current_app.logger.info(type(items))
        current_app.logger.info(items['items'])
        # current_app.logger.info(items['items']['burger'])
        itms = [ord_id, confirm, status, ord_price, []]
        for itm in items['items']:
            id = itm
            value = items['items'][str(itm)]
            # current_app.logger.info("log: {}:{}".format(id,value))
            m = Menu.query.filter_by(id=int(id)).first()
            itms[4].append([
                {
            'id': itm,
            'name': m.name,
            "count": int(value),
            "price": int(m.price)
                }])
        history['orders'].append(itms)
    current_app.logger.info(history)
    return history



@main.route('/')
def mainpage():
    s = Settings.query.filter_by(key='status').first()
    c = int(session['customer'])
    if int(s.value) == 1: kstatus = 1
    else: kstatus = 0
    menu = Menu.query.filter(Menu.balance>0).all()
    b = Basket.query.filter_by(cust_id=c).all()
    basketvalue, basketcount = 0, 0
    for position in b:
        basketvalue+=int(position.menu.price)*int(position.amount)
        basketcount+=int(position.amount)
    h = gethistory(c)
    current_app.logger.info("user: {}".format(c))
    return render_template('index.html', menu=menu, status=kstatus, bv=basketvalue, bc = basketcount, history = h)


@main.route('/api/getbalance', methods=['POST'])
def getbalance():
    product_id = int(request.json['product_id'])
    q = Menu.query.filter_by(id=product_id).first()
    return Response(response=json.dumps({'id': product_id, 'q': q.balance}, ensure_ascii=False), status=200, mimetype='application/json')


@main.route('/api/getbasket', methods=['POST'])
def getbasket():
    customer_id = int(session['customer'])

    db_items = Basket.query.filter_by(cust_id=customer_id).all()
    resp = {'items': {}}
    summ = 0
    for position in db_items:
        p = {}
        p['id'] = position.id
        p['name'] = position.menu.name
        p['amount'] = position.amount
        p['value'] = position.amount*position.menu.price

        summ+=p['value']
        resp['items'][p['id']] = p
    return Response(response=json.dumps({'status': 'good', 'response': resp, 'summ': summ}, ensure_ascii=False), status=200, mimetype='application/json')


@main.route('/api/addtobasket', methods=['POST'])
def addtobasket():
    try:
        customer_id = int(session['customer'])
        item_id = int(request.json['item_id'])
        amount = int(request.json['amount'])
    except:
        return Response(response=json.dumps({'status': "bad", 'e_desc': 'validation_error'}, ensure_ascii=False), status=200, mimetype='application/json')
    
    item = Menu.query.filter_by(id=item_id).first()
    customer = Customer.query.filter_by(id=customer_id).first()
    
    if item.balance < amount: return Response(response=json.dumps({'status': 'bad', 'e_desc': 'q_error'}, ensure_ascii=False), status=200, mimetype='application/json')

    if Basket.query.filter_by(cust_id=customer.id, item=item.id).first():
        b = Basket.query.filter_by(cust_id=customer.id, item=item.id).first()
        if (b.amount + amount)>(item.balance):
            return Response(response=json.dumps({'status': 'bad', 'e_desc': 'not_enough'}))
        b.amount +=amount
        db.session.add(b)
        db.session.commit()
        return Response(response=json.dumps({'status':'good', 'q': amount}, ensure_ascii=False), status=200, mimetype='application/json')
    else:
        b = Basket(cust_id=customer.id, item=item.id, amount=amount)
        db.session.add(b)
        db.session.commit()
        return Response(response=json.dumps({'status':'good', 'q': amount}, ensure_ascii=False), status=200, mimetype='application/json')


    

    

# debug routes

@main.route('/debug/clearbasket')
def dbgclearbasket():
    c = int(session['customer'])
    Basket.query.filter_by(cust_id=c).delete()
    db.session.commit()
    return redirect(url_for('main.mainpage'))

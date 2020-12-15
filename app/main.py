from re import L
from flask import Blueprint, session, render_template, abort, Response
from flask.globals import current_app, request
from flask.helpers import make_response, url_for
from flask_socketio import emit, join_room, leave_room
from werkzeug.utils import redirect
from .models import Basket, Customer, Menu, Order, Settings
import json
from .unitpay_lib import *
from .UnitPay import * 
from .secrets import Password
import random
import datetime
from . import db
from . import socketio


import logging

room = 'kitchen'
main = Blueprint('main', __name__)

unitpay = UnitPay('unitpay.money', Password.unitpaysc)



@main.before_app_first_request
def newCustomer():
    current_app.logger.debug(session)
    if 'customer' not in session:
        customer = Customer()
        db.session.add(customer)
        db.session.commit()
        session['customer'] = str(customer.id)
        session.permanent = True
        current_app.logger.info("New user id: {}".format(customer.id))
    current_app.logger.debug(session)

@main.before_request
def fixCustomer():
    if 'customer' in session:
        session['customer'] = session['customer']
        session.permanent = True
    else:
        customer = Customer()
        db.session.add(customer)
        db.session.commit()
        session['customer'] = str(customer.id)
        session.permanent = True
        current_app.logger.info("New user on fixCustomer trigger: {}".format(customer.id))


@main.route('/payments/handler')
def payhandler():
    try:
        if request.args.get('method')=='check':
            return Response(response=unitpay.getSuccessHandlerResponse('Check Success. Ready to pay.'), status=200, mimetype='appilication/json')
        if request.args.get('method')=='pay':
            current_app.logger.debug(request.args)
            order_id = request.args.get('params[account]')
            order_sum = request.args.get('params[orderSum]')      
            order = Order.query.filter_by(id=order_id).first()
            if not order:
                raise Exception('Order not found')
                
            
            if (int(float(order_sum)) != int(order.ord_price) ) or (int(order_id) != order.id):
                current_app.logger.info('{}:{}. {}:{}'.format(int(float(order_sum)), int(order.ord_price), order_id, order.id))
                if request.args.get('params[account]')=='test':
                   current_app.logger.info('test passed')
                else:
                    return json.dumps({'result': {'message': 'Invalid'}})
            
            else:
                order.status = 1
                order.date = datetime.datetime.now()
                db.session.add(order)
                db.session.commit()
                return json.dumps({'result': {'message': 'Pay success'}})
        if request.args.get('method')=='error':
            pass
        if request.args.get('method')=='check':
            pass
    except Exception as e:
        current_app.logger.critical('EXCEPTION')
        return json.dumps( {'error': {'message': str(e)} } )


@main.route('/api/setpolicy', methods=["POST"])
def setpolicy():
    resp = make_response('setted up')
    resp.set_cookie('policy', '1', max_age=60*60*24*365*2)
    return resp

def gethistory(customer):
    history = { 'orders': [] }
    o = Order.query.filter_by(customer_id=customer).order_by(Order.id.desc()).all()
    if not o:
        return o
    current_app.logger.info("log len o: {}".format(len(o)))

    for ord in o:
        current_app.logger.info("iteration {}".format(ord.id))
        ord_id = ord.id
        ord_price = ord.ord_price
        confirm = ord.confirmation_code
        status = ord.status
        items = json.loads(str(ord.items).replace("'", '"'))
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

@main.route('/api/getpayurl', methods=["POST"])
def getpayurl():
    c = int(session['customer'])
    db_items = Basket.query.filter_by(cust_id=c).all()
    items = {'items': {}}
    summ = 0
    desc = "Оплата заказа в столовой РКСИ"
    for position in db_items:
        items['items'][str(position.item)] = str(position.amount)
        summ+=(position.amount*position.menu.price)
    current_app.logger.info(items)
    conf = random.randint(999, 9999)
    o = Order(customer_id=c, confirmation_code=conf, items=str(items), ord_price=summ, status = 0)
    db.session.add(o)
    db.session.commit()
    url = unitpay.form(Password.publickey, int(summ), int(o.id), str(desc), 'RUB')

    return Response(response=json.dumps({'url': str(url)}), status=200, mimetype='application/json')

@main.route('/policy')
def policy():
    return render_template('policy.html')

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

@main.route('/kitchen')
def render_kitchen():
    return render_template('kitchen.html')

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

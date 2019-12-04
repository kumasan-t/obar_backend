from sqlalchemy.exc import OperationalError
from werkzeug.exceptions import InternalServerError

from obar.models import db, Purchase, Product, Customer


def purchase_leaderboard():
    per_user_purchase = dict()
    try:
        purchases = db.session.query(Purchase).all()
    except OperationalError:
        raise InternalServerError('Purchase table does not exists')
    for purchase in purchases:
        if purchase.purchase_customer_mail_address not in per_user_purchase:
            per_user_purchase[purchase.purchase_customer_mail_address] = 1
        else:
            per_user_purchase[purchase.purchase_customer_mail_address] += 1
    return sorted([{'customer': item[0], 'purchases': item[1]} for item in per_user_purchase.items()],
                  key=lambda x: x['purchases'], reverse=True)


def best_selling_product():
    try:
        products = db.session.query(Product).all()
    except OperationalError:
        raise InternalServerError('Product table does not exists')
    result = sorted(
        [{
            'product_code_uuid': product.product_code_uuid,
            'product_name': product.product_name,
            'product_availability': product.product_availability,
            'product_quantity': product.product_quantity,
            'product_price': product.product_price,
            'product_discount': product.product_discount,
            'product_location_id': product.product_location_id,
            'purchases': len(product.purchaseItem)}
            for product in products if len(product.purchaseItem) is not 0]
        , key=lambda x: x['purchases'], reverse=True)
    return result, 200


def produce_expenses():
    result = []
    try:
        customers = db.session.query(Customer).all()
    except OperationalError:
        raise InternalServerError('Customer table does not exists')
    for customer in customers:
        total_expense = 0
        purchases = []
        for purchase in customer.purchase:
            single_expense = 0
            for item in purchase.purchase_item:
                single_expense += item.purchase_item_price
                total_expense += item.purchase_item_price
            purchases.append(
                {
                    'date': purchase.purchase_date,
                    'code': purchase.purchase_code_uuid,
                    'cost': single_expense
                })
        customer_review = {
            'customer': customer.customer_mail_address,
            'total_expenses': total_expense,
            'purchases': purchases}
        result.append(customer_review)
    return result, 200

from obar.models import db, Purchase, Product


def purchase_leaderboard():
    per_user_purchase = dict()
    for purchase in db.session.query(Purchase).all():
        if purchase.purchase_customer_mail_address not in per_user_purchase:
            per_user_purchase[purchase.purchase_customer_mail_address] = 1
        else:
            per_user_purchase[purchase.purchase_customer_mail_address] += 1
    return sorted([{'customer': item[0], 'purchases': item[1]} for item in per_user_purchase.items()],
                  key=lambda x: x['purchases'], reverse=True)


def best_selling_product():
    products = db.session.query(Product).all()
    result = sorted(
        [{'product_name': product.product_name,
          'product_code': product.product_code_uuid,
          'purchases': len(product.purchaseItem)}
         for product in products if len(product.purchaseItem) is not 0]
        , key=lambda x: x['purchases'], reverse=True)
    return result

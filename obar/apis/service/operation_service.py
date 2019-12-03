from obar.models import db, Purchase, Product, Customer


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


def produce_expenses():
    result = []
    customers = db.session.query(Customer).all()
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
    return result

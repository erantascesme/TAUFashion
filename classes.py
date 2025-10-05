# definition of classes for app
class User():
    def __init__(self, email, username, is_admin):
        self.email = email
        self.username = username
        self.is_admin = is_admin


class Product():
    def __init__(self, id: int, product_name: str, amount: int, cost: float, image_url: str, is_campaign: bool):
        self.id = id
        self.product_name = product_name
        self.amount = amount
        self.cost = cost
        self.image_url = image_url
        self.is_campaign = is_campaign

    def insert_to_db(self, cursor, mydb):
        command = '''insert into products (product_name, amount_in_stock, cost,
                        image_url, is_campaign) values 
                        (%s, %s, %s, %s, %s);'''
        cursor.execute(command, (self.product_name, self.amount, self.cost, self.image_url, self.is_campaign))
        mydb.commit()


class Transaction():
    def __init__(self, order_id, user_email, order_datetime):
        self.total_cost = None
        self.order_id = order_id
        self.user_email = user_email
        self.order_datetime = order_datetime

    def insert_to_db(self, cursor, mydb):
        print(self.order_id, self.user_email, self.order_datetime)
        command = '''insert into transactions (order_id, user_email, order_datetime) values 
                        (%s, %s, %s);'''
        cursor.execute(command, (self.order_id, self.user_email, self.order_datetime))
        mydb.commit()

    def insert_products_to_db(self, cursor, mydb, products: dict):
        for product in products.items():
            command = '''insert into transactiondetails (order_id, product_catalog_number, quantity) values 
                                    (%s, %s, %s);'''
            cursor.execute(command, (self.order_id, product[0], product[1]))
            mydb.commit()

    def calc_total_cost(self, cursor):
        command = '''SELECT SUM(transactiondetails.quantity * products.cost) AS total_cost
        FROM transactiondetails INNER JOIN products ON 
        transactiondetails.product_catalog_number = products.catalog_number
        WHERE transactiondetails.order_id = %s;'''

        cursor.execute(command, (self.order_id,))
        total_cost = cursor.fetchone()[0]
        self.total_cost = total_cost


def update_stock_amount(cursor, mydb, catalog_number, new_amount):
    command = 'UPDATE products SET amount_in_stock = %s WHERE catalog_number = %s'
    cursor.execute(command, (new_amount, catalog_number))
    mydb.commit()


def get_all_products(cursor, in_stock=False):
    query = f'''SELECT catalog_number, product_name, amount_in_stock, cost,
                    image_url, is_campaign FROM products {"WHERE amount_in_stock > 0" if in_stock else ''} ORDER BY is_campaign DESC'''
    cursor.execute(query)
    fetch_list = cursor.fetchall()
    products = []
    for product in fetch_list:
        products.append(Product(product[0], product[1], product[2], product[3], product[4], product[5]))

    return products
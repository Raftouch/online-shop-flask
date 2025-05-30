from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from cloudipsp import Api, Checkout


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=False)
    isAvailable = db.Column(db.Boolean, default=True)

    # def __repr__(self):
    #     return self.title


with app.app_context():
    db.create_all()


@app.route('/')
def home():
    items = Item.query.order_by(Item.title).all()
    return render_template('home.html', data=items)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/buy/<int:id>')
def buy(id):
    item = Item.query.get(id)
    if not item:
        return "Item not found", 404

    try:
        api = Api(merchant_id=1396424,
                secret_key='test')
        checkout = Checkout(api=api)
        data = {
            "currency": "USD",
            "amount": str(item.price * 100)
        }
        url = checkout.url(data).get('checkout_url')
        return redirect(url)
    except Exception as e:
        return f"Error: {e}", 500


@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        price = request.form['price']

        item = Item(title=title, description=description, price=price)

        try:
            db.session.add(item)
            db.session.commit()
            return redirect('/')
        except:
            return "An error has occurred"
    else:
        return render_template('create.html')


if __name__ == "__main__":
    app.run(debug=True)
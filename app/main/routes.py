from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from app import db
from app.main import bp
from app.auth.forms import NurseryProfileForm, ProductForm, FarmerProfileForm, OrderForm
from app.models import User, Product, Post, Message, Order
from app.email import send_email
from flask import current_app

@bp.route('/')
@bp.route('/index')
def index():
    return render_template('index.html', title='Home')

@bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if current_user.role == 'farmer':
        # Farmers don't have a dashboard, they shop
        return render_template('dashboard.html', title='Dashboard')
    
    # Logic for Nursery Owner
    profile_form = NurseryProfileForm()
    product_form = ProductForm()
    
    # Handle Profile Update
    if profile_form.validate_on_submit() and 'submit' in request.form and request.form['submit'] == 'Update Profile':
        current_user.nursery_name = profile_form.nursery_name.data
        current_user.location = profile_form.location.data
        current_user.contact_details = profile_form.contact_details.data
        current_user.payment_methods = profile_form.payment_methods.data
        current_user.bio = profile_form.bio.data
        db.session.commit()
        flash('Nursery profile updated successfully!')
        return redirect(url_for('main.dashboard'))
    
    # Handle Product Addition
    if product_form.validate_on_submit() and 'submit' in request.form and request.form['submit'] == 'Add Plant':
        product = Product(
            name=product_form.name.data,
            breed=product_form.breed.data,
            price=product_form.price.data,
            quantity=product_form.quantity.data,
            description=product_form.description.data,
            image_url=product_form.image_url.data,
            seller=current_user
        )
        db.session.add(product)
        db.session.commit()
        flash('New plant added to inventory!')
        return redirect(url_for('main.dashboard'))

    # Pre-populate profile form
    if request.method == 'GET':
        profile_form.nursery_name.data = current_user.nursery_name
        profile_form.location.data = current_user.location
        profile_form.contact_details.data = current_user.contact_details
        profile_form.payment_methods.data = current_user.payment_methods
        profile_form.bio.data = current_user.bio
        
    products = current_user.products.all()
    posts = current_user.posts.all()
    return render_template('dashboard.html', title='Dashboard', 
                           profile_form=profile_form, product_form=product_form, 
                           products=products, posts=posts)

@bp.route('/marketplace')
def marketplace():
    products = Product.query.order_by(Product.created_at.desc()).all()
    return render_template('marketplace.html', title='Marketplace', products=products)

@bp.route('/forum')
def forum():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('forum.html', title='Forum', posts=posts)

@bp.route('/search')
def search():
    query = request.args.get('q')
    if query:
        products = Product.query.filter(Product.name.contains(query) | Product.description.contains(query)).all()
        users = User.query.filter(User.username.contains(query)).all()
    else:
        products = []
        users = []
    return render_template('search_results.html', title='Search Results', products=products, users=users, query=query)

@bp.route('/chat')
@login_required
def chat():
    messages = Message.query.filter(
        (Message.sender_id == current_user.id) | 
        (Message.receiver_id == current_user.id)
    ).order_by(Message.timestamp.desc()).all()
    return render_template('chat.html', title='Chat', messages=messages)

@bp.route('/calculator')
def calculator():
    return render_template('calculator.html', title='Plant Calculator')

@bp.route('/product/<int:product_id>', methods=['GET', 'POST'])
@login_required
def product_details(product_id):
    product = Product.query.get_or_404(product_id)
    form = ProductForm()
    order_form = OrderForm()

    # Handle Product Edit (Nursery)
    if form.validate_on_submit() and 'submit' in request.form and request.form['submit'] == 'Update Product' and current_user == product.seller:
        product.name = form.name.data
        product.breed = form.breed.data
        product.price = form.price.data
        product.quantity = form.quantity.data
        product.plant_age_days = form.plant_age_days.data
        product.available_days = form.available_days.data
        product.description = form.description.data
        product.image_url = form.image_url.data
        db.session.commit()
        flash('Product updated successfully!')
        return redirect(url_for('main.product_details', product_id=product.id))

    # Handle Order Placement (Farmer)
    if order_form.validate_on_submit() and 'submit' in request.form and request.form['submit'] == 'Place Order':
        if product.quantity >= order_form.quantity.data:
            # Create Order
            total_price = product.price * order_form.quantity.data
            order = Order(
                buyer=current_user,
                product=product,
                quantity=order_form.quantity.data,
                total_price=total_price,
                delivery_address=order_form.delivery_address.data,
                status='pending'
            )
            
            # Send Message to Seller
            msg_content = f"New Order: {current_user.username} wants to buy {order_form.quantity.data} x {product.name}. Delivery Address: {order_form.delivery_address.data}"
            message = Message(
                sender_id=current_user.id,
                receiver_id=product.seller.id,
                content=msg_content
            )
            
            db.session.add(order)
            db.session.add(message)
            db.session.commit()
            
            # Send Email Notifications
            try:
                sender = current_app.config['MAIL_USERNAME']
                
                # Email to Seller
                send_email(
                    subject=f'[FarmCONN] New Order for {product.name}',
                    sender=sender,
                    recipients=[product.seller.email],
                    text_body=f"""You have a new order!
                    
Product: {product.name}
Quantity: {order_form.quantity.data}
Buyer: {current_user.username}
Delivery Address: {order_form.delivery_address.data}
Total Price: ₹{total_price}

Login to your dashboard to view more details.""",
                    html_body=f"""<h3>You have a new order!</h3>
<p><strong>Product:</strong> {product.name}</p>
<p><strong>Quantity:</strong> {order_form.quantity.data}</p>
<p><strong>Buyer:</strong> {current_user.username}</p>
<p><strong>Delivery Address:</strong> {order_form.delivery_address.data}</p>
<p><strong>Total Price:</strong> ₹{total_price}</p>
<p><a href="{url_for('main.dashboard', _external=True)}">Login to Dashboard</a></p>"""
                )
                
                # Email to Buyer
                send_email(
                    subject=f'[FarmCONN] Order Confirmation: {product.name}',
                    sender=sender,
                    recipients=[current_user.email],
                    text_body=f"""Your order has been placed successfully!
                    
Product: {product.name}
Quantity: {order_form.quantity.data}
Total Price: ₹{total_price}
Seller: {product.seller.nursery_name}

The seller will contact you shortly.""",
                    html_body=f"""<h3>Order Confirmation</h3>
<p>Your order for <strong>{product.name}</strong> has been placed.</p>
<p><strong>Quantity:</strong> {order_form.quantity.data}</p>
<p><strong>Total Price:</strong> ₹{total_price}</p>
<p><strong>Seller:</strong> {product.seller.nursery_name}</p>
<p>The seller will contact you shortly.</p>"""
                )
            except Exception as e:
                print(f"Error sending email: {e}")
                flash('Order placed, but email notification failed.', 'warning')
            
            flash(f'Order placed successfully! Total: ₹{total_price}')
            return redirect(url_for('main.product_details', product_id=product.id))
        else:
            flash('Error: Not enough stock available.', 'danger')

    # Pre-populate edit form
    if request.method == 'GET' and current_user == product.seller:
        form.name.data = product.name
        form.breed.data = product.breed
        form.price.data = product.price
        form.quantity.data = product.quantity
        form.plant_age_days.data = product.plant_age_days
        form.available_days.data = product.available_days
        form.description.data = product.description
        form.image_url.data = product.image_url

    return render_template('product_details.html', title=product.name, product=product, form=form, order_form=order_form)

@bp.route('/profiles/<username>', methods=['GET', 'POST'])
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    products = user.products.all()
    
    profile_form = None
    product_form = None
    farmer_form = None
    
    if user == current_user:
        if user.role == 'nursery':
            profile_form = NurseryProfileForm()
            product_form = ProductForm()
            
            # Handle Nursery Profile Update
            if profile_form.validate_on_submit() and 'submit' in request.form and request.form['submit'] == 'Update Profile':
                current_user.nursery_name = profile_form.nursery_name.data
                current_user.owner_name = profile_form.owner_name.data
                current_user.location = profile_form.location.data
                current_user.contact_details = profile_form.contact_details.data
                current_user.payment_methods = profile_form.payment_methods.data
                current_user.bio = profile_form.bio.data
                db.session.commit()
                flash('Your profile has been updated.')
                return redirect(url_for('main.profile', username=current_user.username))
            
            # Handle Product Addition
            if product_form.validate_on_submit() and 'submit' in request.form and request.form['submit'] == 'Add Plant':
                product = Product(
                    name=product_form.name.data,
                    breed=product_form.breed.data,
                    price=product_form.price.data,
                    quantity=product_form.quantity.data,
                    plant_age_days=product_form.plant_age_days.data,
                    available_days=product_form.available_days.data,
                    description=product_form.description.data,
                    image_url=product_form.image_url.data,
                    seller=current_user
                )
                db.session.add(product)
                db.session.commit()
                flash('New plant added to inventory!')
                return redirect(url_for('main.profile', username=current_user.username))
                
            # Pre-populate nursery profile form
            if request.method == 'GET':
                profile_form.nursery_name.data = current_user.nursery_name
                profile_form.owner_name.data = current_user.owner_name
                profile_form.location.data = current_user.location
                profile_form.contact_details.data = current_user.contact_details
                profile_form.payment_methods.data = current_user.payment_methods
                profile_form.bio.data = current_user.bio

        elif user.role == 'farmer':
            farmer_form = FarmerProfileForm()
            
            # Handle Farmer Profile Update
            if farmer_form.validate_on_submit():
                current_user.owner_name = farmer_form.name.data
                current_user.location = farmer_form.location.data
                current_user.contact_details = farmer_form.contact_details.data
                db.session.commit()
                flash('Your profile has been updated.')
                return redirect(url_for('main.profile', username=current_user.username))

            # Pre-populate farmer profile form
            if request.method == 'GET':
                farmer_form.name.data = current_user.owner_name
                farmer_form.location.data = current_user.location
                farmer_form.contact_details.data = current_user.contact_details
    return render_template('profile.html', user=user, products=products,profile_form=profile_form,product_form=product_form,farmer_form=farmer_form)

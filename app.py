# Flask web application for e-commerce platform
# Handles routes, authentication, cart management, orders, and customer support

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_cors import CORS
import json
import time
from datetime import datetime
from main import *
import os
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Initialize Flask application
app = Flask(__name__)
app.secret_key = 'votre_cle_secrete_ici'  # Secret key for session management
CORS(app)  # Enable Cross-Origin Resource Sharing

# Cache configuration for static files
# Sets HTTP cache headers to improve performance by caching CSS, JS, and images
@app.after_request
def set_cache_headers(response):
    # Cache static files for 1 hour to reduce server load and improve page load times
    if request.endpoint and request.endpoint.startswith('static'):
        response.cache_control.max_age = 3600
        response.cache_control.public = True
    return response

# Initialize repositories (data storage layers)
users = UserRepository()  # User account management
products = ProductRepository()  # Product catalog
carts = CartRepository()  # Shopping carts
orders = OrderRepository()  # Order history
invoices = InvoiceRepository()  # Invoice generation
payments = PaymentRepository()  # Payment records
threads = ThreadRepository()  # Customer support threads
sessions = SessionManager()  # User session management

# Initialize business logic services
auth = AuthService(users, sessions)  # Authentication and authorization
catalog = CatalogService(products)  # Product catalog browsing
cart_svc = CartService(carts, products)  # Shopping cart operations
billing = BillingService(invoices)  # Invoice generation
delivery_svc = DeliveryService()  # Shipping and delivery management
gateway = PaymentGateway()  # Payment processing (simulated)
order_svc = OrderService(orders, products, carts, payments, invoices, billing, delivery_svc, gateway, users)  # Order lifecycle
cs = CustomerService(threads, users)  # Customer support

# Custom Jinja2 template filters
@app.template_filter('timestamp_to_date')
def timestamp_to_date_filter(value):
    """Convert Unix timestamp (epoch seconds) to readable local date string.
    
    Returns empty string if value is None/0/invalid.
    Used in templates to format order dates and timestamps.
    """
    if not value:
        return ""
    try:
        ts = int(value)
        return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M')
    except (ValueError, OSError, OverflowError, TypeError):
        return ""

# Utility functions for product management
def get_product_category(product_name):
    """Extract category (homme/femme) from product name by parsing keywords.
    
    Returns 'homme', 'femme', or None if no match found.
    Used for filtering products by gender category.
    """
    name_lower = product_name.lower()
    if 'homme' in name_lower:
        return 'homme'
    elif 'femme' in name_lower:
        return 'femme'
    return None

# Direct mapping of product names to their image filenames
# Fast lookup for product images without filesystem scanning
PRODUCT_IMAGE_MAPPING = {
    "Basket Homme Noir": "basket_homme_1.png",
    "Basket Homme Sport": "basket_homme_2.png",
    "Basket Femme Rose": "basket_femme_1.png",
    "Basket Femme Beige": "basket_femme_2.png",
    "Basket Femme Ville": "basket_femme_3.png",
    "Basket Femme Moderne": "basket_femme_4.png",
    "Running Homme": "running_homme_1.png",
    "Running Femme": "running_femme_1.png",
}

# Image cache to avoid repeated filesystem operations
# Stores resolved image paths by product ID and name
_image_cache = {}
_images_dir_cache = None

def _get_images_directory():
    """Cache the directory listing of product images folder.
    
    Scans the images directory once and stores result in memory
    to avoid repeated os.listdir() calls which are expensive.
    """
    global _images_dir_cache
    if _images_dir_cache is None:
        base_dir = os.path.join(os.path.dirname(__file__), 'static', 'images', 'products')
        if os.path.exists(base_dir):
            _images_dir_cache = set(os.listdir(base_dir))
        else:
            _images_dir_cache = set()
    return _images_dir_cache

def get_product_image(product_id, product_name):
    """Return the URL path to product image if it exists (with caching).
    
    Uses a multi-tier lookup strategy:
    1. Check result cache (fastest)
    2. Check direct name mapping (fast)
    3. Scan directory using cached listing (slower but cached)
    4. Try cleaned product name (fallback)
    
    Returns None if no matching image found.
    """
    # Check cache first to avoid repeated lookups
    cache_key = f"{product_id}_{product_name}"
    if cache_key in _image_cache:
        return _image_cache[cache_key]
    
    base_dir = os.path.join(os.path.dirname(__file__), 'static', 'images', 'products')
    os.makedirs(base_dir, exist_ok=True)  # Create directory if it doesn't exist
    
    result = None
    
    # Try direct mapping first (fastest path)
    if product_name in PRODUCT_IMAGE_MAPPING:
        filename = PRODUCT_IMAGE_MAPPING[product_name]
        path = os.path.join(base_dir, filename)
        if os.path.exists(path):
            result = url_for('static', filename=f'images/products/{filename}')
    
    # Fallback: use cached directory listing (avoids repeated os.listdir())
    if not result:
        images_set = _get_images_directory()
        name_lower = product_name.lower()
        
        # Detect product type from name keywords
        product_type = None
        if 'basket' in name_lower:
            product_type = 'basket'
        elif 'running' in name_lower:
            product_type = 'running'
        elif 'sneaker' in name_lower:
            product_type = 'basket'
        
        # Detect gender from name keywords
        gender = None
        if 'homme' in name_lower:
            gender = 'homme'
        elif 'femme' in name_lower:
            gender = 'femme'
        
        # Match files by prefix pattern (e.g., "basket_homme_*.png")
        if product_type and gender:
            prefix = f"{product_type}_{gender}".lower()
            matching_files = [f for f in images_set if f.lower().startswith(prefix)]
            if matching_files:
                matching_file = sorted(matching_files)[0]  # Take first match
                result = url_for('static', filename=f'images/products/{matching_file}')
    
    # Cache the result for future requests
    _image_cache[cache_key] = result
    return result

# ============================================================================
# INITIAL TEST DATA - Product catalog seeding
# ============================================================================

# Men's sneakers products
p1 = Product(
    id=str(uuid.uuid4()), 
    name="Basket Homme Noir", 
    description="Baskets modernes pour homme en noir, confortables et élégantes. Parfaites pour la ville.", 
    price_cents=8999,  # Price in cents (89.99€)
    stock_qty=25
)
p2 = Product(
    id=str(uuid.uuid4()), 
    name="Basket Homme Sport", 
    description="Baskets sportives homme, design moderne et performance. Idéales pour toutes les occasions.", 
    price_cents=9499, 
    stock_qty=30
)

# Women's sneakers products
p3 = Product(
    id=str(uuid.uuid4()), 
    name="Basket Femme Rose", 
    description="Baskets féminines en rose et blanc, tendance et confortables. Style urbain.", 
    price_cents=8499, 
    stock_qty=35
)
p4 = Product(
    id=str(uuid.uuid4()), 
    name="Basket Femme Beige", 
    description="Baskets modernes pour femme en beige et rose, élégantes et polyvalentes.", 
    price_cents=8799, 
    stock_qty=28
)
p5 = Product(
    id=str(uuid.uuid4()), 
    name="Basket Femme Ville", 
    description="Baskets femme parfaites pour la ville, confort et style au rendez-vous.", 
    price_cents=8299, 
    stock_qty=32
)
p6 = Product(
    id=str(uuid.uuid4()), 
    name="Basket Femme Moderne", 
    description="Baskets modernes pour femme, design épuré et confort optimal.", 
    price_cents=8999, 
    stock_qty=27
)

# Running shoes - Men
p7 = Product(
    id=str(uuid.uuid4()), 
    name="Running Homme", 
    description="Chaussures de running pour homme, performance et confort pour vos entraînements.", 
    price_cents=10999, 
    stock_qty=20
)

# Running shoes - Women
p8 = Product(
    id=str(uuid.uuid4()), 
    name="Running Femme", 
    description="Chaussures de running femme bleu et rose, légères et performantes.", 
    price_cents=10499, 
    stock_qty=22
)

# Add all products to the repository
products.add(p1)
products.add(p2)
products.add(p3)
products.add(p4)
products.add(p5)
products.add(p6)
products.add(p7)
products.add(p8)

# Initialize test user (regular customer only)
client = auth.register("client@shop.test", "Secret123!", "Alice", "Martin", "12 Rue des Fleurs")

# ============================================================================
# AUTHENTICATION HELPER FUNCTIONS
# ============================================================================

def require_auth():
    """Check if user is authenticated.
    
    Returns the User object if authenticated, None otherwise.
    Used as a decorator helper for protected routes.
    """
    if 'user_id' not in session:
        return None
    return users.get(session['user_id'])


# ============================================================================
# PUBLIC ROUTES - Product browsing and catalog
# ============================================================================

@app.route('/')
def index():
    """Homepage route - displays all active products.
    
    Enriches each product with image URL and category for template rendering.
    """
    products_list = catalog.list_products()
    # Add image URLs and categories to products for template display
    for p in products_list:
        p.image_url = get_product_image(p.id, p.name)
        p.category = get_product_category(p.name)
    return render_template('index.html', products=products_list, search_term=None, category=None)

@app.route('/category/<category>')
def category_filter(category):
    """Filter products by category (homme/femme).
    
    Validates category parameter and filters products accordingly.
    Returns filtered product list or redirects if invalid category.
    """
    if category not in ['homme', 'femme']:
        flash('Catégorie invalide', 'error')
        return redirect(url_for('index'))
    all_products = catalog.list_products()
    filtered = [p for p in all_products if get_product_category(p.name) == category]
    # Add image URLs and categories to filtered products
    for p in filtered:
        p.image_url = get_product_image(p.id, p.name)
        p.category = get_product_category(p.name)
    return render_template('index.html', products=filtered, category=category, search_term=None)

@app.route('/search')
def search_products():
    """Search products by name or description.
    
    Accepts query parameter 'q' for search term.
    Returns filtered product list matching the search term.
    Displays results on a dedicated search results page.
    """
    search_term = request.args.get('q', '').strip()
    
    if not search_term:
        flash('Veuillez entrer un terme de recherche', 'info')
        return redirect(url_for('index'))
    
    all_products = catalog.list_products()
    search_lower = search_term.lower()
    
    # Filter products matching search term in name or description
    filtered = []
    for p in all_products:
        if search_lower in p.name.lower() or search_lower in p.description.lower():
            filtered.append(p)
    
    # Add image URLs and categories to filtered products
    for p in filtered:
        p.image_url = get_product_image(p.id, p.name)
        p.category = get_product_category(p.name)
    
    return render_template('index.html', products=filtered, search_term=search_term)

@app.route('/product/<product_id>')
def product_detail(product_id):
    """Product detail page route.
    
    Displays detailed information about a specific product including
    image, description, price, and stock availability.
    """
    p = products.get(product_id)
    if not p:
        flash('Produit introuvable', 'error')
        return redirect(url_for('index'))
    image_url = get_product_image(p.id, p.name)
    category = get_product_category(p.name)
    return render_template('product.html', product=p, image_url=image_url, category=category)

# ============================================================================
# AUTHENTICATION ROUTES
# ============================================================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login route.
    
    GET: Display login form
    POST: Process login credentials, create session, redirect to dashboard
    """
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            token = auth.login(email, password)  # Authenticate user
            user = users.get_by_email(email)
            # Store user session data
            session['user_id'] = user.id
            session['user_email'] = user.email
            flash('Connexion réussie !', 'success')
            return redirect(url_for('dashboard'))
        except ValueError as e:
            flash(str(e), 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration route.
    
    GET: Display registration form
    POST: Create new user account, redirect to login
    
    Validates password strength and email format before registration.
    """
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        address = request.form.get('address', '').strip()
        
        # Basic validation
        if not all([email, password, first_name, last_name, address]):
            flash('Tous les champs sont requis.', 'error')
        else:
            # Validate email format
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                flash('Format email invalide.', 'error')
            else:
                try:
                    user = auth.register(email, password, first_name, last_name, address)
                    flash('Inscription réussie ! Vous pouvez maintenant vous connecter.', 'success')
                    return redirect(url_for('login'))
                except ValueError as e:
                    flash(str(e), 'error')
    return render_template('register.html')

@app.route('/logout')
def logout():
    """User logout route.
    
    Destroys session and redirects to homepage.
    """
    if 'user_id' in session:
        auth.logout(session.get('token', ''))
    session.clear()
    flash('Déconnexion réussie !', 'success')
    return redirect(url_for('index'))

# ============================================================================
# PROTECTED USER ROUTES - Require authentication
# ============================================================================

@app.route('/dashboard')
def dashboard():
    """User dashboard route - displays account information and order history.
    
    Shows user profile, order list, and total amount spent across all orders.
    """
    user = require_auth()
    if not user:
        return redirect(url_for('login'))
    
    user_orders = order_svc.view_orders(user.id)
    # Calculate total spent by calling total_cents() method for each order
    total_spent = sum(order.total_cents() for order in user_orders)
    return render_template('dashboard.html', user=user, orders=user_orders, total_spent=total_spent)

@app.route('/cart')
def cart():
    """Shopping cart page route.
    
    Displays current cart contents with product details and total price.
    """
    user = require_auth()
    if not user:
        return redirect(url_for('login'))
    
    cart = cart_svc.view_cart(user.id)
    cart_total = cart_svc.cart_total(user.id)
    return render_template('cart.html', cart=cart, total=cart_total, products=products)

# ============================================================================
# CART API ENDPOINTS - JSON responses for AJAX operations
# ============================================================================

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    """Add product to shopping cart (AJAX endpoint).
    
    Accepts JSON: {product_id, quantity}
    Returns JSON success/error response with updated quantities.
    """
    user = require_auth()
    if not user:
        return jsonify({'error': 'Non authentifié'}), 401
    
    data = request.get_json()
    product_id = data['product_id']
    quantity = int(data.get('quantity', 1))
    
    try:
        cart_svc.add_to_cart(user.id, product_id, quantity)
        # Get updated cart to return current quantities
        cart = cart_svc.view_cart(user.id)
        product_quantity = cart.items.get(product_id).quantity if product_id in cart.items else 0
        total_items = sum(item.quantity for item in cart.items.values())
        return jsonify({
            'success': True,
            'message': 'Produit ajouté au panier',
            'product_quantity': product_quantity,
            'total_items': total_items
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    """Remove product from shopping cart (AJAX endpoint).
    
    Accepts JSON: {product_id, quantity}
    Returns JSON success/error response with updated quantities.
    """
    user = require_auth()
    if not user:
        return jsonify({'error': 'Non authentifié'}), 401
    
    data = request.get_json()
    product_id = data['product_id']
    quantity = int(data.get('quantity', 1))
    
    try:
        cart_svc.remove_from_cart(user.id, product_id, quantity)
        # Get updated cart to return current quantities
        cart = cart_svc.view_cart(user.id)
        product_quantity = cart.items.get(product_id).quantity if product_id in cart.items else 0
        total_items = sum(item.quantity for item in cart.items.values())
        return jsonify({
            'success': True,
            'message': 'Produit retiré du panier',
            'product_quantity': product_quantity,
            'total_items': total_items
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@app.route('/checkout', methods=['POST'])
def checkout():
    """Create order from cart (AJAX endpoint).
    
    Creates an order, reserves stock, but does NOT clear cart
    (cart is cleared only after successful payment).
    Returns order ID and total for payment step.
    """
    try:
        user = require_auth()
        if not user:
            return jsonify({'error': 'Non authentifié', 'success': False}), 401
        
        order = order_svc.checkout(user.id)
        return jsonify({'success': True, 'order_id': order.id, 'total': order.total_cents()})
    except ValueError as e:
        return jsonify({'error': str(e), 'success': False}), 400
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Erreur serveur: {str(e)}', 'success': False}), 500

@app.route('/payment', methods=['POST'])
def payment():
    """Process payment for an order (AJAX endpoint).
    
    Validates card details using Luhn algorithm and expiration date checks.
    Processes payment through PaymentGateway and clears cart on success.
    Accepts JSON: {order_id, card_number, exp_month, exp_year, cvc}
    """
    user = require_auth()
    if not user:
        return jsonify({'error': 'Non authentifié'}), 401
    
    data = request.get_json()
    order_id = data['order_id']
    card_number = data['card_number']
    exp_month = int(data['exp_month'])
    exp_year = int(data['exp_year'])
    cvc = data['cvc']

    # Server-side validation (card format, expiration date, CVC)
    def luhn_ok(num: str) -> bool:
        """Luhn algorithm for credit card number validation.
        
        Validates card number checksum to detect transcription errors.
        Returns True if valid, False otherwise.
        """
        total = 0
        double = False
        for ch in reversed(num):
            if not ch.isdigit():
                return False
            d = ord(ch) - 48
            if double:
                d *= 2
                if d > 9:
                    d -= 9
            total += d
            double = not double
        return total % 10 == 0

    now = datetime.now()
    # Validate card number format and Luhn checksum
    if not (card_number and card_number.isdigit() and 13 <= len(card_number) <= 19 and luhn_ok(card_number)):
        return jsonify({'error': 'Numéro de carte invalide'}), 400
    # Validate expiration month
    if not (1 <= exp_month <= 12):
        return jsonify({'error': "Mois d'expiration invalide"}), 400
    # Validate expiration date (not expired)
    if exp_year < now.year or (exp_year == now.year and exp_month < now.month):
        return jsonify({'error': "Carte expirée"}), 400
    # Validate CVC (3 or 4 digits)
    if not (len(cvc) in (3,4) and cvc.isdigit()):
        return jsonify({'error': 'CVC invalide'}), 400
    
    try:
        payment = order_svc.pay_by_card(order_id, card_number, exp_month, exp_year, cvc)
        return jsonify({'success': True, 'payment_id': payment.id})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


# ============================================================================
# ADDITIONAL API ENDPOINTS
# ============================================================================

@app.route('/api/orders')
def api_orders():
    """Get user's order list (AJAX endpoint for support page).
    
    Returns JSON array of orders with id, total, and creation timestamp.
    Used by support page to let users reference orders when creating tickets.
    """
    user = require_auth()
    if not user:
        return jsonify({'error': 'Non authentifié'}), 401
    user_orders = order_svc.view_orders(user.id)
    return jsonify({'orders': [
        {
            'id': o.id,
            'total_cents': o.total_cents(),
            'created_at': int(o.created_at)
        } for o in user_orders
    ]})


@app.route('/api/support/threads', methods=['POST'])
def api_support_new_thread():
    """Create a new customer support thread (AJAX endpoint).
    
    Creates a support ticket with initial message.
    Accepts JSON: {subject, order_id (optional), message}
    Returns thread ID on success.
    """
    user = require_auth()
    if not user:
        return jsonify({'error': 'Non authentifié'}), 401
    data = request.get_json() or {}
    subject = data.get('subject', '').strip()
    order_id = data.get('order_id') or None
    message = data.get('message', '').strip()
    if not subject or not message:
        return jsonify({'error': 'Sujet et message requis'}), 400
    th = cs.open_thread(user.id, subject, order_id=order_id)
    cs.post_message(th.id, user.id, message)
    return jsonify({'success': True, 'thread_id': th.id})

@app.route('/orders')
def orders():
    user = require_auth()
    if not user:
        return redirect(url_for('login'))
    
    user_orders = order_svc.view_orders(user.id)
    return render_template('orders.html', orders=user_orders)

@app.route('/support')
def support():
    user = require_auth()
    if not user:
        return redirect(url_for('login'))
    
    user_threads = threads.list_by_user(user.id)
    return render_template('support.html', threads=user_threads)


# API endpoints pour AJAX
@app.route('/api/products')
def api_products():
    products_list = catalog.list_products()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'description': p.description,
        'price_cents': p.price_cents,
        'stock_qty': p.stock_qty
    } for p in products_list])

@app.route('/api/cart')
def api_cart():
    user = require_auth()
    if not user:
        return jsonify({'error': 'Non authentifié'}), 401
    
    cart = cart_svc.view_cart(user.id)
    cart_items = []
    for item in cart.items.values():
        product = products.get(item.product_id)
        if product:
            cart_items.append({
                'product_id': item.product_id,
                'name': product.name,
                'price_cents': product.price_cents,
                'quantity': item.quantity,
                'total_cents': product.price_cents * item.quantity
            })
    
    return jsonify({
        'items': cart_items,
        'total_cents': cart_svc.cart_total(user.id)
    })


@app.route('/api/profile/update', methods=['POST'])
def api_profile_update():
    """Update user profile (AJAX endpoint).
    
    Validates and updates user profile information including email and password.
    Accepts JSON: {first_name, last_name, address, email, email_confirm, current_password, new_password, new_password_confirm}
    Returns updated user data on success.
    """
    user = require_auth()
    if not user:
        return jsonify({'error': 'Non authentifié'}), 401
    
    data = request.get_json() or {}
    
    # Validation des champs
    first_name = data.get('first_name', '').strip()
    last_name = data.get('last_name', '').strip()
    address = data.get('address', '').strip()
    new_email = data.get('email', '').strip()
    email_confirm = data.get('email_confirm', '').strip()
    current_password = data.get('current_password', '').strip()
    new_password = data.get('new_password', '').strip()
    new_password_confirm = data.get('new_password_confirm', '').strip()
    
    # Validation du mot de passe actuel
    from main import PasswordHasher
    if not current_password:
        return jsonify({'error': 'Mot de passe actuel requis pour confirmer les modifications'}), 400
    
    if not PasswordHasher.verify(current_password, user.password_hash):
        return jsonify({'error': 'Mot de passe actuel incorrect'}), 400
    
    # Validation prénom (2-50 caractères, lettres, espaces, tirets)
    if not first_name:
        return jsonify({'error': 'Le prénom est requis'}), 400
    if len(first_name) < 2 or len(first_name) > 50:
        return jsonify({'error': 'Le prénom doit contenir entre 2 et 50 caractères'}), 400
    if not all(c.isalpha() or c in (' ', '-', "'") for c in first_name):
        return jsonify({'error': 'Le prénom ne peut contenir que des lettres, espaces, tirets et apostrophes'}), 400
    
    # Validation nom (2-50 caractères, lettres, espaces, tirets)
    if not last_name:
        return jsonify({'error': 'Le nom est requis'}), 400
    if len(last_name) < 2 or len(last_name) > 50:
        return jsonify({'error': 'Le nom doit contenir entre 2 et 50 caractères'}), 400
    if not all(c.isalpha() or c in (' ', '-', "'") for c in last_name):
        return jsonify({'error': 'Le nom ne peut contenir que des lettres, espaces, tirets et apostrophes'}), 400
    
    # Validation adresse (10-200 caractères)
    if not address:
        return jsonify({'error': "L'adresse est requise"}), 400
    if len(address) < 10 or len(address) > 200:
        return jsonify({'error': "L'adresse doit contenir entre 10 et 200 caractères"}), 400
    
    # Validation email si modifié
    if new_email and new_email != user.email:
        # Validation format email
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, new_email):
            return jsonify({'error': 'Format email invalide'}), 400
        
        # Vérifier que les deux emails correspondent
        if new_email != email_confirm:
            return jsonify({'error': 'Les adresses email ne correspondent pas'}), 400
        
        # Vérifier que l'email n'est pas déjà utilisé
        existing_user = users.get_by_email(new_email)
        if existing_user:
            return jsonify({'error': 'Cette adresse email est déjà utilisée'}), 400
    elif new_email and new_email == user.email:
        # Si l'email est identique, on ne le modifie pas
        new_email = None
    
    # Validation nouveau mot de passe si modifié
    if new_password:
        # Vérifier que les deux mots de passe correspondent
        if new_password != new_password_confirm:
            return jsonify({'error': 'Les mots de passe ne correspondent pas'}), 400
        
        # Valider la force du nouveau mot de passe
        try:
            PasswordHasher.validate_password_strength(new_password)
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
    
    try:
        # Mettre à jour le profil
        user.update_profile(
            first_name=first_name,
            last_name=last_name,
            address=address
        )
        
        # Mettre à jour l'email si modifié
        if new_email:
            user.email = new_email
        
        # Mettre à jour le mot de passe si modifié
        if new_password:
            user.password_hash = PasswordHasher.hash(new_password)
        
        # Sauvegarder les modifications
        users.update(user)
        
        # Mettre à jour la session si l'email a changé
        if new_email and new_email != session.get('user_email'):
            session['user_email'] = user.email
        
        return jsonify({
            'success': True,
            'message': 'Profil mis à jour avec succès',
            'user': {
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'address': user.address
            }
        })
    except Exception as e:
        return jsonify({'error': f'Erreur lors de la mise à jour: {str(e)}'}), 500

# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    # Run Flask development server
    # debug=False improves performance in development
    # Set debug=True only if you need Flask debug mode (auto-reload, debugger)
    app.run(debug=False, host='0.0.0.0', port=5000)

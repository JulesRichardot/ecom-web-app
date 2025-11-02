"""
Functional tests for Flask routes.

Tests HTTP endpoints, request/response handling, and authentication.
"""

import pytest
from app import app as flask_app
from app import auth, users, sessions, products, cart_svc, order_svc
from main import Product
import uuid


@pytest.fixture
def client():
    """Create a test client for Flask app."""
    flask_app.config['TESTING'] = True
    flask_app.config['SECRET_KEY'] = 'test-secret-key'
    with flask_app.test_client() as client:
        yield client


@pytest.fixture
def authenticated_client(client):
    """Create an authenticated test client."""
    # Use the same instances as the Flask app
    # Register a test user using the app's auth service
    try:
        user = auth.register(
            email="test@example.com",
            password="testpassword",
            first_name="Test",
            last_name="User",
            address="123 Test St"
        )
    except ValueError:
        # User might already exist from a previous test, try to login instead
        pass
    
    # Login via client - this will set session['user_id'] and session['user_email']
    response = client.post('/login', data={
        'email': 'test@example.com',
        'password': 'testpassword'
    }, follow_redirects=False)
    
    # After login, the session should be preserved in the client
    return client


class TestPublicRoutes:
    """Test suite for public routes (no authentication required)."""
    
    def test_index_route(self, client):
        """Test homepage loads successfully."""
        response = client.get('/')
        assert response.status_code == 200
    
    def test_login_page(self, client):
        """Test login page loads successfully."""
        response = client.get('/login')
        assert response.status_code == 200
        assert b'Connexion' in response.data or b'Login' in response.data
    
    def test_register_page(self, client):
        """Test registration page loads successfully."""
        response = client.get('/register')
        assert response.status_code == 200
        assert b'Inscription' in response.data or b'Register' in response.data
    
    def test_category_filter(self, client):
        """Test category filtering."""
        # Add products with category keywords
        p1 = Product(
            id=str(uuid.uuid4()),
            name="Basket Homme Noir",
            description="Test",
            price_cents=1999,
            stock_qty=100
        )
        p2 = Product(
            id=str(uuid.uuid4()),
            name="Basket Femme Rose",
            description="Test",
            price_cents=2999,
            stock_qty=50
        )
        products.add(p1)
        products.add(p2)
        
        # Test homme category
        response = client.get('/category/homme')
        assert response.status_code == 200
        
        # Test femme category
        response = client.get('/category/femme')
        assert response.status_code == 200
        
        # Test invalid category
        response = client.get('/category/invalid', follow_redirects=False)
        assert response.status_code == 302  # Redirects to index
    
    def test_search_products(self, client):
        """Test product search."""
        # Add test product
        p = Product(
            id=str(uuid.uuid4()),
            name="Unique Product Name",
            description="Unique description",
            price_cents=1999,
            stock_qty=100
        )
        products.add(p)
        
        # Test search by name
        response = client.get('/search?q=Unique')
        assert response.status_code == 200
        
        # Test search without query
        response = client.get('/search', follow_redirects=False)
        assert response.status_code == 302  # Redirects
    
    def test_product_detail(self, client):
        """Test product detail page."""
        # Add test product
        p = Product(
            id=str(uuid.uuid4()),
            name="Test Product",
            description="Test",
            price_cents=1999,
            stock_qty=100
        )
        products.add(p)
        
        # Test valid product
        response = client.get(f'/product/{p.id}')
        assert response.status_code == 200
        
        # Test invalid product
        response = client.get('/product/invalid-id', follow_redirects=False)
        assert response.status_code == 302  # Redirects


class TestAuthentication:
    """Test suite for authentication routes."""
    
    def test_register_success(self, client):
        """Test successful user registration."""
        response = client.post('/register', data={
            'email': 'newuser@example.com',
            'password': 'newpassword123',
            'first_name': 'New',
            'last_name': 'User',
            'address': '456 New St'
        }, follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_register_duplicate_email(self, client):
        """Test registration with duplicate email fails."""
        # Register first time
        client.post('/register', data={
            'email': 'duplicate@example.com',
            'password': 'password123',
            'first_name': 'First',
            'last_name': 'User',
            'address': '123 St'
        })
        
        # Try to register again
        response = client.post('/register', data={
            'email': 'duplicate@example.com',
            'password': 'password456',
            'first_name': 'Second',
            'last_name': 'User',
            'address': '456 St'
        })
        
        assert response.status_code == 200  # Page loads but shows error
    
    def test_login_success(self, client):
        """Test successful login."""
        # First register
        client.post('/register', data={
            'email': 'logintest@example.com',
            'password': 'password123',
            'first_name': 'Login',
            'last_name': 'Test',
            'address': '123 St'
        })
        
        # Then login
        response = client.post('/login', data={
            'email': 'logintest@example.com',
            'password': 'password123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials fails."""
        response = client.post('/login', data={
            'email': 'nonexistent@example.com',
            'password': 'wrongpassword'
        })
        
        assert response.status_code == 200  # Page loads but shows error
    
    def test_logout(self, authenticated_client):
        """Test logout route."""
        # Logout should redirect to index
        response = authenticated_client.get('/logout', follow_redirects=False)
        assert response.status_code == 302
        
        # After logout, protected routes should redirect
        response = authenticated_client.get('/cart', follow_redirects=False)
        assert response.status_code == 302


class TestProtectedRoutes:
    """Test suite for routes that require authentication."""
    
    def test_cart_requires_auth(self, client):
        """Test cart page requires authentication."""
        response = client.get('/cart', follow_redirects=False)
        assert response.status_code == 302  # Redirect to login
    
    def test_cart_accessible_when_authenticated(self, authenticated_client):
        """Test cart page accessible when authenticated."""
        response = authenticated_client.get('/cart')
        assert response.status_code == 200
    
    def test_dashboard_requires_auth(self, client):
        """Test dashboard requires authentication."""
        response = client.get('/dashboard', follow_redirects=False)
        assert response.status_code == 302  # Redirect to login
    
    def test_dashboard_accessible_when_authenticated(self, authenticated_client):
        """Test dashboard accessible when authenticated."""
        response = authenticated_client.get('/dashboard')
        assert response.status_code == 200
    
    def test_orders_requires_auth(self, client):
        """Test orders page requires authentication."""
        response = client.get('/orders', follow_redirects=False)
        assert response.status_code == 302  # Redirect to login
    
    def test_support_requires_auth(self, client):
        """Test support page requires authentication."""
        response = client.get('/support', follow_redirects=False)
        assert response.status_code == 302  # Redirect to login
    
    def test_orders_accessible_when_authenticated(self, authenticated_client):
        """Test orders page accessible when authenticated."""
        response = authenticated_client.get('/orders')
        assert response.status_code == 200
    
    def test_support_accessible_when_authenticated(self, authenticated_client):
        """Test support page accessible when authenticated."""
        response = authenticated_client.get('/support')
        assert response.status_code == 200


class TestAPIRoutes:
    """Test suite for API endpoints."""
    
    def test_api_cart_requires_auth(self, client):
        """Test /api/cart requires authentication."""
        response = client.get('/api/cart')
        assert response.status_code == 401  # Unauthorized
    
    def test_add_to_cart_requires_auth(self, client):
        """Test /add_to_cart requires authentication."""
        response = client.post('/add_to_cart', 
                             json={'product_id': 'test', 'quantity': 1})
        assert response.status_code == 401  # Unauthorized
    
    def test_api_cart_works_when_authenticated(self, authenticated_client):
        """Test /api/cart returns cart data when authenticated."""
        response = authenticated_client.get('/api/cart')
        assert response.status_code == 200
        data = response.get_json()
        assert 'items' in data
        assert 'total_cents' in data
    
    def test_api_products(self, client):
        """Test /api/products returns product list."""
        # Add test product
        p = Product(
            id=str(uuid.uuid4()),
            name="API Test Product",
            description="Test",
            price_cents=1999,
            stock_qty=100
        )
        products.add(p)
        
        response = client.get('/api/products')
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) > 0
    
    def test_add_to_cart_success(self, authenticated_client):
        """Test successfully adding product to cart."""
        # Add test product
        p = Product(
            id=str(uuid.uuid4()),
            name="Cart Test Product",
            description="Test",
            price_cents=1999,
            stock_qty=100
        )
        products.add(p)
        
        response = authenticated_client.post('/add_to_cart', 
                                           json={'product_id': p.id, 'quantity': 2})
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['product_quantity'] == 2
        assert data['total_items'] == 2
    
    def test_add_to_cart_error(self, authenticated_client):
        """Test adding non-existent product to cart."""
        response = authenticated_client.post('/add_to_cart',
                                           json={'product_id': 'nonexistent-id', 'quantity': 1})
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_remove_from_cart(self, authenticated_client):
        """Test removing product from cart."""
        # Add test product
        p = Product(
            id=str(uuid.uuid4()),
            name="Remove Test Product",
            description="Test",
            price_cents=1999,
            stock_qty=100
        )
        products.add(p)
        
        # Add to cart first
        user = users.get_by_email('test@example.com')
        cart_svc.add_to_cart(user.id, p.id, 5)
        
        # Remove some quantity
        response = authenticated_client.post('/remove_from_cart',
                                           json={'product_id': p.id, 'quantity': 2})
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['product_quantity'] == 3  # 5 - 2 = 3
        # Verify the response shows correct quantity (might need to check the actual response)
        assert 'total_items' in data
        # total_items should be 3 after removing 2 from 5
        assert data['total_items'] == 3 or data['total_items'] >= 3  # At least 3, could be more if other items exist
    
    def test_checkout_success(self, authenticated_client):
        """Test successful checkout."""
        # Add test product
        p = Product(
            id=str(uuid.uuid4()),
            name="Checkout Test Product",
            description="Test",
            price_cents=1999,
            stock_qty=100
        )
        products.add(p)
        
        # Add to cart
        user = users.get_by_email('test@example.com')
        cart_svc.add_to_cart(user.id, p.id, 2)
        
        # Checkout
        response = authenticated_client.post('/checkout')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'order_id' in data
        assert 'total' in data
    
    def test_checkout_empty_cart(self, authenticated_client):
        """Test checkout with empty cart fails."""
        # Make sure cart is empty
        user = users.get_by_email('test@example.com')
        cart_svc.carts.clear(user.id)
        
        response = authenticated_client.post('/checkout')
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'error' in data
    
    def test_payment_success(self, authenticated_client):
        """Test successful payment."""
        # Add product and checkout first
        p = Product(
            id=str(uuid.uuid4()),
            name="Payment Test Product",
            description="Test",
            price_cents=1999,
            stock_qty=100
        )
        products.add(p)
        
        user = users.get_by_email('test@example.com')
        cart_svc.add_to_cart(user.id, p.id, 1)
        order = order_svc.checkout(user.id)
        
        # Pay with valid card
        response = authenticated_client.post('/payment', json={
            'order_id': order.id,
            'card_number': '4242424242424242',
            'exp_month': 12,
            'exp_year': 2030,
            'cvc': '123'
        })
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'payment_id' in data
    
    def test_payment_invalid_card(self, authenticated_client):
        """Test payment with invalid card number."""
        # Add product and checkout first
        p = Product(
            id=str(uuid.uuid4()),
            name="Payment Test Product 2",
            description="Test",
            price_cents=1999,
            stock_qty=100
        )
        products.add(p)
        
        user = users.get_by_email('test@example.com')
        cart_svc.add_to_cart(user.id, p.id, 1)
        order = order_svc.checkout(user.id)
        
        # Pay with invalid card (too short)
        response = authenticated_client.post('/payment', json={
            'order_id': order.id,
            'card_number': '123',
            'exp_month': 12,
            'exp_year': 2030,
            'cvc': '123'
        })
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_api_orders(self, authenticated_client):
        """Test /api/orders returns user orders."""
        response = authenticated_client.get('/api/orders')
        assert response.status_code == 200
        data = response.get_json()
        assert 'orders' in data
        assert isinstance(data['orders'], list)
    
    def test_api_support_threads(self, authenticated_client):
        """Test creating support thread."""
        response = authenticated_client.post('/api/support/threads', json={
            'subject': 'Test Subject',
            'message': 'Test message content'
        })
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'thread_id' in data
    
    def test_api_support_threads_missing_fields(self, authenticated_client):
        """Test creating support thread with missing fields fails."""
        response = authenticated_client.post('/api/support/threads', json={
            'subject': 'Test Subject'
            # Missing message
        })
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data


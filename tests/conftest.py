"""
Pytest configuration and shared fixtures for all tests.

This file contains fixtures that can be used across all test files.
"""

import pytest
from main import (
    UserRepository, ProductRepository, CartRepository, OrderRepository,
    InvoiceRepository, PaymentRepository, ThreadRepository, SessionManager,
    AuthService, CatalogService, CartService, OrderService, BillingService,
    DeliveryService, PaymentGateway, CustomerService, Product, User
)
import uuid


@pytest.fixture
def users():
    """Create a fresh UserRepository for each test."""
    return UserRepository()


@pytest.fixture
def products():
    """Create a fresh ProductRepository for each test."""
    repo = ProductRepository()
    # Add some test products
    p1 = Product(
        id=str(uuid.uuid4()),
        name="Test Product 1",
        description="Test description 1",
        price_cents=1999,
        stock_qty=100
    )
    p2 = Product(
        id=str(uuid.uuid4()),
        name="Test Product 2",
        description="Test description 2",
        price_cents=2999,
        stock_qty=50
    )
    repo.add(p1)
    repo.add(p2)
    return repo


@pytest.fixture
def carts():
    """Create a fresh CartRepository for each test."""
    return CartRepository()


@pytest.fixture
def orders():
    """Create a fresh OrderRepository for each test."""
    return OrderRepository()


@pytest.fixture
def invoices():
    """Create a fresh InvoiceRepository for each test."""
    return InvoiceRepository()


@pytest.fixture
def payments():
    """Create a fresh PaymentRepository for each test."""
    return PaymentRepository()


@pytest.fixture
def threads():
    """Create a fresh ThreadRepository for each test."""
    return ThreadRepository()


@pytest.fixture
def sessions():
    """Create a fresh SessionManager for each test."""
    return SessionManager()


@pytest.fixture
def auth_service(users, sessions):
    """Create an AuthService instance for testing."""
    return AuthService(users, sessions)


@pytest.fixture
def catalog_service(products):
    """Create a CatalogService instance for testing."""
    return CatalogService(products)


@pytest.fixture
def cart_service(carts, products):
    """Create a CartService instance for testing."""
    return CartService(carts, products)


@pytest.fixture
def billing_service(invoices):
    """Create a BillingService instance for testing."""
    return BillingService(invoices)


@pytest.fixture
def delivery_service():
    """Create a DeliveryService instance for testing."""
    return DeliveryService()


@pytest.fixture
def payment_gateway():
    """Create a PaymentGateway instance for testing."""
    return PaymentGateway()


@pytest.fixture
def order_service(orders, products, carts, payments, invoices, billing_service, delivery_service, payment_gateway, users):
    """Create an OrderService instance for testing."""
    return OrderService(orders, products, carts, payments, invoices, billing_service, delivery_service, payment_gateway, users)


@pytest.fixture
def customer_service(threads, users):
    """Create a CustomerService instance for testing."""
    return CustomerService(threads, users)


@pytest.fixture
def test_user(auth_service):
    """Create a test user for testing."""
    return auth_service.register(
        email="test@example.com",
        password="testpassword",
        first_name="Test",
        last_name="User",
        address="123 Test Street"
    )


@pytest.fixture
def test_product(products):
    """Get the first test product."""
    product_list = products.list_active()
    return product_list[0] if product_list else None


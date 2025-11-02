"""
Unit tests for OrderService.

Tests order creation, payment processing, and stock management.
"""

import pytest
from main import OrderStatus


class TestOrderService:
    """Test suite for OrderService."""
    
    def test_checkout_empty_cart(self, order_service, test_user):
        """Test checkout with empty cart raises ValueError."""
        with pytest.raises(ValueError, match="Panier vide"):
            order_service.checkout(test_user.id)
    
    def test_checkout_success(self, order_service, test_user, test_product, cart_service):
        """Test successful checkout creates order without reserving stock."""
        # Add product to cart
        cart_service.add_to_cart(test_user.id, test_product.id, 2)
        
        # Store initial stock
        initial_stock = test_product.stock_qty
        
        # Checkout
        order = order_service.checkout(test_user.id)
        
        assert order is not None
        assert order.user_id == test_user.id
        assert order.status == OrderStatus.CREE
        assert len(order.items) == 1
        assert order.items[0].quantity == 2
        
        # Stock should NOT be reserved yet (only after payment)
        product_after_checkout = order_service.products.get(test_product.id)
        assert product_after_checkout.stock_qty == initial_stock
    
    def test_checkout_insufficient_stock(self, order_service, test_user, test_product, cart_service):
        """Test checkout with insufficient stock raises ValueError."""
        # Add product to cart with valid quantity
        cart_service.add_to_cart(test_user.id, test_product.id, 50)
        
        # Simulate stock reduction (e.g., other orders between adding to cart and checkout)
        # Reduce stock below the quantity in cart by modifying the product in the repository
        product_in_repo = order_service.products.get(test_product.id)
        product_in_repo.stock_qty = 30  # Cart has 50, but only 30 available now
        
        # Checkout should fail because stock is insufficient
        with pytest.raises(ValueError, match="Stock insuffisant"):
            order_service.checkout(test_user.id)
    
    def test_pay_by_card_success(self, order_service, test_user, test_product, cart_service):
        """Test successful payment reserves stock and clears cart."""
        # Add product and checkout
        cart_service.add_to_cart(test_user.id, test_product.id, 2)
        order = order_service.checkout(test_user.id)
        
        initial_stock = test_product.stock_qty
        
        # Pay with valid card
        payment = order_service.pay_by_card(
            order.id, "4242424242424242", 12, 2030, "123"
        )
        
        assert payment.succeeded is True
        assert payment.provider_ref is not None
        
        # Check order status
        updated_order = order_service.orders.get(order.id)
        assert updated_order.status == OrderStatus.PAYEE
        assert updated_order.payment_id == payment.id
        
        # Stock should be reserved now
        product_after_payment = order_service.products.get(test_product.id)
        assert product_after_payment.stock_qty == initial_stock - 2
        
        # Cart should be cleared
        cart = cart_service.view_cart(test_user.id)
        assert len(cart.items) == 0
    
    def test_pay_by_card_failure(self, order_service, test_user, test_product, cart_service):
        """Test failed payment does not reserve stock."""
        # Add product and checkout
        cart_service.add_to_cart(test_user.id, test_product.id, 2)
        order = order_service.checkout(test_user.id)
        
        initial_stock = test_product.stock_qty
        
        # Pay with invalid card (ends with 0000)
        with pytest.raises(ValueError, match="Paiement refusé"):
            order_service.pay_by_card(order.id, "4242424242420000", 12, 2030, "123")
        
        # Stock should NOT be reserved
        product_after_failed_payment = order_service.products.get(test_product.id)
        assert product_after_failed_payment.stock_qty == initial_stock
    
    def test_request_cancellation_success(self, order_service, test_user, test_product, cart_service, payment_gateway):
        """Test order cancellation releases stock."""
        # Create and pay for order
        cart_service.add_to_cart(test_user.id, test_product.id, 2)
        order = order_service.checkout(test_user.id)
        order_service.pay_by_card(order.id, "4242424242424242", 12, 2030, "123")
        
        initial_stock = test_product.stock_qty
        
        # Cancel order
        cancelled_order = order_service.request_cancellation(test_user.id, order.id)
        
        assert cancelled_order.status == OrderStatus.ANNULEE
        assert cancelled_order.cancelled_at is not None
        
        # Stock should be released
        product_after_cancel = order_service.products.get(test_product.id)
        assert product_after_cancel.stock_qty == initial_stock + 2


"""
Unit tests for CartService.

Tests cart operations: add, remove, view, and total calculation.
"""

import pytest
from main import CartService


class TestCartService:
    """Test suite for CartService."""
    
    def test_add_to_cart_success(self, cart_service, test_user, test_product):
        """Test successfully adding product to cart."""
        cart_service.add_to_cart(test_user.id, test_product.id, 2)
        
        cart = cart_service.view_cart(test_user.id)
        assert test_product.id in cart.items
        assert cart.items[test_product.id].quantity == 2
    
    def test_add_to_cart_multiple_products(self, cart_service, test_user, products):
        """Test adding multiple different products to cart."""
        product_list = products.list_active()
        product1 = product_list[0]
        product2 = product_list[1]
        
        cart_service.add_to_cart(test_user.id, product1.id, 2)
        cart_service.add_to_cart(test_user.id, product2.id, 3)
        
        cart = cart_service.view_cart(test_user.id)
        assert len(cart.items) == 2
        assert cart.items[product1.id].quantity == 2
        assert cart.items[product2.id].quantity == 3
    
    def test_add_to_cart_increase_quantity(self, cart_service, test_user, test_product):
        """Test that adding same product again increases quantity."""
        cart_service.add_to_cart(test_user.id, test_product.id, 2)
        cart_service.add_to_cart(test_user.id, test_product.id, 3)
        
        cart = cart_service.view_cart(test_user.id)
        assert cart.items[test_product.id].quantity == 5
    
    def test_add_to_cart_insufficient_stock(self, cart_service, test_user, test_product):
        """Test adding product with insufficient stock raises ValueError."""
        # Try to add more than available stock
        with pytest.raises(ValueError, match="Stock insuffisant"):
            cart_service.add_to_cart(test_user.id, test_product.id, 999)
    
    def test_add_to_cart_nonexistent_product(self, cart_service, test_user):
        """Test adding non-existent product raises ValueError."""
        fake_product_id = "nonexistent-id"
        with pytest.raises(ValueError, match="Produit introuvable"):
            cart_service.add_to_cart(test_user.id, fake_product_id, 1)
    
    def test_remove_from_cart_success(self, cart_service, test_user, test_product):
        """Test successfully removing product from cart."""
        cart_service.add_to_cart(test_user.id, test_product.id, 5)
        cart_service.remove_from_cart(test_user.id, test_product.id, 2)
        
        cart = cart_service.view_cart(test_user.id)
        assert cart.items[test_product.id].quantity == 3
    
    def test_remove_from_cart_completely(self, cart_service, test_user, test_product):
        """Test removing all quantity removes product from cart."""
        cart_service.add_to_cart(test_user.id, test_product.id, 2)
        cart_service.remove_from_cart(test_user.id, test_product.id, 999)  # Remove all
        
        cart = cart_service.view_cart(test_user.id)
        assert test_product.id not in cart.items
    
    def test_cart_total_calculation(self, cart_service, test_user, products):
        """Test cart total calculation is correct."""
        product_list = products.list_active()
        product1 = product_list[0]  # price: 1999 cents
        product2 = product_list[1]  # price: 2999 cents
        
        cart_service.add_to_cart(test_user.id, product1.id, 2)  # 2 * 1999 = 3998
        cart_service.add_to_cart(test_user.id, product2.id, 1)  # 1 * 2999 = 2999
        
        total = cart_service.cart_total(test_user.id)
        assert total == 6997  # 3998 + 2999
    
    def test_view_empty_cart(self, cart_service, test_user):
        """Test viewing empty cart returns cart with no items."""
        cart = cart_service.view_cart(test_user.id)
        assert len(cart.items) == 0


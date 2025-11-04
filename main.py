# E-commerce application core business logic
# Contains data models, repositories, and service classes
# This file implements the domain logic independent of Flask/web framework

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional
import uuid
import hashlib
import time


# ============================================================================
# DATA MODELS - Domain entities
# ============================================================================

class OrderStatus(Enum):
    """Order lifecycle status enumeration.
    
    Represents all possible states an order can be in:
    - CREE: Order created, pending validation
    - VALIDEE: Order validated
    - PAYEE: Payment completed
    - EXPEDIEE: Order shipped
    - LIVREE: Order delivered
    - ANNULEE: Order cancelled
    - REMBOURSEE: Order refunded
    """
    CREE = auto()
    VALIDEE = auto()
    PAYEE = auto()
    EXPEDIEE = auto()
    LIVREE = auto()
    ANNULEE = auto()
    REMBOURSEE = auto()


@dataclass
class User:
    """User account model.
    
    Represents a customer user in the system.
    Contains authentication and profile information.
    """
    id: str  # Unique user identifier
    email: str  # User email (used for login)
    password_hash: str  # Hashed password (SHA256 in this implementation)
    first_name: str
    last_name: str
    address: str  # Delivery address

    def update_profile(self, **fields):
        """Update user profile fields (allows partial updates).
        
        Allows modification of first_name, last_name, address, and email.
        Prevents modification of id and password_hash (use separate method for password).
        """
        for k, v in fields.items():
            if hasattr(self, k) and k not in {"id", "password_hash"}:
                setattr(self, k, v)


@dataclass
class Product:
    """Product catalog item model.
    
    Represents a sellable product with pricing and inventory information.
    """
    id: str  # Unique product identifier
    name: str  # Product name
    description: str  # Product description
    price_cents: int  # Price in cents (to avoid floating point issues)
    stock_qty: int  # Available inventory quantity
    active: bool = True  # Whether product is active/visible in catalog


@dataclass
class CartItem:
    """Shopping cart item model.
    
    Represents a product added to a user's shopping cart with quantity.
    """
    product_id: str  # Reference to Product
    quantity: int  # Quantity of this product in cart





@dataclass
class Cart:
    """Shopping cart model for a user.
    
    Manages a collection of cart items and provides methods to add/remove items
    and calculate totals. Each user has one cart.
    """
    user_id: str  # Owner of this cart
    items: Dict[str, CartItem] = field(default_factory=dict)  # key: product_id

    def add(self, product: Product, qty: int = 1):
        """Add product to cart or increase quantity if already present.
        
        Validates product availability and stock before adding.
        Raises ValueError if validation fails.
        """
        if qty <= 0:
            raise ValueError("Quantité invalide.")
        if not product.active:
            raise ValueError("Produit inactif.")
        if product.stock_qty < qty:
            raise ValueError("Stock insuffisant.")
        # Add to existing item or create new one
        if product.id in self.items:
            self.items[product.id].quantity += qty
        else:
            self.items[product.id] = CartItem(product_id=product.id, quantity=qty)

    def remove(self, product_id: str, qty: int = 1):
        """Remove product from cart or decrease quantity.
        
        If qty <= 0, removes item completely. Otherwise decreases quantity.
        """
        if product_id not in self.items:
            return
        if qty <= 0:
            del self.items[product_id]
            return
        self.items[product_id].quantity -= qty
        if self.items[product_id].quantity <= 0:
            del self.items[product_id]

    def clear(self):
        """Remove all items from cart."""
        self.items.clear()

    def total_cents(self, product_repo: "ProductRepository") -> int:
        """Calculate total cart value in cents.
        
        Sums up (price * quantity) for all items, skipping inactive products.
        """
        total = 0
        for it in self.items.values():
            p = product_repo.get(it.product_id)
            if p is None or not p.active:
                continue
            total += p.price_cents * it.quantity
        return total


@dataclass
class InvoiceLine:
    product_id: str
    name: str
    unit_price_cents: int
    quantity: int
    line_total_cents: int


@dataclass
class Invoice:
    id: str
    order_id: str
    user_id: str
    lines: List[InvoiceLine]
    total_cents: int
    issued_at: float  # epoch timestamp


@dataclass
class Payment:
    id: str
    order_id: str
    user_id: str
    amount_cents: int
    provider: str  # ex: "CB"
    provider_ref: str
    succeeded: bool
    created_at: float


@dataclass
class Delivery:
    id: str
    order_id: str
    carrier: str
    tracking_number: Optional[str]
    address: str
    status: str  # ex: "PREPAREE", "EN_COURS", "LIVREE"


@dataclass
class MessageThread:
    id: str
    user_id: str
    order_id: Optional[str]
    subject: str
    messages: List["Message"] = field(default_factory=list)
    closed: bool = False


@dataclass
class Message:
    id: str
    thread_id: str
    author_user_id: Optional[str]  # None = agent support
    body: str
    created_at: float


@dataclass
class OrderItem:
    product_id: str
    name: str
    unit_price_cents: int
    quantity: int


@dataclass
class Order:
    id: str
    user_id: str
    items: List[OrderItem]
    status: OrderStatus
    created_at: float
    validated_at: Optional[float] = None
    paid_at: Optional[float] = None
    shipped_at: Optional[float] = None
    delivered_at: Optional[float] = None
    cancelled_at: Optional[float] = None
    refunded_at: Optional[float] = None
    delivery: Optional[Delivery] = None
    invoice_id: Optional[str] = None
    payment_id: Optional[str] = None

    def total_cents(self) -> int:
        return sum(i.unit_price_cents * i.quantity for i in self.items)


# =========================
# ====== REPOSITORIES =====
# =========================

class UserRepository:
    def __init__(self):
        self._by_id: Dict[str, User] = {}
        self._by_email: Dict[str, User] = {}

    def add(self, user: User):
        self._by_id[user.id] = user
        self._by_email[user.email.lower()] = user

    def get(self, user_id: str) -> Optional[User]:
        return self._by_id.get(user_id)

    def get_by_email(self, email: str) -> Optional[User]:
        return self._by_email.get(email.lower())
    
    def update(self, user: User):
        """Update user in repository. Handles email changes."""
        old_user = self._by_id.get(user.id)
        if old_user and old_user.email.lower() != user.email.lower():
            # Remove old email mapping if email changed
            self._by_email.pop(old_user.email.lower(), None)
        self._by_id[user.id] = user
        self._by_email[user.email.lower()] = user


class ProductRepository:
    def __init__(self):
        self._by_id: Dict[str, Product] = {}

    def add(self, product: Product):
        self._by_id[product.id] = product

    def get(self, product_id: str) -> Optional[Product]:
        return self._by_id.get(product_id)

    def list_active(self) -> List[Product]:
        return [p for p in self._by_id.values() if p.active]

    def reserve_stock(self, product_id: str, qty: int):
        p = self.get(product_id)
        if not p or p.stock_qty < qty:
            raise ValueError("Stock insuffisant.")
        p.stock_qty -= qty

    def release_stock(self, product_id: str, qty: int):
        p = self.get(product_id)
        if p:
            p.stock_qty += qty


class CartRepository:
    def __init__(self):
        self._by_user: Dict[str, Cart] = {}

    def get_or_create(self, user_id: str) -> Cart:
        if user_id not in self._by_user:
            self._by_user[user_id] = Cart(user_id=user_id)
        return self._by_user[user_id]

    def clear(self, user_id: str):
        self.get_or_create(user_id).clear()


class OrderRepository:
    def __init__(self):
        self._by_id: Dict[str, Order] = {}
        self._by_user: Dict[str, List[str]] = {}

    def add(self, order: Order):
        self._by_id[order.id] = order
        self._by_user.setdefault(order.user_id, []).append(order.id)

    def get(self, order_id: str) -> Optional[Order]:
        return self._by_id.get(order_id)

    def list_by_user(self, user_id: str) -> List[Order]:
        return [self._by_id[oid] for oid in self._by_user.get(user_id, [])]

    def update(self, order: Order):
        self._by_id[order.id] = order


class InvoiceRepository:
    def __init__(self):
        self._by_id: Dict[str, Invoice] = {}

    def add(self, invoice: Invoice):
        self._by_id[invoice.id] = invoice

    def get(self, invoice_id: str) -> Optional[Invoice]:
        return self._by_id.get(invoice_id)


class PaymentRepository:
    def __init__(self):
        self._by_id: Dict[str, Payment] = {}

    def add(self, payment: Payment):
        self._by_id[payment.id] = payment

    def get(self, payment_id: str) -> Optional[Payment]:
        return self._by_id.get(payment_id)


class ThreadRepository:
    def __init__(self):
        self._by_id: Dict[str, MessageThread] = {}

    def add(self, thread: MessageThread):
        self._by_id[thread.id] = thread

    def get(self, thread_id: str) -> Optional[MessageThread]:
        return self._by_id.get(thread_id)

    def list_by_user(self, user_id: str) -> List[MessageThread]:
        return [t for t in self._by_id.values() if t.user_id == user_id]


# =========================
# ====== SERVICES =========
# =========================

class PasswordHasher:
    """Secure password hashing using bcrypt.
    
    Supports both bcrypt (new) and SHA256 (legacy) for backward compatibility.
    Automatically migrates SHA256 hashes to bcrypt on successful login.
    """
    
    @staticmethod
    def hash(password: str) -> str:
        """Hash password using bcrypt with salt.
        
        Returns a bcrypt hash string that can be verified later.
        """
        import bcrypt
        # Generate salt and hash password (bcrypt handles salting automatically)
        salt = bcrypt.gensalt(rounds=12)  # 12 rounds = good balance between security and performance
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify(password: str, stored_hash: str) -> bool:
        """Verify password against stored hash.
        
        Supports both bcrypt (new) and SHA256 (legacy) for backward compatibility.
        Returns True if password matches, False otherwise.
        """
        import bcrypt
        import hashlib
        
        # Check if it's a legacy SHA256 hash
        if stored_hash.startswith('sha256::'):
            # Legacy SHA256 verification
            expected_hash = f"sha256::{hashlib.sha256(password.encode()).hexdigest()}"
            return expected_hash == stored_hash
        
        # Modern bcrypt verification
        try:
            return bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
        except (ValueError, TypeError):
            # Invalid hash format
            return False
    
    @staticmethod
    def needs_rehash(stored_hash: str) -> bool:
        """Check if password hash needs to be rehashed (legacy SHA256).
        
        Returns True if hash is legacy SHA256 and should be migrated to bcrypt.
        """
        return stored_hash.startswith('sha256::')
    
    @staticmethod
    def validate_password_strength(password: str):
        """Validate password strength requirements.
        
        Raises ValueError if password doesn't meet security requirements:
        - Minimum 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - At least one special character
        """
        if len(password) < 8:
            raise ValueError("Le mot de passe doit contenir au moins 8 caractères.")
        
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
        
        errors = []
        if not has_upper:
            errors.append("une majuscule")
        if not has_lower:
            errors.append("une minuscule")
        if not has_digit:
            errors.append("un chiffre")
        if not has_special:
            errors.append("un caractère spécial (!@#$%^&*...)")
        
        if errors:
            raise ValueError(f"Le mot de passe doit contenir {', '.join(errors)}.")


class SessionManager:
    """Gestion simple de sessions en mémoire."""
    def __init__(self):
        self._sessions: Dict[str, str] = {}  # token -> user_id

    def create_session(self, user_id: str) -> str:
        token = str(uuid.uuid4())
        self._sessions[token] = user_id
        return token

    def destroy_session(self, token: str):
        self._sessions.pop(token, None)

    def get_user_id(self, token: str) -> Optional[str]:
        return self._sessions.get(token)


class AuthService:
    def __init__(self, users: UserRepository, sessions: SessionManager):
        self.users = users
        self.sessions = sessions

    def register(self, email: str, password: str, first_name: str, last_name: str, address: str) -> User:
        """Register a new user with password strength validation."""
        if self.users.get_by_email(email):
            raise ValueError("Email déjà utilisé.")
        
        # Validate password strength
        PasswordHasher.validate_password_strength(password)
        
        user = User(
            id=str(uuid.uuid4()),
            email=email,
            password_hash=PasswordHasher.hash(password),
            first_name=first_name,
            last_name=last_name,
            address=address
        )
        self.users.add(user)
        return user

    def login(self, email: str, password: str) -> str:
        """Authenticate user and create session.
        
        Automatically migrates legacy SHA256 password hashes to bcrypt on successful login.
        """
        user = self.users.get_by_email(email)
        if not user or not PasswordHasher.verify(password, user.password_hash):
            raise ValueError("Identifiants invalides.")
        
        # Migrate legacy SHA256 hash to bcrypt on successful login
        if PasswordHasher.needs_rehash(user.password_hash):
            user.password_hash = PasswordHasher.hash(password)
            self.users.update(user)
        
        return self.sessions.create_session(user.id)

    def logout(self, token: str):
        self.sessions.destroy_session(token)


class CatalogService:
    def __init__(self, products: ProductRepository):
        self.products = products

    def list_products(self) -> List[Product]:
        return self.products.list_active()


class CartService:
    def __init__(self, carts: CartRepository, products: ProductRepository):
        self.carts = carts
        self.products = products

    def add_to_cart(self, user_id: str, product_id: str, qty: int = 1):
        product = self.products.get(product_id)
        if not product:
            raise ValueError("Produit introuvable.")
        self.carts.get_or_create(user_id).add(product, qty)

    def remove_from_cart(self, user_id: str, product_id: str, qty: int = 1):
        self.carts.get_or_create(user_id).remove(product_id, qty)

    def view_cart(self, user_id: str) -> Cart:
        return self.carts.get_or_create(user_id)

    def cart_total(self, user_id: str) -> int:
        return self.carts.get_or_create(user_id).total_cents(self.products)


class PaymentGateway:
    """Simulation d'un prestataire CB (à remplacer par Stripe/Adyen/etc.)."""
    def charge_card(self, card_number: str, exp_month: int, exp_year: int, cvc: str, amount_cents: int, idempotency_key: str) -> Dict:
        # MOCK: succès si carte ne finit pas par '0000'
        ok = not card_number.endswith("0000")
        return {
            "success": ok,
            "transaction_id": str(uuid.uuid4()) if ok else None,
            "failure_reason": None if ok else "CARTE_REFUSEE"
        }

    def refund(self, transaction_id: str, amount_cents: int) -> Dict:
        return {
            "success": True,
            "refund_id": str(uuid.uuid4())
        }


class BillingService:
    def __init__(self, invoices: InvoiceRepository):
        self.invoices = invoices

    def issue_invoice(self, order: Order) -> Invoice:
        lines = [
            InvoiceLine(
                product_id=i.product_id,
                name=i.name,
                unit_price_cents=i.unit_price_cents,
                quantity=i.quantity,
                line_total_cents=i.unit_price_cents * i.quantity
            )
            for i in order.items
        ]
        inv = Invoice(
            id=str(uuid.uuid4()),
            order_id=order.id,
            user_id=order.user_id,
            lines=lines,
            total_cents=sum(l.line_total_cents for l in lines),
            issued_at=time.time()
        )
        self.invoices.add(inv)
        return inv


class DeliveryService:
    def prepare_delivery(self, order: Order, address: str, carrier: str = "POSTE") -> Delivery:
        delivery = Delivery(
            id=str(uuid.uuid4()),
            order_id=order.id,
            carrier=carrier,
            tracking_number=None,
            address=address,
            status="PREPAREE"
        )
        return delivery

    def ship(self, delivery: Delivery) -> Delivery:
        delivery.status = "EN_COURS"
        delivery.tracking_number = delivery.tracking_number or f"TRK-{uuid.uuid4().hex[:10].upper()}"
        return delivery

    def mark_delivered(self, delivery: Delivery) -> Delivery:
        delivery.status = "LIVREE"
        return delivery


class OrderService:
    def __init__(
        self,
        orders: OrderRepository,
        products: ProductRepository,
        carts: CartRepository,
        payments: PaymentRepository,
        invoices: InvoiceRepository,
        billing: BillingService,
        delivery_svc: DeliveryService,
        gateway: PaymentGateway,
        users: UserRepository
    ):
        self.orders = orders
        self.products = products
        self.carts = carts
        self.payments = payments
        self.invoices = invoices
        self.billing = billing
        self.delivery_svc = delivery_svc
        self.gateway = gateway
        self.users = users

    # ----- CHECKOUT -----

    def checkout(self, user_id: str) -> Order:
        """Create order from cart without reserving stock.
        
        Stock is only reserved after successful payment.
        This allows users to abandon checkout without affecting inventory.
        """
        cart = self.carts.get_or_create(user_id)
        if not cart.items:
            raise ValueError("Panier vide.")
        # Verify stock availability (but don't reserve yet)
        order_items: List[OrderItem] = []
        for it in cart.items.values():
            p = self.products.get(it.product_id)
            if not p or not p.active:
                raise ValueError("Produit indisponible.")
            if p.stock_qty < it.quantity:
                raise ValueError(f"Stock insuffisant pour {p.name}.")
            # Don't reserve stock here - only verify availability
            order_items.append(OrderItem(
                product_id=p.id,
                name=p.name,
                unit_price_cents=p.price_cents,
                quantity=it.quantity
            ))
        order = Order(
            id=str(uuid.uuid4()),
            user_id=user_id,
            items=order_items,
            status=OrderStatus.CREE,
            created_at=time.time()
        )
        self.orders.add(order)
        # Ne pas vider le panier ici - il sera vidé uniquement après un paiement réussi
        return order

    def pay_by_card(self, order_id: str, card_number: str, exp_month: int, exp_year: int, cvc: str) -> Payment:
        """Process payment for an order and reserve stock only on success.
        
        Stock is reserved only after successful payment to prevent inventory
        issues if user abandons checkout.
        """
        order = self.orders.get(order_id)
        if not order:
            raise ValueError("Commande introuvable.")
        if order.status not in {OrderStatus.CREE, OrderStatus.VALIDEE}:
            raise ValueError("Statut de commande incompatible avec le paiement.")
        
        # Verify stock availability again (in case it changed between checkout and payment)
        for it in order.items:
            p = self.products.get(it.product_id)
            if not p or not p.active:
                raise ValueError(f"Produit {it.name} indisponible.")
            if p.stock_qty < it.quantity:
                raise ValueError(f"Stock insuffisant pour {it.name}.")
        
        amount = order.total_cents()
        res = self.gateway.charge_card(
            card_number, exp_month, exp_year, cvc, amount, idempotency_key=order.id
        )
        payment = Payment(
            id=str(uuid.uuid4()),
            order_id=order.id,
            user_id=order.user_id,
            amount_cents=amount,
            provider="CB",
            provider_ref=res.get("transaction_id"),
            succeeded=res["success"],
            created_at=time.time()
        )
        self.payments.add(payment)
        if not payment.succeeded:
            raise ValueError("Paiement refusé.")
        
        # Reserve stock only after successful payment
        for it in order.items:
            self.products.reserve_stock(it.product_id, it.quantity)
        
        order.payment_id = payment.id
        order.status = OrderStatus.PAYEE
        order.paid_at = time.time()
        # Facture
        inv = self.billing.issue_invoice(order)
        order.invoice_id = inv.id
        self.orders.update(order)
        # Vider le panier uniquement après un paiement réussi
        self.carts.clear(order.user_id)
        return payment

    def view_orders(self, user_id: str) -> List[Order]:
        return self.orders.list_by_user(user_id)

    def request_cancellation(self, user_id: str, order_id: str) -> Order:
        order = self.orders.get(order_id)
        if not order or order.user_id != user_id:
            raise ValueError("Commande introuvable.")
        if order.status in {OrderStatus.EXPEDIEE, OrderStatus.LIVREE}:
            raise ValueError("Trop tard pour annuler : commande expédiée.")
        order.status = OrderStatus.ANNULEE
        order.cancelled_at = time.time()
        # restituer le stock
        for it in order.items:
            self.products.release_stock(it.product_id, it.quantity)
        self.orders.update(order)
        return order



class CustomerService:
    """Service client: fils de discussion & messages côté UI + réponses agents."""
    def __init__(self, threads: ThreadRepository, users: UserRepository):
        self.threads = threads
        self.users = users

    def open_thread(self, user_id: str, subject: str, order_id: Optional[str] = None) -> MessageThread:
        th = MessageThread(id=str(uuid.uuid4()), user_id=user_id, order_id=order_id, subject=subject)
        self.threads.add(th)
        return th

    def post_message(self, thread_id: str, author_user_id: Optional[str], body: str) -> Message:
        th = self.threads.get(thread_id)
        if not th or th.closed:
            raise ValueError("Fil introuvable ou fermé.")
        if author_user_id is not None and not self.users.get(author_user_id):
            raise ValueError("Auteur inconnu.")
        msg = Message(id=str(uuid.uuid4()), thread_id=thread_id, author_user_id=author_user_id, body=body, created_at=time.time())
        th.messages.append(msg)
        return msg

    def close_thread(self, thread_id: str, user_id: str):
        """Close a support thread (can be called by the thread owner).
        
        Args:
            thread_id: ID of the thread to close
            user_id: ID of the user closing the thread (must be the thread owner)
        """
        th = self.threads.get(thread_id)
        if not th:
            raise ValueError("Fil introuvable.")
        # Only the thread owner can close their own thread
        if th.user_id != user_id:
            raise PermissionError("Seul le créateur du ticket peut le fermer.")
        th.closed = True
        return th


# =========================
# ====== DEMO ============
# =========================

if __name__ == "__main__":
    # Repos & services
    users = UserRepository()
    products = ProductRepository()
    carts = CartRepository()
    orders = OrderRepository()
    invoices = InvoiceRepository()
    payments = PaymentRepository()
    threads = ThreadRepository()
    sessions = SessionManager()

    auth = AuthService(users, sessions)
    catalog = CatalogService(products)
    cart_svc = CartService(carts, products)
    billing = BillingService(invoices)
    delivery_svc = DeliveryService()
    gateway = PaymentGateway()
    order_svc = OrderService(orders, products, carts, payments, invoices, billing, delivery_svc, gateway, users)
    cs = CustomerService(threads, users)

    # Données de test
    p1 = Product(id=str(uuid.uuid4()), name="T-Shirt Logo", description="Coton bio", price_cents=1999, stock_qty=100)
    p2 = Product(id=str(uuid.uuid4()), name="Sweat Capuche", description="Molleton", price_cents=4999, stock_qty=50)
    products.add(p1); products.add(p2)

    # Données de test (password must meet security requirements)
    client = auth.register("client@shop.test", "Secret123!", "Alice", "Martin", "12 Rue des Fleurs")

    # Données de test
    token = auth.login("client@shop.test", "Secret123!")
    user_id = sessions.get_user_id(token)

    # Affichage catalogue
    print("Produits:", [f"{p.name} {p.price_cents/100:.2f}€" for p in catalog.list_products()])

    # Données de test
    cart_svc.add_to_cart(user_id, p1.id, 2)
    cart_svc.add_to_cart(user_id, p2.id, 1)
    print("Total panier €:", cart_svc.cart_total(user_id)/100)

    # Données de test
    order = order_svc.checkout(user_id)
    print("Commande créée:", order.id, "Total €:", order.total_cents()/100)

    # Données de test
    payment = order_svc.pay_by_card(order.id, "4242424242424242", 12, 2030, "123")
    print("Paiement OK:", payment.provider_ref)

    # Données de test
    th = cs.open_thread(user_id, "Taille trop petite", order_id=order.id)
    cs.post_message(th.id, user_id, "Bonjour, je souhaite échanger le T-Shirt.")
    cs.post_message(th.id, None, "Bonjour, nous pouvons proposer un échange. Merci de renvoyer l'article.")
    cs.close_thread(th.id, user_id)
    print("Fil messages:", len(th.messages), "Fermé:", th.closed)

    # Données de test
    auth.logout(token)

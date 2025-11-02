// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Display a flash notification message to the user
 * @param {string} message - The message text to display
 * @param {string} type - Message type: 'success', 'error', 'info', 'warning'
 */
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `flash-message flash-${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
        ${message}
        <button class="flash-close" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    const container = document.querySelector('.flash-messages') || createFlashContainer();
    container.appendChild(notification);
    
    // Auto-remove notification after 5 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}

/**
 * Create flash messages container if it doesn't exist
 * @returns {HTMLElement} The flash messages container
 */
function createFlashContainer() {
    const container = document.createElement('div');
    container.className = 'flash-messages';
    document.body.appendChild(container);
    return container;
}

/**
 * Format price from cents to euros
 * @param {number} cents - Price in cents
 * @returns {string} Formatted price string (e.g., "89.99€")
 */
function formatPrice(cents) {
    return (cents / 100).toFixed(2) + '€';
}

/**
 * Format Unix timestamp to localized date string
 * @param {number} timestamp - Unix timestamp in seconds
 * @returns {string} Formatted date string
 */
function formatDate(timestamp) {
    return new Date(timestamp * 1000).toLocaleDateString('fr-FR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// ============================================================================
// CART MANAGEMENT FUNCTIONS
// ============================================================================

/**
 * Update cart item count badge in navigation
 * Fetches cart data from API and updates the counter
 */
function updateCartCount() {
    fetch('/api/cart')
        .then(response => response.json())
        .then(data => {
            if (data.items) {
                const totalItems = data.items.reduce((sum, item) => sum + item.quantity, 0);
                const cartCountElement = document.getElementById('cart-count');
                if (cartCountElement) {
                    cartCountElement.textContent = totalItems;
                }
            }
        })
        .catch(error => console.error('Error updating cart count:', error));
}

/**
 * Add product to shopping cart via AJAX
 * @param {string} productId - Product ID to add
 * @param {number} quantity - Quantity to add (default: 1)
 * @returns {Promise<boolean>} True if successful, false otherwise
 */
function addToCart(productId, quantity = 1) {
    return fetch('/add_to_cart', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            product_id: productId,
            quantity: quantity
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Produit ajouté au panier !', 'success');
            updateCartCount();  // Update cart badge
            return true;
        } else {
            showNotification(data.error || 'Erreur lors de l\'ajout au panier', 'error');
            return false;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Erreur de connexion', 'error');
        return false;
    });
}

/**
 * Remove product from shopping cart via AJAX
 * @param {string} productId - Product ID to remove
 * @param {number} quantity - Quantity to remove (default: 1)
 * @returns {Promise<boolean>} True if successful, false otherwise
 */
function removeFromCart(productId, quantity = 1) {
    return fetch('/remove_from_cart', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            product_id: productId,
            quantity: quantity
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Produit retiré du panier', 'success');
            updateCartCount();  // Update cart badge
            return true;
        } else {
            showNotification(data.error || 'Erreur lors de la suppression', 'error');
            return false;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Erreur de connexion', 'error');
        return false;
    });
}

// ============================================================================
// ORDER MANAGEMENT FUNCTIONS
// ============================================================================

/**
 * Create order from current cart
 * @returns {Promise<string|null>} Order ID if successful, null otherwise
 */
function checkout() {
    return fetch('/checkout', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Commande créée avec succès !', 'success');
            return data.order_id;
        } else {
            showNotification(data.error || 'Erreur lors de la commande', 'error');
            return null;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Erreur de connexion', 'error');
        return null;
    });
}

/**
 * Process payment for an order
 * @param {string} orderId - Order ID to pay for
 * @param {Object} cardData - Payment card information {card_number, exp_month, exp_year, cvc}
 * @returns {Promise<boolean>} True if payment successful, false otherwise
 */
function processPayment(orderId, cardData) {
    return fetch('/payment', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            order_id: orderId,
            ...cardData
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Paiement réussi ! Votre commande est confirmée.', 'success');
            return true;
        } else {
            showNotification(data.error || 'Erreur de paiement', 'error');
            return false;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Erreur de connexion', 'error');
        return false;
    });
}

// ============================================================================
// MODAL MANAGEMENT FUNCTIONS
// ============================================================================

/**
 * Open a modal dialog
 * @param {string} modalId - ID of the modal element to open
 */
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';  // Prevent background scrolling
    }
}

/**
 * Close a modal dialog
 * @param {string} modalId - ID of the modal element to close
 */
function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';  // Restore scrolling
    }
}

// ============================================================================
// FORM VALIDATION FUNCTIONS
// ============================================================================

/**
 * Validate email address format
 * @param {string} email - Email address to validate
 * @returns {boolean} True if valid email format
 */
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

/**
 * Validate credit card number format
 * @param {string} cardNumber - Card number to validate
 * @returns {boolean} True if valid format (13-19 digits)
 */
function validateCardNumber(cardNumber) {
    // Remove spaces before validation
    const cleaned = cardNumber.replace(/\s/g, '');
    // Check that it's numeric and has correct length
    return /^\d{13,19}$/.test(cleaned);
}

/**
 * Validate CVC code format
 * @param {string} cvc - CVC code to validate
 * @returns {boolean} True if valid format (3 or 4 digits)
 */
function validateCVC(cvc) {
    return /^\d{3,4}$/.test(cvc);
}

// ============================================================================
// INPUT FORMATTING FUNCTIONS
// ============================================================================

/**
 * Format card number input with spaces every 4 digits
 * @param {HTMLInputElement} input - Input element to format
 */
function formatCardNumber(input) {
    let value = input.value.replace(/\s/g, '');
    let formattedValue = value.replace(/(.{4})/g, '$1 ').trim();
    input.value = formattedValue;
}

/**
 * Limit input field length
 * @param {HTMLInputElement} input - Input element to limit
 * @param {number} maxLength - Maximum allowed length
 */
function limitInputLength(input, maxLength) {
    if (input.value.length > maxLength) {
        input.value = input.value.slice(0, maxLength);
    }
}

// Gestion des quantités
function changeQuantity(productId, change) {
    const input = document.getElementById('qty-' + productId);
    if (input) {
        const currentValue = parseInt(input.value);
        const newValue = Math.max(1, Math.min(input.max, currentValue + change));
        input.value = newValue;
    }
}

// Animation des éléments
function animateElement(element, animationClass) {
    element.classList.add(animationClass);
    setTimeout(() => {
        element.classList.remove(animationClass);
    }, 1000);
}

// Gestion des erreurs
function handleError(error, context = '') {
    console.error(`Error ${context}:`, error);
    showNotification('Une erreur inattendue s\'est produite', 'error');
}

// Utilitaires pour les dates
function timestampToDate(timestamp) {
    return new Date(timestamp * 1000).toLocaleDateString('fr-FR');
}

function timestampToDateTime(timestamp) {
    return new Date(timestamp * 1000).toLocaleString('fr-FR');
}

// Gestion des statuts de commande
function getStatusInfo(status) {
    const statusMap = {
        'CREE': { label: 'En attente', icon: 'fas fa-clock', color: 'warning' },
        'VALIDEE': { label: 'Validée', icon: 'fas fa-check', color: 'info' },
        'PAYEE': { label: 'Payée', icon: 'fas fa-credit-card', color: 'success' },
        'EXPEDIEE': { label: 'Expédiée', icon: 'fas fa-truck', color: 'primary' },
        'LIVREE': { label: 'Livrée', icon: 'fas fa-home', color: 'success' },
        'ANNULEE': { label: 'Annulée', icon: 'fas fa-times', color: 'danger' },
        'REMBOURSEE': { label: 'Remboursée', icon: 'fas fa-undo', color: 'info' }
    };
    return statusMap[status] || { label: status, icon: 'fas fa-question', color: 'secondary' };
}

// Gestion des filtres et recherche
function filterProducts(products, searchTerm) {
    if (!searchTerm) return products;
    
    const term = searchTerm.toLowerCase();
    return products.filter(product => 
        product.name.toLowerCase().includes(term) ||
        product.description.toLowerCase().includes(term)
    );
}

function sortProducts(products, sortBy) {
    switch (sortBy) {
        case 'price-asc':
            return products.sort((a, b) => a.price_cents - b.price_cents);
        case 'price-desc':
            return products.sort((a, b) => b.price_cents - a.price_cents);
        case 'name-asc':
            return products.sort((a, b) => a.name.localeCompare(b.name));
        case 'name-desc':
            return products.sort((a, b) => b.name.localeCompare(a.name));
        default:
            return products;
    }
}

// Gestion des favoris (si implémenté)
function toggleFavorite(productId) {
    const favorites = JSON.parse(localStorage.getItem('favorites') || '[]');
    const index = favorites.indexOf(productId);
    
    if (index > -1) {
        favorites.splice(index, 1);
        showNotification('Retiré des favoris', 'info');
    } else {
        favorites.push(productId);
        showNotification('Ajouté aux favoris', 'success');
    }
    
    localStorage.setItem('favorites', JSON.stringify(favorites));
    updateFavoriteButtons();
}

function updateFavoriteButtons() {
    const favorites = JSON.parse(localStorage.getItem('favorites') || '[]');
    document.querySelectorAll('.favorite-btn').forEach(btn => {
        const productId = btn.dataset.productId;
        if (favorites.includes(productId)) {
            btn.classList.add('active');
            btn.innerHTML = '<i class="fas fa-heart"></i>';
        } else {
            btn.classList.remove('active');
            btn.innerHTML = '<i class="far fa-heart"></i>';
        }
    });
}

// Gestion des notifications push (si implémenté)
function requestNotificationPermission() {
    if ('Notification' in window) {
        Notification.requestPermission().then(permission => {
            if (permission === 'granted') {
                showNotification('Notifications activées', 'success');
            }
        });
    }
}

function sendNotification(title, body) {
    if ('Notification' in window && Notification.permission === 'granted') {
        new Notification(title, { body, icon: '/static/favicon.ico' });
    }
}

// ============================================================================
// THEME MANAGEMENT FUNCTIONS
// ============================================================================

/**
 * Toggle between light and dark theme
 * Saves preference to localStorage
 */
function toggleTheme() {
    const currentTheme = localStorage.getItem('theme') || 'light';
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    
    showNotification(`Thème ${newTheme === 'dark' ? 'sombre' : 'clair'} activé`, 'info');
}

/**
 * Initialize theme from localStorage on page load
 */
function initTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
}

// ============================================================================
// MOBILE NAVIGATION FUNCTIONS
// ============================================================================

/**
 * Toggle mobile navigation menu visibility
 */
function toggleMobileMenu() {
    const navMenu = document.querySelector('.nav-menu');
    const navToggle = document.querySelector('.nav-toggle');
    
    navMenu.classList.toggle('active');
    navToggle.classList.toggle('active');
}

// ============================================================================
// SEARCH FUNCTIONALITY
// ============================================================================

/**
 * Initialize search bar functionality
 * Filters products in real-time on the current page (works on all pages)
 */
function initSearch() {
    const searchInput = document.getElementById('search-input');
    if (!searchInput) return;
    
    let hasScrolled = false; // Track if we've already scrolled for this search
    
    searchInput.addEventListener('input', function(e) {
        const searchTerm = e.target.value.trim().toLowerCase();
        const productsGrid = document.getElementById('products-grid');
        
        if (!productsGrid) return;
        
        // Scroll to products section when user starts typing
        if (searchTerm && !hasScrolled) {
            const productsSection = document.getElementById('products');
            if (productsSection) {
                productsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
                hasScrolled = true;
            }
        }
        
        // Reset scroll flag if search is cleared
        if (!searchTerm) {
            hasScrolled = false;
        }
        
        const productCards = productsGrid.querySelectorAll('.product-card');
        let visibleCount = 0;
        
        productCards.forEach(card => {
            const productName = card.querySelector('.product-name');
            const productDescription = card.querySelector('.product-description');
            
            const nameText = productName ? productName.textContent.toLowerCase() : '';
            const descText = productDescription ? productDescription.textContent.toLowerCase() : '';
            
            const matches = !searchTerm || nameText.includes(searchTerm) || descText.includes(searchTerm);
            
            if (matches) {
                card.style.display = '';
                visibleCount++;
            } else {
                card.style.display = 'none';
            }
        });
        
        // Handle no results message
        let noResultsMsg = productsGrid.querySelector('.no-results-message');
        
        if (searchTerm && visibleCount === 0) {
            if (!noResultsMsg) {
                noResultsMsg = document.createElement('div');
                noResultsMsg.className = 'no-results-message';
                noResultsMsg.style.gridColumn = '1 / -1';
                noResultsMsg.style.textAlign = 'center';
                noResultsMsg.style.padding = '3rem';
                noResultsMsg.style.color = 'var(--text-secondary)';
                productsGrid.appendChild(noResultsMsg);
            }
            noResultsMsg.innerHTML = '<i class="fas fa-search" style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.5;"></i><h3>Aucun produit trouvé</h3><p>Aucun produit ne correspond à votre recherche "' + searchTerm + '"</p>';
            noResultsMsg.style.display = 'block';
        } else if (noResultsMsg) {
            noResultsMsg.style.display = 'none';
        }
    });
    
    searchInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            // Also scroll on Enter key
            const productsSection = document.getElementById('products');
            if (productsSection) {
                productsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        }
    });
}

// ============================================================================
// PAGE INITIALIZATION
// ============================================================================

/**
 * Initialize page when DOM is loaded
 * Sets up event listeners, restores theme, updates cart count
 */
document.addEventListener('DOMContentLoaded', function() {
    // Remove page-loading class after fade-in animation completes
    setTimeout(() => {
        document.body.classList.remove('page-loading');
    }, 250);
    
    // Update cart count badge
    updateCartCount();
    
    // Initialize theme from saved preference
    initTheme();
    
    // Initialize search functionality
    initSearch();
    
    // Mise à jour des boutons favoris
    updateFavoriteButtons();
    
    // Gestion des modals
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', function(e) {
            if (e.target === this) {
                this.style.display = 'none';
                document.body.style.overflow = 'auto';
            }
        });
    });
    
    // Gestion de la navigation mobile
    const navToggle = document.querySelector('.nav-toggle');
    if (navToggle) {
        navToggle.addEventListener('click', toggleMobileMenu);
    }
    
    // Formatage automatique des numéros de carte
    document.querySelectorAll('input[type="text"]').forEach(input => {
        if (input.placeholder && input.placeholder.includes('carte')) {
            input.addEventListener('input', function() {
                formatCardNumber(this);
            });
        }
    });
    
    // Limitation de la longueur des inputs
    document.querySelectorAll('input[maxlength]').forEach(input => {
        input.addEventListener('input', function() {
            limitInputLength(this, parseInt(this.maxLength));
        });
    });
    
    // Gestion des formulaires
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> En cours...';
                
                // Réactiver le bouton après 3 secondes en cas d'erreur
                setTimeout(() => {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = submitBtn.dataset.originalText || 'Envoyer';
                }, 3000);
            }
        });
    });
    
    // Sauvegarde du texte original des boutons
    document.querySelectorAll('button[type="submit"]').forEach(btn => {
        btn.dataset.originalText = btn.innerHTML;
    });
    
    // Gestion des erreurs globales
    window.addEventListener('error', function(e) {
        console.error('Global error:', e.error);
        showNotification('Une erreur inattendue s\'est produite', 'error');
    });
    
    // Gestion des promesses rejetées
    window.addEventListener('unhandledrejection', function(e) {
        console.error('Unhandled promise rejection:', e.reason);
        showNotification('Une erreur de connexion s\'est produite', 'error');
    });
});

// Export des fonctions pour utilisation globale
window.EShop = {
    showNotification,
    addToCart,
    removeFromCart,
    updateCartCount,
    checkout,
    processPayment,
    openModal,
    closeModal,
    validateEmail,
    validateCardNumber,
    validateCVC,
    formatCardNumber,
    changeQuantity,
    toggleFavorite,
    updateFavoriteButtons,
    toggleTheme,
    getStatusInfo,
    filterProducts,
    sortProducts,
    formatPrice,
    formatDate,
    timestampToDate,
    timestampToDateTime
};

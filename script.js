/**
 * ShopEasy Main JavaScript
 * Handles cart operations, UI animations, and checkout flow
 */

document.addEventListener('DOMContentLoaded', () => {
    // Initialize Navbar Scroll Effect
    const navbar = document.getElementById('navbar');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.classList.add('navbar-scrolled');
        } else {
            navbar.classList.remove('navbar-scrolled');
        }
    });

    // Mobile Menu Toggle
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const mobileMenu = document.getElementById('mobileMenu');
    if (mobileMenuBtn && mobileMenu) {
        mobileMenuBtn.addEventListener('click', () => {
            mobileMenu.classList.toggle('active');
            mobileMenuBtn.querySelector('i').classList.toggle('fa-bars');
            mobileMenuBtn.querySelector('i').classList.toggle('fa-times');
        });

        // Close menu on click outside
        document.addEventListener('click', (e) => {
            if (!mobileMenu.contains(e.target) && !mobileMenuBtn.contains(e.target)) {
                mobileMenu.classList.remove('active');
                mobileMenuBtn.querySelector('i').classList.add('fa-bars');
                mobileMenuBtn.querySelector('i').classList.remove('fa-times');
            }
        });
    }

    // Admin Sidebar Toggle (for mobile)
    const adminSidebarBtn = document.getElementById('adminSidebarToggle');
    const adminSidebar = document.querySelector('.admin-sidebar');
    if (adminSidebarBtn && adminSidebar) {
        adminSidebarBtn.addEventListener('click', () => {
            adminSidebar.classList.toggle('active');
        });
    }

    // User Dropdown
    const userDropdownBtn = document.getElementById('userDropdownBtn');
    const userDropdown = document.getElementById('userDropdown');
    if (userDropdownBtn && userDropdown) {
        userDropdownBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            userDropdown.classList.toggle('show');
        });
        document.addEventListener('click', () => {
            userDropdown.classList.remove('show');
        });
    }

    // Initialize Cart Badge
    updateCartBadge();
});

/**
 * Toast Notifications
 */
function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;

    const icon = {
        success: 'fa-check-circle',
        error: 'fa-exclamation-circle',
        warning: 'fa-exclamation-triangle',
        info: 'fa-info-circle'
    }[type] || 'fa-info-circle';

    toast.innerHTML = `
        <i class="fas ${icon}"></i>
        <span>${message}</span>
    `;

    container.appendChild(toast);

    // Trigger animation
    setTimeout(() => toast.classList.add('show'), 100);

    // Remove after 3 seconds
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 500);
    }, 3000);
}

/**
 * Cart Operations
 */
async function updateCartBadge() {
    try {
        const response = await fetch('/api/cart/count');
        const data = await response.json();
        const badge = document.getElementById('cartBadge');
        if (badge) {
            badge.textContent = data.count || 0;
            badge.style.display = data.count > 0 ? 'flex' : 'none';
        }
    } catch (err) {
        console.error('Failed to update cart badge:', err);
    }
}

async function addToCart(productId) {
    try {
        const response = await fetch('/api/cart/add', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ product_id: productId, quantity: 1 })
        });
        const data = await response.json();

        if (response.ok) {
            showToast('Product added to cart!', 'success');
            // Update badge directly from response
            const badge = document.getElementById('cartBadge');
            if (badge && data.cart_count !== undefined) {
                badge.textContent = data.cart_count;
                badge.style.display = data.cart_count > 0 ? 'flex' : 'none';
            }
        } else {
            showToast(data.message || 'Failed to add to cart', 'error');
            if (response.status === 401) {
                setTimeout(() => window.location.href = '/login', 1500);
            }
        }
    } catch (err) {
        showToast('Something went wrong', 'error');
    }
}

// Product Detail Size Selection
function selectSize(btn, size) {
    // Remove active class from all size buttons
    document.querySelectorAll('.size-btn').forEach(b => b.classList.remove('active'));
    // Add active class to clicked button
    btn.classList.add('active');
    // Set hidden input value
    const sizeInput = document.getElementById('selectedSize');
    if (sizeInput) sizeInput.value = size;
}

// Add to Cart from Product Page with Qty and Size
async function addToCartWithQty(productId) {
    const qtyInput = document.getElementById('detailQty');
    const quantity = qtyInput ? parseInt(qtyInput.value) : 1;

    const sizeInput = document.getElementById('selectedSize');
    const size = sizeInput ? sizeInput.value : null;

    // Check if size selection is required but missing
    if (document.querySelector('.size-options') && !size) {
        showToast('Please select a size first!', 'warning');
        return;
    }

    try {
        const response = await fetch('/api/cart/add', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ product_id: productId, quantity: quantity, size: size })
        });

        const data = await response.json();
        if (response.ok) {
            showToast(`${quantity} item(s) added to cart!`, 'success');
            // Update badge directly from response
            const badge = document.getElementById('cartBadge');
            if (badge && data.cart_count !== undefined) {
                badge.textContent = data.cart_count;
                badge.style.display = data.cart_count > 0 ? 'flex' : 'none';
            }
        } else {
            showToast(data.message || 'Error adding to cart', 'error');
            if (response.status === 401) {
                setTimeout(() => window.location.href = '/login', 1500);
            }
        }
    } catch (error) {
        showToast('Something went wrong', 'error');
    }
}

async function updateCartQty(itemId, newQty) {
    if (newQty < 1) return;

    try {
        const response = await fetch('/api/cart/update', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ item_id: itemId, quantity: newQty })
        });

        if (response.ok) {
            window.location.reload();
        } else {
            const data = await response.json();
            showToast(data.message || 'Update failed', 'error');
        }
    } catch (err) {
        showToast('Failed to update quantity', 'error');
    }
}

async function removeCartItem(itemId) {
    try {
        const response = await fetch('/api/cart/remove', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ item_id: itemId })
        });

        if (response.ok) {
            const itemElement = document.getElementById(`cartItem-${itemId}`);
            if (itemElement) {
                itemElement.classList.add('removing');
                setTimeout(() => window.location.reload(), 400);
            } else {
                window.location.reload();
            }
        }
    } catch (err) {
        showToast('Failed to remove item', 'error');
    }
}

function changeDetailQty(delta) {
    const input = document.getElementById('detailQty');
    if (!input) return;
    let val = parseInt(input.value) + delta;
    if (val < 1) val = 1;
    if (input.max && val > parseInt(input.max)) val = parseInt(input.max);
    input.value = val;
}

async function buyNow(productId) {
    const qtyInput = document.getElementById('detailQty');
    const quantity = qtyInput ? parseInt(qtyInput.value) : 1;

    const sizeInput = document.getElementById('selectedSize');
    const size = sizeInput ? sizeInput.value : null;

    // Check size if required
    if (document.querySelector('.size-options') && !size) {
        showToast('Please select a size first!', 'warning');
        return;
    }

    try {
        const response = await fetch('/api/cart/add', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ product_id: productId, quantity: quantity, size: size })
        });

        if (response.ok) {
            window.location.href = '/checkout';
        } else {
            const data = await response.json();
            showToast(data.message || 'Error processing request', 'error');
            if (response.status === 401) {
                setTimeout(() => window.location.href = '/login', 1500);
            }
        }
    } catch (error) {
        showToast('Something went wrong', 'error');
    }
}

/**
 * Checkout Flow
 */
function goToStep(step) {
    if (step === 2) {
        // Validate shipping form
        const form = document.getElementById('shippingForm');
        if (form && !form.checkValidity()) {
            form.reportValidity();
            const firstInvalid = form.querySelector(':invalid');
            if (firstInvalid) {
                firstInvalid.focus();
                firstInvalid.classList.add('shake');
                setTimeout(() => firstInvalid.classList.remove('shake'), 500);
            }
            return;
        }

        // Fill review details
        const details = `
            <div class="review-details-grid">
                <div class="review-detail-card">
                    <i class="fas fa-user-circle"></i>
                    <div>
                        <span class="detail-label">Deliver to</span>
                        <strong>${document.getElementById('fullName').value}</strong>
                    </div>
                </div>
                <div class="review-detail-card">
                    <i class="fas fa-phone-alt"></i>
                    <div>
                        <span class="detail-label">Phone</span>
                        <strong>${document.getElementById('phone').value}</strong>
                    </div>
                </div>
                <div class="review-detail-card full-width">
                    <i class="fas fa-map-marker-alt"></i>
                    <div>
                        <span class="detail-label">Address</span>
                        <strong>${document.getElementById('address').value}, ${document.getElementById('city').value}, ${document.getElementById('state').value} - ${document.getElementById('zipcode').value}</strong>
                    </div>
                </div>
            </div>
        `;
        const reviewDiv = document.getElementById('reviewShippingDetails');
        if (reviewDiv) reviewDiv.innerHTML = details;
    }

    // Update Indicators
    document.querySelectorAll('.step').forEach((el, idx) => {
        const s = idx + 1;
        el.classList.remove('active', 'completed');
        if (s === step) el.classList.add('active');
        else if (s < step) el.classList.add('completed');
    });

    // Show Step with animation
    const steps = document.querySelectorAll('.checkout-step');
    steps.forEach(s => {
        s.style.opacity = '0';
        s.style.transform = 'translateY(20px)';
        setTimeout(() => s.classList.add('hidden'), 300);
    });

    setTimeout(() => {
        const nextStep = document.getElementById(`step${step}`);
        if (nextStep) {
            nextStep.classList.remove('hidden');
            setTimeout(() => {
                nextStep.style.opacity = '1';
                nextStep.style.transform = 'translateY(0)';
            }, 50);
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
    }, 350);
}



function toggleQrCode(show) {
    const qrSection = document.getElementById('qrCodeSection');
    if (qrSection) {
        if (show) {
            qrSection.classList.remove('hidden');
        } else {
            qrSection.classList.add('hidden');
        }
    }
}

function selectPayment(method) {
    document.querySelectorAll('.payment-option').forEach(opt => {
        opt.classList.remove('active');
        const radio = opt.querySelector('input[type="radio"]');
        if (radio) {
            if (radio.value === method) {
                opt.classList.add('active');
                radio.checked = true;
                const check = opt.querySelector('.payment-check');
                if (check) check.classList.remove('hidden');
            } else {
                const check = opt.querySelector('.payment-check');
                if (check) check.classList.add('hidden');
            }
        }
    });

    // Toggle QR section for UPI
    const upiSection = document.getElementById('upiQrSection');
    if (upiSection) {
        if (method === 'upi') {
            upiSection.classList.remove('hidden');
        } else {
            upiSection.classList.add('hidden');
        }
    }
}

async function processPayment() {
    const checkedRadio = document.querySelector('input[name="payment"]:checked');
    if (!checkedRadio) return;

    const paymentMethod = checkedRadio.value;

    // Shipping data
    const shippingData = {
        full_name: document.getElementById('fullName').value,
        phone: document.getElementById('phone').value,
        address: document.getElementById('address').value,
        city: document.getElementById('city').value,
        state: document.getElementById('state').value,
        zipcode: document.getElementById('zipcode').value,
    };

    if (paymentMethod === 'cod' || paymentMethod === 'free' || paymentMethod === 'upi') {
        submitOrder(shippingData, paymentMethod);
    } else {
        // Razorpay Integration
        initiateRazorpay(shippingData);
    }
}

function initiateRazorpay(shippingData) {
    if (RAZORPAY_KEY.includes('XXXXX')) {
        showToast('Razorpay keys not set. Simulating payment...', 'warning');
        setTimeout(() => {
            submitOrder(shippingData, 'razorpay', 'pay_sim_12345');
        }, 1500);
        return;
    }

    // This assumes RAZORPAY_KEY and ORDER_TOTAL are set in checkout.html
    const options = {
        "key": RAZORPAY_KEY,
        "amount": Math.round(ORDER_TOTAL * 100), // In paise
        "currency": "INR",
        "name": "ShopEasy",
        "description": "Order Purchase",
        "handler": function (response) {
            submitOrder(shippingData, 'razorpay', response.razorpay_payment_id);
        },
        "prefill": {
            "name": shippingData.full_name,
            "contact": shippingData.phone
        },
        "theme": { "color": "#212121" }
    };
    const rzp = new Razorpay(options);
    rzp.open();
}

async function submitOrder(shippingData, paymentMethod, paymentId = null) {
    const payBtn = document.getElementById('payBtn');
    payBtn.disabled = true;
    payBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';

    const orderData = {
        ...shippingData,
        payment_method: paymentMethod,
        payment_id: paymentId
    };

    try {
        const response = await fetch('/api/checkout', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(orderData)
        });
        const data = await response.json();

        if (response.ok) {
            window.location.href = `/success?order_id=${data.order_id}`;
        } else {
            showToast(data.message || 'Order failed', 'error');
            payBtn.disabled = false;
            payBtn.innerHTML = 'COMPLETE PURCHASE';
        }
    } catch (err) {
        showToast('Connection error', 'error');
        payBtn.disabled = false;
        payBtn.innerHTML = 'COMPLETE PURCHASE';
    }
}

/**
 * Admin Functions
 */
function switchAdminTab(tabName) {
    // Update tabs
    document.querySelectorAll('.admin-tab').forEach(tab => {
        tab.classList.remove('active');
        if (tab.getAttribute('onclick').includes(tabName)) tab.classList.add('active');
    });

    // Update content
    document.querySelectorAll('.admin-content').forEach(content => {
        content.classList.add('hidden');
    });
    document.getElementById(`${tabName}Tab`).classList.remove('hidden');
}

function openEditProduct(productId) {
    const modal = document.getElementById('editModal');
    if (!modal) return;

    fetch(`/api/product/${productId}`)
        .then(res => res.json())
        .then(data => {
            // Populate form fields
            const form = document.getElementById('editForm');
            form.action = `/admin/product/edit/${data.id}`;

            document.getElementById('editName').value = data.name;
            document.getElementById('editCategory').value = data.category;
            document.getElementById('editDesc').value = data.description;
            document.getElementById('editPrice').value = data.price;
            document.getElementById('editOrigPrice').value = data.original_price || '';
            document.getElementById('editStock').value = data.stock;
            document.getElementById('editFeatured').checked = data.featured;
            document.getElementById('editHighlights').value = data.highlights || '';
            document.getElementById('editSizes').value = data.sizes || '';

            modal.classList.add('active');
        })
        .catch(err => showToast('Failed to fetch product details', 'error'));
}

function closeEditModal() {
    const modal = document.getElementById('editModal');
    if (modal) modal.classList.remove('active');
}

/**
 * Password Visibility Toggle
 */
function togglePassword(button) {
    const group = button.closest('.password-group');
    const input = group.querySelector('input');
    const icon = button.querySelector('i');

    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.replace('fa-eye', 'fa-eye-slash');
    } else {
        input.type = 'password';
        icon.classList.replace('fa-eye-slash', 'fa-eye');
    }
}

document.addEventListener('DOMContentLoaded', function () {
    initDarkMode();
    updateCartCount();
    initPageTransition();
    initBackToTop();
    initTypingEffect();
    initCartPreview();
    initSeasonalBanner();
    initAddToCart();
    initQtyControls();
    initRemoveItem();
    initQuickAddToCart();
});

function initAddToCart() {
    const form = document.getElementById('add-to-cart-form');
    if (!form) return;
    form.addEventListener('submit', function (e) {
        e.preventDefault();
        const formData = new FormData(this);
        fetch('/cart/add', {
            method: 'POST',
            body: new URLSearchParams(formData)
        })
        .then(r => r.json())
        .then(data => {
            if (data.status === 'ok') {
                updateCartCount();
                pulseCartBadge();
                showToast('Added to cart!', 'success');
            }
        });
    });
}

function initQtyControls() {
    document.querySelectorAll('.qty-plus').forEach(btn => {
        btn.addEventListener('click', function () {
            const input = this.parentElement.querySelector('.qty-input');
            const max = parseInt(input.getAttribute('max')) || 99;
            if (parseInt(input.value) < max) {
                input.value = parseInt(input.value) + 1;
                updateQuantity(input);
            }
        });
    });
    document.querySelectorAll('.qty-minus').forEach(btn => {
        btn.addEventListener('click', function () {
            const input = this.parentElement.querySelector('.qty-input');
            if (parseInt(input.value) > 1) {
                input.value = parseInt(input.value) - 1;
                updateQuantity(input);
            }
        });
    });
    document.querySelectorAll('.qty-input').forEach(input => {
        input.addEventListener('change', function () {
            if (parseInt(this.value) < 1) this.value = 1;
            const max = parseInt(this.getAttribute('max')) || 99;
            if (parseInt(this.value) > max) this.value = max;
            updateQuantity(this);
        });
    });
}

function initRemoveItem() {
    document.querySelectorAll('.remove-item').forEach(btn => {
        btn.addEventListener('click', function () {
            const pid = this.dataset.productId;
            const fd = new FormData();
            fd.append('product_id', pid);
            fetch('/cart/remove', {
                method: 'POST',
                body: new URLSearchParams(fd)
            })
            .then(r => r.json())
            .then(data => {
                if (data.status === 'ok') {
                    const row = document.querySelector('tr[data-product-id="' + pid + '"]');
                    if (row) row.remove();
                    updateCartCount();
                    location.reload();
                }
            });
        });
    });
}

function updateQuantity(input) {
    const row = input.closest('tr');
    if (!row) return;
    const pid = row.dataset.productId;
    const fd = new FormData();
    fd.append('product_id', pid);
    fd.append('quantity', input.value);
    fetch('/cart/update', {
        method: 'POST',
        body: new URLSearchParams(fd)
    })
    .then(r => r.json())
    .then(data => {
        if (data.status === 'ok') {
            updateCartCount();
            if (data.total !== undefined) {
                const el = document.getElementById('cart-total');
                if (el) el.textContent = '$' + data.total.toFixed(2);
            }
            location.reload();
        }
    });
}

function updateCartCount() {
    fetch('/cart/count')
    .then(r => r.json())
    .then(data => {
        const el = document.getElementById('cart-count');
        if (el) el.textContent = data.count;
    })
    .catch(() => {});
}

function showToast(message, type) {
    const existing = document.querySelector('.toast-narmo');
    if (existing) existing.remove();
    const toast = document.createElement('div');
    toast.className = 'toast-narmo';
    const icons = { success: 'bi-check-circle-fill', error: 'bi-exclamation-circle-fill', info: 'bi-info-circle-fill' };
    toast.innerHTML = '<i class="bi ' + (icons[type] || icons.success) + ' me-2"></i> ' + message;
    document.body.appendChild(toast);
    requestAnimationFrame(() => toast.classList.add('show'));
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 2500);
}

function pulseCartBadge() {
    const el = document.getElementById('cart-count');
    if (!el) return;
    el.style.transition = 'transform 0.15s';
    el.style.transform = 'scale(1.4)';
    setTimeout(() => { el.style.transform = 'scale(1)'; }, 200);
}

function initDarkMode() {
    const toggle = document.getElementById('dark-toggle');
    if (!toggle) return;
    const stored = localStorage.getItem('narmo-theme');
    if (stored === 'dark' || (!stored && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
        document.documentElement.setAttribute('data-theme', 'dark');
        toggle.innerHTML = '<i class="bi bi-sun-fill"></i>';
    }
    toggle.addEventListener('click', function () {
        const html = document.documentElement;
        const isDark = html.getAttribute('data-theme') === 'dark';
        if (isDark) {
            html.removeAttribute('data-theme');
            localStorage.setItem('narmo-theme', 'light');
            this.innerHTML = '<i class="bi bi-moon-fill"></i>';
        } else {
            html.setAttribute('data-theme', 'dark');
            localStorage.setItem('narmo-theme', 'dark');
            this.innerHTML = '<i class="bi bi-sun-fill"></i>';
        }
    });
}

function initPageTransition() {
    document.body.classList.remove('page-loading');
    document.body.classList.add('page-ready');
}

function initBackToTop() {
    const btn = document.getElementById('back-to-top');
    if (!btn) return;
    window.addEventListener('scroll', function () {
        btn.classList.toggle('visible', window.scrollY > 400);
    });
    btn.addEventListener('click', function () {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
}

function initTypingEffect() {
    const el = document.querySelector('.typing-text');
    if (!el) return;
    const text = el.textContent;
    el.textContent = '';
    el.insertAdjacentHTML('afterbegin', '<span></span><span class="typing-cursor"></span>');
    const span = el.querySelector('span');
    let i = 0;
    function type() {
        if (i < text.length) {
            span.textContent += text.charAt(i);
            i++;
            setTimeout(type, 50 + Math.random() * 40);
        } else {
            el.querySelector('.typing-cursor').style.animation = 'blink 0.7s step-end infinite';
        }
    }
    setTimeout(type, 600);
}
function initCartPreview() {
    const wrap = document.querySelector('.cart-preview-wrap');
    if (!wrap) return;
    const dropdown = wrap.querySelector('.cart-preview-dropdown');
    let hideTimer = null;
    wrap.addEventListener('mouseenter', function () {
        clearTimeout(hideTimer);
        fetch('/cart/preview')
        .then(r => r.json())
        .then(function (data) {
            if (data.count === 0) {
                dropdown.innerHTML = '<div class="cart-preview-empty"><i class="bi bi-bag" style="font-size:1.5rem;display:block;margin-bottom:0.5rem;"></i>Your cart is empty</div>';
            } else {
                var html = '';
                data.items.forEach(function (item) {
                    html += '<div class="cart-preview-item">' +
                        '<img src="/static/images/products/' + item.image + '" alt="" onerror="this.src=\'https://placehold.co/44x44/F1F5F9/64748B?text=N\'">' +
                        '<div class="name">' + item.name + '</div>' +
                        '<span class="qty">x' + item.quantity + '</span>' +
                        '<span class="subtotal">$' + item.subtotal.toFixed(2) + '</span>' +
                    '</div>';
                });
                if (data.count > 5) {
                    html += '<div style="padding:0.5rem 1rem;font-size:0.75rem;color:var(--gray);text-align:center;">+' + (data.count - 5) + ' more items</div>';
                }
                html += '<div class="cart-preview-footer"><span>Total</span><span>$' + data.total.toFixed(2) + '</span></div>' +
                    '<a href="/cart/" style="display:block;text-align:center;padding:0.6rem;background:var(--accent);color:#fff;font-weight:600;font-size:0.85rem;text-decoration:none;">View Cart <i class="bi bi-arrow-right"></i></a>';
                dropdown.innerHTML = html;
            }
            dropdown.classList.add('show');
        });
    });
    wrap.addEventListener('mouseleave', function () {
        hideTimer = setTimeout(function () {
            dropdown.classList.remove('show');
        }, 300);
    });
}

function initQuickAddToCart() {
    document.addEventListener('click', function (e) {
        const btn = e.target.closest('.add-to-cart-btn');
        if (!btn) return;
        const pid = btn.dataset.productId;
        if (!pid) return;
        const fd = new FormData();
        fd.append('product_id', pid);
        fd.append('quantity', 1);
        fetch('/cart/add', {
            method: 'POST',
            body: new URLSearchParams(fd)
        })
        .then(r => r.json())
        .then(data => {
            if (data.status === 'ok') {
                updateCartCount();
                pulseCartBadge();
                showToast('Added to cart!', 'success');
            }
        });
    });
}

function initSeasonalBanner() {
    const banner = document.getElementById('seasonal-banner');
    if (!banner) return;
    if (localStorage.getItem('narmo-banner-dismissed')) {
        banner.style.display = 'none';
        return;
    }
    banner.querySelector('.dismiss-banner').addEventListener('click', function () {
        banner.style.display = 'none';
        localStorage.setItem('narmo-banner-dismissed', '1');
    });
}

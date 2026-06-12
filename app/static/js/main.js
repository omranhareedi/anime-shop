document.addEventListener('DOMContentLoaded', function () {
    initDarkMode();
    updateCartCount();
    initPageLoader();
    initPageTransition();
    initBackToTop();
    initTypingEffect();
    initCartPreview();
    initSeasonalBanner();
    initAddToCart();
    initQtyControls();
    initRemoveItem();
    initQuickAddToCart();
    initButtonRipple();
    initCounterAnimation();
    initCartGlowCheck();
    initSearchToggle();
    initImageFallback();
});

function initImageFallback() {
    document.addEventListener('error', function (e) {
        var img = e.target;
        if (img.tagName !== 'IMG' || img.dataset.errorHandled) return;
        img.dataset.errorHandled = '1';
        var text = img.getAttribute('alt') || 'Image';
        img.src = 'https://placehold.co/400x400/F1F5F9/64748B?text=' + encodeURIComponent(text);
    }, true);
}

function initPageLoader() {
    var loader = document.getElementById('page-loader');
    var bar = document.getElementById('narmo-loading-bar');
    if (loader) {
        loader.classList.add('hidden');
        setTimeout(function () { loader.style.display = 'none'; }, 700);
    }
    if (bar) {
        bar.classList.add('active');
        setTimeout(function () { bar.classList.remove('active'); }, 600);
    }
    window.addEventListener('beforeunload', function () {
        if (bar) bar.classList.add('active');
    });
}

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

function updateCartCount(suppressShake) {
    fetch('/cart/count')
    .then(r => r.json())
    .then(data => {
        const el = document.getElementById('cart-count');
        if (el) {
            el.textContent = data.count;
            if (parseInt(data.count) > 0) {
                el.classList.add('has-items');
            } else {
                el.classList.remove('has-items');
            }
        }
    })
    .catch(() => {});
}

function initCartGlowCheck() {
    var el = document.getElementById('cart-count');
    if (el && parseInt(el.textContent) > 0) {
        el.classList.add('has-items');
    }
}

function initButtonRipple() {
    document.addEventListener('click', function (e) {
        var btn = e.target.closest('.btn-primary-narmo, .btn-outline-narmo, .btn-add-cart, .btn-submit, .btn-titan, .btn-ripple');
        if (!btn) return;
        var rect = btn.getBoundingClientRect();
        var ripple = document.createElement('span');
        ripple.className = 'ripple-effect';
        var size = Math.max(rect.width, rect.height);
        ripple.style.width = ripple.style.height = size + 'px';
        ripple.style.left = (e.clientX - rect.left - size / 2) + 'px';
        ripple.style.top = (e.clientY - rect.top - size / 2) + 'px';
        btn.appendChild(ripple);
        setTimeout(function () { ripple.remove(); }, 600);
    });
}

function initCounterAnimation() {
    document.querySelectorAll('.hero-stat-value').forEach(function (el) {
        var text = el.textContent;
        var num = parseFloat(text);
        if (isNaN(num)) return;
        var suffix = text.replace(/[\d.]/g, '');
        el.textContent = '0' + suffix;
        var target = num;
        var duration = 1200;
        var start = performance.now();
        function update(now) {
            var elapsed = now - start;
            var progress = Math.min(elapsed / duration, 1);
            var eased = 1 - Math.pow(1 - progress, 3);
            var current = Math.floor(eased * target);
            el.textContent = current + suffix;
            if (progress < 1) {
                requestAnimationFrame(update);
            } else {
                el.textContent = target + suffix;
            }
        }
        requestAnimationFrame(update);
    });
}

function triggerTitanShake(el) {
    if (!el) return;
    el.classList.add('shake-titan');
    setTimeout(function () { el.classList.remove('shake-titan'); }, 500);
}

function triggerStomp() {
    document.body.classList.add('titan-stomp');
    setTimeout(function () { document.body.classList.remove('titan-stomp'); }, 800);
}

function showToast(message, type) {
    const old = document.querySelector('.toast-narmo');
    if (old) old.remove();
    const toast = document.createElement('div');
    toast.className = 'toast-narmo show';
    const icons = { success: 'bi-check-circle-fill', error: 'bi-exclamation-circle-fill', info: 'bi-info-circle-fill' };
    toast.innerHTML = '<i class="bi ' + (icons[type] || icons.success) + '"></i><span>' + message + '</span>';
    document.body.appendChild(toast);
    toast.onclick = function () { toast.remove(); };
    setTimeout(function () { if (toast.parentNode) toast.remove(); }, 2000);
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
    const toggleMobile = document.getElementById('dark-toggle-mobile');
    if (!toggle) return;
    const stored = localStorage.getItem('narmo-theme');
    var isDark = stored === 'dark' || (!stored && window.matchMedia('(prefers-color-scheme: dark)').matches);
    if (isDark) {
        document.documentElement.setAttribute('data-theme', 'dark');
        toggle.innerHTML = '<i class="bi bi-sunrise-fill"></i>';
        if (toggleMobile) toggleMobile.innerHTML = '<i class="bi bi-sunrise-fill me-1"></i> Light Mode';
    } else {
        if (toggleMobile) toggleMobile.innerHTML = '<i class="bi bi-moon-stars-fill me-1"></i> Dark Mode';
    }
    function spinIcon(btn) {
        btn.classList.add('dark-toggle-spin');
        setTimeout(function () { btn.classList.remove('dark-toggle-spin'); }, 400);
    }
    function apply(isDark) {
        var html = document.documentElement;
        if (isDark) {
            html.setAttribute('data-theme', 'dark');
            localStorage.setItem('narmo-theme', 'dark');
            toggle.innerHTML = '<i class="bi bi-sunrise-fill"></i>';
            if (toggleMobile) toggleMobile.innerHTML = '<i class="bi bi-sunrise-fill me-1"></i> Light Mode';
        } else {
            html.removeAttribute('data-theme');
            localStorage.setItem('narmo-theme', 'light');
            toggle.innerHTML = '<i class="bi bi-moon-stars-fill"></i>';
            if (toggleMobile) toggleMobile.innerHTML = '<i class="bi bi-moon-stars-fill me-1"></i> Dark Mode';
        }
    }
    toggle.addEventListener('click', function () {
        spinIcon(this);
        isDark = document.documentElement.getAttribute('data-theme') === 'dark';
        apply(!isDark);
    });
    if (toggleMobile) {
        toggleMobile.addEventListener('click', function () {
            spinIcon(this);
            isDark = document.documentElement.getAttribute('data-theme') === 'dark';
            apply(!isDark);
        });
    }
}

function initPageTransition() {
    document.body.classList.remove('page-loading');
    document.body.classList.add('page-ready');
    setTimeout(function () { document.body.classList.remove('page-ready'); }, 400);
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
                dropdown.innerHTML = '<div class="cart-preview-empty"><i class="bi bi-bag-fill" style="font-size:1.5rem;display:block;margin-bottom:0.5rem;color:var(--gray);"></i>Your cart is empty</div>';
            } else {
                var html = '';
                data.items.forEach(function (item) {
                    html += '<div class="cart-preview-item">' +
                        '<img src="' + (item.image.startsWith('http') ? item.image : '/static/images/products/' + item.image) + '" alt="' + item.name + '">' +
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
                triggerTitanShake(document.querySelector('.cart-badge'));
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

function initSearchToggle() {
    var toggle = document.getElementById('nav-search-toggle');
    var form = document.querySelector('.nav-search-form');
    var input = form ? form.querySelector('.nav-search-input') : null;
    if (!toggle || !form) return;
    toggle.addEventListener('click', function (e) {
        e.stopPropagation();
        form.classList.toggle('open');
        if (form.classList.contains('open') && input) {
            input.focus();
        }
    });
    if (input) {
        input.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') {
                form.classList.remove('open');
                input.blur();
            }
        });
    }
    document.addEventListener('click', function (e) {
        if (form.classList.contains('open') && !form.contains(e.target) && !toggle.contains(e.target)) {
            form.classList.remove('open');
        }
    });
}

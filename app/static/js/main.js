document.addEventListener('DOMContentLoaded', function () {
    initDarkMode();
    updateCartCount();

    const addForm = document.getElementById('add-to-cart-form');
    if (addForm) {
        addForm.addEventListener('submit', function (e) {
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
                    showToast('Added to cart!', 'success');
                }
            });
        });
    }

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

    document.querySelectorAll('.remove-item').forEach(btn => {
        btn.addEventListener('click', function () {
            const productId = this.dataset.productId;
            const formData = new FormData();
            formData.append('product_id', productId);
            fetch('/cart/remove', {
                method: 'POST',
                body: new URLSearchParams(formData)
            })
            .then(r => r.json())
            .then(data => {
                if (data.status === 'ok') {
                    const row = document.querySelector(`tr[data-product-id="${productId}"]`);
                    if (row) row.remove();
                    updateCartCount();
                    location.reload();
                }
            });
        });
    });
});

function updateQuantity(input) {
    const row = input.closest('tr');
    if (!row) return;
    const productId = row.dataset.productId;
    const formData = new FormData();
    formData.append('product_id', productId);
    formData.append('quantity', input.value);

    fetch('/cart/update', {
        method: 'POST',
        body: new URLSearchParams(formData)
    })
    .then(r => r.json())
    .then(data => {
        if (data.status === 'ok') {
            updateCartCount();
            if (data.total !== undefined) {
                document.getElementById('cart-total').textContent = '$' + data.total.toFixed(2);
            }
            location.reload();
        }
    });
}

function updateCartCount() {
    fetch('/cart/count')
    .then(r => r.json())
    .then(data => {
        document.getElementById('cart-count').textContent = data.count;
    })
    .catch(() => {});
}

function showToast(message, type) {
    const toast = document.createElement('div');
    toast.className = 'toast-narmo';
    toast.innerHTML = `<i class="bi bi-check-circle-fill me-2"></i> ${message}`;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
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

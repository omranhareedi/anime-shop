document.addEventListener('DOMContentLoaded', function () {
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
    fetch('/cart/')
    .then(r => r.text())
    .then(html => {
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        const badge = doc.getElementById('cart-count');
        if (badge) {
            document.getElementById('cart-count').textContent = badge.textContent;
        }
    });
}

function showToast(message, type) {
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-bg-${type} border-0 position-fixed bottom-0 end-0 m-3`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>`;
    document.body.appendChild(toast);
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    setTimeout(() => toast.remove(), 3000);
}

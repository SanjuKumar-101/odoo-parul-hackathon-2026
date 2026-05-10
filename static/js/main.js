// Auto-dismiss alerts after 4 seconds
document.addEventListener('DOMContentLoaded', function () {
    setTimeout(() => {
        document.querySelectorAll('.alert').forEach(el => {
            let alert = bootstrap.Alert.getOrCreateInstance(el);
            alert.close();
        });
    }, 4000);

    // Confirm delete actions
    document.querySelectorAll('form[data-confirm]').forEach(form => {
        form.addEventListener('submit', function (e) {
            if (!confirm(this.dataset.confirm)) e.preventDefault();
        });
    });
});

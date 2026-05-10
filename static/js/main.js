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

    // Prevent trip end dates from being earlier than their start dates.
    document.querySelectorAll('form').forEach(form => {
        const startDate = form.querySelector('input[name="start_date"]');
        const endDate = form.querySelector('input[name="end_date"]');
        if (!startDate || !endDate) return;

        const syncEndDateMin = () => {
            endDate.min = startDate.value || '';
            if (startDate.value && endDate.value && endDate.value < startDate.value) {
                endDate.value = startDate.value;
            }
        };

        startDate.addEventListener('change', syncEndDateMin);
        syncEndDateMin();
    });

    // Presentation-only currency formatting for pages that mark values with data-money.
    const currencySelector = document.querySelector('[data-currency-selector]');
    const moneyValues = document.querySelectorAll('[data-money]');
    if (currencySelector && moneyValues.length) {
        const browserCurrency = navigator.language === 'en-IN' ? 'INR' : 'USD';
        const savedCurrency = localStorage.getItem('traveloopCurrency') || browserCurrency;
        currencySelector.value = savedCurrency;

        const applyCurrency = currency => {
            localStorage.setItem('traveloopCurrency', currency);
            const formatter = new Intl.NumberFormat(undefined, {
                style: 'currency',
                currency,
                maximumFractionDigits: 2
            });

            moneyValues.forEach(el => {
                const amount = Number(el.dataset.money);
                if (!Number.isNaN(amount)) el.textContent = formatter.format(amount);
            });
        };

        currencySelector.addEventListener('change', () => applyCurrency(currencySelector.value));
        applyCurrency(currencySelector.value);
    }
});

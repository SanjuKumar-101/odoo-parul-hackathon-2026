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

    // Currency formatting for values stored in INR. Rates are local fallback rates
    // to avoid third-party API dependency during judging/demo.
    const currencySelector = document.querySelector('[data-currency-selector]');
    const moneyValues = document.querySelectorAll('[data-money]');
    if (currencySelector && moneyValues.length) {
        const currencyRatesFromInr = {
            INR: 1,
            USD: 0.012,
            EUR: 0.011,
            GBP: 0.0095,
            JPY: 1.8,
            AUD: 0.018,
            AED: 0.044,
            THB: 0.43,
            IDR: 190,
            ZAR: 0.22
        };
        const savedCurrency = localStorage.getItem('traveloopCurrency') || 'INR';
        currencySelector.value = savedCurrency;

        const applyCurrency = currency => {
            localStorage.setItem('traveloopCurrency', currency);
            const rate = currencyRatesFromInr[currency] || 1;
            const formatter = new Intl.NumberFormat(undefined, {
                style: 'currency',
                currency,
                maximumFractionDigits: 2
            });

            moneyValues.forEach(el => {
                const amount = Number(el.dataset.money);
                if (!Number.isNaN(amount)) el.textContent = formatter.format(amount * rate);
            });
        };

        currencySelector.addEventListener('change', () => applyCurrency(currencySelector.value));
        applyCurrency(currencySelector.value);
    }
});

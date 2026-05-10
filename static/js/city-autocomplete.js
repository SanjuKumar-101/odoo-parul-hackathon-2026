/**
 * City Autocomplete — reusable for any input with data-city-autocomplete
 * Usage: <input type="text" name="destination" data-city-autocomplete>
 */
function initCityAutocomplete(inputEl, options = {}) {
    const wrapper = document.createElement('div');
    wrapper.style.position = 'relative';
    inputEl.parentNode.insertBefore(wrapper, inputEl);
    wrapper.appendChild(inputEl);

    const dropdown = document.createElement('ul');
    dropdown.className = 'list-group shadow';
    dropdown.style.cssText = 'position:absolute;top:100%;left:0;right:0;z-index:9999;max-height:220px;overflow-y:auto;display:none;';
    wrapper.appendChild(dropdown);

    // Warning element
    const warning = document.createElement('div');
    warning.className = 'alert alert-warning py-2 px-3 mt-1 small';
    warning.style.display = 'none';
    warning.innerHTML = '<i class="bi bi-exclamation-triangle me-2"></i>We haven\'t added this city yet. We\'ll add it soon — sorry for the inconvenience!';
    wrapper.appendChild(warning);

    let debounceTimer;
    let selectedFromList = false;

    inputEl.addEventListener('input', function () {
        selectedFromList = false;
        warning.style.display = 'none';
        const q = this.value.trim();
        if (q.length < 1) { dropdown.style.display = 'none'; return; }

        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            fetch(`/api/cities?q=${encodeURIComponent(q)}`)
                .then(r => r.json())
                .then(cities => {
                    dropdown.innerHTML = '';
                    if (cities.length === 0) {
                        dropdown.style.display = 'none';
                        return;
                    }
                    cities.forEach(city => {
                        const li = document.createElement('li');
                        li.className = 'list-group-item list-group-item-action d-flex justify-content-between align-items-center';
                        li.style.cursor = 'pointer';
                        li.innerHTML = `
                            <span><i class="bi bi-geo-alt me-2 text-primary"></i><strong>${city.name}</strong></span>
                            <span class="badge bg-light text-muted border">${city.country}</span>`;
                        li.addEventListener('mousedown', function (e) {
                            e.preventDefault();
                            inputEl.value = city.name;
                            selectedFromList = true;
                            warning.style.display = 'none';
                            dropdown.style.display = 'none';
                        });
                        dropdown.appendChild(li);
                    });
                    dropdown.style.display = 'block';
                });
        }, 300);
    });

    // Validate on blur — if typed manually and not in list
    inputEl.addEventListener('blur', function () {
        setTimeout(() => { dropdown.style.display = 'none'; }, 150);
        if (selectedFromList || this.value.trim() === '') return;
        fetch(`/api/cities/validate?name=${encodeURIComponent(this.value.trim())}`)
            .then(r => r.json())
            .then(data => {
                warning.style.display = data.exists ? 'none' : 'block';
            });
    });

    inputEl.addEventListener('focus', function () {
        warning.style.display = 'none';
        if (this.value.trim().length > 0) this.dispatchEvent(new Event('input'));
    });
}

// Auto-init all inputs with data-city-autocomplete attribute
document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('[data-city-autocomplete]').forEach(el => {
        initCityAutocomplete(el);
    });
});

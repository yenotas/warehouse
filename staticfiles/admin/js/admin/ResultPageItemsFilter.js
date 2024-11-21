{
    function initResultQuickFilter() {
        const options = [];
        const navResult = document.getElementById('result_list');
        if (!navResult) {
            return;
        }
        navResult.querySelectorAll('tbody tr').forEach((container) => {
            options.push({title: container.innerHTML, node: container});
        });

        function checkValue(event) {
            let filterValue = event.target.value;
            if (filterValue) {
                filterValue = filterValue.toLowerCase();
            }
            if (event.key === 'Escape') {
                filterValue = '';
                event.target.value = ''; // clear input
            }
            let matches = false;
            for (const o of options) {
                let displayValue = '';
                if (filterValue) {
                    if (o.title.toLowerCase().indexOf(filterValue) === -1) {
                        displayValue = 'none';
                    } else {
                        matches = true;
                    }
                }
                // show/hide parent <TR>
                o.node.parentNode.parentNode.style.display = displayValue;
            }
            if (!filterValue || matches) {
                event.target.classList.remove('no-results');
            } else {
                event.target.classList.add('no-results');
            }
            sessionStorage.setItem('resultFilterValue', filterValue);
        }

        const nav = document.getElementById('result_filter');
        nav.addEventListener('change', checkValue, false);
        nav.addEventListener('input', checkValue, false);
        nav.addEventListener('keyup', checkValue, false);

        const storedValue = sessionStorage.getItem('resultFilterValue');
        if (storedValue) {
            nav.value = storedValue;
            checkValue({target: nav, key: ''});
        }
    }
    window.initResultQuickFilter = initResultQuickFilter;
    initResultQuickFilter();
}
// Simple filtering for results
document.addEventListener('DOMContentLoaded', function() {
    const filterLabelled = document.getElementById('filterLabelled');
    const filterNoLabel = document.getElementById('filterNoLabel');
    const filterChange = document.getElementById('filterChange');
    const filterMultiple = document.getElementById('filterMultiple');
    
    if (!filterLabelled) return;
    
    function applyFilters() {
        const rows = document.querySelectorAll('.result-row');
        rows.forEach(row => {
            const status = row.getAttribute('data-status');
            const hasMultiple = row.getAttribute('data-multiple') === 'True';
            const hasChange = row.getAttribute('data-change') === 'True';
            
            let show = true;
            
            if (status === 'labelled' && !filterLabelled.checked) show = false;
            if (status === 'no_label_detected' && !filterNoLabel.checked) show = false;
            if (status === 'scan_error' && !filterLabelled.checked && !filterNoLabel.checked) show = false;
            
            if (hasChange && !filterChange.checked) show = false;
            if (hasMultiple && !filterMultiple.checked && !hasChange) {
                // Don't hide if it's multiple but let change filter take precedence
            }
            if (hasMultiple && !filterMultiple.checked && hasChange && filterChange.checked) {
                // Keep if change is shown
            }
            
            // Simpler logic
            let shouldShow = false;
            if (status === 'labelled' && filterLabelled.checked) shouldShow = true;
            if (status === 'no_label_detected' && filterNoLabel.checked) shouldShow = true;
            if (status === 'scan_error') shouldShow = true; // always show errors
            
            if (hasChange && filterChange.checked) shouldShow = true;
            if (hasMultiple && filterMultiple.checked && status === 'labelled') shouldShow = true;
            
            // If no filters match the specific flags, check base status
            if (!filterChange.checked && !filterMultiple.checked) {
                if (status === 'labelled' && filterLabelled.checked) shouldShow = true;
                else if (status === 'no_label_detected' && filterNoLabel.checked) shouldShow = true;
                else if (status === 'scan_error') shouldShow = true;
                else shouldShow = false;
            } else {
                // With flag filters, show if it matches any checked flag
                shouldShow = false;
                if (status === 'labelled' && filterLabelled.checked) shouldShow = true;
                if (status === 'no_label_detected' && filterNoLabel.checked) shouldShow = true;
                if (hasChange && filterChange.checked) shouldShow = true;
                if (hasMultiple && filterMultiple.checked) shouldShow = true;
                if (status === 'scan_error') shouldShow = true;
            }
            
            row.style.display = shouldShow ? '' : 'none';
            // Also hide detail row
            const detailRow = row.nextElementSibling;
            if (detailRow && detailRow.classList.contains('detail-row')) {
                detailRow.style.display = shouldShow ? '' : 'none';
            }
        });
    }
    
    [filterLabelled, filterNoLabel, filterChange, filterMultiple].forEach(f => {
        if (f) f.addEventListener('change', applyFilters);
    });
    
    applyFilters();
});

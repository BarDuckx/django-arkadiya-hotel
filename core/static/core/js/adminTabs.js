function openTab(tabId, btnElement) {
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    document.getElementById(tabId).classList.add('active');
    btnElement.classList.add('active');

    window.history.replaceState(null, null, "?tab=" + tabId);
}

window.onload = function () {
    const urlParams = new URLSearchParams(window.location.search);
    const tab = urlParams.get('tab');
    if (tab) {
        const btnToClick = document.querySelector(`button[onclick="openTab('${tab}', this)"]`);
        if (btnToClick) btnToClick.click();
    }
}
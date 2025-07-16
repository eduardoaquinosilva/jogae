document.addEventListener('DOMContentLoaded', function() {
    const sidebar = document.getElementById('friends-sidebar');
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const rootHtml = document.documentElement;

    if (sidebar && sidebarToggle) {
        
        if (rootHtml.classList.contains('sidebar-is-collapsed')) {
            sidebar.classList.add('collapsed');
            sidebarToggle.innerHTML = '&laquo;';
            sidebarToggle.title = 'Expandir Amigos';
        }

        sidebarToggle.addEventListener('click', function() {
            if (rootHtml.classList.contains('sidebar-is-collapsed')) {
                rootHtml.classList.remove('sidebar-is-collapsed');
            }
            
            sidebar.classList.toggle('collapsed');

            if (sidebar.classList.contains('collapsed')) {
                localStorage.setItem('sidebarState', 'collapsed');
                sidebarToggle.innerHTML = '&laquo;';
                sidebarToggle.title = 'Expandir Amigos';
            } else {
                localStorage.removeItem('sidebarState');
                sidebarToggle.innerHTML = '&raquo;';
                sidebarToggle.title = 'Recolher Amigos';
            }
        });
    }
});
// static/js/main.js

document.addEventListener('DOMContentLoaded', function() {
    // Lógica para a sidebar
    const sidebar = document.getElementById('friends-sidebar');
    const sidebarToggle = document.getElementById('sidebar-toggle');

    // Verifica se os elementos existem na página antes de adicionar o listener
    if (sidebar && sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            // Adiciona ou remove a classe 'collapsed' da sidebar
            sidebar.classList.toggle('collapsed');

            // Alterna o ícone do botão
            if (sidebar.classList.contains('collapsed')) {
                sidebarToggle.innerHTML = '&laquo;'; // Ícone para expandir
                sidebarToggle.title = 'Expandir Amigos';
            } else {
                sidebarToggle.innerHTML = '&raquo;'; // Ícone para recolher
                sidebarToggle.title = 'Recolher Amigos';
            }
        });
    }
});
// Small admin interactions: sidebar toggle
document.addEventListener('DOMContentLoaded', function () {
  const toggle = document.getElementById('sidebarToggle');
  const sidebar = document.querySelector('.admin-sidebar');
  const root = document.getElementById('admin-root');

  if (toggle && sidebar) {
    toggle.addEventListener('click', function () {
      sidebar.classList.toggle('collapsed');
      root.classList.toggle('sidebar-collapsed');
    });
  }
});

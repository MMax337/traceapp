
// Edit of the route
document.addEventListener('DOMContentLoaded', function() {
  const editNameBtn = document.getElementById('edit-name-btn');
  const editNameForm = document.getElementById('edit-name-form');
  const routeNameDisplay = document.getElementById('route-name-display');
  const routeNameInput = document.getElementById('route-name-input');
  const cancelEditBtn = document.getElementById('cancel-edit-btn');

  if (editNameBtn) {
    editNameBtn.addEventListener('click', function() {
      routeNameDisplay.classList.add('hidden');
      editNameBtn.classList.add('hidden');
      editNameForm.classList.remove('hidden');
      routeNameInput.focus();
      routeNameInput.select();
    });
  }

  if (cancelEditBtn) {
    cancelEditBtn.addEventListener('click', function() {
      editNameForm.classList.add('hidden');
      routeNameDisplay.classList.remove('hidden');
      editNameBtn.classList.remove('hidden');
    });
  }

});

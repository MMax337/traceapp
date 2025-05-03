// register_points_handler.js
// This script handles transferring saved route points to the registration form

document.addEventListener('DOMContentLoaded', function() {
  const form = document.querySelector('form');
  const pointsDataField = document.getElementById('points-data');

  if (form && pointsDataField) {
    // Add submit handler to populate the hidden field with routes data
    form.addEventListener('submit', function(event) {
      try {
        const routesData = localStorage.getItem('routes');

        if (routesData) {
          pointsDataField.value = routesData;
        }

      } catch (error) {
        console.error('Error retrieving points data from localStorage', error);
      }
    });
  }
});
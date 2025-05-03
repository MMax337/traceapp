function getRouteID() {
  // Extract the route ID from the URL
  const pathParts = window.location.pathname.split('/');
  const routeId = pathParts[pathParts.indexOf('routes') + 1];

  if (!routeId) {
    console.error("Cannot determine routeId from URL");
    alert("ERROR");
  }

  return routeId;
}


function setupSaveRouteButton() {
  const saveRouteBtn = document.getElementById('save-route-btn');
  if (!saveRouteBtn) return;

  saveRouteBtn.addEventListener('click', function() {
    // Extract the route ID from the URL
    const routeId = getRouteID();

    if (!routeId) {
      return;
    }

    const pointsData = points.map((point, index) => ({
      x: point.x,
      y: point.y,
      color: point.color,
      order: index
    }));

    // Przygotuj nagłówki
    const headers = {
      'Content-Type': 'application/json',
      'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
    };
    
    // Wyślij żądanie API
    fetch(`/api/routes/${routeId}/bulk-update-points/`, {
      method: 'POST',
      headers: headers,
      body: JSON.stringify({ points: pointsData })
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
    .then(data => {
      if (data.status === 'success') {
        alert('Points are successfully saved!');
      } else {
        alert('Error when saving the points.');
      }
    })
    .catch(error => {
      console.error('Error when saving points', error);
      alert('Error when saving the points.');

    });
  });
}

function setupRegisterToSaveBtn() {
  const registerToSaveBtn = document.getElementById('register-to-save-btn');
  if (!registerToSaveBtn) return;

  registerToSaveBtn.addEventListener('click', function() {
    // Extract the route ID from the URL
    const routeId = getRouteID();

    if (!routeId) {
      return;
    }

    // Prepare points data
    const pointsData = points.map((point, index) => ({
      x: point.x,
      y: point.y,
      color: point.color,
      order: index
    }));

    const storageKey = `routes`;

    try {
      // Get existing routes data or initialize new object
      let routesData = {};
      const existingData = localStorage.getItem(storageKey);

      if (existingData) {
        routesData = JSON.parse(existingData);
      }

      // Add or update this route's data
      routesData[routeId] = {
        id: routeId,
        points: pointsData,
        // lastModified: new Date().toISOString()
      };

      // Save back to localStorage
      localStorage.setItem(storageKey, JSON.stringify(routesData));

      alert('Points saved to your browser. Create an account to save them permanently!');
    } catch (error) {
      console.error('Error saving points to localStorage', error);
      alert('Error saving points to your browser. Your browser storage might be full or disabled.');
    }
  });
}

document.addEventListener('DOMContentLoaded', setupRegisterToSaveBtn);
document.addEventListener('DOMContentLoaded', setupSaveRouteButton);
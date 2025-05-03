// Function to switch between tabs
function switchTab(activeTab, inactiveTab, activeCarousel, inactiveCarousel) {
  // Update tab classes
  activeTab.classList.add('text-blue-700', 'bg-white', 'border-blue-300');
  activeTab.classList.remove('text-gray-900', 'bg-gray-50', 'border-gray-300');

  inactiveTab.classList.add('text-gray-900', 'bg-white', 'border-gray-300');
  inactiveTab.classList.remove('text-blue-700', 'bg-white', 'border-blue-300');

  // Show/hide carousels
  activeCarousel.classList.remove('hidden');
  inactiveCarousel.classList.add('hidden');
}

// Group backgrounds into sets of specified size
function groupBackgrounds(backgrounds, groupSize) {
  const groups = [];
  for (let i = 0; i < backgrounds.length; i += groupSize) {
    groups.push(backgrounds.slice(i, i + groupSize));
  }
  return groups;
}

// Create a background card element
function createBackgroundCard(background, isUserBackground = false) {
  const backgroundDiv = document.createElement('div');
  backgroundDiv.className = 'w-1/3 px-2';
  
  // Create card content with delete button for user backgrounds
  let cardContent = `
    <div class="bg-white rounded-xl shadow-md overflow-hidden transform transition hover:scale-105 hover:shadow-lg relative">
      <div class="bg-select-item cursor-pointer" data-background-id="${background.id}">
        <div class="h-40 bg-gray-200 relative overflow-hidden">
          <img src="${background.image}" alt="${background.name}" class="w-full h-full object-cover">
        </div>
        <div class="p-4">
          <h3 class="font-bold text-gray-800 mb-2">${background.name}</h3>
          <p class="text-indigo-600 inline-flex items-center">
            Click to create the route
            <svg xmlns="http://www.w3.org/2000/svg" class="ml-1 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
            </svg>
          </p>
        </div>
      </div>`;
  
  // Add delete button for user backgrounds
  if (isUserBackground) {
    cardContent += `
      <button class="delete-background absolute bottom-4 right-4 px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700 transition" 
              data-background-id="${background.id}">
        Delete
      </button>`;
  }
  
  // Close the container
  cardContent += `
    </div>`;
  
  backgroundDiv.innerHTML = cardContent;
  return backgroundDiv;
}

// Generate carousel HTML
function generateCarousel(backgroundGroups, container, isUserBackground = false) {
  // Clear existing content
  container.innerHTML = '';
  
  if (backgroundGroups.length === 0) {
    container.innerHTML = '<div class="w-full text-center py-8 text-gray-500">Brak dostępnych obrazów tła.</div>';
    return;
  }
  
  // Generate HTML for each group
  backgroundGroups.forEach(group => {
    const groupDiv = document.createElement('div');
    groupDiv.className = 'snap-start flex-shrink-0 w-full flex gap-4';

    // Generate HTML for each background in the group
    group.forEach(background => {
      groupDiv.appendChild(createBackgroundCard(background, isUserBackground));
    });

    // Add empty placeholder divs if the group isn't full
    const missingItems = 3 - group.length;
    for (let i = 0; i < missingItems; i++) {
      const emptyDiv = document.createElement('div');
      emptyDiv.className = 'w-1/3 px-2';
      groupDiv.appendChild(emptyDiv);
    }

    container.appendChild(groupDiv);
  });
}

// Add click event listeners for backgrounds
function setupBackgroundClickListeners(bgField, routeForm) {
  document.addEventListener('click', function(event) {
    const bgItem = event.target.closest('.bg-select-item');
    if (bgItem && bgField && routeForm) {
      const bgId = bgItem.getAttribute('data-background-id');
      if (bgId) {
        bgField.value = bgId;

        // Set default route name if field exists
        const routeNameField = document.getElementById('routeName');
        if (routeNameField) {
          routeNameField.value = "New route";
        }

        routeForm.submit();
      }
    }
  });
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
  const userBgTab = document.getElementById('userBgTab');
  const generalBgTab = document.getElementById('generalBgTab');
  const userBackgroundsCarousel = document.getElementById('userBackgroundsCarousel');
  const generalBackgroundsCarousel = document.getElementById('generalBackgroundsCarousel');
  const routeForm = document.getElementById('routeForm');
  const bgField = document.querySelector('#id_background');
 
  // Initialize tabs if they exist
  if (userBgTab && generalBgTab) {
    userBgTab.addEventListener('click', function() {
      switchTab(userBgTab, generalBgTab, userBackgroundsCarousel, generalBackgroundsCarousel);
    });

    generalBgTab.addEventListener('click', function() {
      switchTab(generalBgTab, userBgTab, generalBackgroundsCarousel, userBackgroundsCarousel);
    });
  }

  // Initialize carousels
  const userBackgroundGroups = groupBackgrounds(userBackgrounds, 3);
  const generalBackgroundGroups = groupBackgrounds(generalBackgrounds, 3);

  if (userBackgroundsCarousel) {
    generateCarousel(userBackgroundGroups, userBackgroundsCarousel, true); // true indicates user backgrounds
  }

  if (generalBackgroundsCarousel) {
    generateCarousel(generalBackgroundGroups, generalBackgroundsCarousel, false);
  }

  // Set up background click listeners
  setupBackgroundClickListeners(bgField, routeForm);
  
  // Add click event for delete buttons
  document.addEventListener('click', function(event) {
    // Find the delete button element that was clicked
    const deleteBtn = event.target.closest('.delete-background');
    
    if (deleteBtn) {
      event.preventDefault();
      event.stopPropagation(); // Prevent clicking on the background item
      
      const bgId = deleteBtn.getAttribute('data-background-id');
      
      if (confirm('Are you sure you want to delete this background?')) {
        // Submit the delete form
        const deleteForm = document.getElementById('deleteBackgroundForm');
        const bgIdField = document.getElementById('deleteBackgroundId');
        
        if (deleteForm && bgIdField) {
          bgIdField.value = bgId;
          deleteForm.submit();
        }
      }
    }
  });
});
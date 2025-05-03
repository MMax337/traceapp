// route_editor_points.js - Point management functionality

// Constants and global variables
const MAX_POINTS = 18;
const points = [];
let container;
let pointsList;
let activeDeleteButton = null;
let deleteButtonTimeout = null;

// Initialize the points module
function initPoints() {
  container = document.getElementById('background-image-container');
  pointsList = document.getElementById('points-list');
}

// Handler for image click
function handleImageClick(event) {
  const rect = event.target.getBoundingClientRect();
  const x = event.clientX - rect.left;
  const y = event.clientY - rect.top;
  const color = getSelectedColor(); // This function is defined in route_editor_colors.js

  addPoint({ x, y, color });
}

// Add a point to the route
function addPoint({ x, y, color, backend = false }) {
  if (!backend && points.length >= MAX_POINTS) {
    alert(`Maximum ${MAX_POINTS} points allowed.`);
    return;
  }

  // Ensure container is defined
  if (!container) {
    container = document.getElementById('background-image-container');
  }
  
  if (!pointsList) {
    pointsList = document.getElementById('points-list');
  }

  // Create point dot
  const dot = document.createElement('div');
  dot.className = 'absolute rounded-full transition-colors z-20 cursor-pointer point';
  dot.style.width = '10px';
  dot.style.height = '10px';
  dot.style.backgroundColor = color;
  dot.style.left = `${x}px`;
  dot.style.top = `${y}px`;
  dot.style.transform = 'translate(-50%, -50%)';
  dot.setAttribute('data-x', x);
  dot.setAttribute('data-y', y);
  dot.setAttribute('data-color', color);
  container.appendChild(dot);

  // Create delete button 
  const deleteBtn = createDeleteButton(x, y);
  container.appendChild(deleteBtn);

  // Add hover behavior
  addPointHoverBehavior(dot, deleteBtn);

  // Create sidebar entry
  const li = createSidebarEntry(x, y, color, dot);
  pointsList.appendChild(li);

  // Store point data
  points.push({ x, y, color, dot, li, deleteBtn });

  // Draw lines between points
  drawLines();
}

// Delete a point
function deletePoint(dotElement) {
  const idx = points.findIndex(p => p.dot === dotElement);
  if (idx === -1) return;

  const point = points[idx];
  point.dot.remove();
  point.li.remove();
  point.deleteBtn.remove();
  points.splice(idx, 1);

  // Hide active delete button if this was it
  if (activeDeleteButton === point.deleteBtn) {
    activeDeleteButton = null;
  }

  drawLines();
}

// Get all points data (for saving to backend)
function getPointsData() {
  return points.map((point, index) => ({
    x: point.x,
    y: point.y,
    color: point.color,
    order: index
  }));
}

// Create delete button element
function createDeleteButton(x, y) {
  const deleteBtn = document.createElement('button');
  deleteBtn.textContent = 'Delete';
  deleteBtn.className = 'absolute hidden bg-red-600 text-white font-bold text-xs px-2 py-1 rounded z-30';
  deleteBtn.style.left = `${x}px`;
  deleteBtn.style.top = `${y-20}px`;
  deleteBtn.style.transform = 'translate(-50%, -50%)';
  
  return deleteBtn;
}

// Add hover behavior to point and delete button
function addPointHoverBehavior(dot, deleteBtn) {
  dot.addEventListener('mouseenter', () => {
    // Hide any previously active delete button
    if (activeDeleteButton && activeDeleteButton !== deleteBtn) {
      activeDeleteButton.classList.add('hidden');
    }
    
    // Clear any running timeout
    if (deleteButtonTimeout) {
      clearTimeout(deleteButtonTimeout);
      deleteButtonTimeout = null;
    }
    
    // Show this delete button
    deleteBtn.classList.remove('hidden');
    activeDeleteButton = deleteBtn;
  });

  dot.addEventListener('mouseleave', () => {
    // Set timeout to hide this delete button
    if (deleteButtonTimeout) {
      clearTimeout(deleteButtonTimeout);
    }
    
    deleteButtonTimeout = setTimeout(() => {
      if (activeDeleteButton === deleteBtn) {
        deleteBtn.classList.add('hidden');
        activeDeleteButton = null;
      }
      deleteButtonTimeout = null;
    }, 500);
  });

  // Prevent the delete button from hiding when hovering over it
  deleteBtn.addEventListener('mouseenter', () => {
    if (deleteButtonTimeout) {
      clearTimeout(deleteButtonTimeout);
      deleteButtonTimeout = null;
    }
  });
  
  // Hide after leaving the delete button
  deleteBtn.addEventListener('mouseleave', () => {
    if (deleteButtonTimeout) {
      clearTimeout(deleteButtonTimeout);
    }
    
    deleteButtonTimeout = setTimeout(() => {
      deleteBtn.classList.add('hidden');
      if (activeDeleteButton === deleteBtn) {
        activeDeleteButton = null;
      }
      deleteButtonTimeout = null;
    }, 500);
  });

  deleteBtn.addEventListener('click', () => {
    deletePoint(dot);
  });
}

// Create sidebar entry for a point
function createSidebarEntry(x, y, color, dot) {
  const li = document.createElement('li');
  li.className = 'group flex items-center justify-between px-2 py-1 rounded hover:bg-gray-200 relative';

  const label = document.createElement('span');
  label.className = 'whitespace-nowrap';
  label.textContent = `(${Math.round(x)}, ${Math.round(y)})`;

  // Color picker for each point in the sidebar
  const colorInput = document.createElement('input');
  colorInput.type = 'color';
  colorInput.value = color;
  colorInput.className = 'w-6 h-6 cursor-pointer opacity-0 group-hover:opacity-100 transition-opacity';
  colorInput.addEventListener('input', (e) => {
    const newColor = e.target.value;
    dot.style.backgroundColor = newColor;
    dot.setAttribute('data-color', newColor);
    
    // Update color in our data structure
    const pointData = points.find(p => p.dot === dot);
    if (pointData) {
      pointData.color = newColor;
    }
    
    drawLines(); // Redraw lines with updated colors
  });

  const deleteSideBtn = document.createElement('button');
  deleteSideBtn.textContent = '✖';
  deleteSideBtn.className = 'text-red-600 opacity-0 group-hover:opacity-100 transition-opacity duration-200 text-xs';
  deleteSideBtn.addEventListener('click', () => {
    deletePoint(dot);
  });

  li.appendChild(label);
  li.appendChild(colorInput);
  li.appendChild(deleteSideBtn);

  let removeBlink;
  li.addEventListener('mouseenter', () => {
    removeBlink = makeBlink(dot);
  });
  li.addEventListener('mouseleave', () => {
    if (removeBlink) removeBlink();
  });
  
  return li;
}

// Make a point blink (highlight) when hovering over its sidebar entry
const makeBlink = (el) => {
  el.classList.add('point-highlight');
  return () => el.classList.remove('point-highlight');
};

// Draw lines between points
function drawLines() {
  // Clear old lines
  document.querySelectorAll('.line-segment').forEach(el => el.remove());

  for (let i = 1; i < points.length; i++) {
    const p1 = points[i - 1];
    const p2 = points[i];

    const dx = p2.x - p1.x;
    const dy = p2.y - p1.y;
    const length = Math.sqrt(dx * dx + dy * dy);
    const angle = Math.atan2(dy, dx) * (180 / Math.PI);

    const line = document.createElement('div');
    line.className = 'absolute h-[2px] line-segment z-10'; // Points are z-20
    line.style.width = `${length}px`;
    line.style.left = `${p1.x}px`;
    line.style.top = `${p1.y}px`;
    line.style.backgroundColor = p1.color; // Use first point's color
    line.style.transformOrigin = '0 0';
    line.style.transform = `rotate(${angle}deg)`;

    container.appendChild(line);
  }
}

document.addEventListener('DOMContentLoaded', function() {
  initPoints();

  // Set up image click handler
  const image = document.getElementById('background-image');
  if (image) {
    image.addEventListener('click', handleImageClick);
  }
});

// Make functions available globally
window.addPoint = addPoint;
window.deletePoint = deletePoint;
window.getPointsData = getPointsData;
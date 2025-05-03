// route_editor_colors.js - Color selection functionality

let selectedColor = '#ef4444'; // Default red color
let colorPicker;

function initColorPickers() {
  // Get color picker element
  colorPicker = document.getElementById('color-picker');

  // Handle custom color picker change
  if (colorPicker) {
    colorPicker.addEventListener('change', (e) => {
      setColor(e.target.value);
    });
  }

  // Handle color button clicks
  const colorButtons = document.querySelectorAll('.color-select');
  colorButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const color = btn.dataset.color;
      setColor(color);

      // Visually mark the selected color button
      colorButtons.forEach(b => b.classList.remove('ring-2', 'ring-offset-2', 'ring-indigo-500'));
      btn.classList.add('ring-2', 'ring-offset-2', 'ring-indigo-500');
    });
  });

  // Select the default color button
  if (colorButtons.length > 0) {
    colorButtons[0].click();
  }
}

// Set the current color
function setColor(color) {
  selectedColor = color;
  if (colorPicker) {
    colorPicker.value = color;
  }
}

// Get the currently selected color
function getSelectedColor() {
  return selectedColor;
}

document.addEventListener('DOMContentLoaded', initColorPickers)

window.initColorPickers = initColorPickers;
window.setColor = setColor;
window.getSelectedColor = getSelectedColor;
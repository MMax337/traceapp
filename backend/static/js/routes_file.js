document.addEventListener('DOMContentLoaded', function() {
  const fileInput = document.getElementById('backgroundInput');
  const chooseFileBtn = document.getElementById('chooseFileBtn');
  const fileNameSpan = document.getElementById('fileName');

  if (chooseFileBtn) {
      chooseFileBtn.addEventListener('click', function () {
          fileInput.click();
      });
  }

  if (fileInput) {
      fileInput.addEventListener('change', function () {
          if (fileInput.files.length > 0) {
              fileNameSpan.textContent = fileInput.files[0].name;
          } else {
              fileNameSpan.textContent = '';
          }
      });
  }
});
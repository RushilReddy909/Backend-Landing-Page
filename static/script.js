document.addEventListener("DOMContentLoaded", function () {
  function handleToggle(event) {
    const switchId = event.target.id;
    const field = switchId.replace("switch-", "");

    if (event.target.checked) {
      //Show Modal
      const modalHTML = `
          <div class="modal fade" id="valueModal" tabindex="-1" aria-labelledby="valueModalLabel" aria-hidden="true">
              <div class="modal-dialog">
                  <div class="modal-content">
                      <div class="modal-header">
                          <h5 class="modal-title" id="valueModalLabel">Enter ${field} Value</h5>
                          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                      </div>
                      <div class="modal-body">
                          <label for="fieldValue" class="form-label">New ${field} Value:</label>
                          <input type="text" id="fieldValue" class="form-control" placeholder="Enter your ${field}" />
                      </div>
                      <div class="modal-footer">
                          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                          <button type="button" class="btn btn-primary" id="saveFieldValue">Save</button>
                      </div>
                  </div>
              </div>
          </div>
      `;

      // Append modal to body
      document.body.insertAdjacentHTML("beforeend", modalHTML);

      // Initialize modal
      const valueModal = new bootstrap.Modal(
        document.getElementById("valueModal")
      );
      valueModal.show();

      // Add event listener to the "Save" button
      document
        .getElementById("saveFieldValue")
        .addEventListener("click", () => {
          const fieldValue = document.getElementById("fieldValue").value;

          if (!fieldValue) {
            alert("Please enter a value for the field.");
            return;
          }

          // Make the POST request to update the field
          fetch("/update_perm", {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: new URLSearchParams({
              field,
              action: "grant",
              value: fieldValue,
            }),
          })
            .then((response) => response.json())
            .then((data) => {
              if (data.success) {
                valueModal.hide();
                document.getElementById("valueModal").remove(); // Remove modal from DOM
                showToast("Field updated successfully.", "success");
              } else {
                showToast(
                  `Failed to update permission: ${data.message}`,
                  "danger"
                );
              }
            })
            .catch((error) => {
              showToast(`Error: ${error.message}`, "danger");
            });
        });

      // Remove the modal from DOM after it is hidden
      document
        .getElementById("valueModal")
        .addEventListener("hidden.bs.modal", () => {
          document.getElementById("valueModal").remove();
        });
    } else {
      fetch("/update_perm", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({ field: field, action: "revoke" }),
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            showToast("Permission revoked successfully.", "success");
          } else {
            showToast(`Failed to revoke permission: ${data.message}`, "danger");
          }
        })
        .catch((error) => {
          showToast(`Error: ${error.message}`, "danger");
        });
    }
  }

  function showToast(message, type = "info") {
    const toastContainer = document.getElementById("toast-container");

    // Create a unique ID for the toast
    const toastId = `toast-${Date.now()}`;

    // Toast HTML template
    const toastHTML = `
              <div id="${toastId}" class="toast align-items-center text-bg-${type} border-0 mb-2" role="alert" aria-live="assertive" aria-atomic="true">
              <div class="d-flex">
                  <div class="toast-body">
                  ${message}
                  </div>
                  <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
              </div>
              </div>
          `;

    // Append the toast to the container
    toastContainer.insertAdjacentHTML("beforeend", toastHTML);

    // Initialize and show the toast using Bootstrap's JavaScript API
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, { delay: 5000 }); // Auto-hide after 5 seconds
    toast.show();

    // Remove the toast from DOM after it hides
    toastElement.addEventListener("hidden.bs.toast", () => {
      toastElement.remove();
    });
  }

  const switches = document.querySelectorAll(".form-check-input");
  switches.forEach((switchElem) => {
    switchElem.addEventListener("change", handleToggle);
  });
});

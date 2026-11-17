/**
 * ==========================================================
 * Error Modal
 * ==========================================================
 */

const errorModal = {
    overlay: document.getElementById("error-modal"),
    title: document.getElementById("error-title"),
    message: document.getElementById("error-message"),
    closeButton: document.getElementById("error-close"),
};


function showErrorModal(
    modalTitle,
    modalMessage
) {

    errorModal.title.textContent = modalTitle;

    errorModal.message.textContent = modalMessage;

    errorModal.overlay.classList.add("active");

}


function hideErrorModal() {

    errorModal.overlay.classList.remove("active");

}


errorModal.closeButton.addEventListener(
    "click",
    hideErrorModal
);

errorModal.overlay.addEventListener(
    "click",
    (event) => {

        if (event.target === errorModal.overlay) {

            hideErrorModal();

        }

    }
);

document.addEventListener(
    "keydown",
    (event) => {

        if (
            event.key === "Escape" &&
            errorModal.overlay.classList.contains("active")
        ) {

            hideErrorModal();

        }

    }
);
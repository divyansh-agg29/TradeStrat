/**
 * ==========================================================
 * Error Modal
 * ==========================================================
 */

const modal =
    document.getElementById("error-modal");

const title =
    document.getElementById("error-title");

const message =
    document.getElementById("error-message");

const closeButton =
    document.getElementById("error-close");


function showErrorModal(
    modalTitle,
    modalMessage
) {

    title.textContent = modalTitle;

    message.textContent = modalMessage;

    modal.classList.add("active");

}


function hideErrorModal() {

    modal.classList.remove("active");

}


closeButton.addEventListener(
    "click",
    hideErrorModal
);

modal.addEventListener(
    "click",
    (event) => {

        if (event.target === modal) {

            hideErrorModal();

        }

    }
);

document.addEventListener(
    "keydown",
    (event) => {

        if (
            event.key === "Escape" &&
            modal.classList.contains("active")
        ) {

            hideErrorModal();

        }

    }
);
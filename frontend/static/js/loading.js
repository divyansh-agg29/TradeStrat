/**
 * ==========================================================
 * Loading Overlay
 * ==========================================================
 */

/**
 * Show the loading overlay.
 */
function showLoadingOverlay() {

    document
        .getElementById("loading-overlay")
        .classList.add("active");

}

/**
 * Hide the loading overlay.
 */
function hideLoadingOverlay() {

    document
        .getElementById("loading-overlay")
        .classList.remove("active");

}
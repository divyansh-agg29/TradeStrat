/**
 * Landing page interactions.
 *
 * - Sticky navigation with background on scroll
 * - Scroll-based fade-in animations (Intersection Observer)
 * - Smooth scroll for anchor links
 */

(function () {

    // ========== Sticky Navigation ==========

    const nav = document.getElementById("landing-nav");

    function handleNavScroll() {
        if (window.scrollY > 40) {
            nav.classList.add("scrolled");
        } else {
            nav.classList.remove("scrolled");
        }
    }

    window.addEventListener("scroll", handleNavScroll, { passive: true });
    handleNavScroll();


    // ========== Smooth Scroll for Anchor Links ==========

    document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
        anchor.addEventListener("click", function (e) {
            var targetId = this.getAttribute("href");
            if (targetId === "#") return;

            var target = document.querySelector(targetId);
            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: "smooth", block: "start" });
            }
        });
    });

})();

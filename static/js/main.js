// static/js/main.js (Source file for esbuild)

// --- Alpine.js Core and Plugins ---
import Alpine from 'alpinejs';
import focus from '@alpinejs/focus';
import intersect from '@alpinejs/intersect';

Alpine.plugin(focus);
Alpine.plugin(intersect);
window.Alpine = Alpine;
Alpine.start();
console.log("Alpine.js initialized with focus and intersect plugins.");

// --- Page Preloader ---
window.addEventListener('load', function() {
    const loader = document.getElementById('page-loader');
    if (loader) {
        setTimeout(() => {
            loader.classList.add('opacity-0');
            setTimeout(() => {
                if (loader.parentNode) {
                    loader.style.display = 'none';
                }
            }, 500);
        }, 250);
    }
});

// --- Macy.js Masonry Layout Initialization ---
document.addEventListener('DOMContentLoaded', function () {
    const galleryElement = document.getElementById('masonry-gallery');

    if (typeof Macy !== 'undefined' && galleryElement) {
        const imageItems = galleryElement.querySelectorAll('div.group');

        if (imageItems.length > 0) {
            galleryElement.style.opacity = '0';
            console.log("Macy.js: Initializing on #masonry-gallery with", imageItems.length, "items.");

            const macyInstance = Macy({
                container: '#masonry-gallery',
                trueOrder: false,
                waitForImages: true,
                margin: { x: 24, y: 24 },
                columns: 1,
                breakAt: {
                    768: 2,
                }
            });

            // Use runOnImageLoad to ensure actions happen after images are ready
            macyInstance.runOnImageLoad(function(){
                galleryElement.style.opacity = '1';
                console.log("Macy.js: runOnImageLoad complete, gallery faded in and recalculated.");
                // It's good practice to recalculate once all images are loaded
                macyInstance.recalculate(true, true);
            }, true);

        } else {
            galleryElement.style.opacity = '1';
            console.log("Macy.js: Gallery container #masonry-gallery found, but no image items.");
        }
    } else if (galleryElement && typeof Macy === 'undefined') {
        console.error("Macy.js: Gallery container #masonry-gallery found, but Macy library is not loaded.");
        if(galleryElement) galleryElement.style.opacity = '1';
    } else if (galleryElement) { // Gallery element exists but no children or Macy not loaded
        galleryElement.style.opacity = '1';
    }
});

console.log("main.js (source) processing complete. Alpine started. Macy.js setup attempted if applicable.");
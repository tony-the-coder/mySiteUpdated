// static/js/admin_image_preview.js

document.addEventListener('DOMContentLoaded', function() {
    console.log("Admin image preview script executing..."); // Check if script runs

    document.body.addEventListener('change', function(event) {
        // Check if the changed element is one of our inline image inputs
        if (event.target.type === 'file' && event.target.name && event.target.name.startsWith('images-') && event.target.name.endsWith('-image')) {

            const fileInput = event.target;
            const file = fileInput.files[0];

            // Find the parent table row (tr) for this inline item
            // Using closest('tr') should work for TabularInline
            const inlineRow = fileInput.closest('tr'); // Changed selector target

            if (!inlineRow) {
                console.error("Could not find parent table row (tr) for preview.");
                return;
            }

            // Find the preview container TD within this row using its class
            // **** CORRECTED SELECTOR ****
            const previewTd = inlineRow.querySelector('.field-image_preview');

            if (!previewTd) {
                console.error("Could not find preview TD (.field-image_preview) within the row.");
                return;
            }

            // Find or create the preview image tag inside the TD
            let previewImg = previewTd.querySelector('img'); // Look for existing img

            if (file && file.type.startsWith('image/')) {
                const reader = new FileReader();

                reader.onload = function(e) {
                    // If preview img tag doesn't exist, create it
                    if (!previewImg) {
                        previewImg = document.createElement('img');
                        previewImg.style.maxWidth = '150px'; // Apply styling
                        previewImg.style.maxHeight = '150px';
                        previewImg.style.display = 'none'; // Start hidden until src is set
                        previewTd.innerHTML = ''; // Clear the "(No image)" text or old img
                        previewTd.appendChild(previewImg); // Add the new img tag
                    }
                    // Update the src and ensure it's visible
                    previewImg.src = e.target.result;
                    previewImg.style.display = 'block';
                    console.log("Preview updated for:", fileInput.name);
                }
                reader.readAsDataURL(file);

            } else {
                // If no file selected, or not an image, clear the preview
                if (previewImg) {
                    // If an img tag exists, hide it and clear src
                    previewImg.src = '';
                    previewImg.style.display = 'none';
                }
                 // Optionally restore "(No image)" text if needed, careful not to overwrite saved image previews from python
                 // Check if there's an actual image associated server-side before adding "(No image)"
                 if (!previewTd.querySelector('img[src^="/media/"]') && !previewTd.querySelector('a[href^="/media/"]')) {
                       // Only add "(No image)" if there isn't already a saved preview link/img
                       // This part might need refinement based on exact HTML for saved images
                       // For simplicity now, we'll just hide the preview img if file is invalid/cleared
                 }
                 console.log("Preview cleared or file not an image for:", fileInput.name);
            }
        }
    });

    console.log("Admin image preview event listener attached.");
});
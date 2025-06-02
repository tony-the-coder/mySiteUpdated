// static/js/staff_image_preview.js

document.addEventListener('DOMContentLoaded', function() {
    console.log("Staff image preview script executing...");

    // Target the container that holds all the inline forms
    const formsetContainer = document.querySelector('.inline-formset');

    if (formsetContainer) {
        // Use event delegation for file input changes
        formsetContainer.addEventListener('change', function(event) {
            // Check if it's the image file input within our formset structure
            if (event.target.type === 'file' && event.target.name && event.target.name.startsWith('images-') && event.target.name.endsWith('-image')) {

                const fileInput = event.target;
                const file = fileInput.files[0];

                // Find the parent div for this specific inline form (class 'inline-related')
                const inlineFormDiv = fileInput.closest('.inline-related');
                if (!inlineFormDiv) {
                    console.error("Could not find parent inline form div (.inline-related)");
                    return;
                }

                // Find the designated preview container within this form (class 'image-preview-container')
                const previewContainer = inlineFormDiv.querySelector('.image-preview-container');
                if (!previewContainer) {
                    console.error("Could not find preview container (.image-preview-container)");
                    return;
                }

                // Find or create the actual img element for the preview
                let previewImg = previewContainer.querySelector('img.staff-image-preview'); // Use specific class

                if (file && file.type.startsWith('image/')) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        if (!previewImg) {
                            // Create img tag if it doesn't exist
                            previewImg = document.createElement('img');
                            previewImg.style.maxWidth = '150px';
                            previewImg.style.maxHeight = '150px';
                            previewImg.style.marginTop = '0.25rem';
                            previewImg.classList.add('staff-image-preview', 'rounded', 'border', 'border-gray-300', 'dark:border-gray-600');
                            previewContainer.innerHTML = ''; // Clear placeholder
                            previewContainer.appendChild(previewImg);
                        }
                        previewImg.src = e.target.result;
                        previewImg.style.display = 'block';
                        console.log("Staff preview updated for:", fileInput.name);
                    }
                    reader.readAsDataURL(file);

                } else {
                    // Clear preview if no file or not an image
                    if (previewImg) {
                        previewImg.src = '';
                        previewImg.style.display = 'none';
                    }
                     const existingSavedPreviewHTML = previewContainer.getAttribute('data-original-preview'); // Check if we stored original
                     if (existingSavedPreviewHTML) {
                         previewContainer.innerHTML = existingSavedPreviewHTML; // Restore original
                     } else if (!previewContainer.querySelector('img[src^="/media/"]') && previewContainer.innerText.indexOf('saved') < 0 ) {
                         // Only add placeholder if no saved image and not already showing placeholder
                         previewContainer.innerHTML = '<span class="text-xs text-gray-500 italic">(Select image file)</span>';
                     }
                    console.log("Staff preview cleared or file not an image for:", fileInput.name);
                }
            }
        });

        // Store original preview HTML for saved images (optional enhancement)
         formsetContainer.querySelectorAll('.inline-related .image-preview-container').forEach(container => {
            if (container.querySelector('img[src^="/media/"]')) {
                container.setAttribute('data-original-preview', container.innerHTML);
            }
         });

        console.log("Staff image preview event listener attached to formset.");
    } else {
         console.log("Inline formset container (.inline-formset) not found for preview script.");
    }
});
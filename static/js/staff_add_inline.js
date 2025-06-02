// static/js/staff_add_inline.js

document.addEventListener('DOMContentLoaded', function() {
    const addButton = document.getElementById('add-image-form-button');
    const formsetContainer = document.getElementById('image-formset-container');
    const emptyFormTemplate = document.getElementById('empty-image-form');
    const totalFormsInput = document.querySelector('input[name="images-TOTAL_FORMS"]'); // Input name is prefix-TOTAL_FORMS

    if (!addButton || !formsetContainer || !emptyFormTemplate || !totalFormsInput) {
        console.warn("Add inline form elements not found. Dynamic adding disabled.");
        return;
    }

    // Get the raw HTML template for one empty form
    // We need the content *inside* the hidden div's inner div
    const emptyFormHtml = emptyFormTemplate.querySelector('.inline-related').outerHTML;

    addButton.addEventListener('click', function() {
        if (!totalFormsInput || !emptyFormHtml) return;

        // Get the current number of forms (this is the index for the new form)
        let formIdx = parseInt(totalFormsInput.value, 10);

        // Create new form HTML, replacing '__prefix__' with the new index
        let newFormHtml = emptyFormHtml.replace(/__prefix__/g, formIdx);

        // Create a temporary div to append the new form HTML
        // This makes it easier to insert into the container
        let tempDiv = document.createElement('div');
        tempDiv.innerHTML = newFormHtml;
        let newFormElement = tempDiv.firstElementChild; // Get the actual .inline-related div

        // Append the new form to the container
        formsetContainer.appendChild(newFormElement);

        // Increment the total forms count in the management form
        totalFormsInput.value = formIdx + 1;

        console.log("Added new image form, index:", formIdx);
    });

     console.log("Add inline form script initialized.");
});
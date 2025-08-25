js = """
() => {
    // Create a single, powerful observer to watch for all element changes.
    const observer = new MutationObserver(() => {
        
        // --- 1. Handle the 'Edit Code' button ---
        const ed_btn = document.querySelector('.ed_btn');
        const ed_group = document.querySelector('.ed');
        // Check if the button exists AND we haven't already attached the event
        if (ed_btn && ed_group && !ed_btn.dataset.bound) {
            console.log("Found 'Edit Code' button, attaching event.");
            ed_btn.addEventListener('click', function () {
                // Toggle visibility instead of just setting to 'block'
                ed_group.style.display = ed_group.style.display === 'none' ? 'block' : 'none';
            });
            ed_btn.dataset.bound = 'true'; // Mark as done
        }

        // --- 2. Handle the 'DataFrame' button ---
        const df_btn = document.querySelector('.df_btn');
        const df_group = document.querySelector('.df');
        // Check if the button exists AND we haven't already attached the event
        if (df_btn && df_group && !df_btn.dataset.bound) {
            console.log("Found 'DataFrame' button, attaching event.");
            df_btn.addEventListener('click', function () {
                // Toggle visibility
                df_group.style.display = df_group.style.display === 'none' ? 'block' : 'none';
            });
            df_btn.dataset.bound = 'true'; // Mark as done
        }

        // --- 3. Handle all dynamically added 'suggestion-btn' buttons ---
        const suggestion_buttons = document.querySelectorAll('.suggestion-btn');
        const textarea = document.querySelector('#chatbot_input textarea');
        if (suggestion_buttons.length > 0 && textarea) {
            suggestion_buttons.forEach((btn) => {
                // Check if this specific button needs an event attached
                if (!btn.dataset.bound) {
                    btn.addEventListener('click', () => {
                        textarea.value = btn.textContent;
                        // This dispatch is crucial for Gradio to recognize the change
                        textarea.dispatchEvent(new Event("input", { bubbles: true }));
                    });
                    btn.dataset.bound = "true"; // Mark this specific button as done
                }
            });
        }
    });

    // Start observing the entire document for changes to its structure.
    observer.observe(document.body, {
        childList: true, // Watch for added/removed nodes
        subtree: true,   // Watch all descendants
    });
}
"""
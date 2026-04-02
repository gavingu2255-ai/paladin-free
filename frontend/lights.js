export function updateLights(arr) {
    // We iterate up to 7, matching your HTML structure
    for (let i = 0; i < 7; i++) {
        const el = document.getElementById(`light-${i + 1}`);
        
        if (el) {
            // If the array value is 1, add the 'active' class
            // If it's 0 (or anything else), remove it
            if (arr[i] === 1) {
                el.classList.add("active");
            } else {
                el.classList.remove("active");
            }
        }
    }
}
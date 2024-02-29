// Function to handle input in the search bar
function handleSearchInput(event) {
    const query = event.target.value.trim(); // Trim to remove leading/trailing spaces
    console.log("Search query:", query);
}

// Event listener for input changes in the search bar
document.getElementById('search-bar').addEventListener('input', handleSearchInput);

// Function to fetch search results based on user input
function fetchSearchResults(query) {
    // Example using Fetch API
    fetch('/search', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: query }),
    })
    .then(response => response.json())
    .then(data => {
        // Call function to update search results on the webpage
        updateSearchResults(data.results);
    })
    .catch(error => {
        console.error('Error fetching search results:', error);
    });
}

// Function to update search results on the webpage
function updateSearchResults(results) {
    const searchResultsContainer = document.getElementById('search-results');

    // Clear previous search results
    searchResultsContainer.innerHTML = '';

    // Iterate over the results and create HTML elements to display them
    results.forEach(result => {
        const resultElement = document.createElement('div');
        resultElement.textContent = result.name; // Assuming 'name' is a property of each search result
        searchResultsContainer.appendChild(resultElement);
    });
}

// Event listener for input changes in the search bar
document.getElementById('search-bar').addEventListener('input', function(event) {
    const query = event.target.value.trim(); // Trim to remove leading/trailing spaces
    if (query !== '') {
        fetchSearchResults(query);
    } else {
        // Clear search results if the search bar is empty
        document.getElementById('search-results').innerHTML = '';
    }
});

function fetchSearchResults(query) {
    fetch('/search', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: query }),
    })
    .then(response => response.json())
    .then(data => {
        // Handle the search results
        console.log("Search results:", data.results);
    })
    .catch(error => {
        console.error('Error fetching search results:', error);
    });
}

document.getElementById('search-bar').addEventListener('input', function(event) {
    const query = event.target.value.trim();
    if (query !== '') {
        fetchSearchResults(query);
    } else {
        console.log("Search query is empty.");
    }
});

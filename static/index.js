function fetchSearchResults(query) {
    return fetch('/search', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: query }),
    })
    .then(response => response.json())
    .catch(error => {
        console.error('Error fetching search results:', error);
    });
}

function debounce(func, delay) {
    let timeoutId;
    return function() {
        const context = this;
        const args = arguments;
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func.apply(context, args), delay);
    };
}

function showResults(query) {
    const resultsContainer = document.getElementById('searchResults');
    resultsContainer.innerHTML = '';

    if (query.trim() === '') {
        document.querySelector('.search-box').style.borderRadius = '20px';
        return;
    }

    fetchSearchResults(query)
    .then(data => {
        data.results.forEach(result => {
            const li = document.createElement('li');
            li.textContent = result;
            li.classList.add('search-result-item');
            li.addEventListener('click', () => {
                // Redirect to a page
                window.location.href = '/playerInfo/' + result; // Assuming the result is part of the URL
            });
            resultsContainer.appendChild(li);
        });
        if (data.results.length === 0) {
            document.querySelector('.search-box').style.borderRadius = '20px'; // Set border-radius to default
        } else {
            document.querySelector('.search-box').style.borderRadius = '20px 20px 0 0'; // Set border-radius to top only
        }
    }) .catch(error => {
        console.error('Error displaying search results:', error);
    });
}
const debouncedShowResults = debounce(showResults, 300);

document.getElementById('search-bar').addEventListener('input', function(event) {
    debouncedShowResults(event.target.value);
});



function shelfDeshelf(book_id) {
    const button = document.getElementById('shelfDeshelfBook'+book_id);
    if (button.innerText === 'Add to shelf') {
        addToShelf(book_id)
        button.innerText = 'Remove from shelf';
    } else if (button.innerText === 'Remove from shelf')   {
        removeFromShelf(book_id)
        button.innerText = 'Add to shelf';
    }
}


function addToShelf(book_id) {
    fetch('/add_to_shelf', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ book_id: book_id })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log(data.message); // or handle success in your UI
    })
    .catch(error => {
        console.error('There was a problem with the fetch operation:', error);
    });
}

function removeFromShelf(book_id) {
    fetch('/remove_from_shelf', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ book_id: book_id })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log(data.message); // or handle success in your UI
    })
    .catch(error => {
        console.error('There was a problem with the fetch operation:', error);
    });
}

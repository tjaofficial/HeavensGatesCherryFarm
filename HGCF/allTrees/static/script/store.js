// Function to open Quick View for a product
function openQuickView(productId) {
    const prodID = productId
    const modal = document.getElementById(`${productId}`);
    modal.style.display = 'block';
    modal.id='openedModal';
  }
  
  // Function to close Quick View
  function closeQuickView(productId) {
    const modal = document.getElementById('openedModal');
    modal.style.display = 'none';
    modal.id = modal.dataset.prodid;
  }
  
  // Close Quick View modal if the user clicks outside the modal
  window.onclick = function (event) {
    const modal = document.getElementById('openedModal');
    if (event.target === modal) {
      modal.style.display = 'none';
      modal.id = modal.dataset.prodid;
    }
  };

function addThisShit(prodID){
    // Create a request object and specify the URL and method
    var url = "/store";
    var data = {
        product_id: prodID  // Replace with the actual product ID
    };

    fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken") // Include the CSRF token
        },
        body: JSON.stringify(data) // Convert data to JSON string
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("Network response was not ok");
        }
        return response.json(); // Parse the response as JSON
    })
    .then(data => {
        console.log(data)
        // Request was successful, handle the response here
        const parsedData = data;
        // Redirect the user to a different page
        if (parsedData.redirectUrl) {
            window.location.href = parsedData.redirectUrl;
        }
    })
    .catch(error => {
        // Request failed, handle errors here
        console.error("Fetch error:", error);
    });
}
// Function to get CSRF token from cookies (use as shown above)
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Check if the cookie name matches the one you're looking for
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


  
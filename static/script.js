function validateForm() {
    var author = document.getElementById("author").value;
    var books = document.getElementById("books").value;
    var genre = document.getElementById("genre").value;
    var length = document.querySelector('input[name="length"]:checked');

    if (author === "" || books === "" || genre === "" || length === null) {
        alert("Please fill in all required fields.");
        return false;
    }
}


document.getElementById("initialForm").addEventListener("submit", function() {
    document.getElementById('container').style.display = "none";
    document.getElementById('loading').style.display = "block"
  });






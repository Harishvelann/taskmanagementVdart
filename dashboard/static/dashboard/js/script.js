console.log("TaskPro dashboard JS loaded!");

window.onload = function() {
    const cards = document.querySelectorAll(".card");
    cards.forEach(card => {
        card.addEventListener("click", () => {
            alert("Clicked: " + card.textContent);
        });
    });
};

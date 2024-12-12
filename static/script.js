console.log("script.js loaded!");

function showPopup(subject, students) {
    console.log("showPopup called with:", subject, students);

    const popup = document.getElementById("popup");
    const title = document.getElementById("popup-title");
    const list = document.getElementById("popup-list");

    title.textContent = `Absentees for ${subject}`;
    list.innerHTML = "";

    students.forEach(student => {
        const li = document.createElement("li");
        li.textContent = student;
        list.appendChild(li);
    });

    popup.classList.add("visible");
}

function closePopup() {
    const popup = document.getElementById("popup");
    popup.classList.remove("visible");
}

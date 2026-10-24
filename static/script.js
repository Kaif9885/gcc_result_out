const searchForm = document.getElementById("searchForm");
const searchButton = document.getElementById("searchBtn");
const message = document.getElementById("message");
const boardSelect = document.getElementById("board");
const classSelect = document.getElementById("studentClass");

function updateClassOptions() {
  classSelect.replaceChildren(new Option("Select class", "", true, true));
  classSelect.options[0].disabled = true;

  if (boardSelect.value === "CBSE") {
    classSelect.add(new Option("Class 10", "10"));
    return;
  }

  if (boardSelect.value === "BSEB") {
    for (let classNumber = 1; classNumber <= 9; classNumber += 1) {
      classSelect.add(new Option(`Class ${classNumber}`, String(classNumber)));
    }
    classSelect.add(new Option("Class 10 Boys", "10|boys"));
    classSelect.add(new Option("Class 10 Girls", "10|girls"));
    classSelect.add(new Option("Class 11", "11"));
    classSelect.add(new Option("Class 12", "12"));
  }
}

boardSelect.addEventListener("change", updateClassOptions);
updateClassOptions();

searchForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const name = document.getElementById("name").value.trim();
  const roll = document.getElementById("roll").value.trim();
  const classSelection = document.getElementById("studentClass").value;
  const [studentClass, classSection = ""] = classSelection.split("|");
  const board = document.getElementById("board").value;
  const subject = document.getElementById("subject").value;
  const chapter = document.getElementById("chapter").value;
  message.textContent = "";
  searchButton.disabled = true;
  searchButton.textContent = "Searching...";

  try {
    const params = new URLSearchParams({
      name,
      roll,
      class: studentClass,
      section: classSection,
      board,
      subject,
      chapter,
    });
    const response = await fetch(`/api/student?${params}`);

    if (response.status === 404) {
      message.textContent = "No result found. Check your name and roll number.";
      message.className = "message error";
      return;
    }
    if (!response.ok) {
      throw new Error(`Request failed with status ${response.status}`);
    }

    const student = await response.json();
    Object.assign(student, {
      board,
      subject,
      chapter,
      class_section: classSection,
    });
    sessionStorage.setItem("studentResult", JSON.stringify(student));
    window.location.assign("/result");
  } catch (error) {
    console.error("Unable to retrieve student result:", error);
    message.textContent = "Could not load your result. Please try again.";
    message.className = "message error";
  } finally {
    searchButton.disabled = false;
    searchButton.textContent = "View result";
  }
});

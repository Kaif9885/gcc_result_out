const searchForm = document.getElementById("searchForm");
const searchButton = document.getElementById("searchBtn");
const message = document.getElementById("message");

searchForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const name = document.getElementById("name").value.trim();
  const roll = document.getElementById("roll").value.trim();
  const studentClass = document.getElementById("studentClass").value;
  message.textContent = "";
  searchButton.disabled = true;
  searchButton.textContent = "Searching...";

  try {
    const params = new URLSearchParams({ name, roll, class: studentClass });
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

const resultRow = document.getElementById("resultRow");
const resultError = document.getElementById("resultError");
const topResultsRows = document.getElementById("topResultsRows");
const topResultsError = document.getElementById("topResultsError");
const resultClass = document.getElementById("resultClass");
const resultDetails = document.getElementById("resultDetails");
const storedResult = sessionStorage.getItem("studentResult");

if (storedResult) {
  try {
    const student = JSON.parse(storedResult);
    const sectionLabel = student.class_section ? ` ${student.class_section.toUpperCase()}` : "";
    resultClass.textContent = `CLASS - ${student.student_class}${sectionLabel}`;
    resultDetails.textContent = [student.board, student.subject, student.chapter]
      .filter(Boolean)
      .join(" · ");
    for (const value of [
      student.roll,
      student.name,
      student.total_marks,
      student.marks ?? "N/A",
    ]) {
      const cell = document.createElement("td");
      cell.textContent = value ?? "";
      resultRow.appendChild(cell);
    }
  } catch (error) {
    console.error("Unable to read stored student result:", error);
    resultError.textContent = "The saved result could not be displayed. Please search again.";
    resultError.hidden = false;
  }
} else {
  resultError.textContent = "No result to display. Please search using your name and roll number.";
  resultError.hidden = false;
}

function positionLabel(position) {
  const suffix = position % 100 >= 11 && position % 100 <= 13
    ? "th"
    : { 1: "st", 2: "nd", 3: "rd" }[position % 10] || "th";
  return `${position}${suffix}`;
}

async function loadTopResults() {
  try {
    const student = JSON.parse(storedResult);
    const params = new URLSearchParams({ class: student.student_class });
    if (student.board) params.set("board", student.board);
    if (student.subject) params.set("subject", student.subject);
    if (student.chapter) params.set("chapter", student.chapter);
    if (student.class_section) params.set("section", student.class_section);
    const response = await fetch(`/api/top-students?${params}`);
    if (!response.ok) {
      throw new Error(`Request failed with status ${response.status}`);
    }

    const students = await response.json();
    document.getElementById("topResultsTitle").textContent = "TOP - 3 RESULTS";
    for (const topStudent of students) {
      const row = document.createElement("tr");
      for (const value of [
        positionLabel(topStudent.position),
        topStudent.name,
        topStudent.total_marks,
        topStudent.marks,
      ]) {
        const cell = document.createElement("td");
        cell.textContent = value ?? "";
        row.appendChild(cell);
      }
      topResultsRows.appendChild(row);
    }
  } catch (error) {
    console.error("Unable to load top student results:", error);
    topResultsError.textContent = "Top results could not be loaded.";
    topResultsError.hidden = false;
  }
}

loadTopResults();

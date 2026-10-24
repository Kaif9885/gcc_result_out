const loginForm = document.getElementById("teacherLogin");
const loginButton = document.getElementById("teacherLoginButton");
const teacherMessage = document.getElementById("teacherMessage");
const teacherDashboard = document.getElementById("teacherDashboard");
const teacherStudentRows = document.getElementById("teacherStudentRows");
const teacherTopRows = document.getElementById("teacherTopRows");
const teacherTopEmpty = document.getElementById("teacherTopEmpty");
const teacherTopCount = document.getElementById("teacherTopCount");
const teacherGreeting = document.getElementById("teacherGreeting");
const studentCount = document.getElementById("studentCount");
const teacherRecordsTitle = document.getElementById("teacherRecordsTitle");
const teacherBoardSelect = document.getElementById("teacherBoard");
const teacherClassSelect = document.getElementById("teacherClass");

function updateTeacherClassOptions() {
  teacherClassSelect.replaceChildren(new Option("Select class", "", true, true));
  teacherClassSelect.options[0].disabled = true;

  if (teacherBoardSelect.value === "CBSE") {
    teacherClassSelect.add(new Option("Class 10", "10"));
    return;
  }

  if (teacherBoardSelect.value === "BSEB" || !teacherBoardSelect.value) {
    for (let classNumber = 1; classNumber <= 9; classNumber += 1) {
      teacherClassSelect.add(new Option(`Class ${classNumber}`, String(classNumber)));
    }
    teacherClassSelect.add(new Option("Class 10 Boys", "10|boys"));
    teacherClassSelect.add(new Option("Class 10 Girls", "10|girls"));
    teacherClassSelect.add(new Option("Class 11", "11"));
    teacherClassSelect.add(new Option("Class 12", "12"));
  }
}

teacherBoardSelect.addEventListener("change", updateTeacherClassOptions);
updateTeacherClassOptions();

loginForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  teacherMessage.textContent = "";
  teacherMessage.className = "message";
  loginButton.disabled = true;
  loginButton.textContent = "Checking...";

  try {
    const response = await fetch("/api/teacher/students", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify((() => {
        const [studentClass, classSection = ""] = document.getElementById("teacherClass").value.split("|");
        return {
          teacher_name: document.getElementById("teacherName").value.trim(),
          password: document.getElementById("teacherPassword").value,
          student_class: Number(studentClass),
          class_section: classSection,
          board: document.getElementById("teacherBoard").value,
          subject: document.getElementById("teacherSubject").value,
          chapter: document.getElementById("teacherChapter").value,
        };
      })()),
    });

    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.detail || "Unable to sign in.");
    }

    teacherStudentRows.replaceChildren();
    teacherTopRows.replaceChildren();
    for (const student of payload.students) {
      const row = document.createElement("tr");
      for (const value of [
        `Class ${student.student_class}`,
        student.roll,
        student.name,
        student.total_marks,
        student.marks ?? "N/A",
      ]) {
        const cell = document.createElement("td");
        cell.textContent = value ?? "";
        row.appendChild(cell);
      }
      teacherStudentRows.appendChild(row);
    }

    for (const student of payload.top_students) {
      const row = document.createElement("tr");
      for (const value of [
        positionLabel(student.position),
        `Class ${student.student_class}`,
        student.roll,
        student.name,
        student.marks,
      ]) {
        const cell = document.createElement("td");
        cell.textContent = value ?? "";
        row.appendChild(cell);
      }
      teacherTopRows.appendChild(row);
    }

    teacherTopEmpty.hidden = payload.top_students.length > 0;
    teacherTopCount.hidden = payload.top_students.length === 0;
    teacherTopCount.textContent = `${payload.top_students.length} student(s) across the top 3 ranks, including ties`;
    const classLabel = payload.class_section
      ? `Class ${payload.student_class} ${payload.class_section}`
      : `Class ${payload.student_class}`;
    teacherGreeting.textContent = `Welcome, ${payload.teacher_name} · ${classLabel}`;
    studentCount.textContent = `${payload.students.length} student record(s)`;
    document.getElementById("teacherTopTitle").textContent = "TOP 3 STUDENTS";
    teacherRecordsTitle.textContent = `${classLabel} · ${payload.board} · ${payload.subject} · ${payload.chapter} · ALL STUDENT RECORDS`;
    loginForm.hidden = true;
    teacherDashboard.hidden = false;
    document.body.classList.add("teacher-page-dashboard");
  } catch (error) {
    teacherMessage.textContent = error.message || "Could not load student data. Please try again.";
    teacherMessage.className = "message error";
  } finally {
    loginButton.disabled = false;
    loginButton.textContent = "View selected class records";
  }
});

document.getElementById("teacherLogout").addEventListener("click", () => {
  teacherStudentRows.replaceChildren();
  teacherTopRows.replaceChildren();
  teacherTopCount.hidden = true;
  teacherDashboard.hidden = true;
  loginForm.reset();
  loginForm.hidden = false;
  document.body.classList.remove("teacher-page-dashboard");
  teacherMessage.textContent = "";
});

function positionLabel(position) {
  const suffix = position % 100 >= 11 && position % 100 <= 13
    ? "th"
    : { 1: "st", 2: "nd", 3: "rd" }[position % 10] || "th";
  return `${position}${suffix}`;
}
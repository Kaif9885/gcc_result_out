const loginForm = document.getElementById("teacherLogin");
const loginButton = document.getElementById("teacherLoginButton");
const teacherMessage = document.getElementById("teacherMessage");
const teacherDashboard = document.getElementById("teacherDashboard");
const teacherStudentRows = document.getElementById("teacherStudentRows");
const teacherTopRows = document.getElementById("teacherTopRows");
const teacherTopEmpty = document.getElementById("teacherTopEmpty");
const teacherGreeting = document.getElementById("teacherGreeting");
const studentCount = document.getElementById("studentCount");

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
      body: JSON.stringify({
        teacher_name: document.getElementById("teacherName").value.trim(),
        password: document.getElementById("teacherPassword").value,
      }),
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

    for (const [index, student] of payload.top_students.entries()) {
      const row = document.createElement("tr");
      for (const value of [
        ["🥇", "🥈", "🥉"][index],
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
    teacherGreeting.textContent = `Welcome, ${payload.teacher_name} · All student records`;
    studentCount.textContent = `${payload.students.length} student record(s)`;
    loginForm.hidden = true;
    teacherDashboard.hidden = false;
  } catch (error) {
    teacherMessage.textContent = error.message || "Could not load student data. Please try again.";
    teacherMessage.className = "message error";
  } finally {
    loginButton.disabled = false;
    loginButton.textContent = "View all student data";
  }
});

document.getElementById("teacherLogout").addEventListener("click", () => {
  teacherStudentRows.replaceChildren();
  teacherTopRows.replaceChildren();
  teacherDashboard.hidden = true;
  loginForm.reset();
  loginForm.hidden = false;
  teacherMessage.textContent = "";
});
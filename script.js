let students = JSON.parse(localStorage.getItem('students')) || [];
let editingId = null;

function save() { localStorage.setItem('students', JSON.stringify(students)); }

function generateId() { return 'STU' + String(students.length + 1).padStart(3, '0'); }

function updateStats() {
    document.getElementById('totalStudents').textContent = students.length;

    if (students.length === 0) {
        document.getElementById('avgGpa').textContent = '0.00';
        document.getElementById('totalMajors').textContent = '0';
        document.getElementById('highestGpa').textContent = '0.00';
        return;
    }

    const avgGpa = students.reduce((s, st) => s + st.gpa, 0) / students.length;
    const majors = new Set(students.map(s => s.major));
    const highestGpa = Math.max(...students.map(s => s.gpa));

    document.getElementById('avgGpa').textContent = avgGpa.toFixed(2);
    document.getElementById('totalMajors').textContent = majors.size;
    document.getElementById('highestGpa').textContent = highestGpa.toFixed(2);
}

function getGpaClass(gpa) {
    if (gpa >= 3.5) return 'gpa-high';
    if (gpa >= 2.5) return 'gpa-medium';
    return 'gpa-low';
}

function renderTable() {
    const tbody = document.getElementById('studentTableBody');
    const search = document.getElementById('searchInput').value.toLowerCase();
    const sortField = document.getElementById('sortField').value;
    const sortOrder = document.getElementById('sortOrder').value;

    let filtered = students.filter(s =>
        s.name.toLowerCase().includes(search) ||
        s.studentId.toLowerCase().includes(search) ||
        s.email.toLowerCase().includes(search)
    );

    filtered.sort((a, b) => {
        let valA = a[sortField];
        let valB = b[sortField];
        if (typeof valA === 'string') valA = valA.toLowerCase();
        if (typeof valB === 'string') valB = valB.toLowerCase();
        if (valA < valB) return sortOrder === 'asc' ? -1 : 1;
        if (valA > valB) return sortOrder === 'asc' ? 1 : -1;
        return 0;
    });

    if (filtered.length === 0) {
        tbody.innerHTML = '';
        document.getElementById('noResults').style.display = 'block';
        return;
    }

    document.getElementById('noResults').style.display = 'none';

    tbody.innerHTML = filtered.map(s => `
        <tr>
            <td>${s.name}</td>
            <td>${s.studentId}</td>
            <td>${s.email}</td>
            <td>${s.major}</td>
            <td><span class="gpa-badge ${getGpaClass(s.gpa)}">${s.gpa.toFixed(2)}</span></td>
            <td>
                <button class="action-btn edit-btn" onclick="editStudent('${s.id}')">Edit</button>
                <button class="action-btn delete-btn" onclick="deleteStudent('${s.id}')">Delete</button>
            </td>
        </tr>
    `).join('');
}

function resetForm() {
    document.getElementById('studentForm').reset();
    document.getElementById('studentId').value = '';
    document.getElementById('formTitle').textContent = 'Add Student';
    document.getElementById('submitBtn').textContent = 'Add Student';
    document.getElementById('cancelBtn').style.display = 'none';
    editingId = null;
}

function editStudent(id) {
    const student = students.find(s => s.id === id);
    if (!student) return;

    editingId = id;
    document.getElementById('studentId').value = student.id;
    document.getElementById('name').value = student.name;
    document.getElementById('studentIdInput').value = student.studentId;
    document.getElementById('email').value = student.email;
    document.getElementById('major').value = student.major;
    document.getElementById('gpa').value = student.gpa;
    document.getElementById('formTitle').textContent = 'Edit Student';
    document.getElementById('submitBtn').textContent = 'Update Student';
    document.getElementById('cancelBtn').style.display = 'block';
}

function deleteStudent(id) {
    if (!confirm('Are you sure you want to delete this student?')) return;
    students = students.filter(s => s.id !== id);
    save();
    updateStats();
    renderTable();
    if (editingId === id) resetForm();
}

document.getElementById('studentForm').addEventListener('submit', function (e) {
    e.preventDefault();
    const data = {
        name: document.getElementById('name').value.trim(),
        studentId: document.getElementById('studentIdInput').value.trim(),
        email: document.getElementById('email').value.trim(),
        major: document.getElementById('major').value,
        gpa: parseFloat(document.getElementById('gpa').value)
    };

    if (editingId) {
        const idx = students.findIndex(s => s.id === editingId);
        if (idx !== -1) {
            students[idx] = { ...students[idx], ...data };
        }
    } else {
        data.id = Date.now().toString();
        students.push(data);
    }

    save();
    updateStats();
    renderTable();
    resetForm();
});

document.getElementById('cancelBtn').addEventListener('click', resetForm);
document.getElementById('searchInput').addEventListener('input', renderTable);
document.getElementById('sortField').addEventListener('change', renderTable);
document.getElementById('sortOrder').addEventListener('change', renderTable);

updateStats();
renderTable();

function toggleSection(sectionId) {
    const section = document.getElementById(sectionId);
    const allSections = document.querySelectorAll('.section');

    allSections.forEach(sec => {
        if (sec.id !== sectionId) {
            sec.style.display = 'none';
            sec.classList.add('hidden');
        }
    });

    if (section.style.display === 'none' || section.classList.contains('hidden')) {
        section.style.display = 'block';
        section.classList.remove('hidden');
    } else {
        section.style.opacity = 0;
        section.style.transform = 'translateY(20px)';
        setTimeout(() => {
            section.style.display = 'none';
            section.classList.add('hidden');
        }, 300);
    }
}

let taskCount = 0;
function addTaskField() {
    const container = document.getElementById('task-fields');
    const taskDiv = document.createElement('div');
    taskDiv.className = 'task-field';
    taskDiv.innerHTML = `
        <input type="text" name="task_title_${taskCount}" placeholder="Task Title" required>
        <textarea name="task_description_${taskCount}" placeholder="Task Description" rows="2"></textarea>
        <input type="datetime-local" name="task_deadline_${taskCount}" required>
        <input type="number" name="task_stage_${taskCount}" placeholder="Stage" min="0" value="0">
        <input type="checkbox" name="task_completed_${taskCount}" id="completed_${taskCount}">
        <label for="completed_${taskCount}">Completed</label>
        <button type="button" class="btn btn-danger btn-sm mt-2" onclick="this.parentElement.remove()">Remove</button>
    `;
    container.appendChild(taskDiv);
    taskCount++;
}

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('form[id$="-form"]').forEach(form => {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(form);
            const url = form.action;
            try {
                const response = await fetch(url, {
                    method: 'POST',
                    body: formData,
                    headers: { 'X-Requested-With': 'XMLHttpRequest' }
                });
                const data = await response.json();
                if (data.success) {
                    const list = document.getElementById(`${form.id.split('-')[1]}s-list`);
                    const card = createCard(data.item, form.id.split('-')[1]);
                    list.insertAdjacentHTML('afterbegin', card);
                    form.reset();
                    document.getElementById('task-fields').innerHTML = '';
                } else {
                    alert('Error: ' + data.error);
                }
            } catch (error) {
                console.error('Error:', error);
            }
        });
    });

    document.addEventListener('click', async (e) => {
        if (e.target.classList.contains('edit-btn')) {
            const card = e.target.closest('.task-card');
            const id = card.dataset.id;
            const type = card.closest('.section').id.split('-')[0];
            const fields = card.querySelectorAll('.editable');

            fields.forEach(field => {
                const currentValue = field.textContent;
                const fieldName = field.dataset.field;
                if (fieldName === 'deadline' || fieldName === 'due_date') {
                    field.innerHTML = `<input type="datetime-local" name="${fieldName}" value="${currentValue.split(' ').reverse().join('T').replace(':', '')}" />`;
                } else if (fieldName === 'stage') {
                    field.innerHTML = `<input type="number" name="${fieldName}" value="${currentValue}" min="0" />`;
                } else {
                    field.innerHTML = `<input type="text" name="${fieldName}" value="${currentValue}" />`;
                }
            });

            e.target.textContent = 'Save';
            e.target.classList.remove('edit-btn');
            e.target.classList.add('save-btn');
        } else if (e.target.classList.contains('save-btn')) {
            const card = e.target.closest('.task-card');
            const id = card.dataset.id;
            const type = card.closest('.section').id.split('-')[0];
            const formData = new FormData();
            card.querySelectorAll('input').forEach(input => {
                formData.append(input.name, input.value);
            });

            try {
                const response = await fetch(`/dashboard/${type}/${id}/update/`, {
                    method: 'POST',
                    body: formData,
                    headers: { 'X-Requested-With': 'XMLHttpRequest', 'X-CSRFToken': getCsrfToken() }
                });
                const data = await response.json();
                if (data.success) {
                    updateCard(card, data.item);
                    e.target.textContent = 'Edit';
                    e.target.classList.remove('save-btn');
                    e.target.classList.add('edit-btn');
                } else {
                    alert('Error: ' + data.error);
                }
            } catch (error) {
                console.error('Error:', error);
            }
        }
    });

    document.addEventListener('click', async (e) => {
        if (e.target.classList.contains('delete-btn')) {
            const card = e.target.closest('.task-card');
            const id = card.dataset.id;
            const url = e.target.dataset.url;

            try {
                const response = await fetch(url, {
                    method: 'POST',
                    headers: { 'X-Requested-With': 'XMLHttpRequest', 'X-CSRFToken': getCsrfToken() }
                });
                const data = await response.json();
                if (data.success) {
                    card.remove();
                } else {
                    alert('Error: ' + data.error);
                }
            } catch (error) {
                console.error('Error:', error);
            }
        }
    });

    document.addEventListener('click', async (e) => {
        if (e.target.classList.contains('toggle-complete')) {
            const card = e.target.closest('.task-card');
            const id = card.dataset.id;
            const url = e.target.dataset.url || `/dashboard/${card.closest('.section').id.split('-')[0]}/${id}/${e.target.textContent.toLowerCase()}/`;

            try {
                const response = await fetch(url, {
                    method: 'POST',
                    headers: { 'X-Requested-With': 'XMLHttpRequest', 'X-CSRFToken': getCsrfToken() }
                });
                const data = await response.json();
                if (data.success) {
                    updateCard(card, data.item);
                } else {
                    alert('Error: ' + data.error);
                }
            } catch (error) {
                console.error('Error:', error);
            }
        }
    });

    function getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }

    function createCard(item, type) {
        const template = {
            task: `
                <div class="card task-card ${item.completed ? 'border-success' : 'border-warning'}" data-id="${item.id}">
                    <div class="card-body text-center">
                        <h5 class="card-title text-dark editable" data-field="title">${item.title}</h5>
                        <p class="card-text text-muted editable" data-field="description">${item.description.slice(0, 50)}${item.description.length > 50 ? '...' : ''}</p>
                        <p><strong>Stage:</strong> <span class="badge bg-info editable" data-field="stage">${item.stage}</span></p>
                        <p><strong>Deadline:</strong> <span class="editable" data-field="deadline">${new Date(item.deadline).toLocaleString()}</span></p>
                        <div class="d-flex justify-content-center gap-2 flex-wrap">
                            <button class="btn btn-sm ${item.completed ? 'btn-warning' : 'btn-success'} hover-btn toggle-complete" data-id="${item.id}">${item.completed ? 'Reopen' : 'Complete'}</button>
                            <button class="btn btn-sm btn-primary hover-btn edit-btn" data-id="${item.id}">Edit</button>
                            <button class="btn btn-sm btn-danger hover-btn delete-btn" data-id="${item.id}" data-url="/dashboard/task/${item.id}/delete/">Delete</button>
                        </div>
                    </div>
                </div>
            `,
            project: `
                <div class="card task-card" data-id="${item.id}">
                    <div class="card-body text-center">
                        <h5 class="card-title text-dark editable" data-field="name">${item.name}</h5>
                        <p class="card-text text-muted editable" data-field="description">${item.description.slice(0, 50)}${item.description.length > 50 ? '...' : ''}</p>
                        <p><strong>Members:</strong> <span class="badge bg-success">${item.members_count}</span></p>
                        <p><strong>Tasks:</strong> <span class="badge bg-primary">${item.tasks_count}</span></p>
                        <div class="d-flex justify-content-center gap-2">
                            <button class="btn btn-sm btn-primary hover-btn edit-btn" data-id="${item.id}">Edit</button>
                            <button class="btn btn-sm btn-danger hover-btn delete-btn" data-id="${item.id}" data-url="/dashboard/project/${item.id}/delete/">Delete</button>
                        </div>
                    </div>
                </div>
            `,
        };
        return template[type] || '';
    }

    function updateCard(card, item) {
        const type = card.closest('.section').id.split('-')[0];
        if (type === 'task') {
            card.classList.toggle('border-success', item.completed);
            card.classList.toggle('border-warning', !item.completed);
            card.querySelector('[data-field="title"]').textContent = item.title;
            card.querySelector('[data-field="description"]').textContent = item.description.slice(0, 50) + (item.description.length > 50 ? '...' : '');
            card.querySelector('[data-field="stage"]').textContent = item.stage;
            card.querySelector('[data-field="deadline"]').textContent = new Date(item.deadline).toLocaleString();
            const toggleBtn = card.querySelector('.toggle-complete');
            toggleBtn.textContent = item.completed ? 'Reopen' : 'Complete';
            toggleBtn.classList.toggle('btn-warning', item.completed);
            toggleBtn.classList.toggle('btn-success', !item.completed);
            toggleBtn.dataset.url = item.completed ? `/dashboard/task/${item.id}/reopen/` : `/dashboard/task/${item.id}/complete/`;
        }
    }
});
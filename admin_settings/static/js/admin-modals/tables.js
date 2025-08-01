export function openEditTableTypeModal(id) {
  fetch(`/settings/table-types/${id}/`)
    .then(r => r.json())
    .then(data => {
      const form = document.getElementById('editTableTypeForm');
      form.elements.id.value = data.id;
      form.elements.name.value = data.name;
      form.elements.description.value = data.description;
      form.elements.max_capacity.value = data.max_capacity;
      document.getElementById('edit-table-type-modal').classList.remove('hidden');
    });
}

export function saveTableType() {
  const form = document.getElementById('editTableTypeForm');
  const id = form.elements.id.value;
  fetch(`/settings/table-types/${id}/update/`, {
    method: 'POST',
    body: new FormData(form),
    headers: { 'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value }
  })
  .then(r => r.json())
  .then(() => location.reload());
}

export async function openEditTableModal(tableId) {
  const modal = document.getElementById('edit-table-modal');
  if (!modal) return;          // защита от ошибки

  const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;

  try {
    const res = await fetch(`/settings/tables/${tableId}/`, {
      headers: { 'Accept': 'application/json', 'X-CSRFToken': csrfToken }
    });
    const data = await res.json();

    modal.querySelector('#editTableId').value        = data.id;
    modal.querySelector('#editTableNumber').value    = data.number;
    modal.querySelector('#editTableType').value      = data.table_type.id;
    modal.querySelector('#editTableDescription').value = data.description;
    modal.querySelector('#editTableIsActive').checked = data.is_active;

    modal.classList.remove('hidden');
  } catch (e) {
    showNotification('Ошибка загрузки: ' + e.message, 'error');
  }
}

export async function saveTableChanges() {
  const form   = document.getElementById('editTableForm');
  const id     = form.elements.id.value;
  const saveBtn = document.getElementById('saveTableBtn');

  saveBtn.disabled = true;
  saveBtn.textContent = 'Сохранение…';

  try {
    const res = await fetch(`/settings/tables/${id}/update/`, {
      method: 'POST',
      body: new FormData(form),
      headers: { 'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value }
    });
    if (!res.ok) throw new Error();
    showNotification('Сохранено', 'success');
    form.closest('.modal').classList.add('hidden');
    setTimeout(() => location.reload(), 1000);
  } catch (e) {
    showNotification('Ошибка: ' + e.message, 'error');
  } finally {
    saveBtn.disabled = false;
    saveBtn.textContent = 'Сохранить';
  }
}

export async function deleteTableType(tableTypeId) {
  const token = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
  const res   = await fetch(`/settings/table-types/${tableTypeId}/delete/`, {
    method: 'POST',
    headers: { 'X-CSRFToken': token }
  });

  const data = await res.json();
  if (data.status === 'success') {
    location.reload();          // страница обновится, строка исчезнет
  } else {
    alert(data.message);
  }
}
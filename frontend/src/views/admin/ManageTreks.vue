<template>
  <div class="container-fluid mt-4 px-4">

    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="mb-0">Treks</h2>
      <button class="btn btn-dark" @click="openCreateModal">+ Add New Trek</button>
    </div>

    <!-- Search -->
    <div class="mb-3">
      <input v-model="search" type="text" class="form-control"
        placeholder="Search treks..." style="max-width: 360px;" />
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-secondary"></div>
    </div>

    <!-- Table -->
    <div class="card border-0 shadow-sm" v-else>
      <div class="card-body p-0">
        <table class="table table-hover mb-0">
          <thead class="table-light">
            <tr>
              <th>ID</th>
              <th>Trek Name</th>
              <th>Location</th>
              <th>Difficulty</th>
              <th>Slots</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="filteredTreks.length === 0">
              <td colspan="7" class="text-center text-muted py-4">No treks found.</td>
            </tr>
            <tr v-for="trek in filteredTreks" :key="trek.id">
              <td class="text-muted">{{ trek.id }}</td>
              <td>{{ trek.trek_name }}</td>
              <td>{{ trek.location }}</td>
              <td>
                <span class="badge" :class="difficultyBadge(trek.difficulty)">
                  {{ trek.difficulty }}
                </span>
              </td>
              <td>{{ trek.available_slots }} / {{ trek.total_slots }}</td>
              <td>
                <span class="badge" :class="statusBadge(trek.status)">
                  {{ trek.status }}
                </span>
              </td>
              <td>
                <button class="btn btn-sm btn-outline-secondary me-1"
                  @click="openEditModal(trek)">✏️</button>
                <button class="btn btn-sm btn-outline-danger"
                  @click="deleteTrek(trek)">🗑️</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <div class="modal fade" id="trekModal" tabindex="-1" ref="modalEl">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ editing ? 'Edit Trek' : 'Add New Trek' }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div v-if="formError" class="alert alert-danger py-2">{{ formError }}</div>
            <div class="row g-3">
              <div class="col-md-6">
                <label class="form-label">Trek Name *</label>
                <input v-model="form.trek_name" class="form-control" />
              </div>
              <div class="col-md-6">
                <label class="form-label">Location *</label>
                <input v-model="form.location" class="form-control" />
              </div>
              <div class="col-md-4">
                <label class="form-label">Difficulty *</label>
                <select v-model="form.difficulty" class="form-select">
                  <option value="">Select...</option>
                  <option>Easy</option>
                  <option>Moderate</option>
                  <option>Hard</option>
                </select>
              </div>
              <div class="col-md-4">
                <label class="form-label">Duration (days) *</label>
                <input v-model="form.duration_days" type="number" min="1" class="form-control" />
              </div>
              <div class="col-md-4">
                <label class="form-label">Total Slots *</label>
                <input v-model="form.total_slots" type="number" min="1" class="form-control" :disabled="editing" />
              </div>
              <div class="col-md-6">
                <label class="form-label">Start Date *</label>
                <input v-model="form.start_date" type="date" class="form-control" />
              </div>
              <div class="col-md-6">
                <label class="form-label">End Date *</label>
                <input v-model="form.end_date" type="date" class="form-control" />
              </div>
              <div class="col-md-6" v-if="editing">
                <label class="form-label">Status</label>
                <select v-model="form.status" class="form-select">
                  <option>Pending</option>
                  <option>Open</option>
                  <option>Closed</option>
                  <option>Completed</option>
                </select>
              </div>
              <div class="col-md-6">
                <label class="form-label">Assign Staff</label>
                <select v-model="form.assigned_staff_id" class="form-select">
                  <option :value="null">— Unassigned —</option>
                  <option v-for="s in staffList" :key="s.id" :value="s.id">
                    {{ s.full_name }} ({{ s.email }})
                  </option>
                </select>
              </div>
              <div class="col-12">
                <label class="form-label">Description</label>
                <textarea v-model="form.description" class="form-control" rows="3"></textarea>
              </div>
              <div class="col-12">
                <label class="form-label">Important Instructions</label>
                <textarea v-model="form.instructions" class="form-control" rows="2"></textarea>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button class="btn btn-dark" @click="submitForm" :disabled="saving">
              {{ saving ? 'Saving...' : (editing ? 'Update Trek' : 'Create Trek') }}
            </button>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Modal } from 'bootstrap'
import api from '../../services/api'

const treks = ref([])
const staffList = ref([])
const loading = ref(true)
const saving = ref(false)
const search = ref('')
const editing = ref(false)
const formError = ref('')
const modalEl = ref(null)
let bsModal = null

const emptyForm = () => ({
  trek_name: '', location: '', difficulty: '',
  duration_days: '', total_slots: '', start_date: '',
  end_date: '', status: 'Pending', description: '',
  instructions: '', assigned_staff_id: null
})

const form = ref(emptyForm())
let editingId = null

onMounted(async () => {
  await loadTreks()
  await loadStaff()
  bsModal = new Modal(modalEl.value)
})

async function loadTreks() {
  loading.value = true
  try {
    const res = await api.get('/admin/treks')
    treks.value = res.data
  } finally {
    loading.value = false
  }
}

async function loadStaff() {
  try {
    const res = await api.get('/admin/staff')
    staffList.value = res.data.filter(s => s.status === 'active')
  } catch {}
}

const filteredTreks = computed(() => {
  if (!search.value) return treks.value
  const q = search.value.toLowerCase()
  return treks.value.filter(t =>
    t.trek_name.toLowerCase().includes(q) ||
    t.location.toLowerCase().includes(q)
  )
})

function openCreateModal() {
  editing.value = false
  editingId = null
  form.value = emptyForm()
  formError.value = ''
  bsModal.show()
}

function openEditModal(trek) {
  editing.value = true
  editingId = trek.id
  form.value = {
    trek_name: trek.trek_name,
    location: trek.location,
    difficulty: trek.difficulty,
    duration_days: trek.duration_days,
    total_slots: trek.total_slots,
    start_date: trek.start_date,
    end_date: trek.end_date,
    status: trek.status,
    description: trek.description || '',
    instructions: trek.instructions || '',
    assigned_staff_id: trek.assigned_staff_id
  }
  formError.value = ''
  bsModal.show()
}

async function submitForm() {
  formError.value = ''
  saving.value = true
  try {
    if (editing.value) {
      await api.put(`/admin/treks/${editingId}`, form.value)
    } else {
      await api.post('/admin/treks', form.value)
    }
    bsModal.hide()
    await loadTreks()
  } catch (err) {
    formError.value = err.response?.data?.error || 'Failed to save trek.'
  } finally {
    saving.value = false
  }
}

async function deleteTrek(trek) {
  if (!confirm(`Delete "${trek.trek_name}"? This cannot be undone.`)) return
  try {
    await api.delete(`/admin/treks/${trek.id}`)
    await loadTreks()
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to delete trek.')
  }
}

function difficultyBadge(d) {
  return { 'bg-success': d === 'Easy', 'bg-warning text-dark': d === 'Moderate', 'bg-danger': d === 'Hard' }
}
function statusBadge(s) {
  return {
    'bg-secondary': s === 'Pending',
    'bg-success': s === 'Open',
    'bg-danger': s === 'Closed',
    'bg-primary': s === 'Completed'
  }
}
</script>
<template>
  <div class="container-fluid mt-4 px-4">

    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="mb-0">Trekking Staff</h2>
      <button class="btn btn-dark" @click="openModal">+ Create New Staff</button>
    </div>

    <div class="mb-3">
      <input v-model="search" type="text" class="form-control"
        placeholder="Search staff..." style="max-width: 360px;"
        @input="loadStaff" />
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-secondary"></div>
    </div>

    <div class="card border-0 shadow-sm" v-else>
      <div class="card-body p-0">
        <table class="table table-hover mb-0">
          <thead class="table-light">
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Email</th>
              <th>Contact</th>
              <th>Status</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="staff.length === 0">
              <td colspan="6" class="text-center text-muted py-4">No staff found.</td>
            </tr>
            <tr v-for="s in staff" :key="s.id">
              <td class="text-muted">TS{{ String(s.id).padStart(3,'0') }}</td>
              <td>{{ s.full_name }}</td>
              <td>{{ s.email }}</td>
              <td>{{ s.contact_number || '—' }}</td>
              <td>
                <span class="badge" :class="s.status === 'active' ? 'bg-success' : 'bg-danger'">
                  {{ s.status }}
                </span>
              </td>
              <td>
                <button v-if="s.status !== 'active'" class="btn btn-sm btn-outline-success me-1"
                  @click="updateStatus(s, 'active')">Whitelist</button>
                <button v-if="s.status !== 'blacklisted'" class="btn btn-sm btn-outline-danger"
                  @click="updateStatus(s, 'blacklisted')">Blacklist</button>
                <button v-if="s.status === 'blacklisted'" class="btn btn-sm btn-outline-secondary ms-1"
                  @click="updateStatus(s, 'inactive')">Deactivate</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Create Staff Modal -->
    <div class="modal fade" id="staffModal" tabindex="-1" ref="modalEl">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Create New Trekking Staff</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div v-if="formError" class="alert alert-danger py-2">{{ formError }}</div>
            <div class="mb-3">
              <label class="form-label">Full Name *</label>
              <input v-model="form.full_name" class="form-control" />
            </div>
            <div class="mb-3">
              <label class="form-label">Email *</label>
              <input v-model="form.email" type="email" class="form-control" />
            </div>
            <div class="mb-3">
              <label class="form-label">Contact Number</label>
              <input v-model="form.contact_number" class="form-control" />
            </div>
            <div class="mb-3">
              <label class="form-label">Password *</label>
              <input v-model="form.password" type="password" class="form-control" />
            </div>
            <p class="text-muted small">
              <em>The staff member will use these credentials to log in.</em>
            </p>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button class="btn btn-dark" @click="createStaff" :disabled="saving">
              {{ saving ? 'Creating...' : 'Create Staff' }}
            </button>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Modal } from 'bootstrap'
import api from '../../services/api'

const staff = ref([])
const loading = ref(true)
const saving = ref(false)
const search = ref('')
const formError = ref('')
const modalEl = ref(null)
let bsModal = null

const form = ref({ full_name: '', email: '', contact_number: '', password: '' })

onMounted(async () => {
  await loadStaff()
  bsModal = new Modal(modalEl.value)
})

async function loadStaff() {
  loading.value = true
  try {
    const res = await api.get('/admin/staff', { params: { search: search.value } })
    staff.value = res.data
  } finally {
    loading.value = false
  }
}

function openModal() {
  form.value = { full_name: '', email: '', contact_number: '', password: '' }
  formError.value = ''
  bsModal.show()
}

async function createStaff() {
  formError.value = ''
  saving.value = true
  try {
    await api.post('/admin/staff', form.value)
    bsModal.hide()
    await loadStaff()
  } catch (err) {
    formError.value = err.response?.data?.error || 'Failed to create staff.'
  } finally {
    saving.value = false
  }
}

async function updateStatus(s, newStatus) {
  const action = newStatus === 'blacklisted' ? 'blacklist' : newStatus
  if (!confirm(`${action} ${s.full_name}?`)) return
  try {
    await api.patch(`/admin/staff/${s.id}/status`, { status: newStatus })
    await loadStaff()
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to update status.')
  }
}
</script>
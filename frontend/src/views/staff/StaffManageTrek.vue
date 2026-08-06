<template>
  <div class="container mt-4">

    <RouterLink to="/staff/dashboard" class="btn btn-sm btn-outline-secondary mb-3">
      ← Back to Dashboard
    </RouterLink>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-secondary"></div>
    </div>

    <div v-else-if="trek">

      <div class="card border-0 shadow-sm mb-4">
        <div class="card-body">
          <div class="d-flex justify-content-between align-items-start">
            <div>
              <h3>{{ trek.trek_name }}</h3>
              <p class="text-muted mb-1">📍 {{ trek.location }} &nbsp;|&nbsp;
                🎯 {{ trek.difficulty }} &nbsp;|&nbsp;
                ⏱ {{ trek.duration_days }} days
              </p>
              <p class="text-muted small">
                {{ trek.start_date }} → {{ trek.end_date }}
              </p>
            </div>
            <span class="badge fs-6" :class="statusBadge(trek.status)">
              {{ trek.status }}
            </span>
          </div>

          <hr>

          <!-- Update controls -->
          <div v-if="error" class="alert alert-danger py-2">{{ error }}</div>
          <div v-if="successMsg" class="alert alert-success py-2">{{ successMsg }}</div>

          <div class="row g-3">
            <div class="col-md-4">
              <label class="form-label">Available Slots
                <span class="text-muted">(Total: {{ trek.total_slots }})</span>
              </label>
              <input v-model="form.available_slots" type="number"
                :min="0" :max="trek.total_slots" class="form-control" />
            </div>
            <div class="col-md-4">
              <label class="form-label">Trek Status</label>
              <select v-model="form.status" class="form-select">
                <option>Open</option>
                <option>Closed</option>
                <option>Completed</option>
              </select>
            </div>
            <div class="col-md-4 d-flex align-items-end">
              <button class="btn btn-dark w-100" @click="updateTrek" :disabled="saving">
                {{ saving ? 'Saving...' : 'Update Trek' }}
              </button>
            </div>
          </div>

          <div class="mt-3" v-if="form.status === 'Completed'">
            <div class="alert alert-warning py-2 small">
              ⚠️ Marking as Completed will close all active bookings for this trek.
            </div>
          </div>
        </div>
      </div>

      <!-- Participants -->
      <div class="card border-0 shadow-sm">
        <div class="card-header bg-white">
          <h5 class="mb-0">Participants ({{ participants.length }})</h5>
        </div>
        <div class="card-body p-0">
          <div v-if="participants.length === 0" class="text-center py-4 text-muted">
            No participants yet.
          </div>
          <table v-else class="table table-hover mb-0">
            <thead class="table-light">
              <tr>
                <th>#</th>
                <th>Name</th>
                <th>Email</th>
                <th>Booking Date</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(p, i) in participants" :key="p.id">
                <td class="text-muted">{{ i + 1 }}</td>
                <td>{{ p.user_name }}</td>
                <td>{{ p.user_email }}</td>
                <td>{{ formatDate(p.booking_date) }}</td>
                <td>
                  <span class="badge" :class="bookingBadge(p.status)">
                    {{ p.status }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../../services/api'

const route = useRoute()
const trek = ref(null)
const participants = ref([])
const loading = ref(true)
const saving = ref(false)
const error = ref('')
const successMsg = ref('')
const form = ref({ available_slots: 0, status: 'Open' })

onMounted(async () => {
  try {
    const res = await api.get(`/staff/treks/${route.params.id}`)
    trek.value = res.data.trek
    participants.value = res.data.participants
    form.value.available_slots = trek.value.available_slots
    form.value.status = trek.value.status
  } finally {
    loading.value = false
  }
})

async function updateTrek() {
  error.value = ''
  successMsg.value = ''
  saving.value = true
  try {
    const res = await api.patch(`/staff/treks/${route.params.id}`, form.value)
    trek.value = res.data.trek
    successMsg.value = 'Trek updated successfully.'
    if (form.value.status === 'Completed') {
      participants.value = participants.value.map(p =>
        p.status === 'Booked' ? { ...p, status: 'Completed' } : p
      )
    }
  } catch (err) {
    error.value = err.response?.data?.error || 'Failed to update.'
  } finally {
    saving.value = false
  }
}

function formatDate(d) {
  return new Date(d).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })
}
function statusBadge(s) {
  return { 'bg-secondary': s === 'Pending', 'bg-success': s === 'Open', 'bg-danger': s === 'Closed', 'bg-primary': s === 'Completed' }
}
function bookingBadge(s) {
  return { 'bg-success': s === 'Booked', 'bg-secondary': s === 'Cancelled', 'bg-primary': s === 'Completed' }
}
</script>
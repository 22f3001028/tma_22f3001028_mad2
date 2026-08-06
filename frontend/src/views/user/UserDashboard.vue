<template>
  <div class="container mt-4">
    <h2 class="mb-1">Welcome, {{ user.full_name }}!</h2>
    <p class="text-muted mb-4">Here's a summary of your trekking activity.</p>

    <!-- Stats -->
    <div class="row g-3 mb-4">
      <div class="col-6 col-md-3">
        <div class="card border-0 shadow-sm text-center">
          <div class="card-body">
            <div class="fs-2 fw-bold">{{ activeBookings.length }}</div>
            <div class="text-muted small">Active Bookings</div>
          </div>
        </div>
      </div>
      <div class="col-6 col-md-3">
        <div class="card border-0 shadow-sm text-center">
          <div class="card-body">
            <div class="fs-2 fw-bold">{{ completedBookings.length }}</div>
            <div class="text-muted small">Treks Completed</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Recent bookings -->
    <div class="card border-0 shadow-sm mb-4">
      <div class="card-header bg-white d-flex justify-content-between align-items-center">
        <h5 class="mb-0">My Bookings</h5>
        <RouterLink to="/user/bookings" class="btn btn-sm btn-outline-dark">
          View All →
        </RouterLink>
      </div>
      <div class="card-body p-0">
        <div v-if="loading" class="text-center py-3">
          <div class="spinner-border spinner-border-sm text-secondary"></div>
        </div>
        <div v-else-if="bookings.length === 0" class="text-center py-4 text-muted">
          No bookings yet.
          <RouterLink to="/user/treks" class="d-block mt-2">Browse Treks →</RouterLink>
        </div>
        <table v-else class="table table-hover mb-0">
          <thead class="table-light">
            <tr>
              <th>Trek Name</th>
              <th>Trek Dates</th>
              <th>Status</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="b in bookings.slice(0, 5)" :key="b.id">
              <td>{{ b.trek_name }}</td>
              <td class="small text-muted">{{ b.start_date }} → {{ b.end_date }}</td>
              <td>
                <span class="badge" :class="bookingBadge(b.status)">{{ b.status }}</span>
              </td>
              <td>
                <RouterLink :to="`/user/treks/${b.trek_id}`"
                  class="btn btn-sm btn-outline-secondary">View</RouterLink>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Action buttons -->
    <div class="d-flex gap-2 flex-wrap">
      <RouterLink to="/user/treks" class="btn btn-dark">
        🏔️ Browse Available Treks
      </RouterLink>
      <button class="btn btn-outline-secondary" @click="exportCSV" :disabled="exporting">
        {{ exporting ? '⏳ Preparing export...' : '⬇️ Export Booking History' }}
      </button>
    </div>

    <!-- Export alert -->
    <div v-if="exportMsg" class="alert mt-3 py-2"
      :class="exportSuccess ? 'alert-success' : 'alert-danger'">
      {{ exportMsg }}
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../../services/api'
import { getUser, getToken } from '../../services/auth'

const user = getUser()
const bookings = ref([])
const loading = ref(true)
const exporting = ref(false)
const exportMsg = ref('')
const exportSuccess = ref(true)

onMounted(async () => {
  try {
    const res = await api.get('/bookings/me')
    bookings.value = res.data
  } finally {
    loading.value = false
  }
})

const activeBookings = computed(() =>
  bookings.value.filter(b => b.status === 'Booked')
)
const completedBookings = computed(() =>
  bookings.value.filter(b => b.status === 'Completed')
)

async function exportCSV() {
  exporting.value = true
  exportMsg.value = ''

  try {
    const response = await fetch('http://localhost:5000/api/user/export/bookings', {
      headers: { 'Authorization': `Bearer ${getToken()}` }
    })

    if (!response.ok) throw new Error('Export failed')

    // Convert response to downloadable blob
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = 'booking_history.csv'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)

    exportSuccess.value = true
    exportMsg.value = '✅ Export complete! Your booking history has been downloaded.'

  } catch (err) {
    exportSuccess.value = false
    exportMsg.value = '❌ Export failed. Please try again.'
  } finally {
    exporting.value = false
  }
}

function bookingBadge(s) {
  return {
    'bg-success': s === 'Booked',
    'bg-secondary': s === 'Cancelled',
    'bg-primary': s === 'Completed'
  }
}
</script>
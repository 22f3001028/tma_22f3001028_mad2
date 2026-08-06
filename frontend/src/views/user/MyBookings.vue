<template>
  <div class="container mt-4">
    <h2 class="mb-4">My Bookings</h2>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-secondary"></div>
    </div>

    <div v-else-if="bookings.length === 0" class="text-center py-5 text-muted">
      No bookings found.
      <RouterLink to="/user/treks" class="d-block mt-2">Browse Treks →</RouterLink>
    </div>

    <div class="card border-0 shadow-sm" v-else>
      <div class="card-body p-0">
        <table class="table table-hover mb-0">
          <thead class="table-light">
            <tr>
              <th>Trek Name</th>
              <th>Location</th>
              <th>Trek Dates</th>
              <th>Booking Date</th>
              <th>Status</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="b in activeBookings" :key="b.id">
              <td>{{ b.trek_name }}</td>
              <td>{{ b.location }}</td>
              <td class="small text-muted">{{ b.start_date }} → {{ b.end_date }}</td>
              <td class="small text-muted">{{ formatDate(b.booking_date) }}</td>
              <td>
                <span class="badge bg-success">{{ b.status }}</span>
              </td>
              <td>
                <button class="btn btn-sm btn-outline-danger"
                  @click="cancelBooking(b)"
                  :disabled="b.trek_status !== 'Open'">
                  Cancel
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../../services/api'

const bookings = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    const res = await api.get('/bookings/me')
    bookings.value = res.data
  } finally {
    loading.value = false
  }
})

const activeBookings = computed(() => bookings.value.filter(b => b.status === 'Booked'))

async function cancelBooking(b) {
  if (!confirm(`Cancel your booking for ${b.trek_name}?`)) return
  try {
    await api.delete(`/bookings/${b.id}`)
    b.status = 'Cancelled'
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to cancel booking.')
  }
}

function formatDate(d) {
  return new Date(d).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })
}
</script>
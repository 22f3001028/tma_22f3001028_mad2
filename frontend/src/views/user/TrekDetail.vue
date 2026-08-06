<template>
  <div class="container mt-4" style="max-width: 720px;">

    <RouterLink to="/user/treks" class="btn btn-sm btn-outline-secondary mb-3">
      ← Back to Treks
    </RouterLink>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-secondary"></div>
    </div>

    <div v-else-if="trek" class="card border-0 shadow-sm">
      <div class="card-body p-4">

        <div class="d-flex justify-content-between align-items-start mb-3">
          <h2 class="mb-0">{{ trek.trek_name }}</h2>
          <span class="badge fs-6" :class="difficultyBadge(trek.difficulty)">
            {{ trek.difficulty }}
          </span>
        </div>

        <div class="row g-3 mb-3">
          <div class="col-6">
            <div class="text-muted small">Location</div>
            <div>📍 {{ trek.location }}</div>
          </div>
          <div class="col-6">
            <div class="text-muted small">Duration</div>
            <div>⏱ {{ trek.duration_days }} days</div>
          </div>
          <div class="col-6">
            <div class="text-muted small">Start Date</div>
            <div>🗓 {{ trek.start_date }}</div>
          </div>
          <div class="col-6">
            <div class="text-muted small">End Date</div>
            <div>🗓 {{ trek.end_date }}</div>
          </div>
          <div class="col-6">
            <div class="text-muted small">Available Slots</div>
            <div :class="trek.available_slots > 0 ? 'text-success' : 'text-danger'">
              {{ trek.available_slots }} / {{ trek.total_slots }}
            </div>
          </div>
          <div class="col-6">
            <div class="text-muted small">Status</div>
            <span class="badge" :class="statusBadge(trek.status)">{{ trek.status }}</span>
          </div>
        </div>

        <div v-if="trek.description" class="mb-3">
          <div class="text-muted small mb-1">Description</div>
          <p>{{ trek.description }}</p>
        </div>

        <div v-if="trek.instructions" class="mb-4">
          <div class="text-muted small mb-1">Important Instructions</div>
          <div class="alert alert-info py-2 small">{{ trek.instructions }}</div>
        </div>

        <hr>

        <!-- Booking action -->
        <div v-if="error" class="alert alert-danger py-2">{{ error }}</div>
        <div v-if="successMsg" class="alert alert-success py-2">{{ successMsg }}</div>

        <div v-if="trek.status === 'Open' && trek.available_slots > 0 && !alreadyBooked">
          <button class="btn btn-dark btn-lg w-100" @click="bookTrek" :disabled="booking">
            {{ booking ? 'Booking...' : '🎒 Book Now' }}
          </button>
        </div>
        <div v-else-if="alreadyBooked" class="alert alert-success mb-0">
          ✅ You have already booked this trek.
        </div>
        <div v-else-if="trek.status !== 'Open'" class="alert alert-secondary mb-0">
          This trek is currently {{ trek.status }} and cannot be booked.
        </div>
        <div v-else class="alert alert-danger mb-0">
          This trek is fully booked. No slots available.
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
const loading = ref(true)
const booking = ref(false)
const error = ref('')
const successMsg = ref('')
const alreadyBooked = ref(false)

onMounted(async () => {
  try {
    const [trekRes, bookingRes] = await Promise.all([
      api.get(`/user/treks/${route.params.id}`),
      api.get('/bookings/me')
    ])
    trek.value = trekRes.data
    alreadyBooked.value = bookingRes.data.some(
      b => b.trek_id === trek.value.id && b.status === 'Booked'
    )
  } finally {
    loading.value = false
  }
})

async function bookTrek() {
  error.value = ''
  booking.value = true
  try {
    await api.post('/bookings', { trek_id: trek.value.id })
    successMsg.value = `🎉 Successfully booked ${trek.value.trek_name}!`
    alreadyBooked.value = true
    trek.value.available_slots -= 1
  } catch (err) {
    error.value = err.response?.data?.error || 'Booking failed.'
  } finally {
    booking.value = false
  }
}

function difficultyBadge(d) {
  return { 'bg-success': d === 'Easy', 'bg-warning text-dark': d === 'Moderate', 'bg-danger': d === 'Hard' }
}
function statusBadge(s) {
  return { 'bg-secondary': s === 'Pending', 'bg-success': s === 'Open', 'bg-danger': s === 'Closed', 'bg-primary': s === 'Completed' }
}
</script>
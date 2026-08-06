<template>
  <div class="container mt-4">
    <h2 class="mb-4">Trekking History</h2>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-secondary"></div>
    </div>

    <div v-else-if="history.length === 0" class="text-center py-5 text-muted">
      No trekking history yet.
    </div>

    <div class="card border-0 shadow-sm" v-else>
      <div class="card-body p-0">
        <table class="table mb-0">
          <thead class="table-light">
            <tr>
              <th>Trek Name</th>
              <th>Trek Dates</th>
              <th>Completed On</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="b in history" :key="b.id">
              <td>{{ b.trek_name }}</td>
              <td class="small text-muted">{{ b.start_date }} → {{ b.end_date }}</td>
              <td class="small text-muted">{{ formatDate(b.booking_date) }}</td>
              <td>
                <span class="badge"
                  :class="b.status === 'Completed' ? 'bg-primary' : 'bg-secondary'">
                  {{ b.status }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <p class="text-muted small mt-3">
      History shows all your completed and cancelled treks.
    </p>
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

const history = computed(() =>
  bookings.value.filter(b => b.status === 'Completed' || b.status === 'Cancelled')
)

function formatDate(d) {
  return new Date(d).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })
}
</script>
<template>
  <div class="container-fluid mt-4 px-4">

    <h2 class="mb-4">Dashboard</h2>

    <!-- Error alert -->
    <div v-if="error" class="alert alert-danger">{{ error }}</div>

    <!-- Stats cards -->
    <div class="row g-3 mb-4" v-if="stats">
      <div class="col-6 col-md-3">
        <div class="card text-center border-0 shadow-sm">
          <div class="card-body">
            <div class="fs-1 fw-bold text-dark">{{ stats.total_treks }}</div>
            <div class="text-muted small">Total Treks</div>
            <div class="mt-1">🏔️</div>
          </div>
        </div>
      </div>
      <div class="col-6 col-md-3">
        <div class="card text-center border-0 shadow-sm">
          <div class="card-body">
            <div class="fs-1 fw-bold text-dark">{{ stats.total_users }}</div>
            <div class="text-muted small">Total Users (Trekkers)</div>
            <div class="mt-1">🧑</div>
          </div>
        </div>
      </div>
      <div class="col-6 col-md-3">
        <div class="card text-center border-0 shadow-sm">
          <div class="card-body">
            <div class="fs-1 fw-bold text-dark">{{ stats.total_staff }}</div>
            <div class="text-muted small">Total Trekking Staff</div>
            <div class="mt-1">👷</div>
          </div>
        </div>
      </div>
      <div class="col-6 col-md-3">
        <div class="card text-center border-0 shadow-sm">
          <div class="card-body">
            <div class="fs-1 fw-bold text-dark">{{ stats.total_bookings }}</div>
            <div class="text-muted small">Total Bookings</div>
            <div class="mt-1">📋</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading state -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-secondary" role="status"></div>
      <p class="mt-2 text-muted">Loading dashboard...</p>
    </div>

    <!-- Recent bookings -->
    <div class="card border-0 shadow-sm" v-if="stats">
      <div class="card-header bg-white d-flex justify-content-between align-items-center">
        <h5 class="mb-0">Recent Bookings</h5>
        <RouterLink to="/admin/treks" class="btn btn-sm btn-outline-dark">
          View All Treks →
        </RouterLink>
      </div>
      <div class="card-body p-0">
        <div v-if="stats.recent_bookings.length === 0" class="text-center py-4 text-muted">
          No bookings yet.
        </div>
        <table v-else class="table table-hover mb-0">
          <thead class="table-light">
            <tr>
              <th>Booking ID</th>
              <th>User (Trekker)</th>
              <th>Trek</th>
              <th>Booking Date</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="b in stats.recent_bookings" :key="b.id">
              <td class="text-muted">#{{ b.id }}</td>
              <td>{{ b.user_name }}</td>
              <td>{{ b.trek_name }}</td>
              <td>{{ formatDate(b.booking_date) }}</td>
              <td>
                <span class="badge" :class="statusBadge(b.status)">
                  {{ b.status }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../services/api'

const stats = ref(null)
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    const res = await api.get('/admin/dashboard')
    stats.value = res.data
  } catch (err) {
    error.value = 'Failed to load dashboard data.'
  } finally {
    loading.value = false
  }
})

function formatDate(dateStr) {
  return new Date(dateStr).toLocaleDateString('en-IN', {
    day: '2-digit', month: 'short', year: 'numeric'
  })
}

function statusBadge(status) {
  return {
    'bg-success': status === 'Booked',
    'bg-secondary': status === 'Cancelled',
    'bg-primary': status === 'Completed'
  }
}
</script>
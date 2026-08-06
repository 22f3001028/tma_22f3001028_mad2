<template>
  <div class="container-fluid mt-4 px-4">

    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="mb-0">Reports & Statistics</h2>
      <button
        class="btn btn-dark"
        @click="sendMonthlyReport"
        :disabled="sending">
        {{ sending ? '⏳ Sending...' : '📧 Send Monthly Report to Admin' }}
      </button>
    </div>

    <!-- Report trigger feedback -->
    <div v-if="reportMsg" class="alert py-2 mb-3"
      :class="reportSuccess ? 'alert-success' : 'alert-danger'">
      {{ reportMsg }}
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-secondary"></div>
    </div>

    <div v-else-if="report" class="row g-4">

      <!-- Month header -->
      <div class="col-12">
        <div class="alert alert-dark mb-0">
          📅 Showing data for <strong>{{ report.month }}</strong>
        </div>
      </div>

      <!-- Summary cards -->
      <div class="col-12">
        <div class="card border-0 shadow-sm">
          <div class="card-header bg-white">
            <h5 class="mb-0">📊 Activity Summary</h5>
          </div>
          <div class="card-body">
            <div class="row g-3">
              <div class="col-6 col-md-2">
                <div class="card border-0 bg-light text-center p-3">
                  <div class="fs-2 fw-bold">{{ report.total_treks }}</div>
                  <div class="text-muted small">Total Treks</div>
                </div>
              </div>
              <div class="col-6 col-md-2">
                <div class="card border-0 bg-light text-center p-3">
                  <div class="fs-2 fw-bold text-success">{{ report.open_treks }}</div>
                  <div class="text-muted small">Open Treks</div>
                </div>
              </div>
              <div class="col-6 col-md-2">
                <div class="card border-0 bg-light text-center p-3">
                  <div class="fs-2 fw-bold text-primary">{{ report.completed_treks_total }}</div>
                  <div class="text-muted small">Completed</div>
                </div>
              </div>
              <div class="col-6 col-md-2">
                <div class="card border-0 bg-light text-center p-3">
                  <div class="fs-2 fw-bold">{{ report.monthly_bookings }}</div>
                  <div class="text-muted small">Bookings This Month</div>
                </div>
              </div>
              <div class="col-6 col-md-2">
                <div class="card border-0 bg-light text-center p-3">
                  <div class="fs-2 fw-bold">{{ report.total_users }}</div>
                  <div class="text-muted small">Registered Users</div>
                </div>
              </div>
              <div class="col-6 col-md-2">
                <div class="card border-0 bg-light text-center p-3">
                  <div class="fs-2 fw-bold">{{ report.total_staff }}</div>
                  <div class="text-muted small">Trek Staff</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Popular treks and overview -->
      <div class="col-md-6">
        <div class="card border-0 shadow-sm h-100">
          <div class="card-header bg-white">
            <h5 class="mb-0">🔥 Most Popular Treks</h5>
          </div>
          <div class="card-body p-0">
            <div v-if="report.popular_treks.length === 0"
              class="text-center py-4 text-muted">
              No booking data yet.
            </div>
            <table v-else class="table mb-0">
              <thead class="table-light">
                <tr>
                  <th>Rank</th>
                  <th>Trek Name</th>
                  <th class="text-center">Bookings</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(trek, index) in report.popular_treks" :key="index">
                  <td>
                    <span v-if="index === 0">🥇</span>
                    <span v-else-if="index === 1">🥈</span>
                    <span v-else-if="index === 2">🥉</span>
                    <span v-else class="text-muted">{{ index + 1 }}</span>
                  </td>
                  <td>{{ trek.trek_name }}</td>
                  <td class="text-center">
                    <span class="badge bg-dark">{{ trek.bookings }}</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div class="col-md-6">
        <div class="card border-0 shadow-sm h-100">
          <div class="card-header bg-white">
            <h5 class="mb-0">📋 Quick Overview</h5>
          </div>
          <div class="card-body">
            <ul class="list-group list-group-flush">
              <li class="list-group-item d-flex justify-content-between px-0">
                <span>Total treks in system</span>
                <strong>{{ report.total_treks }}</strong>
              </li>
              <li class="list-group-item d-flex justify-content-between px-0">
                <span>Currently open for booking</span>
                <strong class="text-success">{{ report.open_treks }}</strong>
              </li>
              <li class="list-group-item d-flex justify-content-between px-0">
                <span>Completed treks</span>
                <strong class="text-primary">{{ report.completed_treks_total }}</strong>
              </li>
              <li class="list-group-item d-flex justify-content-between px-0">
                <span>Bookings this month</span>
                <strong>{{ report.monthly_bookings }}</strong>
              </li>
              <li class="list-group-item d-flex justify-content-between px-0">
                <span>Registered trekkers</span>
                <strong>{{ report.total_users }}</strong>
              </li>
              <li class="list-group-item d-flex justify-content-between px-0">
                <span>Trek staff members</span>
                <strong>{{ report.total_staff }}</strong>
              </li>
            </ul>
          </div>
        </div>
      </div>

      <!-- Note about scheduled job -->
      <div class="col-12">
        <div class="alert alert-light border small text-muted">
          ℹ️ The monthly report is automatically emailed to the admin on the
          <strong>1st of every month at 6:00 AM</strong> via the Celery scheduled job.
          Use the button above to send it manually at any time.
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../services/api'

const report = ref(null)
const loading = ref(true)
const sending = ref(false)
const reportMsg = ref('')
const reportSuccess = ref(true)

onMounted(async () => {
  try {
    const res = await api.get('/reports/summary')
    report.value = res.data
  } finally {
    loading.value = false
  }
})

async function sendMonthlyReport() {
  sending.value = true
  reportMsg.value = ''
  try {
    const res = await api.post('/reports/send-monthly')
    reportSuccess.value = true
    reportMsg.value = '✅ ' + res.data.message
  } catch (err) {
    reportSuccess.value = false
    reportMsg.value = '❌ ' + (err.response?.data?.error || 'Failed to send report.')
  } finally {
    sending.value = false
  }
}
</script>
<template>
  <div class="container-fluid mt-4 px-4">

    <h2 class="mb-4">My Dashboard</h2>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-secondary"></div>
    </div>

    <div v-else>
      <!-- Stats -->
      <div class="row g-3 mb-4">
        <div class="col-4">
          <div class="card text-center border-0 shadow-sm">
            <div class="card-body">
              <div class="fs-2 fw-bold">{{ data.assigned_treks }}</div>
              <div class="text-muted small">Assigned Treks</div>
              <div>📋</div>
            </div>
          </div>
        </div>
        <div class="col-4">
          <div class="card text-center border-0 shadow-sm">
            <div class="card-body">
              <div class="fs-2 fw-bold">{{ data.total_participants }}</div>
              <div class="text-muted small">Total Participants</div>
              <div>🧑</div>
            </div>
          </div>
        </div>
        <div class="col-4">
          <div class="card text-center border-0 shadow-sm">
            <div class="card-body">
              <div class="fs-2 fw-bold">{{ data.ongoing_treks }}</div>
              <div class="text-muted small">Ongoing Treks</div>
              <div>🏔️</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Assigned treks table -->
      <div class="card border-0 shadow-sm">
        <div class="card-header bg-white">
          <h5 class="mb-0">My Assigned Treks</h5>
        </div>
        <div class="card-body p-0">
          <div v-if="data.treks.length === 0" class="text-center py-4 text-muted">
            No treks assigned to you yet.
          </div>
          <table v-else class="table table-hover mb-0">
            <thead class="table-light">
              <tr>
                <th>Trek Name</th>
                <th>Dates</th>
                <th>Participants</th>
                <th>Slots</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="trek in data.treks" :key="trek.id">
                <td>{{ trek.trek_name }}</td>
                <td class="small text-muted">{{ trek.start_date }} → {{ trek.end_date }}</td>
                <td>{{ trek.total_slots - trek.available_slots }}</td>
                <td>{{ trek.available_slots }}</td>
                <td>
                  <span class="badge" :class="statusBadge(trek.status)">
                    {{ trek.status }}
                  </span>
                </td>
                <td>
                  <RouterLink :to="`/staff/treks/${trek.id}`"
                    class="btn btn-sm btn-outline-dark">Manage</RouterLink>
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
import api from '../../services/api'

const data = ref({ assigned_treks: 0, total_participants: 0, ongoing_treks: 0, treks: [] })
const loading = ref(true)

onMounted(async () => {
  try {
    const res = await api.get('/staff/dashboard')
    data.value = res.data
  } finally {
    loading.value = false
  }
})

function statusBadge(s) {
  return {
    'bg-secondary': s === 'Pending',
    'bg-success': s === 'Open',
    'bg-danger': s === 'Closed',
    'bg-primary': s === 'Completed'
  }
}
</script>
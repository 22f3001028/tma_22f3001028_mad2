<template>
  <div class="container mt-4">
    <h2 class="mb-4">Browse Treks</h2>

    <!-- Search and filters -->
    <div class="row g-2 mb-4">
      <div class="col-md-4">
        <input v-model="filters.search" type="text"
          class="form-control" placeholder="Search trek name or location..." />
      </div>
      <div class="col-md-2">
        <select v-model="filters.difficulty" class="form-select">
          <option value="">Difficulty: All</option>
          <option>Easy</option>
          <option>Moderate</option>
          <option>Hard</option>
        </select>
      </div>
      <div class="col-md-2">
        <select v-model="filters.location" class="form-select">
          <option value="">Location: All</option>
          <option v-for="loc in uniqueLocations" :key="loc">{{ loc }}</option>
        </select>
      </div>
      <div class="col-auto">
        <button class="btn btn-dark" @click="loadTreks">Search</button>
      </div>
      <div class="col-auto">
        <button class="btn btn-outline-secondary" @click="clearFilters">Clear Filters</button>
      </div>
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-secondary"></div>
    </div>

    <div v-else-if="treks.length === 0" class="text-center py-5 text-muted">
      No open treks found.
    </div>

    <div v-else class="row g-3">
      <div class="col-md-4" v-for="trek in treks" :key="trek.id">
        <div class="card h-100 border-0 shadow-sm">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-start mb-2">
              <h5 class="card-title mb-0">{{ trek.trek_name }}</h5>
              <span class="badge" :class="difficultyBadge(trek.difficulty)">
                {{ trek.difficulty }}
              </span>
            </div>
            <p class="text-muted small mb-1">📍 {{ trek.location }}</p>
            <p class="text-muted small mb-1">⏱ {{ trek.duration_days }} days</p>
            <p class="text-muted small mb-2">
              🗓 {{ trek.start_date }} → {{ trek.end_date }}
            </p>
            <p class="small mb-3">
              <span :class="trek.available_slots > 0 ? 'text-success' : 'text-danger'">
                {{ trek.available_slots > 0 ? `✅ ${trek.available_slots} slots left` : '❌ Fully booked' }}
              </span>
            </p>
          </div>
          <div class="card-footer bg-white border-0">
            <RouterLink :to="`/user/treks/${trek.id}`"
              class="btn btn-dark w-100">View Details</RouterLink>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../../services/api'

const treks = ref([])
const loading = ref(true)
const filters = ref({ search: '', difficulty: '', location: '' })

onMounted(loadTreks)

async function loadTreks() {
  loading.value = true
  try {
    const res = await api.get('/user/treks', { params: filters.value })
    treks.value = res.data
  } finally {
    loading.value = false
  }
}

function clearFilters() {
  filters.value = { search: '', difficulty: '', location: '' }
  loadTreks()
}

const uniqueLocations = computed(() => [...new Set(treks.value.map(t => t.location))])

function difficultyBadge(d) {
  return { 'bg-success': d === 'Easy', 'bg-warning text-dark': d === 'Moderate', 'bg-danger': d === 'Hard' }
}
</script>
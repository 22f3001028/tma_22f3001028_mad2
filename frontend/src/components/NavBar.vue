<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
    <div class="container-fluid">

      <span class="navbar-brand fw-bold">🏔️ Trekking Management</span>

      <button class="navbar-toggler" type="button"
        data-bs-toggle="collapse" data-bs-target="#navbarContent">
        <span class="navbar-toggler-icon"></span>
      </button>

      <div class="collapse navbar-collapse" id="navbarContent">

        <!-- Admin nav links -->
        <ul class="navbar-nav me-auto" v-if="role === 'admin'">
          <li class="nav-item">
            <RouterLink class="nav-link" to="/admin/dashboard">Dashboard</RouterLink>
          </li>
          <li class="nav-item">
            <RouterLink class="nav-link" to="/admin/treks">Treks</RouterLink>
          </li>
          <li class="nav-item">
            <RouterLink class="nav-link" to="/admin/staff">Trekking Staff</RouterLink>
          </li>
          <li class="nav-item">
            <RouterLink class="nav-link" to="/admin/users">Users (Trekkers)</RouterLink>
          </li>
          <li class="nav-item">
  <RouterLink class="nav-link" to="/admin/reports">Reports</RouterLink>
</li>
        </ul>

        <!-- Staff nav links -->
        <ul class="navbar-nav me-auto" v-else-if="role === 'staff'">
          <li class="nav-item">
            <RouterLink class="nav-link" to="/staff/dashboard">Dashboard</RouterLink>
          </li>
        </ul>

        <!-- User nav links -->
        <ul class="navbar-nav me-auto" v-else-if="role === 'user'">
          <li class="nav-item">
            <RouterLink class="nav-link" to="/user/dashboard">Dashboard</RouterLink>
          </li>
          <li class="nav-item">
            <RouterLink class="nav-link" to="/user/treks">Browse Treks</RouterLink>
          </li>
          <li class="nav-item">
            <RouterLink class="nav-link" to="/user/bookings">My Bookings</RouterLink>
          </li>
          <li class="nav-item">
            <RouterLink class="nav-link" to="/user/history">History</RouterLink>
          </li>
          <li class="nav-item">
            <RouterLink class="nav-link" to="/user/profile">Profile</RouterLink>
          </li>
        </ul>

        <!-- Right side: manual dropdown -->
        <ul class="navbar-nav ms-auto">
          <li class="nav-item position-relative" ref="dropdownContainer">
            <button
              class="btn btn-link nav-link text-white d-flex align-items-center gap-1"
              @click="toggleDropdown"
            >
              {{ user.full_name || 'Account' }}
              <span style="font-size:10px">▼</span>
            </button>

            <!-- Manual dropdown menu -->
            <div
              v-if="dropdownOpen"
              class="position-absolute end-0 mt-1 bg-white border rounded shadow-sm"
              style="min-width: 200px; z-index: 9999; top: 100%;"
            >
              <div class="px-3 py-2 text-muted small border-bottom">
                <div>{{ user.email }}</div>
                <div class="fst-italic">Role: {{ user.role }}</div>
              </div>
              <button
                class="d-block w-100 text-start px-3 py-2 text-danger border-0 bg-transparent"
                style="cursor:pointer"
                @click="logout"
              >
                Logout
              </button>
            </div>
          </li>
        </ul>

      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { getUser, clearAuth } from '../services/auth'

const router = useRouter()
const user = computed(() => getUser())
const role = computed(() => user.value.role)
const dropdownOpen = ref(false)
const dropdownContainer = ref(null)

function toggleDropdown() {
  dropdownOpen.value = !dropdownOpen.value
}

function logout() {
  dropdownOpen.value = false
  clearAuth()
  router.push('/login')
}

// Close dropdown when clicking anywhere outside
function handleClickOutside(event) {
  if (dropdownContainer.value && !dropdownContainer.value.contains(event.target)) {
    dropdownOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>
<template>
  <div class="container-fluid mt-4 px-4">

    <h2 class="mb-4">Users (Trekkers)</h2>

    <div class="mb-3">
      <input
        v-model="search"
        type="text"
        class="form-control"
        placeholder="Search users by name or email..."
        style="max-width: 360px;"
        @input="loadUsers"
      />
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-secondary"></div>
      <p class="mt-2 text-muted">Loading users...</p>
    </div>

    <div v-else>
      <p class="text-muted small mb-2">{{ users.length }} user(s) found</p>

      <div class="card border-0 shadow-sm">
        <div class="card-body p-0">
          <table class="table table-hover mb-0">
            <thead class="table-light">
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Email</th>
                <th>Contact</th>
                <th>Joined</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="users.length === 0">
                <td colspan="7" class="text-center text-muted py-4">
                  No users found.
                </td>
              </tr>
              <tr v-for="u in users" :key="u.id">
                <td class="text-muted">UD{{ String(u.id).padStart(3, '0') }}</td>
                <td>{{ u.full_name }}</td>
                <td>{{ u.email }}</td>
                <td>{{ u.contact_number || '—' }}</td>
                <td class="small text-muted">{{ formatDate(u.created_at) }}</td>
                <td>
                  <span class="badge"
                    :class="u.status === 'active' ? 'bg-success' :
                            u.status === 'blacklisted' ? 'bg-danger' : 'bg-secondary'">
                    {{ u.status }}
                  </span>
                </td>
                <td>
                  <button
                    v-if="u.status === 'active'"
                    class="btn btn-sm btn-outline-danger me-1"
                    @click="updateStatus(u, 'blacklisted')">
                    Blacklist
                  </button>
                  <button
                    v-if="u.status === 'active'"
                    class="btn btn-sm btn-outline-secondary"
                    @click="updateStatus(u, 'inactive')">
                    Deactivate
                  </button>
                  <button
                    v-if="u.status !== 'active'"
                    class="btn btn-sm btn-outline-success"
                    @click="updateStatus(u, 'active')">
                    Whitelist
                  </button>
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

const users = ref([])
const loading = ref(true)
const search = ref('')

async function loadUsers() {
  loading.value = true
  try {
    const res = await api.get('/admin/users', {
      params: search.value ? { search: search.value } : {}
    })
    users.value = res.data
  } catch (err) {
    console.error('Failed to load users:', err)
  } finally {
    loading.value = false
  }
}

async function updateStatus(u, newStatus) {
  const action = newStatus === 'blacklisted' ? 'Blacklist' :
                 newStatus === 'inactive' ? 'Deactivate' : 'Whitelist'
  if (!confirm(`${action} ${u.full_name}?`)) return
  try {
    await api.patch(`/admin/users/${u.id}/status`, { status: newStatus })
    await loadUsers()
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to update status.')
  }
}

function formatDate(dateStr) {
  if (!dateStr) return '—'
  return new Date(dateStr).toLocaleDateString('en-IN', {
    day: '2-digit', month: 'short', year: 'numeric'
  })
}

onMounted(loadUsers)
</script>
<template>
  <div class="container mt-4" style="max-width: 560px;">
    <h2 class="mb-4">My Profile</h2>

    <div v-if="successMsg" class="alert alert-success">{{ successMsg }}</div>
    <div v-if="error" class="alert alert-danger">{{ error }}</div>

    <div class="card border-0 shadow-sm">
      <div class="card-body p-4">
        <h5 class="mb-3">Personal Information</h5>
        <div class="mb-3">
          <label class="form-label">Full Name</label>
          <input v-model="form.full_name" class="form-control" />
        </div>
        <div class="mb-3">
          <label class="form-label">Email</label>
          <input :value="user.email" class="form-control" disabled />
          <div class="form-text">Email cannot be changed.</div>
        </div>
        <div class="mb-4">
          <label class="form-label">Contact Number</label>
          <input v-model="form.contact_number" class="form-control" />
        </div>

        <hr>
        <h5 class="mb-3">Change Password <span class="text-muted small fw-normal">(optional)</span></h5>
        <div class="mb-3">
          <label class="form-label">Current Password</label>
          <input v-model="form.current_password" type="password" class="form-control" />
        </div>
        <div class="mb-4">
          <label class="form-label">New Password</label>
          <input v-model="form.new_password" type="password" class="form-control" />
        </div>

        <button class="btn btn-dark w-100" @click="saveProfile" :disabled="saving">
          {{ saving ? 'Saving...' : 'Save Changes' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../services/api'
import { getUser, saveAuth, getToken } from '../../services/auth'

const user = getUser()
const form = ref({
  full_name: user.full_name,
  contact_number: user.contact_number || '',
  current_password: '',
  new_password: ''
})
const saving = ref(false)
const successMsg = ref('')
const error = ref('')

async function saveProfile() {
  successMsg.value = ''
  error.value = ''
  saving.value = true
  try {
    const res = await api.put('/user/profile', form.value)
    // Update stored user data
    saveAuth(getToken(), res.data.user)
    successMsg.value = 'Profile updated successfully.'
    form.value.current_password = ''
    form.value.new_password = ''
  } catch (err) {
    error.value = err.response?.data?.error || 'Failed to update profile.'
  } finally {
    saving.value = false
  }
}
</script>
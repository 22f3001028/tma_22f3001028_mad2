<template>
  <div class="min-vh-100 d-flex align-items-center justify-content-center bg-light">
    <div class="card shadow" style="width: 100%; max-width: 460px;">
      <div class="card-body p-4">

        <div class="text-center mb-4">
          <div class="fs-1">🏔️</div>
          <h4 class="fw-bold">Create User Account</h4>
          <p class="text-muted">Register as a Trekker</p>
        </div>

        <div v-if="error" class="alert alert-danger py-2">{{ error }}</div>
        <div v-if="success" class="alert alert-success py-2">{{ success }}</div>

        <form @submit.prevent="handleRegister">
          <div class="mb-3">
            <label class="form-label">Full Name</label>
            <input v-model="form.full_name" type="text"
              class="form-control" placeholder="Your full name" required />
          </div>

          <div class="mb-3">
            <label class="form-label">Email address</label>
            <input v-model="form.email" type="email"
              class="form-control" placeholder="you@example.com" required />
          </div>

          <div class="mb-3">
            <label class="form-label">Password</label>
            <input v-model="form.password" type="password"
              class="form-control" placeholder="Choose a password" required />
          </div>

          <div class="mb-3">
            <label class="form-label">Confirm Password</label>
            <input v-model="form.confirm_password" type="password"
              class="form-control" placeholder="Repeat your password" required />
          </div>

          <div class="mb-3">
            <label class="form-label">Contact Number</label>
            <input v-model="form.contact_number" type="tel"
              class="form-control" placeholder="e.g. 9876543210" />
          </div>

          <button type="submit" class="btn btn-dark w-100" :disabled="loading">
            {{ loading ? 'Creating account...' : 'Register' }}
          </button>
        </form>

        <hr>
        <p class="text-center text-muted small mb-0">
          Already have an account?
          <RouterLink to="/login">Login here</RouterLink>
        </p>
        <p class="text-center text-muted small mt-2">
          <em>Note: Only Users (Trekkers) can register themselves.<br>
          Trekking Staff are created by Admin.</em>
        </p>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'

const router = useRouter()
const form = ref({
  full_name: '', email: '', password: '',
  confirm_password: '', contact_number: ''
})
const error = ref('')
const success = ref('')
const loading = ref(false)

async function handleRegister() {
  error.value = ''
  success.value = ''

  if (form.value.password !== form.value.confirm_password) {
    error.value = 'Passwords do not match.'
    return
  }

  loading.value = true
  try {
    await api.post('/auth/register', {
      full_name: form.value.full_name,
      email: form.value.email,
      password: form.value.password,
      contact_number: form.value.contact_number
    })

    success.value = 'Account created successfully! Redirecting to login...'
    setTimeout(() => router.push('/login'), 1500)

  } catch (err) {
    error.value = err.response?.data?.error || 'Registration failed. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>
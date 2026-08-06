<template>
  <div class="min-vh-100 d-flex align-items-center justify-content-center bg-light">
    <div class="card shadow" style="width: 100%; max-width: 420px;">
      <div class="card-body p-4">

        <!-- Header -->
        <div class="text-center mb-4">
          <div class="fs-1">🏔️</div>
          <h4 class="fw-bold">Trekking Management</h4>
          <p class="text-muted">Login to your account</p>
        </div>

        <!-- Error alert -->
        <div v-if="error" class="alert alert-danger py-2">{{ error }}</div>

        <!-- Form -->
        <form @submit.prevent="handleLogin">
          <div class="mb-3">
            <label class="form-label">Email address</label>
            <input
              v-model="form.email"
              type="email"
              class="form-control"
              placeholder="you@example.com"
              required
            />
          </div>

          <div class="mb-3">
            <label class="form-label">Password</label>
            <input
              v-model="form.password"
              type="password"
              class="form-control"
              placeholder="Enter your password"
              required
            />
          </div>

          <button
            type="submit"
            class="btn btn-dark w-100"
            :disabled="loading"
          >
            {{ loading ? 'Logging in...' : 'Login' }}
          </button>
        </form>

        <hr>

        <p class="text-center text-muted small mb-0">
          Don't have an account?
          <RouterLink to="/register">Register as User (Trekker)</RouterLink>
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
import { saveAuth } from '../services/auth'

const router = useRouter()
const form = ref({ email: '', password: '' })
const error = ref('')
const loading = ref(false)

async function handleLogin() {
  error.value = ''
  loading.value = true

  try {
    const response = await api.post('/auth/login', form.value)
    const { token, user } = response.data

    saveAuth(token, user)

    // Redirect based on role
    if (user.role === 'admin') router.push('/admin/dashboard')
    else if (user.role === 'staff') router.push('/staff/dashboard')
    else router.push('/user/dashboard')

  } catch (err) {
    error.value = err.response?.data?.error || 'Login failed. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>
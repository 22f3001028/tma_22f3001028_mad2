<template>
  <div>
    <NavBar v-if="showNav" />
    <RouterView />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import NavBar from './components/NavBar.vue'

const route = useRoute()

// Hide navbar on login and register pages
const showNav = computed(() => {
  return !['/', '/login', '/register'].includes(route.path)
})
</script>
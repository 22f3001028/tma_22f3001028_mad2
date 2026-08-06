import { createRouter, createWebHistory } from 'vue-router'

// Auth pages
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'

// Admin pages
import AdminDashboard from '../views/admin/AdminDashboard.vue'
import ManageTreks from '../views/admin/ManageTreks.vue'
import ManageStaff from '../views/admin/ManageStaff.vue'
import ManageUsers from '../views/admin/ManageUsers.vue'
import AdminReports from '../views/admin/AdminReports.vue'
// Staff pages
import StaffDashboard from '../views/staff/StaffDashboard.vue'
import StaffManageTrek from '../views/staff/StaffManageTrek.vue'

// User pages
import UserDashboard from '../views/user/UserDashboard.vue'
import BrowseTreks from '../views/user/BrowseTreks.vue'
import TrekDetail from '../views/user/TrekDetail.vue'
import MyBookings from '../views/user/MyBookings.vue'
import TrekHistory from '../views/user/TrekHistory.vue'
import UserProfile from '../views/user/UserProfile.vue'

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', component: LoginView },
  { path: '/register', component: RegisterView },

  // Admin routes
  { path: '/admin/dashboard', component: AdminDashboard, meta: { role: 'admin' } },
  { path: '/admin/treks', component: ManageTreks, meta: { role: 'admin' } },
  { path: '/admin/staff', component: ManageStaff, meta: { role: 'admin' } },
  { path: '/admin/users', component: ManageUsers, meta: { role: 'admin' } },
  { path: '/admin/reports', component: AdminReports, meta: { role: 'admin' } },

  // Staff routes
  { path: '/staff/dashboard', component: StaffDashboard, meta: { role: 'staff' } },
  { path: '/staff/treks/:id', component: StaffManageTrek, meta: { role: 'staff' } },

  // User routes
  { path: '/user/dashboard', component: UserDashboard, meta: { role: 'user' } },
  { path: '/user/treks', component: BrowseTreks, meta: { role: 'user' } },
  { path: '/user/treks/:id', component: TrekDetail, meta: { role: 'user' } },
  { path: '/user/bookings', component: MyBookings, meta: { role: 'user' } },
  { path: '/user/history', component: TrekHistory, meta: { role: 'user' } },
  { path: '/user/profile', component: UserProfile, meta: { role: 'user' } },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guard — runs before every page change
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const user = JSON.parse(localStorage.getItem('user') || '{}')

  // If the page requires a role and user isn't logged in
  if (to.meta.role && !token) {
    return next('/login')
  }

  // If logged in but wrong role for this page
  if (to.meta.role && user.role !== to.meta.role) {
    // Redirect to their correct dashboard
    if (user.role === 'admin') return next('/admin/dashboard')
    if (user.role === 'staff') return next('/staff/dashboard')
    if (user.role === 'user') return next('/user/dashboard')
    return next('/login')
  }

  // If already logged in and trying to visit login/register
  if ((to.path === '/login' || to.path === '/register') && token) {
    if (user.role === 'admin') return next('/admin/dashboard')
    if (user.role === 'staff') return next('/staff/dashboard')
    if (user.role === 'user') return next('/user/dashboard')
  }

  next()
})

export default router
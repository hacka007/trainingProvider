<template>
  <v-app>
    <v-navigation-drawer
      v-model="drawer"
      app
    >
      <v-list>
        <v-list-item
          title="Training Provider"
          subtitle="Course Management"
        ></v-list-item>

        <v-divider></v-divider>

        <v-list-item
          v-for="(item, i) in menuItems"
          :key="i"
          :to="item.to"
          :prepend-icon="item.icon"
          :title="item.title"
          link
        ></v-list-item>
      </v-list>
    </v-navigation-drawer>

    <v-app-bar app>
      <v-app-bar-nav-icon @click="drawer = !drawer"></v-app-bar-nav-icon>
      <v-toolbar-title>Training Provider</v-toolbar-title>
      <v-spacer></v-spacer>
      <v-btn v-if="!isLoggedIn" to="/login" text>Login</v-btn>
      <v-btn v-else @click="logout" text>Logout</v-btn>
    </v-app-bar>

    <v-main>
      <v-container fluid>
        <router-view></router-view>
      </v-container>
    </v-main>

    <v-footer app>
      <div class="text-center w-100">
        &copy; {{ new Date().getFullYear() }} - Training Provider
      </div>
    </v-footer>
  </v-app>
</template>

<script>
import eventBus from '@/eventBus';

export default {
  name: 'App',
  data() {
    return {
      drawer: false,
      isLoggedIn: false, // This will be updated based on authentication state
      menuItems: [
        { title: 'Home', icon: 'mdi-home', to: '/' },
        { title: 'Trainings', icon: 'mdi-book-open-variant', to: '/trainings' },
        { title: 'My Bookings', icon: 'mdi-calendar-check', to: '/my-bookings' },
      ]
    }
  },
  created() {
    // Check if token exists in localStorage when app initializes
    this.isLoggedIn = localStorage.getItem('token') !== null;

    // Listen for login success event
    eventBus.on('login-success', () => {
      this.isLoggedIn = true;
    });
  },
  methods: {
    logout() {
      // Remove token and user email from localStorage
      localStorage.removeItem('token');
      localStorage.removeItem('userEmail');
      this.isLoggedIn = false;
      // this.$router.push('/login');
    }
  }
}
</script>

<style>
.v-application {
  font-family: 'Roboto', sans-serif;
}
</style>

<template>
  <div class="login">
    <v-row justify="center">
      <v-col cols="12" sm="8" md="6" lg="4">
        <v-card class="mt-10">
          <v-card-title class="text-h4 text-center">Login</v-card-title>
          <v-card-text>
            <v-form ref="form" v-model="valid" @submit.prevent="login">
              <v-text-field
                v-model="credentials.email"
                label="Email"
                type="email"
                required
                :rules="[
                  v => !!v || 'Email is required',
                  v => /.+@.+\..+/.test(v) || 'Email must be valid'
                ]"
                prepend-icon="mdi-email"
              ></v-text-field>

              <v-text-field
                v-model="credentials.password"
                label="Password"
                type="password"
                required
                :rules="[v => !!v || 'Password is required']"
                prepend-icon="mdi-lock"
              ></v-text-field>

              <v-alert
                v-if="error"
                type="error"
                class="mt-4"
              >
                {{ error }}
              </v-alert>

              <v-card-actions class="mt-4">
                <v-spacer></v-spacer>
                <v-btn
                  color="primary"
                  type="submit"
                  :loading="loading"
                  :disabled="!valid || loading"
                >
                  Login
                </v-btn>
              </v-card-actions>
            </v-form>
          </v-card-text>
        </v-card>

        <v-card class="mt-4">
          <v-card-text class="text-center">
            <p>Don't have an account? Please contact the administrator.</p>
            <p>You can still browse trainings and make bookings without logging in.</p>
            <v-btn color="secondary" to="/trainings" class="mt-2">
              Browse Trainings
            </v-btn>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script>
import api from '@/services/api';
import eventBus from '@/eventBus';

export default {
  name: 'LoginView',
  data() {
    return {
      valid: false,
      loading: false,
      error: null,
      credentials: {
        email: '',
        password: ''
      }
    }
  },
  methods: {
    async login() {
      if (!this.$refs.form.validate()) return;

      this.loading = true;
      this.error = null;

      try {
        const response = await api.login(this.credentials);

        // Store token and user email in localStorage
        localStorage.setItem('token', response.data.access_token);
        localStorage.setItem('userEmail', this.credentials.email);

        // Update app state
        eventBus.emit('login-success');

        // Redirect to requested page or home
        const redirectPath = this.$route.query.redirect || '/';
        this.$router.push(redirectPath);
      } catch (err) {
        this.error = err.response?.data?.detail || 'Login failed. Please check your credentials.';
        console.error(err);
      } finally {
        this.loading = false;
      }
    }
  }
}
</script>

<template>
  <div class="home">
    <v-row>
      <v-col cols="12">
        <v-card class="mb-6">
          <v-img
            src="https://images.unsplash.com/photo-1524178232363-1fb2b075b655?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1200&q=80"
            height="400"
            cover
          >
            <v-card-title class="text-white text-h3 font-weight-bold">
              Welcome to Training Provider
            </v-card-title>
            <v-card-subtitle class="text-white text-h5">
              Discover our professional training courses
            </v-card-subtitle>
          </v-img>
        </v-card>
      </v-col>
    </v-row>

    <v-row>
      <v-col cols="12">
        <h2 class="text-h4 mb-4">Featured Trainings</h2>
      </v-col>
    </v-row>

    <v-row>
      <v-col v-if="loading" cols="12" class="text-center">
        <v-progress-circular indeterminate color="primary"></v-progress-circular>
      </v-col>
      <v-col v-else-if="error" cols="12">
        <v-alert type="error">{{ error }}</v-alert>
      </v-col>
      <v-col v-else-if="trainings.length === 0" cols="12">
        <v-alert type="info">No trainings available at the moment.</v-alert>
      </v-col>
      <template v-else>
        <v-col v-for="training in trainings.slice(0, 3)" :key="training.id" cols="12" md="4">
          <v-card height="100%">
            <v-card-title>{{ training.name }}</v-card-title>
            <v-card-subtitle>
              <v-icon small>mdi-account</v-icon> {{ training.instructor }}
              <v-icon small class="ml-4">mdi-currency-usd</v-icon> {{ training.price }}
            </v-card-subtitle>
            <v-card-text>
              <p>{{ training.description.substring(0, 100) }}...</p>
              <p><v-icon small>mdi-clock-outline</v-icon> {{ training.duration_hours }} hours</p>
            </v-card-text>
            <v-card-actions>
              <v-btn color="primary" :to="`/trainings/${training.id}`">View Details</v-btn>
            </v-card-actions>
          </v-card>
        </v-col>
      </template>
    </v-row>

    <v-row class="mt-6">
      <v-col cols="12" class="text-center">
        <v-btn color="primary" size="large" to="/trainings">
          View All Trainings
        </v-btn>
      </v-col>
    </v-row>

    <v-row class="mt-10">
      <v-col cols="12">
        <h2 class="text-h4 mb-4">Why Choose Us</h2>
      </v-col>
      <v-col cols="12" md="4">
        <v-card height="100%">
          <v-card-title>Expert Instructors</v-card-title>
          <v-card-text>
            Our trainings are led by industry professionals with years of experience.
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="4">
        <v-card height="100%">
          <v-card-title>Practical Learning</v-card-title>
          <v-card-text>
            Hands-on exercises and real-world examples to ensure you can apply what you learn.
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="4">
        <v-card height="100%">
          <v-card-title>Flexible Schedule</v-card-title>
          <v-card-text>
            Multiple dates for each training to fit your busy schedule.
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script>
import api from '@/services/api';

export default {
  name: 'HomeView',
  data() {
    return {
      trainings: [],
      loading: true,
      error: null
    }
  },
  async created() {
    try {
      const response = await api.getTrainings();
      console.log(response);
      this.trainings = response.data.data;
      this.loading = false;
    } catch (err) {
      this.error = 'Failed to load trainings. Please try again later.';
      this.loading = false;
      console.error(err);
    }
  }
}
</script>

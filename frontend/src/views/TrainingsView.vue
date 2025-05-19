<template>
  <div class="trainings">
    <h1 class="text-h3 mb-4">Available Trainings</h1>

    <!-- Filters -->
    <v-card class="mb-6">
      <v-card-title>Filter Trainings</v-card-title>
      <v-card-text>
        <v-row>
          <v-col cols="12" md="6">
            <v-text-field
              v-model="searchQuery"
              label="Search by name or instructor"
              prepend-icon="mdi-magnify"
              clearable
            ></v-text-field>
          </v-col>
          <v-col cols="12" md="6">
            <v-row>
              <v-col cols="6">
                <v-menu
                  ref="startDateMenu"
                  v-model="startDateMenu"
                  :close-on-content-click="false"
                  transition="scale-transition"
                  offset-y
                  min-width="auto"
                >
                  <template v-slot:activator="{ props }">
                    <v-text-field
                      v-model="startDate"
                      label="Start Date"
                      prepend-icon="mdi-calendar"
                      readonly
                      v-bind="props"
                    ></v-text-field>
                  </template>
                  <v-date-picker
                    v-model="startDate"
                    @update:model-value="startDateMenu = false"
                  ></v-date-picker>
                </v-menu>
              </v-col>
              <v-col cols="6">
                <v-menu
                  ref="endDateMenu"
                  v-model="endDateMenu"
                  :close-on-content-click="false"
                  transition="scale-transition"
                  offset-y
                  min-width="auto"
                >
                  <template v-slot:activator="{ props }">
                    <v-text-field
                      v-model="endDate"
                      label="End Date"
                      prepend-icon="mdi-calendar"
                      readonly
                      v-bind="props"
                    ></v-text-field>
                  </template>
                  <v-date-picker
                    v-model="endDate"
                    @update:model-value="endDateMenu = false"
                  ></v-date-picker>
                </v-menu>
              </v-col>
            </v-row>
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="12" class="text-right">
            <v-btn color="primary" @click="applyDateFilter" :disabled="!startDate || !endDate">
              Apply Date Filter
            </v-btn>
            <v-btn class="ml-2" @click="clearFilters">
              Clear Filters
            </v-btn>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- Trainings List -->
    <v-row>
      <v-col v-if="loading" cols="12" class="text-center">
        <v-progress-circular indeterminate color="primary"></v-progress-circular>
      </v-col>
      <v-col v-else-if="error" cols="12">
        <v-alert type="error">{{ error }}</v-alert>
      </v-col>
      <v-col v-else-if="filteredTrainings.length === 0" cols="12">
        <v-alert type="info">No trainings found matching your criteria.</v-alert>
      </v-col>
      <template v-else>
        <v-col v-for="training in filteredTrainings" :key="training.id" cols="12" md="6" lg="4">
          <v-card height="100%">
            <v-card-title>{{ training.name }}</v-card-title>
            <v-card-subtitle>
              <v-icon small>mdi-account</v-icon> {{ training.instructor }}
              <v-icon small class="ml-4">mdi-currency-usd</v-icon> {{ training.price }}
            </v-card-subtitle>
            <v-card-text>
              <p>{{ training.description.substring(0, 150) }}...</p>
              <p><v-icon small>mdi-clock-outline</v-icon> {{ training.duration_hours }} hours</p>
              <p><v-icon small>mdi-account-group</v-icon> Max {{ training.max_participants }} participants</p>
            </v-card-text>
            <v-card-actions>
              <v-btn color="primary" :to="`/trainings/${training.id}`">View Details</v-btn>
            </v-card-actions>
          </v-card>
        </v-col>
      </template>
    </v-row>
  </div>
</template>

<script>
import api from '@/services/api';

export default {
  name: 'TrainingsView',
  data() {
    return {
      trainings: [],
      loading: true,
      error: null,
      searchQuery: '',
      startDate: null,
      endDate: null,
      startDateMenu: false,
      endDateMenu: false,
      dateFiltered: false
    }
  },
  computed: {
    filteredTrainings() {
      if (!this.searchQuery) {
        return this.trainings;
      }

      const query = this.searchQuery.toLowerCase();
      return this.trainings.filter(training => 
        training.name.toLowerCase().includes(query) || 
        training.instructor.toLowerCase().includes(query) ||
        training.description.toLowerCase().includes(query)
      );
    }
  },
  methods: {
    async fetchTrainings() {
      this.loading = true;
      this.error = null;

      try {
        let response;
        if (this.dateFiltered && this.startDate && this.endDate) {
          // Format dates for API
          const startDateTime = new Date(this.startDate).toISOString();
          const endDateTime = new Date(this.endDate).toISOString();
          response = await api.getTrainingsByTimePeriod(startDateTime, endDateTime);
        } else {
          response = await api.getTrainings();
        }

        this.trainings = response.data.data;
        this.loading = false;
      } catch (err) {
        this.error = 'Failed to load trainings. Please try again later.';
        this.loading = false;
        console.error(err);
      }
    },
    applyDateFilter() {
      if (this.startDate && this.endDate) {
        // Check if start date is before end date
        const startDateTime = new Date(this.startDate);
        const endDateTime = new Date(this.endDate);

        if (startDateTime >= endDateTime) {
          this.error = 'Start date must be before end date';
          return;
        }

        this.error = null;
        this.dateFiltered = true;
        this.fetchTrainings();
      }
    },
    clearFilters() {
      this.searchQuery = '';
      this.startDate = null;
      this.endDate = null;
      this.dateFiltered = false;
      this.fetchTrainings();
    }
  },
  async created() {
    await this.fetchTrainings();
  }
}
</script>

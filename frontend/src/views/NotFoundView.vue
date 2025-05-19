<template>
  <div class="not-found">
    <v-row justify="center" align="center" style="height: 70vh;">
      <v-col cols="12" sm="8" md="6" class="text-center">
        <h1 class="text-h1 mb-4">404</h1>
        <h2 class="text-h4 mb-6">Page Not Found</h2>
        <p class="text-body-1 mb-8">
          The page you are looking for doesn't exist or has been moved.
        </p>
        <v-btn color="primary" to="/" size="large">
          Go to Home Page
        </v-btn>
      </v-col>
    </v-row>
  </div>
</template>

<script>
export default {
  name: 'NotFoundView'
}
</script>

<style scoped>
.not-found {
  min-height: 100%;
}
</style>
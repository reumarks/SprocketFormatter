<template>
  <div v-if="photoGridData.length > 0" class="photo-grid-container">
    <div class="photo-grid">
      <div v-for="(image, index) in photoGridData" :key="index" class="photo-item"
        @click="$emit('select-image', index)">
        <div class="photo-wrapper">
          <img :src="image.borderedImage" alt="Processed Image" class="photo">
          <div class="top-left circle" v-if="image.name === ''">
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">

export default {
  emits: ['select-image'],
  props: ['photoGridData'],
};
</script>

<style scoped>
.photo-grid-container {
  width: 100%;
  max-height: 100%;
  overflow-y: auto;
  padding: 1rem;
  padding-bottom: 10rem;
  user-select: none;
}

.photo-grid {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 20px;
}

.photo-item {
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
}

.photo-wrapper {
  display: flex;
  position: relative;
}

.photo {
  border-radius: 2px;
  max-height: 3.4in;
  max-width: 3.4in;
}

.photo-wrapper :hover {
  cursor: pointer;
}

.top-left {
  position: absolute;
  top: 4px;
  left: 4px;
}

.circle {
  background-color: rgb(224, 61, 107);
  width: 13px;
  height: 13px;
  border-radius: 100%;
}
</style>

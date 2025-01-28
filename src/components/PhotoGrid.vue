<template>
  <div v-if="photoGridData.length > 0" class="photo-grid-container">
    <div class="photo-grid">
      <div v-for="(image, index) in photoGridData" :key="index" class="photo-item"
        @click="$emit('select-image', index)">
        <img :src="image.borderedImage" alt="Processed Image" class="photo" />
      </div>
    </div>
  </div>
</template>

<script lang="ts">

export interface photoData {
  borderedImage: string,
  image: HTMLImageElement;
  name: string;
  offsetX: number;
  offsetY: number;
  isPortrait: boolean;
  date: string;
}

export default {
  emits: ['select-image'],
  props: ['photoGridData'],
  data(photoGridData: photoData[]) {
    console.log(photoGridData);
  },
};

</script>

<style scoped>
.photo-grid-container {
  width: 100%;
  max-height: 85vh;
  overflow-y: auto;
  padding: 1rem;
  user-select: none;
}

.photo-grid {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
}

.photo-item {
  display: flex;
  max-width: 40%;
  aspect-ratio: 1;
  justify-content: center;
  align-items: center;
}

.photo {
  display: flex;
  max-width: 90%;
  max-height: 90%;
  height: auto;
  width: auto;
  border-radius: 4px;
}
</style>

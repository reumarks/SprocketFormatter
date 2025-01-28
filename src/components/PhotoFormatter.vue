<template>
  <div class="container">
    <header class="header">
      <h1 class="title">Sprocket Formatter</h1>
      <div class="button-bar">
        <input type="file" accept="image/*" multiple @change="handleFileUpload" class="hidden" id="file-input" />
        <label for="file-input" class="button blue-button">Upload Photos</label>
        <button @click="downloadAll" class="button green-button">Download All</button>
      </div>
    </header>

    <PhotoGrid :photoGridData="photoData" @select-image="selectImage" />

    <div class="image-overlay" :class="{ 'hidden': currentPhotoData == null }">
      <div class="image-viewer">
        <canvas ref="editCanvas" class="edit-canvas"></canvas>
        <div v-if="currentPhotoData !== null" class="bottom-bar">
          <input type="text" placeholder="Filename" class="text-input" v-model="currentPhotoData.name"
            @input="renderCanvas" />
          <input type="text" placeholder="Date" class="text-input" v-model="currentPhotoData.date"
            @input="renderCanvas" />
          <button class="button icon-button blue-button" @click="toggleOrientation">
            <IconRotate />
          </button>
          <button class="button icon-button green-button" @click="closeImage">
            <IconCheck />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import IconRotate from './icons/IconRotate.vue';
import IconCheck from './icons/IconCheck.vue';

import type { photoData } from './PhotoGrid.vue';
import PhotoGrid from './PhotoGrid.vue';

export default defineComponent({
  data() {
    return {
      photoData: [] as photoData[],
      currentPhotoData: null as photoData | null,
      canvas: null as HTMLCanvasElement | null,
      context: null as CanvasRenderingContext2D | null,
    };
  },
  components: {
    PhotoGrid,
    IconRotate,
    IconCheck,
  },
  methods: {
    async handleFileUpload(event: Event): Promise<void> {
      const target = event.target as HTMLInputElement;
      const files = target.files;
      if (!files || files.length === 0) return;

      this.photoData = [];

      const addBorder = (imageFile: File): Promise<photoData | null> => {
        return new Promise((resolve) => {
          const reader = new FileReader();
          const currentImageData: photoData = {
            borderedImage: '',
            image: new Image(),
            name: 'unknown',
            offsetX: 0,
            offsetY: 0,
            date: '00/00/25',
            isPortrait: false
          };
          reader.onload = (e: ProgressEvent<FileReader>) => {
            currentImageData.image.onload = () => {
              if (!this.canvas) {
                resolve(null);
                return;
              }

              currentImageData.isPortrait = currentImageData.image.height > currentImageData.image.width;
              this.canvas.width = currentImageData.isPortrait ? 1070 : 1627;
              this.canvas.height = currentImageData.isPortrait ? 1627 : 1070;

              let sourceHeight = currentImageData.image.height;
              let sourceWidth = currentImageData.image.width;

              const imageWidth = this.canvas.width - 188;
              const imageHeight = this.canvas.height - 188;

              if (currentImageData.isPortrait) {
                sourceWidth = (sourceHeight * imageWidth) / imageHeight;
                currentImageData.offsetY = 0;
                currentImageData.offsetX = (currentImageData.image.width - sourceWidth) / 2;
              } else {
                sourceHeight = (sourceWidth * imageHeight) / imageWidth;
                currentImageData.offsetX = 0;
                currentImageData.offsetY = (currentImageData.image.height - (sourceHeight)) / 2;
              }

              this.renderImage(currentImageData);

              currentImageData.borderedImage = this.canvas.toDataURL('image/png');

              resolve(currentImageData);
            };
            if (e.target?.result) {
              currentImageData.image.src = e.target.result as string;
            }
          };
          reader.readAsDataURL(imageFile);
        });
      };

      for (const file of Array.from(files)) {
        try {
          const borderedImageData = await addBorder(file);
          if (borderedImageData) {
            this.photoData.push(borderedImageData);
          }
        } catch (error) {
          console.error('Error processing image:', error);
        }
      }
    },

    renderImage(currentImageData: photoData) {
      if (!this.canvas || !currentImageData) {
        console.error('Failed to get canvas');
        return;
      }

      const borderSize = 94;
      this.canvas.width = currentImageData.isPortrait ? 1070 : 1627;
      this.canvas.height = currentImageData.isPortrait ? 1627 : 1070;

      let sourceHeight = currentImageData.image.height;
      let sourceWidth = currentImageData.image.width;

      const imageWidth = this.canvas.width - borderSize * 2;
      const imageHeight = this.canvas.height - borderSize * 2;

      if (currentImageData.isPortrait) {
        sourceWidth = (sourceHeight * imageWidth) / imageHeight;
      } else {
        sourceHeight = (sourceWidth * imageHeight) / imageWidth;
      }

      if (!this.context) {
        console.error('Failed to get context');
        return;
      }

      this.context.fillStyle = 'white';
      this.context.fillRect(0, 0, this.canvas.width, this.canvas.height);

      this.context.drawImage(
        currentImageData.image,
        currentImageData.offsetX,
        currentImageData.offsetY,
        sourceWidth,
        sourceHeight,
        borderSize,
        borderSize,
        imageWidth,
        imageHeight
      );

      this.context.fillStyle = "black";
      this.context.font = "55px Arial";
      this.context.textAlign = "left";
      this.context.fillText(`${currentImageData.name}.jpeg`, 95, this.canvas.height - 27);
      this.context.textAlign = "right";
      this.context.fillText(`${currentImageData.date}`, this.canvas.width - 95, this.canvas.height - 27);
      this.context.font = "80px Arial";
      this.context.fillText('...', this.canvas.width - 95, 70);
    },

    downloadAll(): void {
      this.photoData.forEach((image, index) => {
        const link = document.createElement('a');
        link.href = image.borderedImage;
        link.download = `bordered-image-${index + 1}.png`;
        link.click();
      });
    },
    selectImage(index: number): void {
      this.currentPhotoData = this.photoData[index];
      this.renderCanvas();
    },
    closeImage(): void {
      if (this.currentPhotoData !== null && this.canvas !== null) {
        this.currentPhotoData.borderedImage = this.canvas.toDataURL('image/png');
      }
      this.currentPhotoData = null;
    },
    toggleOrientation(): void {
      if (!this.currentPhotoData) return;
      this.currentPhotoData.isPortrait = !this.currentPhotoData.isPortrait;
      this.renderCanvas();
    },
    renderCanvas(): void {
      if (this.currentPhotoData === null || this.canvas === null) return;

      this.canvas.width = this.currentPhotoData.isPortrait ? 1070 : 1627;
      this.canvas.height = this.currentPhotoData.isPortrait ? 1627 : 1070;

      let sourceHeight = this.currentPhotoData.image.height;
      let sourceWidth = this.currentPhotoData.image.width;

      const imageWidth = this.canvas.width - 188;
      const imageHeight = this.canvas.height - 188;

      if (this.currentPhotoData.isPortrait) {
        sourceWidth = (sourceHeight * imageWidth) / imageHeight;
      } else {
        sourceHeight = (sourceWidth * imageHeight) / imageWidth;
      }

      this.currentPhotoData.offsetX = this.currentPhotoData.offsetX < 0 ? 0 : this.currentPhotoData.offsetX;
      this.currentPhotoData.offsetY = this.currentPhotoData.offsetY < 0 ? 0 : this.currentPhotoData.offsetY;
      this.currentPhotoData.offsetX = this.currentPhotoData.offsetX > this.currentPhotoData.image.width - sourceWidth ?
        this.currentPhotoData.image.width - sourceWidth : this.currentPhotoData.offsetX;
      this.currentPhotoData.offsetY = this.currentPhotoData.offsetY > this.currentPhotoData.image.height - sourceHeight ?
        this.currentPhotoData.image.height - sourceHeight : this.currentPhotoData.offsetY;

      this.renderImage(this.currentPhotoData);
    },
  },
  mounted() {
    this.canvas = this.$refs.editCanvas as HTMLCanvasElement;
    this.context = this.canvas.getContext('2d');

    let isDragging = false;
    let startX = 0;
    let startY = 0;

    this.canvas.addEventListener('mousedown', (e) => {
      isDragging = true;
      startX = e.offsetX;
      startY = e.offsetY;
    });

    this.canvas.addEventListener('mousemove', (e) => {
      if (!isDragging || !this.currentPhotoData) return;
      const dx = e.offsetX - startX;
      const dy = e.offsetY - startY;
      this.currentPhotoData.offsetX -= dx * 2;
      this.currentPhotoData.offsetY -= dy * 2;
      startX = e.offsetX;
      startY = e.offsetY;
      this.renderCanvas();
    });

    this.canvas.addEventListener('mouseup', () => {
      isDragging = false;
    });

    this.canvas.addEventListener('mouseleave', () => {
      isDragging = false;
    });
  },
});
</script>

<style>
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

.image-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.8);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.image-viewer {
  display: flex;
  flex-direction: column;
  align-items: center;
  max-width: 90%;
  max-height: 90%;
}

.edit-canvas {
  border: 1px solid #ccc;
  border-radius: 4px;
  background-color: #fff;
  max-width: 100%;
  max-height: 80%;
  margin-bottom: 1rem;
}

.edit-canvas:hover {
  cursor: move;
}

.bottom-bar {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}
</style>

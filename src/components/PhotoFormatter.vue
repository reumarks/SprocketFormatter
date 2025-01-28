<template>
  <div class="container">
    <header class="header">
      <h1 class="title">Sprocket Formatter</h1>
      <div class="button-bar">
        <input type="file" accept="image/*" multiple @change="handleFileUpload" class="hidden" id="file-input" />
        <label for="file-input" class="button upload-button">Upload Photos</label>
        <button @click="downloadAll" class="button download-button">Download All</button>
      </div>
    </header>

    <div v-if="images.length > 0" class="photo-grid-container">
      <div class="photo-grid">
        <div v-for="(image, index) in images" :key="index" class="photo-item" @click="selectImage(index)">
          <img :src="image.borderedImage" alt="Processed Image" class="photo" />
        </div>
      </div>
    </div>

    <div class="image-overlay" :class="{ 'hidden': selectedImageIndex == null || !isImageLoaded }">
      <div class="image-viewer">
        <canvas ref="editCanvas" class="edit-canvas"></canvas>
        <div class="bottom-bar">
          <input type="text" placeholder="Filename" class="text-input" v-model="name" @input="renderCanvas" />
          <input type="text" placeholder="Date" class="text-input" v-model="date" @input="renderCanvas" />
          <button class="button rotate-button" @click="toggleOrientation">
            <IconRotate></IconRotate>
          </button>
          <button class="button close-button" @click="closeImage">
            <IconCheck></IconCheck>
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

interface photoData {
  borderedImage: string,
  originalImage: string;
  name: string;
  offsetX: number;
  offsetY: number;
  isPortrait: boolean;
  date: string;
}

export default defineComponent({
  data() {
    return {
      images: [] as photoData[],
      selectedImageIndex: null as number | null,
      isImageLoaded: false,
      isPortrait: true,
      sourceOffsetX: 0,
      sourceOffsetY: 0,
      name: '',
      date: '',
    };
  },
  components: {
    IconRotate,
    IconCheck,
  },
  methods: {
    async handleFileUpload(event: Event): Promise<void> {
      const target = event.target as HTMLInputElement;
      const files = target.files;
      if (!files || files.length === 0) return;

      this.images = [];

      const addBorder = (imageFile: File): Promise<photoData> => {
        return new Promise((resolve) => {
          const reader = new FileReader();
          reader.onload = (e: ProgressEvent<FileReader>) => {
            const img = new Image();
            img.onload = () => {
              const canvas = document.createElement('canvas');
              const context = canvas.getContext('2d');

              if (!context) {
                console.error('Failed to get canvas context');
                resolve({
                  borderedImage: '',
                  originalImage: '',
                  name: 'unknown',
                  offsetX: 0,
                  offsetY: 0,
                  date: '0/0/0000',
                  isPortrait: false
                });
                return;
              }

              const borderSize = 94;
              const isPortrait = img.height > img.width;
              const canvasWidth = isPortrait ? 1070 : 1627;
              const canvasHeight = isPortrait ? 1627 : 1070;

              canvas.width = canvasWidth;
              canvas.height = canvasHeight;

              let sourceOffsetX = 0;
              let sourceOffsetY = 0;
              let sourceHeight = img.height;
              let sourceWidth = img.width;

              const imageWidth = canvasWidth - borderSize * 2;
              const imageHeight = canvasHeight - borderSize * 2;

              if (isPortrait) {
                sourceWidth = (sourceHeight * imageWidth) / imageHeight;
                sourceOffsetX = (img.width - sourceWidth) / 2;
              } else {
                sourceHeight = (sourceWidth * imageHeight) / imageWidth;
                sourceOffsetY = (img.height - sourceHeight) / 2;
              }

              context.fillStyle = 'white';
              context.fillRect(0, 0, canvasWidth, canvasHeight);
              context.drawImage(
                img,
                sourceOffsetX,
                sourceOffsetY,
                sourceWidth,
                sourceHeight,
                borderSize,
                borderSize,
                imageWidth,
                imageHeight
              );

              context.fillStyle = "black";
              context.font = "55px Arial";
              context.textAlign = "left";
              context.fillText('file_name.jpeg', 95, canvasHeight - 27);
              context.textAlign = "right";
              context.fillText('00/00/25', canvasWidth - 95, canvasHeight - 27);
              context.font = "80px Arial";
              context.fillText('...', canvasWidth - 95, 70);

              resolve({
                borderedImage: canvas.toDataURL('image/png'),
                originalImage: '',
                name: 'file_name',
                offsetX: sourceOffsetX,
                offsetY: sourceOffsetY,
                date: '00/00/25',
                isPortrait: isPortrait
              });
            };
            if (e.target?.result) {
              img.src = e.target.result as string;
            }
          };
          reader.readAsDataURL(imageFile);
        });
      };

      for (const file of Array.from(files)) {
        try {
          const borderedImageData = await addBorder(file);
          if (borderedImageData) {
            borderedImageData.originalImage = URL.createObjectURL(file);
            this.images.push(borderedImageData);
          }
        } catch (error) {
          console.error('Error processing image:', error);
        }
      }
    },

    downloadAll(): void {
      this.images.forEach((image, index) => {
        const link = document.createElement('a');
        link.href = image.borderedImage;
        link.download = `bordered-image-${index + 1}.png`;
        link.click();
      });
    },
    selectImage(index: number): void {
      this.isImageLoaded = false;
      this.selectedImageIndex = index;

      this.isPortrait = this.images[this.selectedImageIndex].isPortrait;
      this.sourceOffsetX = this.images[this.selectedImageIndex].offsetX;
      this.sourceOffsetY = this.images[this.selectedImageIndex].offsetY;
      this.name = this.images[this.selectedImageIndex].name;
      this.date = this.images[this.selectedImageIndex].date;

      this.renderCanvas();
    },
    closeImage(): void {
      if (this.selectedImageIndex !== null) {
        const canvas = this.$refs.editCanvas as HTMLCanvasElement;
        this.images[this.selectedImageIndex].borderedImage = canvas.toDataURL('image/png');
        this.images[this.selectedImageIndex].offsetX = this.sourceOffsetX;
        this.images[this.selectedImageIndex].offsetY = this.sourceOffsetY;
        this.images[this.selectedImageIndex].isPortrait = this.isPortrait;
        this.images[this.selectedImageIndex].name = this.name;
        this.images[this.selectedImageIndex].date = this.date;
      }
      this.selectedImageIndex = null;
    },
    toggleOrientation(): void {
      this.isPortrait = !this.isPortrait;
      this.renderCanvas();
    },
    renderCanvas(): void {
      if (this.selectedImageIndex === null) return;

      const canvas = this.$refs.editCanvas as HTMLCanvasElement;
      const context = canvas.getContext('2d');

      if (!context) {
        console.error('Failed to get canvas context');
        return;
      }

      const img = new Image();
      img.onload = () => {
        const borderSize = 94;
        const canvasWidth = this.isPortrait ? 1070 : 1627;
        const canvasHeight = this.isPortrait ? 1627 : 1070;

        canvas.width = canvasWidth;
        canvas.height = canvasHeight;

        const imageWidth = canvasWidth - borderSize * 2;
        const imageHeight = canvasHeight - borderSize * 2;

        let sourceWidth = img.width;
        let sourceHeight = img.height;

        if (this.isPortrait) {
          sourceWidth = (sourceHeight * imageWidth) / imageHeight;
        } else {
          sourceHeight = (sourceWidth * imageHeight) / imageWidth;
        }

        this.sourceOffsetX = this.sourceOffsetX < 0 ? 0 : this.sourceOffsetX;
        this.sourceOffsetY = this.sourceOffsetY < 0 ? 0 : this.sourceOffsetY;
        this.sourceOffsetX = this.sourceOffsetX > img.width - sourceWidth ? img.width - sourceWidth : this.sourceOffsetX;
        this.sourceOffsetY = this.sourceOffsetY > img.height - sourceHeight ? img.height - sourceHeight : this.sourceOffsetY;

        context.fillStyle = 'white';
        context.fillRect(0, 0, canvasWidth, canvasHeight);
        context.drawImage(
          img,
          this.sourceOffsetX,
          this.sourceOffsetY,
          sourceWidth,
          sourceHeight,
          borderSize,
          borderSize,
          imageWidth,
          imageHeight
        );

        this.name = this.name.replace(' ', '_');
        context.fillStyle = "black";
        context.font = "55px Arial";
        context.textAlign = "left";
        context.fillText(this.name + '.jpeg', 95, canvasHeight - 27);
        context.textAlign = "right";
        context.fillText(this.date, canvasWidth - 95, canvasHeight - 27);
        context.font = "80px Arial";
        context.fillText('...', canvasWidth - 95, 70);

        this.isImageLoaded = true;
      };

      img.src = this.images[this.selectedImageIndex].originalImage;
    },
  },
  mounted() {
    const canvas = this.$refs.editCanvas as HTMLCanvasElement;
    let isDragging = false;
    let startX = 0;
    let startY = 0;

    canvas.addEventListener('mousedown', (e) => {
      isDragging = true;
      startX = e.offsetX;
      startY = e.offsetY;
    });

    canvas.addEventListener('mousemove', (e) => {
      if (!isDragging) return;
      const dx = e.offsetX - startX;
      const dy = e.offsetY - startY;
      this.sourceOffsetX -= dx * 2;
      this.sourceOffsetY -= dy * 2;
      startX = e.offsetX;
      startY = e.offsetY;
      this.renderCanvas();
    });

    canvas.addEventListener('mouseup', () => {
      isDragging = false;
    });

    canvas.addEventListener('mouseleave', () => {
      isDragging = false;
    });
  },
});
</script>

<style>
body {
  font-family: Arial, sans-serif;
  margin: 0;
  padding: 0;
}

.container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1rem;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  background-color: #282828;
  padding: 1rem;
  box-shadow: 0 2px 4px rgba(123, 34, 175, 0.1);
  border-radius: 4px;
}

.title {
  user-select: none;
  font-size: 1.5rem;
  font-weight: bold;
  margin: 0;
  padding-right: 1rem;
}

.hidden {
  display: none !important;
}

.button-bar {
  display: flex;
  gap: 0.5rem;
}

.button {
  padding: 0.5rem 1rem;
  font-size: 1rem;
  font-weight: bold;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  text-align: center;
  user-select: none;
}

.upload-button {
  background-color: #007bff;
  color: #fff;
}

.upload-button:hover {
  background-color: #0056b3;
}

.download-button {
  background-color: #28a745;
  color: #fff;
}

.download-button:hover {
  background-color: #1e7e34;
}

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

.text-input {
  padding: 0.5rem;
  font-size: 1rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  width: 150px;
}

.rotate-button {
  background-color: #515151;
  color: #ffffff;
  padding: 0px;
  padding-top: 5px;
  height: 100%;
  aspect-ratio: 1.2;
}

.rotate-button:hover {
  background-color: #3b3b3b;
}

.close-button {
  background-color: #007bff;
  color: #ffffff;
  padding: 0px;
  padding-top: 5px;
  height: 100%;
  aspect-ratio: 1.2;
}

.close-button:hover {
  background-color: #0056b3;
}

.delete-button {
  background-color: #dc3545;
  color: #fff;
}

.delete-button:hover {
  background-color: #b21f2d;
}
</style>

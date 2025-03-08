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

    <PhotoGrid :photoGridData="photoData" :class="{ 'photo-grid-lock': photosLoading == true }"
      @select-image="selectImage" />
  </div>

  <div class="image-overlay" :class="{ 'hidden': currentPhotoData == null }">
    <div class="image-viewer">
      <input v-if="currentPhotoData !== null && !currentPhotoData.isPortrait" type="range" min="1" max="5" step="0.01"
        value="1" style="width: min(100%, 600px)" v-model="currentPhotoData.scale">
      <div class="canvas-wrapper">
        <canvas ref="editCanvas" class="edit-canvas"></canvas>
        <input v-if="currentPhotoData !== null && currentPhotoData.isPortrait" type="range" min="1" max="5" step="0.01"
          value="1" class="vertical zoom-slider" orient="vertical" v-model="currentPhotoData.scale">
      </div>
      <div v-if="currentPhotoData !== null" class="bottom-bar">
        <div class="button-group">
          <input type="text" placeholder="photo_name" class="text-input" v-model="currentPhotoData.name" />
          <VueDatePicker v-model="currentPhotoData.date" :enable-time-picker="false" :format="format" auto-apply
            style="max-width: 140px;">
          </VueDatePicker>
        </div>
        <div class="button-group">
          <button class="button icon-button red-button" style="width: 50px;" @click="deleteImage">
            <IconTrash />
          </button>
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
import IconTrash from './icons/IconTrash.vue';
import IconRotate from './icons/IconRotate.vue';
import IconCheck from './icons/IconCheck.vue';
import PhotoGrid from './PhotoGrid.vue';
import VueDatePicker from '@vuepic/vue-datepicker';
import '@vuepic/vue-datepicker/dist/main.css'
import EXIF from 'exif-js';
import { downloadZip } from 'client-zip';

interface photoData {
  borderedImage: string,
  image: HTMLImageElement;
  name: string;
  filename: string;
  date: Date;
  offsetX: number;
  offsetY: number;
  sourceW: number;
  sourceH: number;
  isPortrait: boolean;
  scale: number;
}

export default defineComponent({
  data() {
    return {
      photoData: [] as photoData[],
      currentPhotoIndex: null as number | null,
      currentPhotoData: null as photoData | null,
      canvas: null as HTMLCanvasElement | null,
      context: null as CanvasRenderingContext2D | null,
      mouseIsPressed: false,
      mouseX: 0 as number | null,
      mouseY: 0 as number | null,
      pmouseX: 0 as number | null,
      pmouseY: 0 as number | null,
      isCanvasActive: false,
      sprocketFont: null as FontFace | null,
      photosLoading: false,
    };
  },
  components: {
    PhotoGrid,
    IconRotate,
    IconCheck,
    IconTrash,
    VueDatePicker,
  },
  methods: {
    format(date: Date) {
      if (date === null) {
        return `00/00/00`;
      }
      const day = ("0" + date.getDate()).slice(-2)
      const month = ("0" + (date.getMonth() + 1)).slice(-2)
      const year = ("" + date.getFullYear()).slice(-2)

      return `${month}/${day}/${year}`;
    },
    async handleMetadataUpload(event: Event): Promise<void> {
      const target = event.target as HTMLInputElement;
      const files = target.files;
      if (!files || files.length === 0) return;
      return new Promise((resolve, reject) => {
        const fileReader = new FileReader()
        fileReader.onload = (e: ProgressEvent<FileReader>) => {
          const jsonObject = JSON.parse(e.target?.result as string)
          for (let jsonPhotoIndex = 0; jsonPhotoIndex < jsonObject.photos.length; jsonPhotoIndex++) {
            for (let currentPhotoIndex = 0; currentPhotoIndex < this.photoData.length; currentPhotoIndex++) {
              if (this.photoData[currentPhotoIndex].filename == jsonObject.photos[jsonPhotoIndex].filename) {
                this.photoData[currentPhotoIndex].date = new Date(jsonObject.photos[jsonPhotoIndex].date)
                this.selectImage(currentPhotoIndex)
                this.closeImage()
              }
            }
          }
          resolve()
        }
        fileReader.onerror = error => reject(error)
        fileReader.readAsText(files[0])
      })
    },

    // @ts-expect-error because
    parseDate(s) {
      const b = s.split(/\D/);
      return new Date(b[0], b[1] - 1, b[2], b[3], b[4], b[5]);
    },
    async handleFileUpload(event: Event): Promise<void> {
      const target = event.target as HTMLInputElement;
      const files = target.files;
      if (!files || files.length === 0) return;

      const addBorder = async (imageFile: File): Promise<photoData | null> => {
        return new Promise(async (resolve) => {
          const reader = new FileReader();

          const currentImageData: photoData = {
            borderedImage: '',
            image: new Image(),
            name: '',
            offsetX: 0,
            offsetY: 0,
            sourceH: 0,
            sourceW: 0,
            scale: 1,
            filename: imageFile.name,
            date: new Date(imageFile.lastModified),
            isPortrait: false,
          };

          const exifDate = await new Promise(resolve =>
            // @ts-expect-error exif does not have proper type support
            EXIF.getData(imageFile, function () {
              // @ts-expect-error exif does not have proper type support
              resolve(EXIF.getTag(this, "DateTimeOriginal"))
            }));

          if (exifDate != undefined) {
            console.log(this.parseDate(exifDate))
            currentImageData.date = this.parseDate(exifDate)
          }

          reader.onload = (e: ProgressEvent<FileReader>) => {
            currentImageData.image.onload = () => {
              if (!this.canvas) {
                resolve(null);
                return;
              }

              currentImageData.isPortrait = currentImageData.image.height > currentImageData.image.width;
              this.canvas.width = currentImageData.isPortrait ? 1070 : 1627;
              this.canvas.height = currentImageData.isPortrait ? 1627 : 1070;

              const imageWidth = this.canvas.width - 188;
              const imageHeight = this.canvas.height - 188;

              if (currentImageData.isPortrait) {
                currentImageData.sourceH = currentImageData.image.height;
                currentImageData.sourceW = (currentImageData.image.height * imageWidth) / imageHeight;
                currentImageData.offsetY = 0;
                currentImageData.offsetX = (currentImageData.image.width - currentImageData.sourceW) / 2;
              } else {
                currentImageData.sourceW = currentImageData.image.width;
                currentImageData.sourceH = (currentImageData.image.width * imageHeight) / imageWidth;
                currentImageData.offsetX = 0;
                currentImageData.offsetY = (currentImageData.image.height - (currentImageData.sourceH)) / 2;
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
      this.photoData = this.photoData.sort((a, b) => a.date.getTime() - b.date.getTime());
      this.photosLoading = false;
    },

    renderImage(currentImageData: photoData) {
      if (!this.canvas || !currentImageData) {
        console.error('Failed to get canvas');
        return;
      }

      const borderSize = 94;

      const imageWidth = this.canvas.width - borderSize * 2;
      const imageHeight = this.canvas.height - borderSize * 2;

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
        currentImageData.sourceW,
        currentImageData.sourceH,
        borderSize,
        borderSize,
        imageWidth,
        imageHeight
      );

      this.context.fillStyle = "black";
      this.context.font = "52px KleeOne";
      this.context.textAlign = "left";
      const name = currentImageData.name == '' ? 'photo_name' : currentImageData.name;
      this.context.fillText(`${name}.jpeg`, 95, this.canvas.height - 35);
      this.context.font = "49px KleeOne";
      this.context.textAlign = "right";
      this.context.fillText(`${this.format(currentImageData.date)}`, this.canvas.width - 95, this.canvas.height - 35);
      this.context.font = "70px KleeOne";
      this.context.fillText('...', this.canvas.width - 95, 70);
    },
    dataURItoBlob(dataURI: string) {
      // convert base64 to raw binary data held in a string
      // doesn't handle URLEncoded DataURIs - see SO answer #6850276 for code that does this
      const byteString = atob(dataURI.split(',')[1]);

      // separate out the mime component
      const mimeString = dataURI.split(',')[0].split(':')[1].split(';')[0]

      // write the bytes of the string to an ArrayBuffer
      const ab = new ArrayBuffer(byteString.length);

      // create a view into the buffer
      const ia = new Uint8Array(ab);

      // set the bytes of the buffer to the correct values
      for (let i = 0; i < byteString.length; i++) {
        ia[i] = byteString.charCodeAt(i);
      }

      // write the ArrayBuffer to a blob, and you're done
      const blob = new Blob([ab], { type: mimeString });
      return blob;

    },
    async downloadAll(): Promise<void> {
      const boarderedImages = this.photoData.map((image, index) => { return { name: `bordered-image-${index + 1}.png`, lastModified: new Date(), input: this.dataURItoBlob(image.borderedImage) } })
      const blob = await downloadZip(boarderedImages).blob()
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob)
      link.download = `SprocketPhotos.zip`
      link.click()
      link.remove()
    },
    selectImage(index: number): void {
      if (this.photosLoading === true) return;
      this.currentPhotoIndex = index;
      this.currentPhotoData = this.photoData[this.currentPhotoIndex];

      if (!this.canvas) return;

      this.canvas.width = this.currentPhotoData.isPortrait ? 1070 : 1627;
      this.canvas.height = this.currentPhotoData.isPortrait ? 1627 : 1070;

      if (this.isCanvasActive == false) {
        this.isCanvasActive = true;
        this.updateCanvas();
      }
    },
    closeImage(): void {
      if (this.currentPhotoData !== null && this.canvas !== null) {
        this.currentPhotoData.borderedImage = this.canvas.toDataURL('image/png');
      }
      this.photoData = this.photoData.sort((a, b) => a.date.getTime() - b.date.getTime());
      this.currentPhotoData = null;
      this.currentPhotoIndex = null;
    },
    deleteImage(): void {
      if (this.currentPhotoIndex === null) return;
      this.photoData.splice(this.currentPhotoIndex, 1);
      this.currentPhotoData = null;
      this.currentPhotoIndex = null;
    },
    toggleOrientation(): void {
      if (!this.currentPhotoData || !this.canvas) return;
      this.currentPhotoData.isPortrait = !this.currentPhotoData.isPortrait;

      this.canvas.width = this.currentPhotoData.isPortrait ? 1070 : 1627;
      this.canvas.height = this.currentPhotoData.isPortrait ? 1627 : 1070;

      const imageWidth = this.canvas.width - 188;
      const imageHeight = this.canvas.height - 188;

      if (this.currentPhotoData.isPortrait) {
        this.currentPhotoData.sourceH = this.currentPhotoData.image.height;
        this.currentPhotoData.sourceW = (this.currentPhotoData.image.height * imageWidth) / imageHeight;
        this.currentPhotoData.offsetY = 0;
        this.currentPhotoData.offsetX = (this.currentPhotoData.image.width - this.currentPhotoData.sourceW) / 2;
      } else {
        this.currentPhotoData.sourceW = this.currentPhotoData.image.width;
        this.currentPhotoData.sourceH = (this.currentPhotoData.image.width * imageHeight) / imageWidth;
        this.currentPhotoData.offsetX = 0;
        this.currentPhotoData.offsetY = (this.currentPhotoData.image.height - (this.currentPhotoData.sourceH)) / 2;
      }

      this.currentPhotoData.scale = 1;
    },
    updateCanvas(): void {
      if (this.canvas === null) return;

      if (this.currentPhotoData === null || this.isCanvasActive === false) {
        this.isCanvasActive = false;
        return;
      }

      if (this.mouseIsPressed) {
        if (this.mouseX && this.pmouseX && this.mouseY && this.pmouseY) {
          this.currentPhotoData.offsetX += (this.pmouseX - this.mouseX) * 2 / Math.sqrt(this.currentPhotoData.scale);
          this.currentPhotoData.offsetY += (this.pmouseY - this.mouseY) * 2 / Math.sqrt(this.currentPhotoData.scale);
        }
      } else {
        this.mouseX = null;
        this.mouseY = null;
      }

      this.pmouseY = this.mouseY;
      this.pmouseX = this.mouseX;

      const imageWidth = this.canvas.width - 188;
      const imageHeight = this.canvas.height - 188;

      if (this.currentPhotoData.isPortrait) {
        this.currentPhotoData.sourceH = this.currentPhotoData.image.height / Math.sqrt(this.currentPhotoData.scale);
        this.currentPhotoData.sourceW = (this.currentPhotoData.image.height * imageWidth) / imageHeight / Math.sqrt(this.currentPhotoData.scale);
      } else {
        this.currentPhotoData.sourceW = this.currentPhotoData.image.width / Math.sqrt(this.currentPhotoData.scale);
        this.currentPhotoData.sourceH = (this.currentPhotoData.image.width * imageHeight) / imageWidth / Math.sqrt(this.currentPhotoData.scale);
      }

      this.currentPhotoData.offsetX = this.constrain(
        this.currentPhotoData.offsetX,
        0,
        this.currentPhotoData.image.width - this.currentPhotoData.sourceW
      );

      this.currentPhotoData.offsetY = this.constrain(
        this.currentPhotoData.offsetY,
        0,
        this.currentPhotoData.image.height - this.currentPhotoData.sourceH
      );

      this.currentPhotoData.name = this.currentPhotoData.name.replace(' ', '_');

      this.renderImage(this.currentPhotoData);

      requestAnimationFrame(this.updateCanvas);
    },
    constrain(value: number, min: number, max: number): number {
      if (value < min) return min;
      if (value > max) return max;
      return value;
    },
  },
  mounted() {
    this.canvas = this.$refs.editCanvas as HTMLCanvasElement;
    this.context = this.canvas.getContext('2d');

    const sprocketFont = new FontFace(
      "KleeOne",
      "url(https://fonts.gstatic.com/s/kleeone/v12/LDI2apCLNRc6A8oT4pbYF_Oreec.woff2)",
    );

    sprocketFont.load().then((font) => {
      document.fonts.add(font);
      console.log('font added');
    });

    this.canvas.addEventListener('mousedown', () => {
      this.mouseIsPressed = true;
    });

    this.canvas.addEventListener('touchstart', () => {
      this.mouseIsPressed = true;
    });

    this.canvas.addEventListener('mousemove', (e) => {
      if (!this.currentPhotoData || !this.canvas) return;

      const boundingRect = this.canvas.getBoundingClientRect();
      const scale = this.canvas.width / boundingRect.width;
      this.mouseX = (e.clientX - boundingRect.left) * scale;
      this.mouseY = (e.clientY - boundingRect.top) * scale;
    });

    this.canvas.addEventListener('touchmove', (e) => {
      e.preventDefault();
      if (!this.currentPhotoData || !this.canvas) return;

      const boundingRect = this.canvas.getBoundingClientRect();
      const scale = this.canvas.width / boundingRect.width;

      const touch = e.touches[0];

      this.mouseX = (touch.screenX - boundingRect.left) * scale;
      this.mouseY = (touch.screenY - boundingRect.top) * scale;
    });

    this.canvas.addEventListener('mouseup', () => {
      this.mouseIsPressed = false;
    });

    this.canvas.addEventListener('touchend', () => {
      this.mouseIsPressed = false;
    });

    this.canvas.addEventListener('mouseleave', () => {
      this.mouseIsPressed = false;
    });

  },
});
</script>

<style>
.photo-grid-lock :hover {
  cursor: wait !important;
}

.image-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.4);
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
  justify-content: center;
  gap: 0.5rem;
}

.canvas-wrapper {
  display: flex;
  position: relative;
  max-width: min(600px, 100%);
  max-height: min(600px, 80%);
}

.edit-canvas {
  border-radius: 2px;
  background-color: #fff;
  max-width: 100%;
  max-height: 100%;
}

.edit-canvas:hover {
  cursor: move;
}

.zoom-slider {
  -webkit-appearance: slider-vertical;
  writing-mode: bt-lr;
  width: 30px;
}

.bottom-bar {
  display: flex;
  gap: 0.5rem;
  flex-direction: row;
  flex-wrap: wrap;
  justify-content: center;
  width: min(100%, 600px)
}

.floating-date {
  position: absolute;
  top: 0px;
  left: 0px;
  display: flex;
  gap: 0.5rem;
}
</style>

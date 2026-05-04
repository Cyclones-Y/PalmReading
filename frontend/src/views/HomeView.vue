<script setup>
import { computed, onBeforeUnmount, ref } from 'vue'
import { useRouter } from 'vue-router'
import { createPalmReading } from '../api/palmReadings'

const router = useRouter()
const fileInput = ref(null)
const cameraInput = ref(null)
const selectedFile = ref(null)
const previewUrl = ref('')
const isUploading = ref(false)
const errorMessage = ref('')

const selectedFileName = computed(() => selectedFile.value?.name || '')

onBeforeUnmount(() => {
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value)
  }
})

function openCamera() {
  cameraInput.value?.click()
}

function openAlbum() {
  fileInput.value?.click()
}

function onFileChange(event) {
  const file = event.target.files?.[0]
  if (!file) {
    return
  }
  selectedFile.value = file
  errorMessage.value = ''
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value)
  }
  previewUrl.value = URL.createObjectURL(file)
}

async function submit() {
  if (!selectedFile.value) {
    errorMessage.value = '请先拍照或选择一张手掌照片'
    return
  }
  isUploading.value = true
  errorMessage.value = ''
  try {
    const response = await createPalmReading(selectedFile.value)
    router.push({
      name: 'reading',
      params: { readingId: response.readingId },
      query: { token: response.shareToken }
    })
  } catch (error) {
    errorMessage.value = error.message || '上传失败，请稍后重试'
  } finally {
    isUploading.value = false
  }
}
</script>

<template>
  <main class="home-shell">
    <section class="capture-panel" aria-labelledby="home-title">
      <div class="home-copy">
        <p class="eyebrow">你的掌心，自有答案的线索</p>
        <h1 id="home-title">从掌心纹路，看见你的性格底色与行动节奏</h1>
        <p class="home-lead">
          上传一张清晰掌心照，系统会将主要掌纹、手型倾向与事业、情感、健康三个维度整理成一份中文解读。排版整洁，适合自己慢慢阅读，也方便分享给朋友。
        </p>

        <div class="home-proof" aria-label="解读内容">
          <span>看见性格底色</span>
          <span>梳理行动节奏</span>
          <span>生成中文报告</span>
        </div>

        <div class="hero-card" aria-hidden="true">
          <div class="hero-card__image"></div>
          <div class="hero-card__content">
            <span>掌纹不是结论，而是一份观察自己的线索。</span>
            <strong>把模糊的倾向整理成清晰的文字，让你更容易读懂当下的状态。</strong>
          </div>
        </div>
      </div>

      <div class="upload-box" aria-label="上传手掌照片">
        <div class="upload-head">
          <p>开启解读</p>
          <h2>上传掌心照，生成你的专属解读</h2>
        </div>

        <div class="preview-frame" :class="{ 'has-preview': previewUrl }">
          <img v-if="previewUrl" :src="previewUrl" alt="已选择的手掌照片预览" />
          <div v-else class="empty-preview">
            <span class="empty-preview__image"></span>
            <span>等待一张清晰掌心照</span>
            <small>手掌展开、光线均匀，掌纹越清楚，报告越有参考感</small>
          </div>
          <i class="preview-corner top-left"></i>
          <i class="preview-corner top-right"></i>
          <i class="preview-corner bottom-left"></i>
          <i class="preview-corner bottom-right"></i>
        </div>

        <p v-if="selectedFileName" class="file-name">{{ selectedFileName }}</p>
        <p v-else class="upload-hint">支持 JPG / PNG / WEBP，单张图片最大 10MB。无需注册，上传后即可生成。</p>

        <div class="upload-actions">
          <button type="button" class="primary-btn" @click="openCamera">直接拍照</button>
          <button type="button" class="secondary-btn" @click="openAlbum">从相册选择</button>
        </div>
        <button type="button" class="submit-btn" :disabled="isUploading" @click="submit">
          {{ isUploading ? '正在生成...' : '生成手相指南' }}
        </button>
        <p v-if="errorMessage" class="error-text">{{ errorMessage }}</p>
        <p class="privacy-note">图片仅用于本次解读，默认 7 天后过期；报告生成后可复制链接分享。</p>
      </div>

      <input
        ref="cameraInput"
        class="visually-hidden"
        type="file"
        accept="image/jpeg,image/png,image/webp"
        capture="environment"
        @change="onFileChange"
      />
      <input
        ref="fileInput"
        class="visually-hidden"
        type="file"
        accept="image/jpeg,image/png,image/webp"
        @change="onFileChange"
      />
    </section>
  </main>
</template>

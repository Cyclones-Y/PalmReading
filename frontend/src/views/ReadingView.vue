<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import PalmReport from '../components/PalmReport.vue'
import { getPalmReading } from '../api/palmReadings'

const route = useRoute()
const reading = ref(null)
const isLoading = ref(true)
const errorMessage = ref('')
const progressTick = ref(0)
let pollTimer = null
let progressTimer = null

const analysisSteps = [
  {
    title: '确认掌心照片',
    description: '查看画面清晰度，整理可见的掌心细节'
  },
  {
    title: '梳理掌形特征',
    description: '结合手型比例与掌心区域，形成初步印象'
  },
  {
    title: '阅读主要纹路',
    description: '依次查看感情线、智慧线、生命线与事业线'
  },
  {
    title: '整理三项主题',
    description: '围绕事业方向、情感关系与日常状态生成解读'
  },
  {
    title: '装订专属报告',
    description: '把解读内容排成完整页面，稍后即可查看'
  }
]

const shareUrl = computed(() => {
  const token = route.query.token || reading.value?.shareToken
  if (!token) {
    return ''
  }
  const basePath = import.meta.env.BASE_URL.replace(/\/$/, '')
  return `${window.location.origin}${basePath}/r/${token}`
})

const progressPercent = computed(() => {
  if (reading.value?.status === 'succeeded') {
    return 100
  }
  return Math.min(92, 8 + progressTick.value * 4)
})

const activeStepIndex = computed(() => {
  if (reading.value?.status === 'succeeded') {
    return analysisSteps.length - 1
  }
  const index = Math.floor((progressPercent.value / 100) * analysisSteps.length)
  return Math.min(analysisSteps.length - 1, index)
})

const currentStep = computed(() => analysisSteps[activeStepIndex.value])

onMounted(() => {
  startProgressLoop()
  fetchReading()
})

onBeforeUnmount(() => {
  clearTimers()
})

async function fetchReading() {
  isLoading.value = true
  try {
    const payload = await getPalmReading(route.params.readingId)
    reading.value = payload
    errorMessage.value = ''
    if (payload.status === 'processing') {
      pollTimer = window.setTimeout(fetchReading, 1200)
    } else {
      stopProgressLoop()
    }
  } catch (error) {
    errorMessage.value = error.status === 410 ? '报告已过期' : error.message
    stopProgressLoop()
  } finally {
    isLoading.value = false
  }
}

function startProgressLoop() {
  if (progressTimer) {
    return
  }
  progressTimer = window.setInterval(() => {
    progressTick.value += 1
  }, 900)
}

function stopProgressLoop() {
  if (progressTimer) {
    window.clearInterval(progressTimer)
    progressTimer = null
  }
}

function clearTimers() {
  if (pollTimer) {
    window.clearTimeout(pollTimer)
    pollTimer = null
  }
  stopProgressLoop()
}

function stepNumber(index) {
  return String(index + 1).padStart(2, '0')
}
</script>

<template>
  <section v-if="errorMessage" class="state-page">
    <div class="state-card">
      <h1>{{ errorMessage }}</h1>
      <RouterLink to="/" class="secondary-btn">重新生成</RouterLink>
    </div>
  </section>

  <section v-else-if="!reading || reading.status === 'processing'" class="state-page">
    <div class="state-card analysis-card" aria-live="polite">
      <p class="eyebrow">掌心解读正在准备</p>
      <h1>正在整理你的专属报告</h1>
      <p>请稍等片刻，报告准备好后会自动打开。当前正在：{{ currentStep.title }}</p>

      <div class="analysis-visual" aria-hidden="true">
        <div class="scan-frame">
          <span class="scan-print"></span>
          <span class="scan-line"></span>
        </div>
      </div>

      <div class="progress-panel">
        <div class="progress-head">
          <span>{{ currentStep.description }}</span>
          <strong>{{ progressPercent }}%</strong>
        </div>
        <div class="progress-track">
          <div class="progress-fill" :style="{ width: `${progressPercent}%` }"></div>
        </div>
      </div>

      <ol class="analysis-steps">
        <li
          v-for="(step, index) in analysisSteps"
          :key="step.title"
          :class="{ done: index < activeStepIndex, active: index === activeStepIndex }"
        >
          <span class="step-index">{{ stepNumber(index) }}</span>
          <span>
            <b>{{ step.title }}</b>
            <small>{{ step.description }}</small>
          </span>
        </li>
      </ol>
    </div>
  </section>

  <section v-else-if="reading.status === 'failed'" class="state-page">
    <div class="state-card">
      <h1>生成失败</h1>
      <p>本次解读暂时没有生成成功，请重新上传一张更清晰的掌心照，或稍后再试。</p>
      <RouterLink to="/" class="secondary-btn">重新上传</RouterLink>
    </div>
  </section>

  <PalmReport v-else :result="reading.result" :share-url="shareUrl" />
</template>

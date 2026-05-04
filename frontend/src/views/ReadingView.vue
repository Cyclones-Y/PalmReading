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
    title: '接收手掌照片',
    description: '校验图片格式，并准备进入掌纹识别流程'
  },
  {
    title: '识别手型轮廓',
    description: '定位掌心、手指比例和主要掌区'
  },
  {
    title: '提取主要掌纹',
    description: '整理感情线、智慧线、生命线和事业线'
  },
  {
    title: '生成三项解读',
    description: '围绕事业、情感与健康生成中文分析'
  },
  {
    title: '排版报告页面',
    description: '套用极简复古模板，准备展示完整指南'
  }
]

const shareUrl = computed(() => {
  const token = route.query.token || reading.value?.shareToken
  if (!token) {
    return ''
  }
  return `${window.location.origin}/r/${token}`
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
      <p class="eyebrow">ANALYSING PALM LINES</p>
      <h1>正在生成你的手相指南</h1>
      <p>服务器完成后会自动打开报告页。当前正在：{{ currentStep.title }}</p>

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
      <p>{{ reading.errorMessage || 'AI 分析暂时不可用，请稍后重试。' }}</p>
      <RouterLink to="/" class="secondary-btn">重新上传</RouterLink>
    </div>
  </section>

  <PalmReport v-else :result="reading.result" :share-url="shareUrl" />
</template>

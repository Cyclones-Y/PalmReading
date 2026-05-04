<script setup>
import { computed, onBeforeUnmount, ref } from 'vue'
import PalmIllustration from './PalmIllustration.vue'
import { fallbackReading } from '../data/fallbackReading'

const props = defineProps({
  result: {
    type: Object,
    required: true
  },
  shareUrl: {
    type: String,
    default: ''
  }
})

const copyState = ref('idle')
let copyResetTimer = null

const report = computed(() => ({
  ...fallbackReading,
  ...props.result,
  handInfo: {
    ...fallbackReading.handInfo,
    ...(props.result?.handInfo || {})
  }
}))

const majorLines = computed(() => {
  const order = ['heartLine', 'headLine', 'lifeLine', 'fateLine']
  const lines = report.value.majorLines || []
  return order.map((key) => lines.find((line) => line.key === key) || fallbackReading.majorLines.find((line) => line.key === key))
})

const aspects = computed(() => {
  const order = ['career', 'love', 'health']
  const items = report.value.aspects || []
  return order.map((key) => items.find((item) => item.key === key) || fallbackReading.aspects.find((item) => item.key === key))
})

const copyButtonText = computed(() => {
  if (copyState.value === 'copied') {
    return '已复制'
  }
  if (copyState.value === 'failed') {
    return '复制失败'
  }
  return '复制'
})

onBeforeUnmount(() => {
  if (copyResetTimer) {
    window.clearTimeout(copyResetTimer)
  }
})

async function copyShareUrl() {
  if (!props.shareUrl) {
    return
  }
  try {
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(props.shareUrl)
    } else if (!copyWithFallback(props.shareUrl)) {
      throw new Error('copy failed')
    }
    setCopyState('copied')
  } catch {
    setCopyState(copyWithFallback(props.shareUrl) ? 'copied' : 'failed')
  }
}

function setCopyState(state) {
  copyState.value = state
  if (copyResetTimer) {
    window.clearTimeout(copyResetTimer)
  }
  copyResetTimer = window.setTimeout(() => {
    copyState.value = 'idle'
    copyResetTimer = null
  }, 1800)
}

function copyWithFallback(text) {
  const textarea = document.createElement('textarea')
  textarea.value = text
  textarea.setAttribute('readonly', '')
  textarea.style.position = 'fixed'
  textarea.style.top = '-9999px'
  textarea.style.opacity = '0'
  document.body.appendChild(textarea)
  textarea.select()
  const isCopied = document.execCommand('copy')
  document.body.removeChild(textarea)
  return isCopied
}
</script>

<template>
  <main class="report-page">
    <section class="report-top" aria-labelledby="guide-title">
      <div>
        <p class="eyebrow">PALM READING GUIDE</p>
        <h1 id="guide-title">你的手相<br />解读指南</h1>
        <div class="rule"></div>
        <div class="kicker">掌纹 · 性格 · 路径</div>
        <p class="intro">
          根据上传照片生成。传统手相里，左手常被理解为内在天赋与潜在倾向，右手更偏向现实中的行动方式与后天发展；若你有明确惯用手，也可以结合自身习惯理解。以下解读以主要掌纹为核心，不对模糊细纹做过度延伸。
        </p>
        <div class="meta">
          <div class="meta-item">
            <span>手别</span>
            <strong>{{ report.handInfo.handSide }}</strong>
          </div>
          <div class="meta-item">
            <span>手型</span>
            <strong>{{ report.handInfo.handType }}</strong>
          </div>
          <div class="meta-item">
            <span>类型</span>
            <strong>{{ report.handInfo.typeLabel }}</strong>
          </div>
        </div>
      </div>

      <aside class="overview" aria-labelledby="overview-title">
        <h2 id="overview-title">掌相总览</h2>
        <p>{{ report.overview }}</p>
        <div class="traits">
          <div v-for="(trait, index) in report.traits" :key="trait.title" class="trait">
            <div class="icon">{{ index + 1 }}</div>
            <div>
              <b>{{ trait.title }}</b>
              <span>{{ trait.description }}</span>
            </div>
          </div>
        </div>
      </aside>
    </section>

    <section class="report-grid">
      <article class="panel" aria-labelledby="lines-title">
        <h2 id="lines-title">主要掌纹线稿</h2>
        <PalmIllustration :hand-side="report.handInfo.handSide" />
      </article>

      <article class="panel" aria-labelledby="major-title">
        <h2 id="major-title">四条主线解读</h2>
        <div class="line-list">
          <section v-for="(line, index) in majorLines" :key="line.key" class="line-card">
            <span class="mark">{{ index + 1 }}</span>
            <div>
              <h3>{{ line.name }}</h3>
              <p>{{ line.summary }}{{ line.meaning }}</p>
            </div>
          </section>
        </div>
      </article>
    </section>

    <section class="aspect-grid" aria-label="事业、情感、健康解读">
      <article v-for="aspect in aspects" :key="aspect.key" class="mini">
        <div class="symbol">{{ aspect.key === 'career' ? '✦' : aspect.key === 'love' ? '♡' : '☉' }}</div>
        <h2>{{ aspect.title }}</h2>
        <p>{{ aspect.body }}</p>
        <ul>
          <li v-for="point in aspect.points" :key="point">{{ point }}</li>
        </ul>
      </article>
    </section>

    <section class="closing">
      <h2>你的主导能量</h2>
      <p>{{ report.guidingEnergy }}</p>
    </section>

    <section v-if="shareUrl" class="share-strip" aria-label="分享链接">
      <span>分享链接</span>
      <input :value="shareUrl" readonly aria-label="可分享的报告链接" />
      <button
        type="button"
        class="share-copy-btn"
        :class="{ copied: copyState === 'copied', failed: copyState === 'failed' }"
        :aria-label="copyState === 'copied' ? '分享链接已复制' : '复制分享链接'"
        @click="copyShareUrl"
      >
        {{ copyButtonText }}
      </button>
    </section>

    <p class="note">{{ report.disclaimer }}</p>
  </main>
</template>

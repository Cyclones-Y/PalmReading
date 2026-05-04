<script setup>
import { computed } from 'vue'
import leftHandImage from '../assets/left-hand.png'
import rightHandImage from '../assets/right-hand.png'

const props = defineProps({
  handSide: {
    type: String,
    default: ''
  }
})

const isRightHand = computed(() => props.handSide?.includes('右'))
const figureImage = computed(() => (isRightHand.value ? rightHandImage : leftHandImage))
const figureAlt = computed(() => (isRightHand.value ? '右手掌纹线稿' : '左手掌纹线稿'))
</script>

<template>
  <img class="palm-figure" :src="figureImage" :alt="figureAlt" />
</template>

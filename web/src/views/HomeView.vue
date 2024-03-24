<script setup lang="ts">
import { inject, onMounted, onUnmounted, watch, type Ref, ref } from 'vue';
import type { MySocket } from '@/stores/socketTypes';
import { io } from 'socket.io-client';
import { stat } from 'fs';

const url = inject<Ref<string>>('url')!

let socket: MySocket | undefined = undefined

onMounted(setup)
watch(url, setup)

const baseImage = ref<string>()
const image1 = ref<string>()
const image2 = ref<string>()
const image3 = ref<string>()
const connected = ref(false)
const status = ref("")

function setup() {
  if(socket !== undefined) {
    socket!.disconnect()
  }

  socket = io(url.value)

  socket.on('test', () => {
    console.log("Recieved Message");
  });

  socket.emit('test');

  socket.on('image', (name, img) => {
    // console.log("image", name);  

    if(name === "base") {
      baseImage.value = "data:image/jpeg;base64," + img
    }
    if(name === "image1") {
      image1.value = "data:image/jpeg;base64," + img
    }
    if(name === "image2") {
      image2.value = "data:image/jpeg;base64," + img
    }
    if(name === "image3") {
      image3.value = "data:image/jpeg;base64," + img
    }
  })

  socket.on('data', (left, right) => {
    console.log(left, right);
  })

  socket.on('status', (newStatus) => {
    status.value = newStatus
  })

  socket.on('connect', () => {
    connected.value = true
  })

  socket.on('disconnect', () => {
    connected.value = false
  })
}

onUnmounted(() => {
  if(socket !== undefined) {
    socket.disconnect()
  }
})
</script>

<template>
  <main class="p-4 flex flex-col gap-2 items-start">
    <h1 class="font-bold text-3xl">Live View</h1>
    <p v-if="connected">Connected - Status: {{ status }}</p>
    <p v-else>Not Connected</p>
    <div class="grid grid-cols-2 grid-rows-2 gap-2">
      <img :src="baseImage" class="bg-gray-500 w-screen object-contain">
      <img :src="image1" class="bg-gray-500 w-full object-contain">
      <img :src="image2" class="bg-gray-500 w-full object-contain">
      <img :src="image3" class="bg-gray-500 w-full object-contain">
    </div>
  </main>
</template>

<script setup lang="ts">
import { inject, onMounted, onUnmounted, watch, type Ref, ref } from 'vue';
import type { MySocket } from '@/stores/socketTypes';
import { io } from 'socket.io-client';

const url = inject<Ref<string>>('url')!

let socket: MySocket | undefined = undefined

onMounted(setup)
watch(url, setup)

const baseImage = ref<string>()

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
    console.log("image", name);

    if(name === "base") {
      baseImage.value = "data:image/jpeg;base64," + img
    }

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
    <h1 class="font-bold text-3xl">Home Page</h1>
    <img :src="baseImage" class="bg-gray-500 min-w-64 min-h-32 object-contain">
  </main>
</template>

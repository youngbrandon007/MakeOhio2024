<script setup lang="ts">
import { inject, onMounted, onUnmounted, watch, type Ref, ref } from 'vue';
import { io } from 'socket.io-client';
import type { MySocket } from '@/stores/socketTypes';

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

function modeRemte() {
  console.log("mode")
  socket?.emit('mode', "remote")
}

function modeNormal() {
  console.log("mode")
  socket?.emit('mode', "normal")
}

let keysDown = new Set()

onMounted(() => {
  document.onkeydown = (e: KeyboardEvent) => {
    keysDown.add(e.key);
    updateMovement();
  }

  document.onkeyup = (e: KeyboardEvent) => {
    keysDown.delete(e.key);
    updateMovement();
  }
})

const speed = 400;
const turn_speed = 200;

function updateMovement() {
  let turn = (keysDown.has("ArrowLeft") ? 1 : 0) + (keysDown.has("ArrowRight") ? -1 : 0);
  let forward = (keysDown.has("ArrowUp") ? 1 : 0) + (keysDown.has("ArrowDown") ? -1 : 0);

  let right = forward * speed - forward * turn * turn_speed;
  let left = forward * speed + forward * turn * turn_speed;

  console.log(left, right);

  console.log("remote")
  socket?.emit("remote", left, right);
}
</script>

<template>
  <main class="p-4 flex flex-col gap-2">
    <h1 class="font-bold text-3xl">Remote Control</h1>
    <p v-if="connected">Connected</p>
    <p v-else>Not Connected</p>
    <div class="flex flex-row gap-2">
      <button @click="modeRemte" class="py-1 px-2 bg-gray-800 rounded hover:bg-gray-700">Remote Control Mode</button>
      <button @click="modeNormal" class="py-1 px-2 bg-gray-800 rounded hover:bg-gray-700">Normal Mode</button>
    </div>
    <div class="grid grid-cols-2 grid-rows-2 gap-2">
      <img :src="baseImage" class="bg-gray-500 w-full object-contain">
      <img :src="image1" class="bg-gray-500 w-full object-contain">
      <img :src="image2" class="bg-gray-500 w-full object-contain">
      <img :src="image3" class="bg-gray-500 w-full object-contain">
    </div>
    <p>Status: {{ status }}</p>
  </main>
</template>

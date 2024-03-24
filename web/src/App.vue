<script setup lang="ts">
import {provide, ref} from 'vue'

const url = ref("http://localhost:8080/")
provide('url', url)
</script>

<template>
  <div class="min-w-full min-h-screen flex flex-col md:flex-row divide-x divide-y divide-gray-700 bg-gray-950 text-gray-100">
    <div class="p-4 flex flex-col gap-4">
      
      <RouterLink to="/" class="text-gray-300 font-bold text-xl hover:text-gray-100">Home</RouterLink>  
      <RouterLink to="/live" class="text-gray-300 font-bold text-xl hover:text-gray-100">Live</RouterLink>      
      <RouterLink to="/remote" class="text-gray-300 font-bold text-xl hover:text-gray-100">Remote</RouterLink>
      <div class="grow"></div>
      <div>
        <input type="text" class="text-gray-300 bg-gray-950 border-0 ring ring-inset ring-blue-500 p-1 px-2 rounded" v-model="url">
      </div>
    </div>
    <RouterView />
  </div>
</template>

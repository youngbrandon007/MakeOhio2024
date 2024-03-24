import type { Socket } from "socket.io-client";

export type MySocket = Socket<{
  test: () => void, 
  image: (name: string, img: string ) => void,
}, { 
  test: () => void,
  mode: (mode: string) => void,
  remote: (left: number, right: number) => void,
}>
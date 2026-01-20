/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_ROUTER_URL?: string;
  readonly VITE_AGENT1_URL?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

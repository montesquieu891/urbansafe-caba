import { defineConfig } from 'astro/config';
// MapLibre se empaqueta en un chunk diferido (~1,1 MB, ~290 kB gzip) que no bloquea la carga inicial.
// El límite de aviso se ajusta a ese chunk conocido; `npm run audit:dist` controla el presupuesto del JS inicial.
export default defineConfig({ output: 'static', devToolbar: { enabled: false }, vite: { build: { chunkSizeWarningLimit: 1200 } } });

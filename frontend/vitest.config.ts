import { defineConfig } from 'vitest/config';
import path from 'node:path';

export default defineConfig({
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/test/setup.ts'],
    // Sluit Playwright-specs uit — die draaien via een eigen runner.
    exclude: ['e2e/**', 'node_modules/**', '.next/**', 'test-results/**'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html', 'lcov'],
      include: ['src/**/*.{ts,tsx}'],
      exclude: [
        'src/**/*.d.ts',
        'src/**/*.test.{ts,tsx}',
        'src/test/**',
        // Next.js convention-bestanden bevatten meestal geen testbare logica.
        'src/app/**/loading.tsx',
        'src/app/**/error.tsx',
        'src/app/**/not-found.tsx',
        'src/app/**/layout.tsx',
      ],
      thresholds: {
        // V1-ratchet: na 51 tests halen we ~27/76/49/27 — drempel staat nu
        // strakker zodat de coverage niet ongemerkt terug-zakt. Volgende stap:
        //   V2 (na ~100 tests): 50 / 40 / 50 / 50
        //   V3 (volwassen):     70 / 60 / 70 / 70
        // Verhoog deze drempels iedere keer als coverage er ruim overheen gaat,
        // anders is de drempel niet meer dan een vinkje.
        statements: 20,
        branches: 50,
        functions: 40,
        lines: 20,
      },
    },
  },
});

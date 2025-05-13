/** @type {import('@playwright/test').PlaywrightTestConfig} */
const config = {
  testDir: './tests/e2e',
  timeout: 60 * 1000,
  use: {
    baseURL: 'http://localhost:5173',
    headless: true,
    actionTimeout: 10 * 1000,
    navigationTimeout: 30 * 1000,
    ignoreHTTPSErrors: true,
    viewport: { width: 1280, height: 720 },
  },
  webServer: [
    {
      // Start FastAPI backend from project root so 'api' module is on PYTHONPATH
      command: 'python -m uvicorn api.main:app --reload --port 8000',
      port: 8000,
      cwd: '..',
      timeout: 120 * 1000,
      reuseExistingServer: true,
    },
    {
      // Start Vite dev server
      command: 'npm run dev',
      port: 5173,
      cwd: '.',
      timeout: 120 * 1000,
      reuseExistingServer: true,
    },
  ],
};
module.exports = config;
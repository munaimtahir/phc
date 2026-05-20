export const env = {
  username: process.env.PLAYWRIGHT_USERNAME || '',
  password: process.env.PLAYWRIGHT_PASSWORD || '',
  allowMutation: String(process.env.PLAYWRIGHT_ALLOW_MUTATION || 'false').toLowerCase() === 'true',
};

export function skipIfNoCredentials(): void {
  if (!env.username || !env.password) {
    throw new Error('Missing PLAYWRIGHT_USERNAME or PLAYWRIGHT_PASSWORD');
  }
}

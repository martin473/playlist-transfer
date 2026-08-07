import { describe, it, expect } from 'vitest';
import { version } from '../src/index.js';

describe('playlist-bridge-extension', () => {
  it('should have a version string', () => {
    expect(version).toBe('1.0.0');
  });
});

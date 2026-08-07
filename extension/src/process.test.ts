/**
 * Tests for the process module.
 *
 * @module tests/process.test
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { locatePlaylistBridgeExecutable, ExecutableNotFoundError } from './process.js';
import { access, constants, stat } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import path from 'node:path';

// Mock fs/promises functions
vi.mock('node:fs/promises', async () => {
  const actual = await vi.importActual('node:fs/promises');
  return {
    ...actual,
    access: vi.fn(),
    stat: vi.fn(),
  };
});

// Mock existsSync
vi.mock('node:fs', async () => {
  const actual = await vi.importActual('node:fs');
  return {
    ...actual,
    existsSync: vi.fn(),
  };
});

describe('locatePlaylistBridgeExecutable', () => {
  const mockAccess = access as unknown as ReturnType<typeof vi.fn>;
  const mockStat = stat as unknown as ReturnType<typeof vi.fn>;
  const mockExistsSync = existsSync as unknown as ReturnType<typeof vi.fn>;

  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.resetModules();
  });

  describe('158.01 - Read explicit CLI executable configuration', () => {
    it('should return the configured path when provided and valid', async () => {
      const configuredPath = '/usr/local/bin/playlist-bridge';
      const resolvedPath = path.resolve(configuredPath);

      mockAccess.mockResolvedValue(undefined);
      mockStat.mockResolvedValue({
        isFile: () => true,
        isDirectory: () => false,
      });

      const result = await locatePlaylistBridgeExecutable(configuredPath);

      expect(result).toBe(resolvedPath);
      expect(mockAccess).toHaveBeenCalledWith(resolvedPath, constants.F_OK);
      expect(mockAccess).toHaveBeenCalledWith(resolvedPath, constants.X_OK);
      expect(mockStat).toHaveBeenCalledWith(resolvedPath);
    });

    it('should resolve relative paths to absolute paths', async () => {
      const configuredPath = './bin/playlist-bridge';
      const resolvedPath = path.resolve(configuredPath);

      mockAccess.mockResolvedValue(undefined);
      mockStat.mockResolvedValue({
        isFile: () => true,
        isDirectory: () => false,
      });

      const result = await locatePlaylistBridgeExecutable(configuredPath);

      expect(result).toBe(resolvedPath);
      expect(mockAccess).toHaveBeenCalledWith(resolvedPath, constants.F_OK);
    });

    it('should throw ExecutableNotFoundError when configured path does not exist', async () => {
      const configuredPath = '/nonexistent/path';
      const resolvedPath = path.resolve(configuredPath);

      mockAccess.mockRejectedValue(new Error('ENOENT: no such file or directory'));

      await expect(locatePlaylistBridgeExecutable(configuredPath)).rejects.toThrow(
        ExecutableNotFoundError
      );
      await expect(locatePlaylistBridgeExecutable(configuredPath)).rejects.toThrow(
        /does not exist/
      );
    });

    it('should throw ExecutableNotFoundError when configured path is not a file', async () => {
      const configuredPath = '/some/directory';
      const resolvedPath = path.resolve(configuredPath);

      mockAccess.mockResolvedValue(undefined);
      mockStat.mockResolvedValue({
        isFile: () => false,
        isDirectory: () => true,
      });

      await expect(locatePlaylistBridgeExecutable(configuredPath)).rejects.toThrow(
        ExecutableNotFoundError
      );
      await expect(locatePlaylistBridgeExecutable(configuredPath)).rejects.toThrow(
        /exists but is not a file/
      );
    });

    it('should throw ExecutableNotFoundError when configured path is not executable', async () => {
      const configuredPath = '/usr/local/bin/playlist-bridge';
      const resolvedPath = path.resolve(configuredPath);

      mockAccess.mockImplementation((path: string, mode?: number) => {
        if (mode === constants.F_OK) {
          return Promise.resolve();
        }
        if (mode === constants.X_OK) {
          return Promise.reject(new Error('Permission denied'));
        }
        return Promise.resolve();
      });

      mockStat.mockResolvedValue({
        isFile: () => true,
        isDirectory: () => false,
      });

      await expect(locatePlaylistBridgeExecutable(configuredPath)).rejects.toThrow(
        ExecutableNotFoundError
      );
      await expect(locatePlaylistBridgeExecutable(configuredPath)).rejects.toThrow(
        /exists but is not executable/
      );
    });
  });

  describe('158.02 - Validate configured executable (fallback paths)', () => {
    it('should check known installation paths when no configured path provided', async () => {
      const knownPath = path.resolve('/usr/local/bin/playlist-bridge');

      mockExistsSync.mockImplementation((p: string) => {
        return p === knownPath;
      });

      mockAccess.mockResolvedValue(undefined);
      mockStat.mockResolvedValue({
        isFile: () => true,
        isDirectory: () => false,
      });

      const result = await locatePlaylistBridgeExecutable();

      expect(result).toBe(knownPath);
      expect(mockExistsSync).toHaveBeenCalled();
      expect(mockAccess).toHaveBeenCalledWith(knownPath, constants.X_OK);
      expect(mockStat).toHaveBeenCalledWith(knownPath);
    });

    it('should check the extension\'s node_modules/.bin directory', async () => {
      const extensionRoot = path.resolve(__dirname, '..');
      const candidatePath = path.join(extensionRoot, 'node_modules', '.bin', 'playlist-bridge');

      mockExistsSync.mockImplementation((p: string) => {
        return p === candidatePath;
      });

      mockAccess.mockResolvedValue(undefined);
      mockStat.mockResolvedValue({
        isFile: () => true,
        isDirectory: () => false,
      });

      const result = await locatePlaylistBridgeExecutable();

      expect(result).toBe(candidatePath);
    });

    it('should check the current working directory\'s node_modules/.bin', async () => {
      const cwd = process.cwd();
      const candidatePath = path.join(cwd, 'node_modules', '.bin', 'playlist-bridge');

      mockExistsSync.mockImplementation((p: string) => {
        return p === candidatePath;
      });

      mockAccess.mockResolvedValue(undefined);
      mockStat.mockResolvedValue({
        isFile: () => true,
        isDirectory: () => false,
      });

      const result = await locatePlaylistBridgeExecutable();

      expect(result).toBe(candidatePath);
    });

    it('should check the user\'s home directory for global installation', async () => {
      const homeDir = process.env.HOME || process.env.USERPROFILE || '';
      const candidatePath = path.join(homeDir, '.local', 'bin', 'playlist-bridge');

      if (!homeDir) {
        return;
      }

      mockExistsSync.mockImplementation((p: string) => {
        return p === candidatePath;
      });

      mockAccess.mockResolvedValue(undefined);
      mockStat.mockResolvedValue({
        isFile: () => true,
        isDirectory: () => false,
      });

      const result = await locatePlaylistBridgeExecutable();

      expect(result).toBe(candidatePath);
    });

    it('should throw ExecutableNotFoundError when no known path exists', async () => {
      mockExistsSync.mockReturnValue(false);

      await expect(locatePlaylistBridgeExecutable()).rejects.toThrow(
        ExecutableNotFoundError
      );
      await expect(locatePlaylistBridgeExecutable()).rejects.toThrow(
        /Could not locate playlist-bridge executable/
      );
    });

    it('should skip non-executable files in known paths', async () => {
      const nonExecutablePath = '/usr/local/bin/playlist-bridge';

      mockExistsSync.mockImplementation((p: string) => {
        return p === nonExecutablePath;
      });

      mockAccess.mockImplementation((path: string, mode?: number) => {
        if (mode === constants.X_OK) {
          return Promise.reject(new Error('Permission denied'));
        }
        return Promise.resolve();
      });

      mockStat.mockResolvedValue({
        isFile: () => true,
        isDirectory: () => false,
      });

      await expect(locatePlaylistBridgeExecutable()).rejects.toThrow(
        ExecutableNotFoundError
      );
    });

    it('should skip directories in known paths', async () => {
      const dirPath = '/usr/local/bin';

      mockExistsSync.mockImplementation((p: string) => {
        return p === dirPath;
      });

      mockStat.mockResolvedValue({
        isFile: () => false,
        isDirectory: () => true,
      });

      await expect(locatePlaylistBridgeExecutable()).rejects.toThrow(
        ExecutableNotFoundError
      );
    });

    it('should prefer explicit configured path over fallback paths', async () => {
      const configuredPath = '/custom/path/to/playlist-bridge';
      const resolvedPath = path.resolve(configuredPath);

      mockAccess.mockResolvedValue(undefined);
      mockStat.mockResolvedValue({
        isFile: () => true,
        isDirectory: () => false,
      });

      const result = await locatePlaylistBridgeExecutable(configuredPath);

      expect(result).toBe(resolvedPath);
    });
  });
});

/**
 * Process management for the playlist-bridge CLI executable.
 *
 * Provides functions to locate, validate, and invoke the CLI tool
 * from within the Pi extension runtime.
 *
 * @module process
 */

import { access, constants } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import path from 'node:path';

/**
 * Error thrown when the playlist-bridge executable cannot be found.
 */
export class ExecutableNotFoundError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ExecutableNotFoundError';
  }
}

/**
 * Locate the playlist-bridge CLI executable.
 *
 * Uses explicit configuration first (if provided), then falls back to
 * known installation paths. Does not search arbitrary PATH entries silently.
 *
 * @param configuredPath - Optional explicit path to the executable
 * @returns Resolved absolute path to the executable
 * @throws {ExecutableNotFoundError} When the executable cannot be found or is not usable
 *
 * @remarks
 * - If configuredPath is provided, it must exist, be a file, and be executable
 * - Known installation paths are checked in a specific order
 * - Does not search arbitrary PATH entries as a fallback
 */
export async function locatePlaylistBridgeExecutable(
  configuredPath?: string
): Promise<string> {
  // Step 158.01: Read explicit CLI executable configuration
  if (configuredPath) {
    const resolvedPath = path.resolve(configuredPath);

    // Step 158.02: Validate configured executable
    try {
      // Check that the path exists and is a file
      await access(resolvedPath, constants.F_OK);

      // Check that it's a regular file (or symlink to one)
      // access with F_OK only checks existence, we need more
      // Use existsSync for additional checks or handle stat
      const stats = await import('node:fs/promises').then((fs) =>
        fs.stat(resolvedPath)
      );

      if (!stats.isFile()) {
        throw new ExecutableNotFoundError(
          `Configured executable path exists but is not a file: ${resolvedPath}`
        );
      }

      // Check that it's executable (on Unix-like systems)
      try {
        await access(resolvedPath, constants.X_OK);
      } catch {
        throw new ExecutableNotFoundError(
          `Configured executable path exists but is not executable: ${resolvedPath}`
        );
      }

      // Valid executable found
      return resolvedPath;
    } catch (error) {
      if (error instanceof ExecutableNotFoundError) {
        throw error;
      }
      // Re-throw with a clearer message for the user
      throw new ExecutableNotFoundError(
        `Configured executable path does not exist: ${resolvedPath}`
      );
    }
  }

  // Step 158.02 (fallback): Check known installation paths
  const knownPaths = getKnownInstallationPaths();

  for (const candidatePath of knownPaths) {
    try {
      const resolvedPath = path.resolve(candidatePath);

      // Check existence and file type
      if (!existsSync(resolvedPath)) {
        continue;
      }

      const stats = await import('node:fs/promises').then((fs) =>
        fs.stat(resolvedPath)
      );

      if (!stats.isFile()) {
        continue;
      }

      // Check executable permission
      try {
        await access(resolvedPath, constants.X_OK);
        return resolvedPath;
      } catch {
        // Not executable, continue to next candidate
        continue;
      }
    } catch {
      // Ignore errors for this candidate and try the next
      continue;
    }
  }

  // No executable found
  throw new ExecutableNotFoundError(
    'Could not locate playlist-bridge executable. ' +
      'Please ensure the CLI tool is installed and accessible, ' +
      'or provide an explicit path via configuration.'
  );
}

/**
 * Get the list of known installation paths for the playlist-bridge executable.
 *
 * These paths are checked in order of preference. The order is deterministic
 * and does not depend on the user's PATH environment variable.
 *
 * @returns Array of candidate path strings
 */
function getKnownInstallationPaths(): string[] {
  const candidates: string[] = [];

  // Check the current working directory's node_modules/.bin
  const cwd = process.cwd();
  candidates.push(path.join(cwd, 'node_modules', '.bin', 'playlist-bridge'));
  candidates.push(path.join(cwd, 'node_modules', '.bin', 'playlist-bridge.exe'));

  // Check the directory of the current module (extension)
  const __dirname = path.dirname(new URL(import.meta.url).pathname);
  const extensionRoot = path.resolve(__dirname, '..');
  candidates.push(path.join(extensionRoot, 'node_modules', '.bin', 'playlist-bridge'));
  candidates.push(path.join(extensionRoot, 'node_modules', '.bin', 'playlist-bridge.exe'));

  // Check the user's home directory for global installation
  const homeDir = process.env.HOME || process.env.USERPROFILE || '';
  if (homeDir) {
    candidates.push(path.join(homeDir, '.local', 'bin', 'playlist-bridge'));
    // Windows global npm install location
    candidates.push(path.join(homeDir, 'AppData', 'Roaming', 'npm', 'playlist-bridge'));
    candidates.push(path.join(homeDir, 'AppData', 'Roaming', 'npm', 'playlist-bridge.cmd'));
  }

  // Check system-wide locations (Unix-like)
  candidates.push('/usr/local/bin/playlist-bridge');
  candidates.push('/usr/bin/playlist-bridge');

  // Windows system-wide location
  candidates.push('C:\\Program Files\\nodejs\\playlist-bridge');
  candidates.push('C:\\Program Files\\nodejs\\playlist-bridge.cmd');

  return candidates;
}

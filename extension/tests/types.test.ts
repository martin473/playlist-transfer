/**
 * Boundary type and schema alignment tests
 *
 * These tests verify that the TypeScript boundary types correctly
 * accept valid tool inputs and reject invalid variants at compile time.
 * Runtime schema parity is verified in later dispatches.
 *
 * @module types.test
 */

import { describe, it, expect } from 'vitest';
import type {
  PlaylistAuthInput,
  PlaylistTransferInput,
  PlaylistReviewInput,
  PlaylistReviewListInput,
  PlaylistReviewApplyInput,
  TypedToolInput,
  PlaylistToolName,
  PlaylistBridgeEvent,
  PlaylistAuthResult,
  PlaylistTransferResult,
  PlaylistReviewResult,
  CliInvocation,
  ProcessResult,
  ExtensionDependencies,
} from '../src/types.js';

/**
 * Compile-time type assertions for valid inputs.
 * These should satisfy the exact input types.
 */
describe('boundary type validation', () => {
  describe('PlaylistAuthInput', () => {
    it('accepts valid login variants', () => {
      // Valid: login with required fields
      const input: PlaylistAuthInput = {
        action: 'login',
        service: 'spotify',
        profile: 'default',
      };
      expect(input.action).toBe('login');

      // Valid: login with optional clientSecretPath
      const inputWithSecret: PlaylistAuthInput = {
        action: 'login',
        service: 'youtube',
        profile: 'personal',
        clientSecretPath: '/path/to/client_secret.json',
      };
      expect(inputWithSecret.clientSecretPath).toBeDefined();

      // Valid: login with all fields
      const fullInput: PlaylistAuthInput = {
        action: 'login',
        service: 'spotify',
        profile: 'work',
        clientSecretPath: '/custom/path.json',
      };
      expect(fullInput).toBeDefined();
    });

    it('accepts valid status variants', () => {
      const input: PlaylistAuthInput = {
        action: 'status',
        service: 'spotify',
        profile: 'default',
      };
      expect(input.action).toBe('status');

      const youtubeStatus: PlaylistAuthInput = {
        action: 'status',
        service: 'youtube',
        profile: 'music',
      };
      expect(youtubeStatus.service).toBe('youtube');
    });

    it('accepts valid logout variants', () => {
      const input: PlaylistAuthInput = {
        action: 'logout',
        service: 'spotify',
        profile: 'default',
      };
      expect(input.action).toBe('logout');
    });
  });

  describe('PlaylistTransferInput', () => {
    it('accepts valid transfer with required fields', () => {
      const input: PlaylistTransferInput = {
        sourceUrl: 'https://www.youtube.com/playlist?list=PL123',
        sourceProfile: 'youtube-default',
        spotifyProfile: 'spotify-default',
      };
      expect(input.sourceUrl).toContain('youtube');
    });

    it('accepts valid transfer with all optional fields', () => {
      const input: PlaylistTransferInput = {
        sourceUrl: 'https://www.youtube.com/playlist?list=PL456',
        sourceProfile: 'youtube-personal',
        spotifyProfile: 'spotify-work',
        destinationName: 'My Awesome Playlist',
        mode: 'create',
        policy: 'balanced',
        visibility: 'public',
        jobId: 'job-123',
      };
      expect(input.destinationName).toBe('My Awesome Playlist');
      expect(input.mode).toBe('create');
      expect(input.policy).toBe('balanced');
      expect(input.visibility).toBe('public');
      expect(input.jobId).toBe('job-123');
    });

    it('accepts all mode variants', () => {
      const modes: Array<'dry_run' | 'create' | 'merge' | 'replace'> = [
        'dry_run',
        'create',
        'merge',
        'replace',
      ];
      for (const mode of modes) {
        const input: PlaylistTransferInput = {
          sourceUrl: 'https://www.youtube.com/playlist?list=PL123',
          sourceProfile: 'youtube-default',
          spotifyProfile: 'spotify-default',
          mode,
        };
        expect(input.mode).toBe(mode);
      }
    });

    it('accepts all policy variants', () => {
      const policies: Array<'strict' | 'balanced' | 'loose'> = [
        'strict',
        'balanced',
        'loose',
      ];
      for (const policy of policies) {
        const input: PlaylistTransferInput = {
          sourceUrl: 'https://www.youtube.com/playlist?list=PL123',
          sourceProfile: 'youtube-default',
          spotifyProfile: 'spotify-default',
          policy,
        };
        expect(input.policy).toBe(policy);
      }
    });

    it('accepts all visibility variants', () => {
      const visibilities: Array<'private' | 'public'> = ['private', 'public'];
      for (const visibility of visibilities) {
        const input: PlaylistTransferInput = {
          sourceUrl: 'https://www.youtube.com/playlist?list=PL123',
          sourceProfile: 'youtube-default',
          spotifyProfile: 'spotify-default',
          visibility,
        };
        expect(input.visibility).toBe(visibility);
      }
    });

    it('accepts transfer with dry_run and all options', () => {
      const input: PlaylistTransferInput = {
        sourceUrl: 'https://www.youtube.com/playlist?list=PL789',
        sourceProfile: 'youtube-test',
        spotifyProfile: 'spotify-test',
        destinationName: 'Test Playlist',
        mode: 'dry_run',
        policy: 'loose',
        visibility: 'private',
        jobId: 'job-456',
      };
      expect(input.mode).toBe('dry_run');
    });
  });

  describe('PlaylistReviewInput', () => {
    it('accepts valid list action', () => {
      const input: PlaylistReviewInput = {
        action: 'list',
        jobId: 'job-123',
      };
      expect(input.action).toBe('list');
      expect(input.jobId).toBe('job-123');
    });

    it('accepts valid apply action with spotifyTrackId', () => {
      const input: PlaylistReviewInput = {
        action: 'apply',
        jobId: 'job-123',
        sourceItemId: 'source-456',
        spotifyTrackId: 'spotify-789',
      };
      expect(input.action).toBe('apply');
      expect(input.sourceItemId).toBe('source-456');
      expect(input.spotifyTrackId).toBe('spotify-789');
      expect(input.skip).toBeUndefined();
    });

    it('accepts valid apply action with skip true', () => {
      const input: PlaylistReviewInput = {
        action: 'apply',
        jobId: 'job-123',
        sourceItemId: 'source-456',
        skip: true,
      };
      expect(input.action).toBe('apply');
      expect(input.sourceItemId).toBe('source-456');
      expect(input.skip).toBe(true);
      expect(input.spotifyTrackId).toBeUndefined();
    });

    it('accepts valid apply action with skip false', () => {
      const input: PlaylistReviewInput = {
        action: 'apply',
        jobId: 'job-123',
        sourceItemId: 'source-456',
        skip: false,
      };
      expect(input.skip).toBe(false);
    });

    it('accepts apply action with both spotifyTrackId and skip false', () => {
      const input: PlaylistReviewApplyInput = {
        action: 'apply',
        jobId: 'job-123',
        sourceItemId: 'source-456',
        spotifyTrackId: 'spotify-789',
        skip: false,
      };
      expect(input.spotifyTrackId).toBe('spotify-789');
      expect(input.skip).toBe(false);
    });
  });

  describe('TypedToolInput union', () => {
    it('accepts all valid input variants', () => {
      const authInput: TypedToolInput = {
        action: 'login',
        service: 'spotify',
        profile: 'default',
      };
      expect(authInput.action).toBe('login');

      const transferInput: TypedToolInput = {
        sourceUrl: 'https://www.youtube.com/playlist?list=PL123',
        sourceProfile: 'youtube-default',
        spotifyProfile: 'spotify-default',
      };
      expect(transferInput.sourceUrl).toBeDefined();

      const reviewInput: TypedToolInput = {
        action: 'list',
        jobId: 'job-123',
      };
      expect(reviewInput.action).toBe('list');
    });
  });

  describe('PlaylistToolName', () => {
    it('accepts valid tool names', () => {
      const names: PlaylistToolName[] = [
        'playlist_auth',
        'playlist_transfer',
        'playlist_review',
      ];
      for (const name of names) {
        const toolName: PlaylistToolName = name;
        expect(toolName).toBe(name);
      }
    });
  });

  describe('PlaylistBridgeEvent', () => {
    it('accepts valid event structure', () => {
      const event: PlaylistBridgeEvent = {
        schemaVersion: 1,
        type: 'job_start',
        jobId: 'job-123',
        payload: { source: 'youtube', destination: 'spotify' },
      };
      expect(event.schemaVersion).toBe(1);
      expect(event.type).toBe('job_start');
      expect(event.jobId).toBe('job-123');
    });

    it('accepts event without jobId', () => {
      const event: PlaylistBridgeEvent = {
        schemaVersion: 1,
        type: 'progress',
        payload: { count: 42 },
      };
      expect(event.jobId).toBeUndefined();
    });
  });

  describe('PlaylistAuthResult', () => {
    it('accepts valid spotify result', () => {
      const result: PlaylistAuthResult = {
        service: 'spotify',
        profile: 'default',
        state: 'authenticated',
        safeMessage: 'Logged in as user@example.com',
      };
      expect(result.service).toBe('spotify');
      expect(result.state).toBe('authenticated');
    });

    it('accepts valid youtube result', () => {
      const result: PlaylistAuthResult = {
        service: 'youtube',
        profile: 'personal',
        state: 'needs_refresh',
      };
      expect(result.service).toBe('youtube');
      expect(result.state).toBe('needs_refresh');
    });
  });

  describe('PlaylistTransferResult', () => {
    it('accepts valid transfer result', () => {
      const result: PlaylistTransferResult = {
        jobId: 'job-123',
        status: 'completed',
        counts: { source: 100, matched: 95, transferred: 90 },
        destinationId: 'spotify-playlist-456',
        reportPaths: ['/reports/job-123.json'],
      };
      expect(result.status).toBe('completed');
      expect(result.counts.matched).toBe(95);
    });
  });

  describe('PlaylistReviewResult', () => {
    it('accepts valid list result', () => {
      const result: PlaylistReviewResult = {
        jobId: 'job-123',
        unresolved: [{ id: 'item-1', title: 'Song 1' }],
      };
      expect(result.unresolved).toHaveLength(1);
      expect(result.applied).toBeUndefined();
    });

    it('accepts valid apply result', () => {
      const result: PlaylistReviewResult = {
        jobId: 'job-123',
        unresolved: [],
        applied: true,
      };
      expect(result.applied).toBe(true);
    });
  });

  describe('CliInvocation', () => {
    it('accepts valid invocation descriptor', () => {
      const invocation: CliInvocation = {
        executable: '/usr/local/bin/playlist-bridge',
        args: ['auth', '--service', 'spotify'],
        cwd: '/project',
        env: { PATH: '/usr/bin' },
      };
      expect(invocation.executable).toContain('playlist-bridge');
      expect(invocation.args).toContain('auth');
    });
  });

  describe('ProcessResult', () => {
    it('accepts valid process result', () => {
      const result: ProcessResult = {
        exitCode: 0,
        events: [
          {
            schemaVersion: 1,
            type: 'start',
            payload: {},
          },
        ],
        stderrReportPath: '/reports/stderr.log',
      };
      expect(result.exitCode).toBe(0);
      expect(result.events).toHaveLength(1);
    });
  });

  describe('ExtensionDependencies', () => {
    it('accepts valid dependencies', () => {
      const deps: ExtensionDependencies = {
        buildInvocation: async (input: TypedToolInput) => {
          return {
            executable: 'playlist-bridge',
            args: ['auth'],
            cwd: '/project',
            env: {},
          };
        },
        runProcess: async (invocation, signal, onEvent) => {
          return {
            exitCode: 0,
            events: [],
          };
        },
      };
      expect(deps.buildInvocation).toBeInstanceOf(Function);
      expect(deps.runProcess).toBeInstanceOf(Function);
    });
  });
});

/**
 * Compile-time test: These type assertions should fail at compile time
 * if the types are incorrectly defined. They are written as regular tests
 * that exercise the type system via assignment checks.
 */
describe('compile-time type safety', () => {
  describe('PlaylistAuthInput disallows invalid actions', () => {
    // @ts-expect-error - 'invalid' is not a valid action
    const invalidAction = (): PlaylistAuthInput => ({
      action: 'invalid' as 'login',
      service: 'spotify',
      profile: 'default',
    });

    it('should compile with type errors for invalid actions', () => {
      // This test passes if the type check passes (the @ts-expect-error is satisfied)
      expect(invalidAction).toBeDefined();
    });
  });

  describe('PlaylistAuthInput disallows invalid services', () => {
    // @ts-expect-error - 'apple' is not a valid service
    const invalidService = (): PlaylistAuthInput => ({
      action: 'login',
      service: 'apple' as 'spotify',
      profile: 'default',
    });

    it('should compile with type errors for invalid services', () => {
      expect(invalidService).toBeDefined();
    });
  });

  describe('PlaylistTransferInput disallows invalid modes', () => {
    // @ts-expect-error - 'delete' is not a valid mode
    const invalidMode = (): PlaylistTransferInput => ({
      sourceUrl: 'https://youtube.com/playlist',
      sourceProfile: 'default',
      spotifyProfile: 'default',
      mode: 'delete' as 'create',
    });

    it('should compile with type errors for invalid modes', () => {
      expect(invalidMode).toBeDefined();
    });
  });

  describe('PlaylistTransferInput disallows invalid policies', () => {
    // @ts-expect-error - 'aggressive' is not a valid policy
    const invalidPolicy = (): PlaylistTransferInput => ({
      sourceUrl: 'https://youtube.com/playlist',
      sourceProfile: 'default',
      spotifyProfile: 'default',
      policy: 'aggressive' as 'balanced',
    });

    it('should compile with type errors for invalid policies', () => {
      expect(invalidPolicy).toBeDefined();
    });
  });

  describe('PlaylistReviewInput disallows invalid actions', () => {
    // @ts-expect-error - 'delete' is not a valid review action
    const invalidReviewAction = (): PlaylistReviewInput => ({
      action: 'delete' as 'list',
      jobId: 'job-123',
    });

    it('should compile with type errors for invalid review actions', () => {
      expect(invalidReviewAction).toBeDefined();
    });
  });

  describe('PlaylistReviewApplyInput requires sourceItemId', () => {
    // @ts-expect-error - sourceItemId is required for apply action
    const missingSourceItemId = (): PlaylistReviewInput => ({
      action: 'apply',
      jobId: 'job-123',
    });

    it('should compile with type errors when sourceItemId is missing', () => {
      expect(missingSourceItemId).toBeDefined();
    });
  });
});

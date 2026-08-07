/**
 * Playlist Bridge Extension Boundary Types
 *
 * These types define the contract between the Pi extension runtime
 * and the playlist-bridge CLI tool. They are consumed by later
 * extension dispatches for tool invocation, event processing, and
 * process management.
 *
 * @module types
 */

/**
 * Discriminated union of all tool names supported by the extension.
 */
export type PlaylistToolName = 'playlist_auth' | 'playlist_transfer' | 'playlist_review';

/**
 * Input for the authentication tool.
 */
export type PlaylistAuthInput = {
  action: 'login' | 'status' | 'logout';
  service: 'youtube' | 'spotify';
  profile: string;
  clientSecretPath?: string;
};

/**
 * Input for the transfer tool.
 */
export type PlaylistTransferInput = {
  sourceUrl: string;
  sourceProfile: string;
  spotifyProfile: string;
  destinationName?: string;
  mode?: 'dry_run' | 'create' | 'merge' | 'replace';
  policy?: 'strict' | 'balanced' | 'loose';
  visibility?: 'private' | 'public';
  jobId?: string;
};

/**
 * Input for listing review items.
 */
export type PlaylistReviewListInput = {
  action: 'list';
  jobId: string;
};

/**
 * Input for applying a review correction.
 */
export type PlaylistReviewApplyInput = {
  action: 'apply';
  jobId: string;
  sourceItemId: string;
  spotifyTrackId?: string;
  skip?: boolean;
};

/**
 * Union of all review input variants.
 */
export type PlaylistReviewInput = PlaylistReviewListInput | PlaylistReviewApplyInput;

/**
 * Union of all typed tool inputs.
 */
export type TypedToolInput = PlaylistAuthInput | PlaylistTransferInput | PlaylistReviewInput;

/**
 * JSONL event emitted by the CLI during execution.
 */
export type PlaylistBridgeEvent = {
  schemaVersion: 1;
  type: string;
  jobId?: string;
  payload: Record<string, unknown>;
};

/**
 * Result of an authentication operation.
 */
export type PlaylistAuthResult = {
  service: 'youtube' | 'spotify';
  profile: string;
  state: string;
  safeMessage?: string;
};

/**
 * Result of a transfer operation.
 */
export type PlaylistTransferResult = {
  jobId: string;
  status: string;
  counts: Record<string, number>;
  destinationId?: string;
  reportPaths: string[];
};

/**
 * Result of a review operation.
 */
export type PlaylistReviewResult = {
  jobId: string;
  unresolved: unknown[];
  applied?: boolean;
};

/**
 * Invocation descriptor for the CLI process.
 */
export type CliInvocation = {
  executable: string;
  args: string[];
  cwd: string;
  env: NodeJS.ProcessEnv;
};

/**
 * Result of a CLI process execution.
 */
export type ProcessResult = {
  exitCode: number;
  events: PlaylistBridgeEvent[];
  stderrReportPath?: string;
};

/**
 * Dependencies required by the extension to run the CLI.
 */
export type ExtensionDependencies = {
  buildInvocation: (
    input: TypedToolInput
  ) => Promise<CliInvocation> | CliInvocation;
  runProcess: (
    invocation: CliInvocation,
    signal: AbortSignal,
    onEvent: (event: PlaylistBridgeEvent) => void
  ) => Promise<ProcessResult>;
};

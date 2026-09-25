import { beforeEach, expect, test } from 'vitest';
import { clearPending, loadPending, savePending } from './pendingSubmission';

const pending = { player_id: 'child-a', session_id: 's1', command: { submission_id: 'u1', problem_id: 'q1', answer: 5, response_ms: 1200, expected_version: 1 } };

beforeEach(() => sessionStorage.clear());

test('exactly one record is kept and cleared on acknowledgement', () => {
  savePending(pending);
  savePending({ ...pending, command: { ...pending.command, submission_id: 'u2' } });
  expect(loadPending('child-a')?.command.submission_id).toBe('u2');
  clearPending();
  expect(loadPending('child-a')).toBeNull();
});

test('a record for another child is discarded on profile switch', () => {
  savePending(pending);
  expect(loadPending('child-b')).toBeNull();
  expect(sessionStorage.length).toBe(0);
});

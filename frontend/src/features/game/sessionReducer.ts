import type { AttemptResult, SessionSnapshot } from '../../api';

export type GameStatus = 'loading' | 'ready' | 'submitting' | 'offline';

export type GameState = {
  snapshot: SessionSnapshot | null;
  entry: string;
  status: GameStatus;
};

export type GameAction =
  | { type: 'snapshot'; snapshot: SessionSnapshot }
  | { type: 'result'; result: AttemptResult }
  | { type: 'digit'; digit: string }
  | { type: 'erase' }
  | { type: 'submitting' }
  | { type: 'offline' };

export const initialState: GameState = { snapshot: null, entry: '', status: 'loading' };

/** Server snapshots are versioned; an older one never overwrites a newer one. */
export function acceptSnapshot(current: SessionSnapshot | null, incoming: SessionSnapshot): SessionSnapshot {
  return !current || incoming.version >= current.version ? incoming : current;
}

export function gameReducer(state: GameState, action: GameAction): GameState {
  switch (action.type) {
    case 'snapshot': {
      const snapshot = acceptSnapshot(state.snapshot, action.snapshot);
      const sameProblem = snapshot.current_problem?.id === state.snapshot?.current_problem?.id;
      return { ...state, snapshot, entry: sameProblem ? state.entry : '', status: 'ready' };
    }
    case 'result': {
      const snapshot = acceptSnapshot(state.snapshot, action.result.session);
      return { ...state, snapshot, entry: '', status: 'ready' };
    }
    case 'digit':
      if (state.status !== 'ready' || state.snapshot?.phase !== 'answer' || state.entry.length >= 4) return state;  // the catalogue's largest answer is 1000
      return { ...state, entry: state.entry === '0' ? action.digit : state.entry + action.digit };
    case 'erase':
      return state.status === 'ready' ? { ...state, entry: state.entry.slice(0, -1) } : state;
    case 'submitting':
      return { ...state, status: 'submitting' };
    case 'offline':
      return { ...state, status: 'offline' };
  }
}

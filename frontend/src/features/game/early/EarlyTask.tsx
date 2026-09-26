import type { PublicProblem, Theme } from '../../../api';
import PictureCards from './PictureCards';
import { CountScene, FiveFrame, MatchScene, OrderTowers, PatternRow, PickScene, QuickLook, ShareScene } from './scenes';
import { isEarly, optionsOf } from './types';

type Props = { problem: PublicProblem; theme: Theme; disabled: boolean; onAnswer: (value: number) => void };

/** Picture-first task for a 4-5-year-old: a scene per early kind, or number cards for a numeric task issued with options. */
export default function EarlyTask(props: Props) {
  const { problem } = props;
  if (!isEarly(problem)) {
    const options = optionsOf(problem);
    return options ? <PictureCards options={options} theme={props.theme} kind="number" disabled={props.disabled} onChoose={props.onAnswer} /> : null;
  }
  switch (problem.kind) {
    case 'count': return <CountScene {...props} />;
    case 'match': return <MatchScene {...props} />;
    case 'subitize': return <QuickLook {...props} />;
    case 'pattern': return <PatternRow {...props} />;
    case 'frame': return <FiveFrame {...props} />;
    case 'order': return <OrderTowers {...props} />;
    case 'share': return <ShareScene {...props} />;
    default: return <PickScene {...props} />;
  }
}

/** True when the picture-mode input replaces the keypad and the choice pad for this task. */
export function hasEarlyInput(problem: PublicProblem): boolean {
  return isEarly(problem) || optionsOf(problem) !== null;
}

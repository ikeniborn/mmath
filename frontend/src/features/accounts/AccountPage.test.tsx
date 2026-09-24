import { render, screen } from '@testing-library/react';
import { expect, test } from 'vitest';
import AccountPage from './AccountPage';

test('parent entry explains email and recovery limitation', () => {
  render(<AccountPage onAuthenticated={async () => {}} />);
  expect(screen.getByRole('heading', { name: 'Вход для родителя' })).toBeTruthy();
  expect(screen.getByText(/Почта пока не подтверждается/)).toBeTruthy();
});

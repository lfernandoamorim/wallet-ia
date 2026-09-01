import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { ThemeProvider, useTheme } from './ThemeContext';

const TestComponent = () => {
  const { theme, toggleTheme } = useTheme();
  return (
    <div>
      <span data-testid="theme-value">{theme}</span>
      <button onClick={toggleTheme}>Alternar Tema</button>
    </div>
  );
};

describe('ThemeContext', () => {
  it('alterna o tema entre dark e light', () => {
    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );

    const themeSpan = screen.getByTestId('theme-value');
    expect(themeSpan.textContent).toBe('dark');

    const button = screen.getByRole('button', { name: /alternar tema/i });
    fireEvent.click(button);

    expect(themeSpan.textContent).toBe('light');
  });
});

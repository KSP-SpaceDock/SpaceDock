# Frontend Stack Recommendations (StyleX-based)

## Core Framework
- **React 18/19** - Primary UI framework (StyleX is React-native)
- **React Compiler** - Meta's automatic optimization compiler (replaces manual hooks)
- **TypeScript** - Type safety throughout

## Styling System
- **StyleX** (`@stylexjs/stylex`) - Primary CSS-in-JS library
  - Build-time style extraction
  - Zero runtime overhead
  - Atomic CSS class generation
  - Type-safe
  - Used by Facebook, Instagram, WhatsApp
- **@stylexjs/babel-plugin** - Required build-time Babel plugin
- **@stylexjs/cli** - StyleX CLI tools

## Build & Dev Environment
- **Metro** - Meta's bundler (used by React Native, integrates with StyleX)
  - OR **Vite** - Faster alternative, excellent React support
- **Babel** - Required for StyleX transformation
  - `@babel/core`
  - `@babel/preset-env`
  - `@babel/preset-react`
  - `@babel/preset-typescript`
- **ESLint** - Linting
  - `@stylexjs/eslint-plugin` - StyleX-specific linting rules
  - `eslint-plugin-react`
  - `eslint-plugin-react-hooks`

## Testing
- **Jest** - Primary test framework (Meta uses it)
- **React Testing Library** - Component testing
- **Testing Library StyleX** - StyleX-specific queries and utilities
- **Playwright** - E2E testing

## State Management
- **React Context + useReducer** - Built-in state management (Meta's approach)
- **TanStack Query** (`@tanstack/react-query`) - Server state/data fetching
- **Jotai** - Lightweight atomic state (alternative to Redux)

## Routing
- **React Router v7** - Industry standard
- **TanStack Router** - Type-first alternative gaining traction

## Animation
- **Framer Motion** - Production-ready animations
- **React Spring** - Spring physics animations (alternative)

## Icons
- **React Icons** - Comprehensive icon set
- **Lucide** - Modern, open source icon library

## Data & Forms
- **TanStack Form** - Headless form library
- **Zod** - Schema validation
- **date-fns** or **Temporal** - Date handling

## Performance & Optimization
- **React DevTools** - Browser extension
- **Web Vitals** - Performance monitoring (`@web-vitals/browser`)
- **Lighthouse** - Automated audits

## CI/CD & Quality
- **Husky** - Git hooks
- **lint-staged** - Run linters on staged files
- **GitHub Actions** - CI/CD pipeline

## Recommended Directory Structure
```
frontend/
├── src/
│   ├── components/       # React components with StyleX styles
│   ├── hooks/            # Custom React hooks
│   ├── utils/            # Utility functions
│   ├── types/            # TypeScript type definitions
│   ├── styles/           # Global StyleX styles
│   ├── pages/            # Page components
│   └── app.tsx           # Root component
├── babel.config.js
├── stylex.config.js
├── eslint.config.js
├── jest.config.js
├── package.json
└── tsconfig.json
```

## Key Dependencies (package.json)
```json
{
  "dependencies": {
    "react": "^18.3.0",
    "react-dom": "^18.3.0",
    "@stylexjs/stylex": "^0.1.0",
    "@tanstack/react-query": "^5.0.0",
    "react-router-dom": "^7.0.0"
  },
  "devDependencies": {
    "@babel/core": "^7.0.0",
    "@babel/preset-env": "^7.0.0",
    "@babel/preset-react": "^7.0.0",
    "@babel/preset-typescript": "^7.0.0",
    "@stylexjs/babel-plugin": "^0.1.0",
    "@stylexjs/eslint-plugin": "^0.1.0",
    "eslint": "^9.0.0",
    "jest": "^29.0.0",
    "@testing-library/react": "^16.0.0",
    "@testing-library/stylex": "^1.0.0",
    "playwright": "^1.0.0",
    "vite": "^6.0.0"
  }
}
```

## Build Command Example (Metro)
```bash
# Install dependencies
npm install

# Build
npx stylex compile src/ --out-dir dist/
npx metro --config metro.config.js
```

## StyleX Usage Example
```jsx
import { stylex } from '@stylexjs/stylex';

const buttonStyles = stylex.create({
  base: {
    display: 'inline-flex',
    alignItems: 'center',
    padding: '8px 16px',
    borderRadius: 4,
    fontSize: 14,
    fontWeight: 'bold',
    cursor: 'pointer',
    border: 'none',
  },
  primary: {
    background: 'blue',
    color: 'white',
  },
  secondary: {
    background: 'gray',
    color: 'white',
  }
});

export function Button({ variant, children }) {
  return (
    <button
      {...stylex.props(
        buttonStyles.base,
        variant === 'primary' ? buttonStyles.primary : buttonStyles.secondary
      )}
    >
      {children}
    </button>
  );
}
```
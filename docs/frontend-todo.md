# Frontend Rebuild: Complete Todo List

## Current State
- Legacy frontend using Browserify, CoffeeScript, Sass, Tailwind
- No testing framework
- Build takes 30-60s
- No PWA features
- No analytics

## New Stack
- React 18/19 with TypeScript
- Vite for bundling
- StyleX for all styling
- Jest + RTL for testing
- Matomo for analytics
- PWA with service worker

---

## Phase 1: Foundation Setup

### Task 1.1: Initialize New Frontend Directory
```bash
mkdir -p frontend-next/src/{components,hooks,utils,pages,types}
mkdir -p frontend-next/{build,assets,public}
```
[ ] Create directory structure
[ ] Initialize TypeScript config (tsconfig.json)
[ ] Create package.json with new dependencies

### Task 1.2: Install Dependencies
```bash
npm install react react-dom @stylexjs/stylex @stylexjs/babel-plugin
npm install -D @types/react @types/react-dom @vitejs/plugin-react
npm install -D eslint @eslint/js @typescript-eslint/eslint-plugin
npm install -D vitest @testing-library/react @testing-library/stylex
npm install -D husky lint-staged
npm install @stylexjs/stylex @stylexjs/babel-plugin @babel/core @babel/preset-env @babel/preset-react @babel/preset-typescript
npm install -D vite @vitejs/plugin-react @types/node
npm install react-router-dom @tanstack/react-query
npm install -D playwright
```
[ ] Core dependencies
[ ] StyleX and build tools
[ ] Testing tools
[ ] Routing and state management

### Task 1.3: Configure Build Pipeline
```javascript
// vite.config.js
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import stylex from '@stylexjs/vite-plugin';

export default defineConfig({
  plugins: [react(), stylex()],
  build: {
    target: 'es2020',
    sourcemap: true,
  },
  server: {
    port: 5080,
    watch: {
      ignored: ['**/node_modules/**'],
    },
  },
});
```
[ ] Create vite.config.js
[ ] Create babel.config.js for StyleX
[ ] Verify build pipeline works

### Task 1.4: Create Development Script
```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "test": "vitest run",
    "test:watch": "vitest",
    "lint": "eslint . --ext .js,.jsx,.ts,.tsx",
    "lint:fix": "eslint . --ext .js,.jsx,.ts,.tsx --fix",
    "stylelint": "stylelint \"src/**/*.css\"",
    "prettier": "prettier --check \"src/**/*.{js,jsx,ts,tsx,css}\"",
    "prettier:fix": "prettier --write \"src/**/*.{js,jsx,ts,tsx,css}\"",
    "prepare": "husky install"
  }
}
```
[ ] Add dev script
[ ] Add build script
[ ] Add test script
[ ] Add lint script
[ ] Add format script
[ ] Add husky setup

---

## Phase 2: Core Application Structure

### Task 2.1: Create App Shell
```tsx
// frontend-next/src/app.tsx
import { ReactNode } from 'react';

interface AppProps {
  children?: ReactNode;
}

export function App({ children }: AppProps) {
  return (
    <div className="app">
      <header className="header">
        <nav className="nav">
          <a href="/" className="nav-logo">SpaceDock</a>
          <ul className="nav-links">
            <li><a href="/about">About</a></li>
            <li><a href="/contact">Contact</a></li>
          </ul>
        </nav>
      </header>
      <main className="content">
        {children}
      </main>
    </div>
  );
}
```
[ ] Create app shell with header
[ ] Create app shell with footer
[ ] Create navigation bar

### Task 2.2: Create Component Library
```tsx
// frontend-next/src/components/Button.tsx
interface ButtonProps {
  text: string;
  variant?: 'primary' | 'secondary' | 'tertiary';
  onClick?: () => void;
}

export function Button({ text, variant = 'primary', onClick }: ButtonProps) {
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
    },
  });

  return (
    <button
      {...stylex.props(
        buttonStyles.base,
        variant === 'primary' ? buttonStyles.primary : buttonStyles.secondary
      )}
      onClick={onClick}
    >
      {text}
    </button>
  );
}
```
[ ] Create Button component
[ ] Create Card component
[ ] Create Input component
[ ] Create Modal component
[ ] Create Layout component

### Task 2.3: Implement Routing
```tsx
// frontend-next/src/router.tsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { App } from './app';
import { Home } from './pages/Home';
import { About } from './pages/About';
import { Contact } from './pages/Contact';
import { ModPage } from './pages/Mod';
import { SearchPage } from './pages/Search';

export function Router() {
  return (
    <BrowserRouter>
      <App>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/about" element={<About />} />
          <Route path="/contact" element={<Contact />} />
          <Route path="/mod/:id" element={<ModPage />} />
          <Route path="/search" element={<SearchPage />} />
          <Route path="*" element={<div>404</div>} />
        </Routes>
      </App>
    </BrowserRouter>
  );
}
```
[ ] Create router component
[ ] Create page components
[ ] Create 404 page

### Task 2.4: Implement State Management
```tsx
// frontend-next/src/store/counter.ts
import { atom } from 'jotai';

export const counterAtom = atom(0);
```
[ ] Install Jotai
[ ] Create counter store
[ ] Create user store
[ ] Create theme store

---

## Phase 3: Migration - Convert Existing Code

### Task 3.1: Migrate CoffeeScript → TypeScript
```typescript
// Convert all .coffee files to .ts/.tsx
import { Button } from './components/Button';

Button({ text: 'Click me', variant: 'primary' });
```
[ ] Convert all CoffeeScript files
[ ] Convert all Sass files to StyleX components
[ ] Verify all converted files work

### Task 3.2: Migrate Styling
```scss
// Old: Sass
.button {
  padding: 8px 16px;
  border-radius: 4px;
  font-weight: bold;
  
  &.primary {
    background: blue;
    color: white;
  }
}
```

```tsx
// New: StyleX
const buttonStyles = stylex.create({
  base: {
    padding: '8px 16px',
    borderRadius: 4,
    fontWeight: 'bold',
  },
  primary: {
    background: 'blue',
    color: 'white',
  },
});
```
[ ] Convert all Sass to StyleX
[ ] Remove Tailwind CSS dependency
[ ] Verify all styles render correctly

---

## Phase 4: Features & Components

### Task 4.1: Core Features
[ ] Implement user authentication
[ ] Implement mod browsing/search
[ ] Implement mod detail page
[ ] Implement upload flow
[ ] Implement download flow
[ ] Implement user profile

### Task 4.2: Advanced Features
[ ] Implement gamification system
[ ] Implement donation system
[ ] Implement chat system
[ ] Implement notifications
[ ] Implement settings page

---

## Phase 5: Testing

### Task 5.1: Unit Tests
[ ] Write tests for all components
[ ] Write tests for utility functions
[ ] Write tests for store logic

### Task 5.2: Integration Tests
[ ] Write integration tests for critical flows
[ ] Write tests for API integration

### Task 5.3: E2E Tests
[ ] Set up Playwright
[ ] Write E2E tests for critical flows

---

## Phase 6: Optimization

### Task 6.1: Build Optimization
[ ] Enable tree-shaking
[ ] Enable gzip compression
[ ] Optimize bundle splitting

### Task 6.2: Performance Optimization
[ ] Implement code splitting
[ ] Implement lazy loading
[ ] Implement service worker
[ ] Add resource hints

---

## Phase 7: Analytics & Monitoring

### Task 7.1: Matomo Integration
[ ] Install Matomo tracker
[ ] Configure Matomo
[ ] Track page views
[ ] Track custom events
[ ] Track goals
[ ] Set up custom dimensions

### Task 7.2: Error Tracking
[ ] Install Sentry
[ ] Configure Sentry
[ ] Test error reporting

---

## Phase 8: Deployment

### Task 8.1: Container Build
[ ] Update Dockerfile for new frontend
[ ] Test container build
[ ] Verify container runs correctly

### Task 8.2: Swarm Deployment
[ ] Update docker-compose-prod.yml
[ ] Deploy to swarm
[ ] Verify deployment

---

## Completion Checklist

- [ ] All existing functionality works
- [ ] Build time < 10 seconds
- [ ] Test suite passes (unit + integration + E2E)
- [ ] Performance improvements verified
- [ ] Analytics integration working
- [ ] All containerized services running
- [ ] Swarm deployment working
- [ ] Documentation complete

---

## Key Files to Track

- `frontend-next/package.json` - Dependencies
- `frontend-next/tsconfig.json` - TypeScript config
- `frontend-next/vite.config.js` - Build config
- `frontend-next/babel.config.js` - Babel/StyleX config
- `frontend-next/src/` - Source code
- `frontend-next/tests/` - Test files
- `frontend-next/Dockerfile` - Container build

## Current Status: Phase 1 (Foundation Setup)
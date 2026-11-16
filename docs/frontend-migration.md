# Frontend Migration: Current → New Stack

## Current Stack (SpaceDock)

| Category | Current Library | Purpose |
|----------|-----------------|---------|
| Bundler | Browserify | JavaScript bundling |
| Language | CoffeeScript | Primary language |
| Styling | Sass + node-sass | CSS preprocessing |
| CSS Framework | Tailwind CSS | Utility-first styling |
| Post-processing | PostCSS + autoprefixer | Browser compatibility |
| Forms | Vanilla HTML | No form library |
| Charts | Chart.js | Data visualization |
| Uploads | Dropzone.js | File uploads |

## New Stack (StyleX-based)

| Category | New Library | Replaces | Notes |
|----------|-------------|----------|-------|
| Bundler | **Vite** or **Metro** | Browserify | Modern, faster, better DX |
| Language | **TypeScript** | CoffeeScript | Industry standard, better tooling |
| Styling | **StyleX** (`@stylexjs/stylex`) | Sass, Tailwind, PostCSS | Build-time, zero runtime overhead |
| Forms | **TanStack Form** | Vanilla HTML | Headless, type-safe forms |
| Charts | **Chart.js** (keep) or **React Chart.js** | Chart.js | Wrap for React usage |
| Uploads | **React Dropzone** | Dropzone.js | React-friendly wrapper |
| Testing | **Jest + RTL** | None currently | No test framework today |
| Linting | **ESLint + StyleX plugin** | CoffeeLint | Better integration |

## Migration Strategy

### Phase 1: Foundation
1. Replace CoffeeScript with TypeScript
2. Replace Browserify with Vite
3. Set up TypeScript compiler and bundler pipeline
4. Migrate build scripts

### Phase 2: Styling
1. Set up StyleX with Babel plugin
2. Migrate all `.scss` files to StyleX components
3. Remove Tailwind, Sass, PostCSS dependencies
4. Migrate existing CSS variables to StyleX themes

### Phase 3: Forms & Components
1. Wrap Chart.js in React component
2. Replace Dropzone with React Dropzone
3. Set up TanStack Form for all forms
4. Create reusable component library

### Phase 4: Testing & Quality
1. Set up Jest testing framework
2. Write tests for critical components
3. Set up ESLint with StyleX plugin
4. Configure CI/CD integration

## Key Changes

### Before (CoffeeScript + Sass)
```coffeescript
// app.coffee
import { Button } from './components/Button'

Button({ text: 'Click me', variant: 'primary' })
```

### After (TypeScript + StyleX)
```tsx
// app.tsx
import { Button } from './components/Button'

<Button text="Click me" variant="primary" />
```

### Styling Before (Sass)
```scss
// button.scss
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

### Styling After (StyleX)
```tsx
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
# SpaceDock Frontend Development Guidelines

This document provides detailed guidelines for frontend development in SpaceDock, covering CoffeeScript, SCSS, JavaScript, accessibility, and performance optimization.

## CoffeeScript Coding Standards

### Code Organization

- **File Structure**: Organize files by feature or component rather than by type.
- **Component-Based**: Each component should be self-contained with its own CoffeeScript and SCSS files.
- **Naming Conventions**: Use kebab-case for file names (e.g., `mod-card.coffee`).

### Best Practices

1. **Class-Based Components**: Use ES6-style classes for components.
   ```coffeescript
   class ModCard extends Component
     constructor: (element, mod) ->
       super(element)
       @mod = mod
       @render()
   ```

2. **Event Handling**: Use event delegation for dynamic elements.
   ```coffeescript
   document.addEventListener 'click', (e) ->
     if e.target.matches('.like-button')
       modId = e.target.dataset.modId
       toggleLike(modId)
   ```

3. **AJAX Requests**: Use the Fetch API or Axios for asynchronous requests.
   ```coffeescript
   fetch('/api/mods')
     .then(response => response.json())
     .then(mods => @renderMods(mods))
   ```

4. **State Management**: Keep component state localized and avoid global state where possible.

5. **Error Handling**: Always handle errors in asynchronous operations.
   ```coffeescript
   fetch('/api/mods')
     .then(response => response.json())
     .catch(error => console.error('Error fetching mods:', error))
   ```

### Code Style

- **Indentation**: Use 2 spaces for indentation.
- **Line Length**: Limit lines to 80 characters where possible.
- **Comments**: Use JSDoc-style comments for public methods.
  ```coffeescript
  #
  # Renders the mod card
  # @param {Object} mod - The mod data
  #
  render: (mod) ->
  ```

## SCSS Naming Conventions and Architecture

### Architecture

- **7-1 Pattern**: Follow the 7-1 pattern for SCSS architecture.
  - `abstracts/` - Variables, functions, mixins, and placeholders
  - `base/` - Reset and base styles
  - `components/` - Reusable components
  - `layout/` - Grid and header/footer
  - `pages/` - Page-specific styles
  - `themes/` - Theme-specific styles
  - `utils/` - Helpers and utilities

### Naming Conventions

- **BEM Methodology**: Use Block, Element, Modifier (BEM) for naming classes.
  - Block: `.mod-card`
  - Element: `.mod-card__title`
  - Modifier: `.mod-card--featured`

### Variables and Mixins

- **Variables**: Define variables for colors, fonts, and spacing.
  ```scss
  // frontend/styles/abstracts/_variables.scss
  $primary-color: #4285f4;
  $secondary-color: #34a853;
  $error-color: #ea4335;
  ```

- **Mixins**: Create reusable mixins for responsive design and common patterns.
  ```scss
  // frontend/styles/abstracts/_mixins.scss
  @mixin respond-to($breakpoint) {
    @if map-has-key($breakpoints, $breakpoint) {
      @media (min-width: #{map-get($breakpoints, $breakpoint)}) {
        @content;
      }
    }
  }
  ```

### Responsive Design

- Use responsive mixins for breakpoints.
  ```scss
  .mod-card {
    @include respond-to('sm') {
      padding: 24px;
    }
  }
  ```

## JavaScript Module Organization

### Module Structure

- **Entry Points**: Define clear entry points for each page or feature.
- **Dependencies**: Explicitly declare dependencies at the top of each file.
- **Exports**: Use named exports for reusable modules.
  ```coffeescript
  # frontend/coffee/utils/api.coffee
  export fetchMods = (modId) ->
    fetch("/api/mods/#{modId}")
      .then(response => response.json())
  ```

### State Management

- **Local State**: Prefer local component state for UI-related data.
- **Global State**: Use a state management library (e.g., Redux) for shared state.

### Error Handling

- **Centralized Error Handling**: Implement a centralized error handling mechanism.
  ```coffeescript
  window.addEventListener 'error', (event) ->
    logError(event.error)
  ```

## Accessibility Best Practices

### Semantic HTML

- Use semantic HTML elements (`<header>`, `<nav>`, `<main>`, `<footer>`).
- Ensure proper heading hierarchy (`<h1>` to `<h6>`).

### ARIA Attributes

- Use ARIA attributes to enhance accessibility.
  ```html
  <button aria-label="Like this mod">Like</button>
  ```

### Keyboard Navigation

- Ensure all interactive elements are keyboard-accessible.
- Test keyboard navigation thoroughly.

### Color Contrast

- Maintain sufficient color contrast for text.
- Provide alternative text for images.

### Screen Reader Support

- Test with screen readers (e.g., NVDA, VoiceOver).
- Use `aria-hidden="true"` for decorative elements.

## Performance Optimization Tips

### Code Splitting

- Split code into chunks for better loading performance.
- Use dynamic imports for non-critical JavaScript.

### Asset Optimization

- Minify and compress CSS and JavaScript files.
- Optimize images using tools like ImageMagick or Squoosh.

### Caching

- Implement caching strategies for static assets.
- Use service workers for offline support.

### Lazy Loading

- Lazy load images and non-critical components.
  ```html
  <img src="placeholder.jpg" data-src="mod-image.jpg" loading="lazy">
  ```

### Bundle Analysis

- Regularly analyze bundle size using tools like Webpack Bundle Analyzer.
- Remove unused dependencies.

## Security Best Practices

### Input Validation

- Validate all user inputs on both client and server sides.
- Sanitize inputs to prevent XSS attacks.

### Authentication

- Use secure authentication methods (e.g., OAuth, JWT).
- Implement CSRF protection.

### Data Handling

- Avoid storing sensitive data in localStorage or sessionStorage.
- Use HTTPS for all communications.

### Error Handling

- Do not expose sensitive information in error messages.
- Log errors securely.

## Testing

### Unit Testing

- Write unit tests for CoffeeScript components.
  ```coffeescript
  # frontend/test/components/mod_card.test.coffee
  describe 'ModCard component', ->
    it 'should render correctly', ->
      mod = { id: 1, name: 'Test Mod', description: 'Test Description' }
      element = document.createElement('div')
      card = new ModCard(element, mod)
      expect(element.innerHTML).to.contain('Test Mod')
  ```

### Integration Testing

- Test component interactions and API calls.

### End-to-End Testing

- Use tools like Cypress or Selenium for end-to-end testing.

## Resources

- [CoffeeScript Documentation](https://coffeescript.org/)
- [SCSS Documentation](https://sass-lang.com/documentation)
- [Webpack Documentation](https://webpack.js.org/)
- [WCAG Guidelines](https://www.w3.org/WAI/standards-guidelines/wcag/)
- [MDN Web Docs](https://developer.mozilla.org/)

For questions about frontend development, refer to this document or consult the team.
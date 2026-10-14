# SpaceDock Frontend Development Guide

This document provides comprehensive guidance for frontend development in SpaceDock, covering CoffeeScript, SCSS, and JavaScript development.

## Frontend Architecture

SpaceDock uses a modern frontend stack with:

- **CoffeeScript** for application logic
- **SCSS** for styling
- **Twig templates** for HTML structure
- **Webpack** for asset bundling (via npm scripts)

### Directory Structure

```
frontend/
├── coffee/          # CoffeeScript source files
│   ├── app.coffee   # Main application
│   ├── components/  # Reusable components
│   ├── pages/       # Page-specific logic
│   └── utils/       # Utility functions
├── styles/          # SCSS source files
│   ├── main.scss    # Main stylesheet
│   ├── components/  # Component styles
│   ├── pages/       # Page-specific styles
│   └── utils/       # Mixins and variables
├── static/          # Compiled assets
│   ├── css/         # Compiled CSS
│   ├── js/          # Compiled JavaScript
│   └── images/      # Static assets
└── build/           # Build configuration
```

## Development Workflow

### Setting Up Frontend Dependencies

1. Install Node.js and npm
2. Install frontend dependencies:
   ```bash
   npm install
   ```

### Building Frontend Assets

To build assets for development:
```bash
./build-frontend.sh
```

For production builds:
```bash
npm run build:prod
```

### Development Server

Run the development server with hot reloading:
```bash
npm run dev
```

## CoffeeScript Development

### Code Organization

- **app.coffee**: Main application initialization
- **components/**: Reusable UI components
- **pages/**: Page-specific logic
- **utils/**: Helper functions and utilities

### Best Practices

1. **Class-based components**: Use ES6-style classes with CoffeeScript
2. **Event handling**: Use event delegation where appropriate
3. **AJAX requests**: Use the built-in fetch API or axios
4. **State management**: Keep component state localized

### Example Component

```coffeescript
# frontend/coffee/components/mod_card.coffee
class ModCard extends Component
  constructor: (element, mod) ->
    super(element)
    @mod = mod
    @render()

  render: ->
    @element.innerHTML = """
      <div class="mod-card">
        <h3>#{@mod.name}</h3>
        <p>#{@mod.description}</p>
      </div>
    """

  onClick: ->
    window.location.href = "/mod/#{@mod.id}"
```

## SCSS Development

### Style Architecture

- **main.scss**: Main entry point
- **components/**: Component-specific styles
- **pages/**: Page-specific styles
- **utils/**: Variables, mixins, and functions

### Variables and Mixins

```scss
// frontend/styles/utils/_variables.scss
$primary-color: #4285f4;
$secondary-color: #34a853;
$error-color: #ea4335;

$breakpoints: (
  'sm': 576px,
  'md': 768px,
  'lg': 992px,
  'xl': 1200px
);
```

### Responsive Design

```scss
// frontend/styles/utils/_mixins.scss
@mixin respond-to($breakpoint) {
  @if map-has-key($breakpoints, $breakpoint) {
    @media (min-width: #{map-get($breakpoints, $breakpoint)}) {
      @content;
    }
  } @else {
    @warn "Breakpoint `#{$breakpoint}` does not exist in $breakpoints.";
  }
}
```

### Component Styling

```scss
// frontend/styles/components/_mod_card.scss
.mod-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  padding: 16px;
  margin-bottom: 16px;

  h3 {
    color: $primary-color;
    margin-top: 0;
  }

  @include respond-to('sm') {
    padding: 24px;
  }
}
```

## JavaScript Integration

### DOM Manipulation

```coffeescript
# Example: Dynamic content loading
loadMods = (container) ->
  fetch('/api/mods')
    .then(response => response.json())
    .then(mods =>
      container.innerHTML = mods.map(mod =>
        "<div class='mod-item'>#{mod.name}</div>"
      ).join('')
    )
```

### Event Handling

```coffeescript
# Example: Event delegation
document.addEventListener 'click', (e) ->
  if e.target.matches('.like-button')
    modId = e.target.dataset.modId
    toggleLike(modId)
```

## Twig Template Integration

### Passing Data to JavaScript

```twig
{# templates/base.html #}
<script>
  window.SpaceDock = {
    currentUser: {{ current_user.id|json_encode|raw }},
    csrfToken: '{{ csrf_token() }}',
    apiBase: '{{ config('API_BASE_URL') }}'
  };
</script>
```

### Component Placeholders

```twig
{# templates/mods/index.html #}
<div id="mods-container" class="mods-container">
  {# Mod cards will be inserted here by JavaScript #}
</div>
```

## Build Process

### Customizing the Build

Edit `frontend/build/webpack.config.js` to customize:

- Entry points
- Output paths
- Loaders
- Plugins
- Development server options

### Common Build Issues

1. **Missing dependencies**: Run `npm install`
2. **SCSS compilation errors**: Check for syntax errors in SCSS files
3. **CoffeeScript errors**: Verify CoffeeScript syntax
4. **Asset paths**: Ensure paths are correct in webpack config

## Testing Frontend Code

### Unit Testing

```coffeescript
# frontend/test/components/mod_card.test.coffee
describe 'ModCard component', ->
  it 'should render correctly', ->
    mod = { id: 1, name: 'Test Mod', description: 'Test Description' }
    element = document.createElement('div')
    card = new ModCard(element, mod)

    expect(element.innerHTML).to.contain('Test Mod')
    expect(element.innerHTML).to.contain('Test Description')
```

### Integration Testing

Use the development server to test component interactions:
```bash
npm run dev
```

## Deployment

After building assets:
```bash
npm run build:prod
```

The compiled assets will be in `frontend/static/` and served by Flask.

## Best Practices

1. **Component-based architecture**: Build reusable components
2. **Progressive enhancement**: Ensure basic functionality without JavaScript
3. **Accessibility**: Follow WCAG guidelines
4. **Performance**: Optimize asset sizes and loading
5. **Code organization**: Keep files modular and well-documented
6. **Browser support**: Test on supported browsers (Chrome, Firefox, Safari, Edge)

## Resources

- [CoffeeScript Documentation](https://coffeescript.org/)
- [SCSS Documentation](https://sass-lang.com/documentation)
- [Webpack Documentation](https://webpack.js.org/)
- [Twig Documentation](https://twig.symfony.com/)

For questions about frontend development, refer to this document or consult the team.
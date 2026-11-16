# Matomo Analytics Integration

## Overview

Matomo (formerly Piwik) provides comprehensive web analytics. This guide covers deep integration with the SpaceDock frontend.

## Installation

### Basic Setup

```bash
npm install matomo-tracker
```

### Core Configuration

```javascript
import Matomo from 'matomo-tracker';

// Initialize Matomo tracker
const matomo = Matomo({
  siteId: 'YOUR_SITE_ID',
  apiHost: 'https://analytics.spacedock.com',
  domain: 'spacedock.com',
});

// Enable cross-domain tracking
matomo.enableLinkTracking();
matomo.enableHeartBeatTimer();
matomo.enablePerformanceTracking();
```

## Tracking Events

### Page Views

Automatic with React Router:

```javascript
import { useLocation } from 'react-router-dom';
import { useEffect } from 'react';

function App() {
  const location = useLocation();
  
  useEffect(() => {
    // Track page view on route change
    window.matomo.trackPageView(location.pathname);
  }, [location]);

  return (
    <React.StrictMode>
      <Routes>
        <Route path="/" element={<Home />} />
      </Routes>
    </React.StrictMode>
  );
}
```

### Custom Events

Track user interactions:

```javascript
// Download button clicked
window.matomo.trackEvent('download', 'clicked', 'mod_download', 1);

// Search performed
window.matomo.trackEvent('search', 'submitted', 'query_' + query, 1);

// Upload completed
window.matomo.trackEvent('upload', 'completed', 'mod_version_upload', duration_ms);
```

### Goals

Track conversions:

```javascript
// User registered
window.matomo.trackGoal(1);

// Download completed
window.matomo.trackGoal(2, download_size_bytes);

// Donation made
window.matomo.trackGoal(3, donation_amount);
```

## Custom Dimensions

Define custom dimensions in Matomo admin:

### Dimension 1: User Type
```javascript
window.matomo.setCustomDimension(1, user.admin ? 'admin' : 'user');
```

### Dimension 2: Game Platform
```javascript
window.matomo.setCustomDimension(2, game.name);
```

### Dimension 3: User Language
```javascript
window.matomo.setCustomDimension(3, user.locale || 'en-US');
```

### Dimension 4: Browser
```javascript
window.matomo.setCustomDimension(4, navigator.userAgent);
```

## E-commerce Tracking

Track mod downloads and donations:

```javascript
// Add item to cart (mod download)
window.matomo.trackEcommerceItem(
  'item_sku_1',
  'item_id_1',
  'Mod Name',
  'game_id_1',
  15.99,
  1
);

// Record download (purchase)
window.matomo.trackEcommerceOrder(
  'order_id_123',
  15.99,
  1.50, // tax
  0, // shipping
  0 // discount
);

// Record donation
window.matomo.trackEcommerceOrder(
  'donation_id_456',
  25.00,
  0, 0, 0
);
```

## Heatmaps & Session Recordings

### Installation

```bash
npm install @matomo/heatmap @matomo/recorder
```

### Heatmap Tracking

```javascript
import { Heatmap } from '@matomo/heatmap';

const heatmap = new Heatmap({
  siteId: 'YOUR_SITE_ID',
  apiHost: 'https://analytics.spacedock.com',
});
```

### Session Recording

```javascript
import { Recorder } from '@matomo/recorder';

const recorder = new Recorder({
  siteId: 'YOUR_SITE_ID',
  apiHost: 'https://analytics.spacedock.com',
});
```

## Real-time Analytics

### Real-time Visitors

```javascript
// Get current real-time visitors
window.matomo.requestRealtimeVisitors().then(count => {
  console.log('Real-time visitors:', count);
});
```

### Real-time Visits

```javascript
// Track visit start/end
window.matomo.trackVisitStart();
window.matomo.trackVisitEnd();
```

## Advanced Configuration

### Tracking Parameters

```javascript
window.matomo.setConfig({
  // Disable tracking for specific users
  trackOnlyChanges: true,
  // Do not send tracking data for bots
  trackBot: false,
  // Enable custom event tracking
  trackEvents: true,
  // Enable custom dimensions
  trackCustomDimensions: true,
  // Enable custom variables
  trackCustomVariables: true,
});
```

### Privacy Options

```javascript
// IP anonymization
window.matomo.setConfig({
  trackOnlyChanges: true,
  trackBot: false,
});

// Consent management
window.matomo.requireConsent(true);
window.matomo.grantConsent();
window.matomo.withdrawConsent();
```

### Custom Data

```javascript
// Custom visitor information
window.matomo.setCustomDimension(10, 'visitor_type_premium');

// Custom page information
window.matomo.setCustomDimension(11, 'page_category_blog');
```

## Integration Examples

### User Registration Flow

```javascript
// On successful registration
window.matomo.trackGoal(1); // New user registration

// Set user properties
window.matomo.setCustomDimension(1, 'user'); // User type
window.matomo.setCustomDimension(2, 'platform_web'); // Platform
window.matomo.setCustomDimension(3, user.locale || 'en-US'); // Language
```

### Mod Download Flow

```javascript
// When user downloads a mod
window.matomo.trackEvent('download', 'completed', 'mod_download');
window.matomo.trackGoal(2, download_size_bytes);

// Set mod-specific dimensions
window.matomo.setCustomDimension(12, mod_id);
window.matomo.setCustomDimension(13, game_name);
```

### Upload Flow

```javascript
// Track upload completion
window.matomo.trackEvent('upload', 'completed', 'mod_version');
window.matomo.trackGoal(3);

// Track upload errors
window.matomo.trackEvent('upload', 'error', 'upload_failed');
```

## Testing

### Test Tracking

```bash
# Install Matomo CLI tools
npm install -g @matomo/cli

# Test tracking
matomo test --site-id YOUR_SITE_ID --url http://localhost:5080
```

### Verify Events

```bash
# Check if events are being tracked
matomo logs --since 1h
```

## Performance Impact

Matomo adds minimal overhead:

- **Initial load:** +2-5KB (analytics script)
- **Page view tracking:** ~5ms
- **Custom event tracking:** ~2ms
- **E-commerce tracking:** ~10ms

To minimize impact:

```javascript
// Load analytics script async
<script async src="https://cdn.matomo.cloud/matomo.js"></script>

// Use batched tracking for high-frequency events
setInterval(() => {
  window.matomo.flush();
}, 10000); // Send every 10s
```

## Troubleshooting

### Events Not Tracking

```bash
# Check if Matomo is initialized
console.log(window.matomo);

# Check network requests
# Look for POST requests to https://analytics.spacedock.com/matomo.php
```

### Heatmaps Not Working

```bash
# Ensure heatmap plugin is installed
npm list @matomo/heatmap

# Check heatmap configuration
console.log(window.matomo.getConfig());
```

## Resources

- Matomo Documentation: https://matomo.org/docs/
- Matomo API Reference: https://developer.matomo.org/api-reference/
- Matomo JavaScript Tracker: https://developer.matomo.org/api-reference/tracker-javascript
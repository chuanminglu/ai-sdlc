---
applyTo: "**/*.js,**/*.ts,**/*.json"
---
# Chrome Extension Development Guidelines

Apply the [general coding guidelines](./copilot-instructions-general.md) to all code.

## Chrome Extension Specific Guidelines

### Manifest V3 Standards
- Always use Manifest V3 format
- Declare all permissions explicitly and minimally
- Use service workers instead of background pages
- Implement proper content security policy

### Architecture Patterns
- Separate concerns: content scripts, popup, background
- Use message passing for communication between contexts
- Implement proper error handling and fallbacks
- Follow Chrome Extension best practices

### Code Organization
```
src/
├── content/          # Content scripts
├── popup/           # Popup interface
├── background/      # Service worker
├── utils/          # Shared utilities
└── types/          # TypeScript type definitions
```

### Content Scripts
- Keep content scripts lightweight
- Use event delegation for dynamic content
- Implement proper cleanup on page navigation
- Avoid polluting global scope

### Popup Interface
- Design for 400x600px default size
- Implement responsive design principles
- Use semantic HTML elements
- Ensure accessibility compliance

### Message Passing
- Define clear message types and interfaces
- Implement error handling for failed messages
- Use async/await pattern for promise-based messaging
- Add timeout handling for long operations

### Storage Management
- Use Chrome storage API appropriately
- Implement data migration strategies
- Add proper error handling for storage operations
- Consider storage quotas and limits

### Security Best Practices
- Sanitize all user inputs
- Use content security policy
- Avoid eval() and innerHTML with user data
- Implement proper origin validation

### Performance Guidelines
- Minimize DOM manipulation in content scripts
- Use efficient selectors for element queries
- Implement lazy loading where appropriate
- Monitor memory usage and prevent leaks

### Testing Standards
- Write unit tests for utility functions
- Test message passing between contexts
- Validate extension loading and permissions
- Test across different websites and scenarios

## Code Examples

### Message Passing Pattern
```typescript
// content script
chrome.runtime.sendMessage({
  type: 'GET_FORM_DATA',
  payload: formData
}, (response) => {
  if (chrome.runtime.lastError) {
    console.error('Message failed:', chrome.runtime.lastError);
    return;
  }
  // Handle response
});

// popup/background
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'GET_FORM_DATA') {
    // Process data
    sendResponse({ success: true, data: processedData });
  }
  return true; // Keep message channel open for async response
});
```

### Storage Pattern
```typescript
// Save data
await chrome.storage.local.set({ 
  formData: serializedData,
  timestamp: Date.now()
});

// Load data with error handling
try {
  const result = await chrome.storage.local.get(['formData']);
  return result.formData || {};
} catch (error) {
  console.error('Storage error:', error);
  return {};
}
```

### Content Script Pattern
```typescript
// Safe DOM manipulation
function findFormControls(): FormControl[] {
  const forms = document.querySelectorAll('form');
  const controls: FormControl[] = [];
  
  forms.forEach(form => {
    const inputs = form.querySelectorAll('input, select, textarea');
    inputs.forEach(input => {
      if (input instanceof HTMLInputElement || 
          input instanceof HTMLSelectElement || 
          input instanceof HTMLTextAreaElement) {
        controls.push(extractControlData(input));
      }
    });
  });
  
  return controls;
}
```

## Development Workflow
1. Start with manifest.json configuration
2. Implement content script for data extraction
3. Create popup interface
4. Establish message passing
5. Add storage functionality
6. Implement error handling
7. Test across different websites
8. Optimize performance
9. Prepare for Chrome Web Store

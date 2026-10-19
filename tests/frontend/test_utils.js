"""
Frontend utility tests for SpaceDock.

This file contains unit tests for utility functions.
"""

/*** Test Suite: Frontend Utilities ***/

describe('Utility Functions', () => {
    describe('formatDate', () => {
        it('should format a date correctly', () => {
            const date = new Date('2023-01-01T00:00:00Z');
            const formatted = formatDate(date);
            expect(formatted).to.equal('January 1, 2023');
        });
        
        it('should handle invalid dates', () => {
            const formatted = formatDate(null);
            expect(formatted).to.equal('Invalid Date');
        });
    });
    
    describe('truncateText', () => {
        it('should truncate text to specified length', () => {
            const text = 'This is a long text that needs to be truncated';
            const truncated = truncateText(text, 10);
            expect(truncated).to.equal('This is...');
        });
        
        it('should return original text if shorter than limit', () => {
            const text = 'Short';
            const truncated = truncateText(text, 10);
            expect(truncated).to.equal('Short');
        });
    });
    
    describe('debounce', () => {
        it('should debounce function calls', (done) => {
            let callCount = 0;
            const func = () => {
                callCount++;
            };
            const debounced = debounce(func, 100);
            
            debounced();
            debounced();
            debounced();
            
            setTimeout(() => {
                expect(callCount).to.equal(1);
                done();
            }, 150);
        });
    });
    
    describe('isValidEmail', () => {
        it('should validate correct email addresses', () => {
            expect(isValidEmail('test@example.com')).to.be.true;
            expect(isValidEmail('user.name@domain.co.uk')).to.be.true;
        });
        
        it('should reject invalid email addresses', () => {
            expect(isValidEmail('invalid.email')).to.be.false;
            expect(isValidEmail('user@.com')).to.be.false;
            expect(isValidEmail('')).to.be.false;
        });
    });
    
    describe('sanitizeInput', () => {
        it('should sanitize HTML input', () => {
            const dirtyInput = '<script>alert("XSS")</script>Hello';
            const cleanInput = sanitizeInput(dirtyInput);
            expect(cleanInput).to.equal('&lt;script&gt;alert(&quot;XSS&quot;)&lt;/script&gt;Hello');
        });
        
        it('should handle special characters', () => {
            const input = 'Hello & World < 10';
            const sanitized = sanitizeInput(input);
            expect(sanitized).to.equal('Hello &amp; World &lt; 10');
        });
    });
});
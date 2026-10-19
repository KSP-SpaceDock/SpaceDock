"""
Frontend component tests for SpaceDock.

This file contains unit tests for frontend components.
"""

/*** Test Suite: Frontend Components ***/

describe('ModCard component', () => {
    it('should render correctly', () => {
        const mod = {
            id: 1,
            name: 'Test Mod',
            description: 'Test Description',
            author: 'Test Author',
        };
        
        const element = document.createElement('div');
        const card = new ModCard(element, mod);
        
        expect(element.innerHTML).to.contain('Test Mod');
        expect(element.innerHTML).to.contain('Test Description');
        expect(element.innerHTML).to.contain('Test Author');
    });
    
    it('should handle click events', () => {
        const mod = { id: 1, name: 'Test Mod' };
        const element = document.createElement('div');
        const card = new ModCard(element, mod);
        
        spyOn(window, 'location').setProperty('href', 'http://example.com');
        element.querySelector('.mod-card').click();
        
        expect(window.location.href).to.contain('/mod/1');
    });
});

describe('SearchBar component', () => {
    it('should handle search input', () => {
        const element = document.createElement('div');
        const searchBar = new SearchBar(element);
        
        const input = element.querySelector('input');
        input.value = 'test query';
        input.dispatchEvent(new Event('input'));
        
        expect(searchBar.getQuery()).to.equal('test query');
    });
    
    it('should trigger search on button click', () => {
        const element = document.createElement('div');
        const searchBar = new SearchBar(element);
        
        spyOn(searchBar, 'performSearch');
        element.querySelector('button').click();
        
        expect(searchBar.performSearch).to.have.been.called();
    });
});

describe('UserProfile component', () => {
    it('should render user information', () => {
        const user = {
            username: 'testuser',
            email: 'test@example.com',
            mods: [
                { id: 1, name: 'Mod 1' },
                { id: 2, name: 'Mod 2' },
            ],
        };
        
        const element = document.createElement('div');
        const profile = new UserProfile(element, user);
        
        expect(element.innerHTML).to.contain('testuser');
        expect(element.innerHTML).to.contain('test@example.com');
        expect(element.innerHTML).to.contain('Mod 1');
        expect(element.innerHTML).to.contain('Mod 2');
    });
    
    it('should handle edit profile button click', () => {
        const user = { username: 'testuser' };
        const element = document.createElement('div');
        const profile = new UserProfile(element, user);
        
        spyOn(profile, 'openEditModal');
        element.querySelector('.edit-profile').click();
        
        expect(profile.openEditModal).to.have.been.called();
    });
});
"""
Frontend page tests for SpaceDock.

This file contains unit tests for page-specific logic.
"""

/*** Test Suite: Frontend Pages ***/

describe('Mod Page', () => {
    it('should load mod details', () => {
        const mod = {
            id: 1,
            name: 'Test Mod',
            description: 'Test Description',
            versions: [
                { id: 1, friendly_version: '1.0.0' },
                { id: 2, friendly_version: '2.0.0' },
            ],
        };
        
        const element = document.createElement('div');
        const modPage = new ModPage(element, mod);
        
        expect(element.innerHTML).to.contain('Test Mod');
        expect(element.innerHTML).to.contain('Test Description');
        expect(element.innerHTML).to.contain('1.0.0');
        expect(element.innerHTML).to.contain('2.0.0');
    });
    
    it('should handle version selection', () => {
        const mod = {
            id: 1,
            name: 'Test Mod',
            versions: [
                { id: 1, friendly_version: '1.0.0' },
                { id: 2, friendly_version: '2.0.0' },
            ],
        };
        
        const element = document.createElement('div');
        const modPage = new ModPage(element, mod);
        
        spyOn(modPage, 'downloadVersion');
        element.querySelectorAll('.version-select option')[1].selected = true;
        element.querySelector('.version-select').dispatchEvent(new Event('change'));
        
        expect(modPage.downloadVersion).to.have.been.calledWith(2);
    });
});

describe('Search Page', () => {
    it('should display search results', () => {
        const results = [
            { id: 1, name: 'Mod 1', description: 'Description 1' },
            { id: 2, name: 'Mod 2', description: 'Description 2' },
        ];
        
        const element = document.createElement('div');
        const searchPage = new SearchPage(element, results);
        
        expect(element.innerHTML).to.contain('Mod 1');
        expect(element.innerHTML).to.contain('Description 1');
        expect(element.innerHTML).to.contain('Mod 2');
        expect(element.innerHTML).to.contain('Description 2');
    });
    
    it('should handle pagination', () => {
        const results = [
            { id: 1, name: 'Mod 1' },
            { id: 2, name: 'Mod 2' },
        ];
        
        const element = document.createElement('div');
        const searchPage = new SearchPage(element, results);
        
        spyOn(searchPage, 'loadPage');
        element.querySelectorAll('.pagination button')[1].click();
        
        expect(searchPage.loadPage).to.have.been.calledWith(2);
    });
});

describe('User Profile Page', () => {
    it('should display user profile', () => {
        const user = {
            username: 'testuser',
            email: 'test@example.com',
            mods: [
                { id: 1, name: 'Mod 1' },
                { id: 2, name: 'Mod 2' },
            ],
        };
        
        const element = document.createElement('div');
        const profilePage = new UserProfilePage(element, user);
        
        expect(element.innerHTML).to.contain('testuser');
        expect(element.innerHTML).to.contain('test@example.com');
        expect(element.innerHTML).to.contain('Mod 1');
        expect(element.innerHTML).to.contain('Mod 2');
    });
    
    it('should handle mod creation', () => {
        const user = { username: 'testuser' };
        
        const element = document.createElement('div');
        const profilePage = new UserProfilePage(element, user);
        
        spyOn(profilePage, 'openCreateModModal');
        element.querySelector('.create-mod').click();
        
        expect(profilePage.openCreateModModal).to.have.been.called();
    });
});
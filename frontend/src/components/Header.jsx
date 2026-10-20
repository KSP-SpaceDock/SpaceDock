import React from 'react';

const Header = () => {
    return (
        <header className="bg-blue-600 text-white p-4">
            <div className="container mx-auto flex justify-between items-center">
                <h1 className="text-2xl font-bold">SpaceDock</h1>
                <nav>
                    <ul className="flex space-x-4">
                        <li><a href="/" className="hover:underline">Home</a></li>
                        <li><a href="/mods" className="hover:underline">Mods</a></li>
                        <li><a href="/lists" className="hover:underline">Lists</a></li>
                    </ul>
                </nav>
            </div>
        </header>
    );
};

export default Header;
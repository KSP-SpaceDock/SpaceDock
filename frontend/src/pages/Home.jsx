import React from 'react';
import Header from '../components/Header';
import Footer from '../components/Footer';
import ModCard from '../components/ModCard';

const Home = () => {
    const mods = [
        { id: 1, name: 'Mod 1', description: 'Description for Mod 1', author: 'Author 1' },
        { id: 2, name: 'Mod 2', description: 'Description for Mod 2', author: 'Author 2' },
        { id: 3, name: 'Mod 3', description: 'Description for Mod 3', author: 'Author 3' },
    ];

    return (
        <div className="min-h-screen flex flex-col">
            <Header />
            <main className="flex-grow container mx-auto p-4">
                <h1 className="text-3xl font-bold mb-4">Featured Mods</h1>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {mods.map(mod => (
                        <ModCard key={mod.id} mod={mod} />
                    ))}
                </div>
            </main>
            <Footer />
        </div>
    );
};

export default Home;
import React from 'react';

const ModCard = ({ mod }) => {
    return (
        <div className="bg-white rounded-lg shadow-md p-4 mb-4">
            <h2 className="text-xl font-bold mb-2">{mod.name}</h2>
            <p className="text-gray-700 mb-2">{mod.description}</p>
            <p className="text-sm text-gray-500">Author: {mod.author}</p>
        </div>
    );
};

export default ModCard;
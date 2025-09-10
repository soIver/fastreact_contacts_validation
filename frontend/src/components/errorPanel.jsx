// components/ErrorPanel.js
import { XIcon } from '@heroicons/react/outline';
import { useEffect } from 'react';

export default function ErrorPanel({ errors, onClose }) {
    useEffect(() => {
        // Автоматическое закрытие через 5 секунд
        const timer = setTimeout(() => {
            onClose();
        }, 5000);

        return () => clearTimeout(timer);
    }, [onClose]);

    if (!errors || Object.keys(errors).length === 0) return null;

    return (
        <div className="fixed top-0 left-0 right-0 z-50 animate-slideDown">
            <div className="mx-4 mt-4 rounded-lg bg-red-50 p-4 shadow-lg">
                <div className="flex items-start">
                    <div className="flex-1">
                        <h3 className="text-sm font-medium text-red-800">
                            Validation Error
                        </h3>
                        <div className="mt-2 text-sm text-red-700">
                            <ul className="list-disc space-y-1 pl-5">
                                {Object.entries(errors).map(([field, error]) => (
                                    <li key={field}>
                                        <strong>{field.replace('_', ' ')}:</strong> {error}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    </div>
                    <button
                        onClick={onClose}
                        className="ml-4 flex h-7 w-7 items-center justify-center rounded-lg bg-red-100 text-red-500 hover:bg-red-200"
                    >
                        <XIcon className="h-5 w-5" />
                    </button>
                </div>
            </div>
        </div>
    );
}
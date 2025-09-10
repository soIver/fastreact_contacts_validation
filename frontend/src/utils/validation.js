// utils/validation.js

export const validateContact = (contactData) => {
    const errors = {};

    // валидация имени
    if (!contactData.first_name?.trim()) {
        errors.first_name = 'First name is required';
    } else if (contactData.first_name.length < 2) {
        errors.first_name = 'First name must be at least 2 characters';
    }

    // валидация фамилии
    if (!contactData.last_name?.trim()) {
        errors.last_name = 'Last name is required';
    } else if (contactData.last_name.length < 2) {
        errors.last_name = 'Last name must be at least 2 characters';
    }

    // валидация email
    if (contactData.email && !isValidEmail(contactData.email)) {
        errors.email = 'Please enter a valid email address';
    }

    // валидация телефона
    if (contactData.telephone && !isValidPhone(contactData.telephone)) {
        errors.telephone = 'Please enter a valid phone number';
    }

    // валидация заметок
    if (contactData.notes && contactData.notes.length > 500) {
        errors.notes = 'Notes cannot exceed 500 characters';
    }

    return {
        isValid: Object.keys(errors).length === 0,
        errors
    };
};

const isValidEmail = (email) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
};

const isValidPhone = (phone) => {
    const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
    return phoneRegex.test(phone.replace(/[\s\-\(\)]/g, ''));
};

export const formatValidationErrors = (errors) => {
    return Object.values(errors).join(', ');
};
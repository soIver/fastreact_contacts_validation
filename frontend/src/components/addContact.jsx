import { useState } from 'react';
import { PlusIcon, XIcon } from '@heroicons/react/outline';
import ErrorPanel from './errorPanel';
import { validateContact } from '../utils/validation';

export default function AddContact(props) {
  let [isOpen, setIsOpen] = useState(false);

  // states for form (оставляем как было)
  let [firstName, setFirstName] = useState('');
  let [lastName, setLastName] = useState('');
  let [email, setEmail] = useState('');
  let [telephone, setTelephone] = useState('');
  let [company, setCompany] = useState('');
  let [address, setAddress] = useState('');
  let [notes, setNotes] = useState('');

  // Добавляем только состояния для ошибок
  const [validationErrors, setValidationErrors] = useState({});

  let handleSubmit = async (e) => {
    e.preventDefault();

    // Валидация перед отправкой
    const contactData = {
      first_name: firstName,
      last_name: lastName,
      email: email,
      telephone: telephone,
      company: company,
      address: address,
      notes: notes
    };

    const validation = validateContact(contactData);

    if (!validation.isValid) {
      setValidationErrors(validation.errors);
      return; // Не отправляем если есть ошибки
    }

    // Очищаем ошибки если валидация прошла
    setValidationErrors({});

    try {
      let response = await fetch('http://localhost:8000/create-contact', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(contactData),
      });

      if (response.status === 201) {
        // Очищаем форму
        setFirstName('');
        setLastName('');
        setEmail('');
        setTelephone('');
        setCompany('');
        setAddress('');
        setNotes('');

        // reloads the page
        window.location.reload(true);
      }

      if (response.status != 200) {
        console.log(response.text());
      }
    } catch (err) {
      console.log(err);
    }
  };

  // Функция для очистки ошибок при изменении поля
  const clearFieldError = (fieldName) => {
    if (validationErrors[fieldName]) {
      setValidationErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[fieldName];
        return newErrors;
      });
    }
  };

  return (
    <section className="relative z-0">
      {/* ... остальной код без изменений ... */}

      {isOpen ? (
        <div className="bg-gray-100 pb-4">
          {/* Показываем ошибки валидации */}
          {Object.keys(validationErrors).length > 0 && (
            <ErrorPanel
              errors={validationErrors}
              onClose={() => setValidationErrors({})}
            />
          )}

          <p className="p-4 text-sm text-gray-500">
            Please create a new contact.
          </p>

          <div>
            <form action="#" onSubmit={handleSubmit}>
              <div className="mb-4 flex flex-col">
                <div className="border-y border-gray-100">
                  <input
                    type="text"
                    value={firstName}
                    placeholder="First Name"
                    onChange={(e) => {
                      setFirstName(e.target.value);
                      clearFieldError('first_name');
                    }}
                    className={`w-full border-b px-4 py-2 ${validationErrors.first_name ? 'border-red-500 bg-red-50' : ''
                      }`}
                    required
                  />
                  <input
                    type="text"
                    value={lastName}
                    placeholder="Last Name"
                    onChange={(e) => {
                      setLastName(e.target.value);
                      clearFieldError('last_name');
                    }}
                    className={`w-full border-b px-4 py-2 ${validationErrors.last_name ? 'border-red-500 bg-red-50' : ''
                      }`}
                    required
                  />
                  {/* ... остальные поля без изменений ... */}
                </div>
              </div>
              {/* ... остальная форма без изменений ... */}
            </form>
          </div>
        </div>
      ) : null}
    </section>
  );
}
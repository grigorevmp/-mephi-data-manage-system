import React, {useEffect, useState} from 'react';
import '../registration/RegistrationForm.css';
import {registerUser} from "../api";


function RegistrationForm({onRegistration}) {
    const [email, setEmail] = useState('');
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [errorMessage, setErrorMessage] = useState('');
    const [role] = useState('2');

    const API_BASE_URL = 'http://localhost:5000';

    useEffect(() => {
        fetch(`${API_BASE_URL}/get_workspaces`, {
            method: 'GET', headers: {
                'Content-Type': 'application/json',
            }, credentials: 'include',
        })
            .then(response => {
                if (response.status === 200) {
                    window.location.href = '/workspaces';
                }
            });
    }, []);
    const handleSubmit = (event) => {
        event.preventDefault();
        onRegistration(email, password, username, role, setErrorMessage);
    };

    return (
        <div className="login-form-container">
            <header className="login-header">
                Регистрация
            </header>
            {errorMessage && <div className="error-message">{errorMessage}</div>}
            <form className="login-form" onSubmit={handleSubmit}>
                <div className="form-group">
                    <label htmlFor="email">Электронная почта</label>
                    <input
                        type="email"
                        id="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                    />
                </div>
                <div className="form-group">
                    <label htmlFor="username">Имя пользователя</label>
                    <input
                        type="text"
                        id="username"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        required
                    />
                </div>
                <div className="form-group">
                    <label htmlFor="password">Пароль</label>
                    <input
                        type="password"
                        id="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                    />
                </div>
                <button type="submit">Зарегистрироваться</button>
                <button onClick={() => goToLogin()} className="hint">Вход</button>
            </form>
        </div>);
}

export async function handleRegistration(email, password, username, role, setErrorMessage) {
    try {
        const response = await registerUser({email, password, username, role});

        // Handle the response as needed... For example, save the token to localStorage
        if (response === 200) {
            localStorage.setItem('authToken', response.token);

            window.location.href = '/login'; // Redirect to the workspaces page
            // Show the user's workspaces, assuming Search() renders the required content
            console.error('Registration was successful, token provided in the response.');
        } else {
            // If the response doesn't contain a token, let's log an error
            console.error('Registration was unsuccessful, no token provided in the response.');
            setErrorMessage('Невозможно зарегистрировать пользователя с данным логином/почтой');
        }
    } catch (error) {
        // Handle error, e.g., log it to the console or show an error message to the user
        console.error('An error occurred during login:', error);
        setErrorMessage('Невозможно зарегистрировать пользователя с данным логином/почтой');
    }
}

function goToLogin() {
    window.location.href = '/login';
}

export default RegistrationForm;
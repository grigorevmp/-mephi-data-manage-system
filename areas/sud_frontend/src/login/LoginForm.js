import React, {useState} from 'react';
import {loginUser} from '../api';
import './LoginForm.css';


function LoginForm({onLogin}) {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [errorMessage, setErrorMessage] = useState('');

    const handleSubmit = (event) => {
        event.preventDefault();
        onLogin(email, password, setErrorMessage);
    };

    return (
        <div className="login-form-container">
            <header className="login-header">
                Авторизация
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
                    <label htmlFor="password">Пароль</label>
                    <input
                        type="password"
                        id="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                    />
                </div>
                <button type="submit">Вход</button>
                <button onClick={() => goToRegistration()} className="hint">Регистрация</button>
            </form>
        </div>);
}

export async function handleLogin(email, password, setErrorMessage) {
  try {
        const response = await loginUser({email, password});

        if (response === 200) {
            localStorage.setItem('authToken', response.token);

            window.location.href = '/workspaces';
            console.error('Login was successful, no token provided in the response.');
        } else {
            console.error('Login was unsuccessful, no token provided in the response.');
            setErrorMessage('Проверьте логин и пароль');
        }
    } catch (error) {
        console.error('An error occurred during login:', error);
        setErrorMessage('Проверьте логин и пароль');
    }
}

function goToRegistration() {
    window.location.href = '/registration';
}


export default LoginForm;
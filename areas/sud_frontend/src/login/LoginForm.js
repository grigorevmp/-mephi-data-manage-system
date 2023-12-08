import React, {useState} from 'react';
import {loginUser} from '../api';
import './LoginForm.css';


function LoginForm({onLogin}) {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');

    const handleSubmit = (event) => {
        event.preventDefault();
        onLogin(email, password);
    };

    return (
        <div className="login-form-container">
            <header className="login-header">
                Авторизация
            </header>
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

export async function handleLogin(email, password) {
  try {
        const response = await loginUser({email, password});

        // Handle the response as needed... For example, save the token to localStorage
        if (response === 200) {
            localStorage.setItem('authToken', response.token);

            window.location.href = '/workspaces'; // Redirect to the workspaces page
            // Show the user's workspaces, assuming Search() renders the required content
            console.error('Login was successful, no token provided in the response.');
        } else {
            // If the response doesn't contain a token, let's log an error
            console.error('Login was unsuccessful, no token provided in the response.');
        }
    } catch (error) {
        // Handle error, e.g., log it to the console or show an error message to the user
        console.error('An error occurred during login:', error);
    }
}

function goToRegistration() {
    window.location.href = '/registration';
}


export default LoginForm;
import React, {useEffect, useState} from 'react';
import './Admin.css';
import {
    add_department,
    add_user_to_department,
    delete_department,
    delete_user_from_department,
    delete_workspace, update_workspace
} from "../api";

const API_BASE_URL = 'http://localhost:5000';


function Admin() {
    const [workspaces, setWorkspaces] = useState([]);
    const [workspace, setWorkspace] = useState([]);
    const [workspaceOwner, setWorkspaceOwner] = useState([]);
    const [departments, setDepartments] = useState([]);
    const [users, setUsers] = useState([]);
    const [error, setError] = useState(null);
    const [name, setName] = useState(null);
    const [departmentName, setDepartmentName] = useState(null);
    const [status, setStatus] = useState(1);

    const [username, setUsername] = useState("Аноним");
    const [userId, setUserId] = useState("");
    const [userName, setUserName] = useState("");
    const [userDepartments, setUserDepartments] = useState([]);
    const [isAddDepartmentOpen, setDepartmentOpen] = useState(false);
    const [isUserDepartmentOpen, setUserDepartmentOpen] = useState(false);
    const [isChangeUserDepartmentOpen, setChangeUserDepartmentOpen] = useState(false);
    const [isChangeWorkspaceOpen, setChangeWorkspaceOpen] = useState(false);

    const STATUS_MAP = {
        1: 'Активно', 2: 'В архиве', 3: 'Удалено'
    };

    const toggleDepartmentDialog = () => {
        setDepartmentOpen(!isAddDepartmentOpen);
    };

    const toggleChangeWorkspaceOpen = () => {
        setChangeWorkspaceOpen(!isChangeWorkspaceOpen);
    };

    const toggleChangeUserDepartmentDialog = () => {
        setChangeUserDepartmentOpen(!isChangeUserDepartmentOpen);
    };


    const toggleUserDepartmentDialog = () => {
        setUserDepartmentOpen(!isUserDepartmentOpen);
    };

    const handleUserDepartmentClick = (name) => {
        fetch(`${API_BASE_URL}/department/users?name=${name}`, {
            method: 'GET', headers: {
                'Content-Type': 'application/json',
            }, credentials: 'include',
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                setUserDepartments(data["users"]);
                toggleUserDepartmentDialog()
            })
            .catch(error => {
                setError(error.message);
            });
    };

    useEffect(() => {
        fetch(`${API_BASE_URL}/all_workspaces`, {
            method: 'GET', headers: {
                'Content-Type': 'application/json',
            }, credentials: 'include',
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                setWorkspaces(data["workspaces"]);
            })
            .catch(error => {
                setError(error.message);
            });
    }, []);

    useEffect(() => {
        fetch(`${API_BASE_URL}/department`, {
            method: 'GET', headers: {
                'Content-Type': 'application/json',
            }, credentials: 'include',
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                setDepartments(data["departments"]);
            })
            .catch(error => {
                setError(error.message);
            });
    }, []);

    useEffect(() => {
        fetch(`${API_BASE_URL}/user`, {
            method: 'GET', headers: {
                'Content-Type': 'application/json',
            }, credentials: 'include',
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                setUsers(data["users"]);
            })
            .catch(error => {
                setError(error.message);
            });
    }, []);

    useEffect(() => {
        fetch(`${API_BASE_URL}/whoiam`, {
            method: 'GET', headers: {
                'Content-Type': 'application/json',
            }, credentials: 'include',
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                setUsername(data["username"]);
            });
    }, []);

    return (
        <div className="page">

            {/*/ ДИАЛОГ ИЗМЕНЕНИЯ РАБОЧЕГО ПРОСТРАНСТВА /*/}

            {isChangeWorkspaceOpen && (
                <div className="dialog-container">
                    <h3>
                        Редактировать рабочее пространство
                    </h3>
                    <div className="form-group">
                        <label>
                            Статус:
                            <select
                                value={status}
                                onChange={(e) => setStatus(e.target.value)}
                            >
                                {Object.entries(STATUS_MAP).map(([key, value]) => (
                                    <option key={key} value={key}>
                                        {value}
                                    </option>
                                ))}
                            </select>
                        </label>
                        <label htmlFor="name">Владелец</label>
                        <input
                            type="text"
                            id="name"
                            value={workspaceOwner}
                            onChange={(e) => setWorkspaceOwner(e.target.value)}
                            required
                        />
                    </div>
                    <button className="add-workspace-button"
                            onClick={() => updateWorkspace(workspace, status, workspaceOwner)}>Сохранить
                    </button>
                    <button className="add-workspace-button-close" onClick={toggleChangeWorkspaceOpen}>Закрыть
                    </button>
                </div>
            )}

            {/*/ ДИАЛОГ ДОБАВЛЕНИЯ ОТДЕЛА ЮЗЕРУ /*/}

            {isChangeUserDepartmentOpen && (
                <div className="dialog-container">
                    <h3>
                        Изменить отдел для {userName}
                    </h3>
                    <div className="form-group">
                        <label htmlFor="name">Отдел</label>
                        <input
                            type="text"
                            id="name"
                            value={departmentName}
                            onChange={(e) => setDepartmentName(e.target.value)}
                            required
                        />
                    </div>
                    <button className="add-workspace-button"
                            onClick={() => handleAddUserToDepartmentDeleting(departmentName, userId)}>Сохранить
                    </button>
                    <button className="add-workspace-button-close" onClick={toggleChangeUserDepartmentDialog}>Закрыть
                    </button>
                </div>
            )}

            {/*/ ДИАЛОГ СОЗДАНИЯ ОТДЕЛА /*/}

            {isAddDepartmentOpen && (
                <div className="dialog-container">
                    <h3>
                        Создать отдел
                    </h3>
                    <div className="form-group">
                        <label htmlFor="name">Заголовок</label>
                        <input
                            type="text"
                            id="name"
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            required
                        />
                    </div>
                    <button className="add-workspace-button"
                            onClick={() => handleDepartmentAdding(name)}>Сохранить
                    </button>
                    <button className="add-workspace-button-close" onClick={toggleDepartmentDialog}>Закрыть</button>
                </div>
            )}

            {/*/ ДИАЛОГ ПОЛЬЗОВАТЕЛЕЙ В ОТДЕЛЕ /*/}

            {isUserDepartmentOpen && (
                <div className="dialog-container">
                    <h3>
                        Пользователи в отделе
                    </h3>

                    {userDepartments.length > 0 ? (<ul className="all-workspaces-container">
                        {userDepartments.map(user_department => (
                            <div>
                                <li className="item-block-inner">{user_department.email}
                                    <button className="admin-button-action" onClick={() => {
                                        handleDeleteUserFromDepartmentDeleting(departmentName, user_department.id)
                                    }}>Удалить
                                    </button>
                                </li>
                            </div>
                        ))}

                    </ul>) : (<p className="workspace-item-p">Нет пользователей в отделе</p>)}
                    <button className="workspace-archive-button-close" onClick={() => toggleUserDepartmentDialog()}>
                        Закрыть
                    </button>
                </div>
            )}

            <div className="workspaces-container">

                {/*/ ЗАГОЛОВОК /*/}

                <div className="workspace-title-container">
                    <h2 className="workspace-title"><span
                        onClick={() => goHome()}
                        style={{cursor: "pointer"}}
                    >🏠</span> Панель администратора</h2>
                    <div className="username-info-right">
                        <div className="username" onClick={() => goToProfile()}>
                            <p className="request-content">{username}</p>
                        </div>
                    </div>
                </div>

                <div className="workspace-block">

                    {/*/ ВСЕ ПРОСТРАНСТВА /*/}

                    <div className="all-workspaces">
                        <div>
                            <h4>Рабочие пространства</h4>
                            {workspaces != null && workspaces.length > 0 ? (<ul className="all-workspaces-container">
                                {workspaces.map(workspace => (
                                    <li onClick={() => {
                                        setWorkspace(workspace.id)
                                        setWorkspaceOwner(workspace.owner_id)
                                        setStatus(workspace.status)
                                        toggleChangeWorkspaceOpen()
                                    }} key={workspace.id} className="item-block">

                                            <div className="admin-user-block">
                                                <text><b>{workspace.title}</b></text>
                                                <text>Автор: {workspace.owner}</text>
                                            </div>
                                        <div className="workspace-item-action-block">
                                            <div className="workspace-status"
                                                 style={{backgroundColor: getStatusColor(workspace.status)}}>
                                                <p>{STATUS_MAP[workspace.status] || 'Неизвестно'}</p>
                                            </div>
                                            <button className="admin-button-action" onClick={() => {
                                                handleDeleteWorkspace(workspace.id)
                                            }}>
                                                Удалить
                                            </button>
                                        </div>
                                    </li>
                                ))}

                            </ul>) : (<p className="workspace-item-p">Не найдено рабочих пространств</p>)}
                        </div>
                    </div>

                    {/*/ ОТДЕЛЫ /*/}

                    <div className="all-workspaces-secondary">
                        <div>
                            <h4>Отделы</h4>
                            {departments != null && departments.length > 0 ? (<ul className="all-workspaces-container">
                                {departments.map(department => (
                                    <div>
                                        <li onClick={() => {
                                            setDepartmentName(department.department_name)
                                            handleUserDepartmentClick(department.department_name)
                                        }} className="item-block">{department.department_name}
                                            <button className="admin-button-action" onClick={() => {
                                                handleDepartmentDeleting(department.department_name)
                                            }}>
                                                Удалить
                                            </button>
                                        </li>
                                    </div>
                                ))}
                            </ul>) : (<p className="workspace-item-p">Не найдено отделов</p>)}
                        </div>

                        <button className="add-workspace" onClick={toggleDepartmentDialog}><p>+</p></button>
                    </div>

                    {/*/ ЮЗВЕРЫ /*/}

                    <div className="all-workspaces-secondary">
                        <div>
                            <h4>Пользователи</h4>
                            {users != null && users.length > 0 ? (<ul className="all-workspaces-container">
                                {users.map(user => (
                                    <div>
                                        <li className="item-block" key={user.id}>
                                            <div className="admin-user-block">
                                                <text><b>{user.username}</b></text>
                                                <text>{user.id}</text>
                                            </div>

                                            <button className="admin-button-action" onClick={() => {
                                                setUserId(user.id)
                                                setUserName(user.username)
                                                toggleChangeUserDepartmentDialog()
                                            }}>
                                                Изменить отдел
                                            </button>
                                        </li>
                                    </div>
                                ))}
                            </ul>) : (<p className="workspace-item-p">Не найдено пользователей</p>)}
                        </div>
                    </div>
                </div>
            </div>
        </div>);
}

export async function handleDeleteWorkspace(space_id) {
    try {
        const response = await delete_workspace(space_id);

        if (response === 200) {
            localStorage.setItem('authToken', response.token);

            reload();
            console.error('Department adding was successful, token provided in the response.');
        } else {
            console.error('Department adding was unsuccessful, no token provided in the response.');
        }
    } catch (error) {
        console.error('An error occurred during login:', error);
    }
}

export async function updateWorkspace(space_id, new_status, new_owner) {
    try {
        const response = await update_workspace(space_id, {new_status, new_owner});

        if (response === 200) {
            localStorage.setItem('authToken', response.token);

            reload();
            console.error('Department adding was successful, token provided in the response.');
        } else {
            console.error('Department adding was unsuccessful, no token provided in the response.');
        }
    } catch (error) {
        console.error('An error occurred during login:', error);
    }
}

export async function handleDepartmentAdding(department_name) {
    try {
        const response = await add_department({department_name});

        if (response === 200) {
            localStorage.setItem('authToken', response.token);

            reload();
            console.error('Department adding was successful, token provided in the response.');
        } else {
            console.error('Department adding was unsuccessful, no token provided in the response.');
        }
    } catch (error) {
        console.error('An error occurred during login:', error);
    }
}


export async function handleDepartmentDeleting(department_name) {
    try {
        const response = await delete_department({department_name});

        if (response === 200) {
            localStorage.setItem('authToken', response.token);

            reload();
            console.error('Department deleting was successful, token provided in the response.');
        } else {
            console.error('Department deleting was unsuccessful, no token provided in the response.');
        }
    } catch (error) {
        console.error('An error occurred during login:', error);
    }
}

export async function handleAddUserToDepartmentDeleting(name, user_id) {
    try {
        const users = [user_id]
        const response = await add_user_to_department(name, users);

        if (response === 200) {
            localStorage.setItem('authToken', response.token);

            reload();
            console.error('Adding user to department was successful, token provided in the response.');
        } else {
            console.error('Adding user to department unsuccessful, no token provided in the response.');
        }
    } catch (error) {
        console.error('An error occurred during login:', error);
    }
}

export async function handleDeleteUserFromDepartmentDeleting(name, user_id) {
    try {
        const users = [user_id]
        const response = await delete_user_from_department(name, users);

        if (response === 200) {
            localStorage.setItem('authToken', response.token);

            reload();
            console.error('Adding user to department was successful, token provided in the response.');
        } else {
            console.error('Adding user to department unsuccessful, no token provided in the response.');
        }
    } catch (error) {
        console.error('An error occurred during login:', error);
    }
}

function getStatusColor(status) {
    const statusColors = {
        1: 'green',
        2: 'gray',
        3: 'red'
    };

    return statusColors[status] || 'white';
}

function goHome() {
    window.location.href = '/workspaces';
}


function reload() {
    window.location.href = '/admin';
}

function goToProfile() {
    window.location.href = '/me';
}


export default Admin;
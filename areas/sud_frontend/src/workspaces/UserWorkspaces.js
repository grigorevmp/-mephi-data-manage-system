import React, {useState, useEffect} from 'react';
import './UserWorkspaces.css';
import {
    add_department_access,
    add_email_access, add_url_access,
    add_workspace,
    archive_workspace,
    delete_department_access,
    delete_email_access, delete_url_access
} from "../api";

const API_BASE_URL = 'http://localhost:5000';

function UserWorkspaces() {
    const [workspace, setWorkspace] = useState("");
    const [workspaces, setWorkspaces] = useState([]);
    const [workspaces_access, setWorkspaces_access] = useState([]);
    const [workspaces_open, setWorkspaces_open] = useState([]);
    const [username, setUsername] = useState("Anonim");
    const [error, setError] = useState(null);
    const [isDialogOpen, setIsDialogOpen] = useState(false);
    const [isConfirmOpen, setIsConfirmOpen] = useState(false);
    const [isAccessOpen, setIsAccessOpen] = useState(false);
    const [accesses, setAccesses] = useState([]);
    const [email, setEmail] = useState("Anonim");
    const [department, setDepartment] = useState("Anonim");

    const [addUserAccessOpen, setAddUserAccessOpen] = useState(false);
    const [addDepartmentAccessOpen, setDepartmentAccessOpen] = useState(false);

    const [title, setTitle] = useState('');
    const [description, setDescription] = useState('');

    const STATUS_MAP = {
        1: 'Активно', 2: 'В архиве', 3: 'Удалено'
    };

    const R_STATUS_MAP = {
        1: 'Открыт', 2: 'В ревью', 3: 'Принят', 4: 'Отклонён', 5: 'Закрыт',
    };

    const toggleDialog = () => {
        setIsDialogOpen(!isDialogOpen);
    };

    const toggleAddDepartmentAccessDialog = () => {
        toggleAccess()
        setDepartmentAccessOpen(!addDepartmentAccessOpen);
    };

    const toggleAddUserAccessDialog = () => {
        toggleAccess()
        setAddUserAccessOpen(!addUserAccessOpen);
    };

    const toggleConfirm = () => {
        setIsConfirmOpen(!isConfirmOpen);
    };

    const toggleAccess = () => {
        setIsAccessOpen(!isAccessOpen);
    };

    const handleWorkspaceClick = (workspaceId) => {
        fetch(`${API_BASE_URL}/get_workspace/${workspaceId}`, {
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
                setWorkspace(data);
            })
            .catch(error => {
                setError(error.message);
            });
    };

    const handleAccessesClick = (workspaceId) => {
        fetch(`${API_BASE_URL}/accesses/${workspaceId}`, {
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
                setAccesses(data["accesses"]);
                toggleAccess()
            })
            .catch(error => {
                setError(error.message);
            });
    };

    useEffect(() => {
        fetch(`${API_BASE_URL}/get_workspaces`, {
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
        fetch(`${API_BASE_URL}/get_workspaces_access`, {
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
                setWorkspaces_access(data["workspaces"]);
            })
            .catch(error => {
                setError(error.message);
            });
    }, []);

    useEffect(() => {
        fetch(`${API_BASE_URL}/get_workspaces_open`, {
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
                setWorkspaces_open(data["workspaces"]);
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
            })
            .catch(error => {
                setError(error.message);
            });
    }, []);

    if (error) {
        return <div>Error: {error}</div>;
    }

    return (
        <div className="page">

            {/*/ ДИАЛОГ СОЗДАНИЯ  ВОРКСПЕЙСА /*/}

            {isDialogOpen && (
                <div className="dialog-container">
                    <h3>
                        Создать рабочее пространство
                    </h3>
                    <div className="form-group">
                        <label htmlFor="title">Заголовок</label>
                        <input
                            type="text"
                            id="title"
                            value={title}
                            onChange={(e) => setTitle(e.target.value)}
                            required
                        />
                    </div>
                    <div className="form-group">
                        <label htmlFor="description">Описание</label>
                        <input
                            type="description"
                            id="description"
                            value={description}
                            onChange={(e) => setDescription(e.target.value)}
                            required
                        />
                    </div>
                    <button className="add-workspace-button"
                            onClick={() => handleWorkspaceAdding(title, description)}>Сохранить
                    </button>
                    <button className="add-workspace-button-close" onClick={toggleDialog}>Закрыть</button>
                </div>
            )}

            {/*/ ДИАЛОГ ДОБАВЛЕНИЯ ДОСТУПА ПО ПОЧТЕ/*/}
            {addUserAccessOpen && (
                <div className="dialog-container">
                    <h3>
                        Добавить доступ для пользователя
                    </h3>
                    <div className="form-group">
                        <label htmlFor="email">Почта пользователя</label>
                        <input
                            type="text"
                            id="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                        />
                    </div>
                    <button className="add-workspace-button"
                            onClick={() => handleAddUserAccessWorkspace(workspace.id, email)}>Сохранить
                    </button>
                    <button className="add-workspace-button-close" onClick={toggleAddUserAccessDialog}>Закрыть</button>
                </div>
            )}

            {/*/ ДИАЛОГ ДОБАВЛЕНИЯ ДОСТУПА ПО ОТДЕЛУ/*/}
            {addDepartmentAccessOpen && (
                <div className="dialog-container">
                    <h3>
                        Добавить доступ для отделу
                    </h3>
                    <div className="form-group">
                        <label htmlFor="email">Имя отдела</label>
                        <input
                            type="text"
                            id="department"
                            value={department}
                            onChange={(e) => setDepartment(e.target.value)}
                            required
                        />
                    </div>
                    <button className="add-workspace-button"
                            onClick={() => handleAddUserAccessWorkspace(workspace.id, department)}>Сохранить
                    </button>
                    <button className="add-workspace-button-close" onClick={toggleAddDepartmentAccessDialog}>Закрыть</button>
                </div>
            )}

            {/*/ ДИАЛОГ ПОДТВЕРЖЕНИЯ АРХИВИРОВАНИЯ /*/}

            {isConfirmOpen && (
                <div className="dialog-container">
                    <h3>
                        Архивировать рабочее пространство?
                    </h3>
                    <button className="workspace-archive-button"
                            onClick={() => handleWorkspaceArchiving(workspace.id)}>Да
                    </button>
                    <button className="workspace-archive-button-close" onClick={toggleConfirm}>Нет</button>
                </div>
            )}

            {/*/ ДИАЛОГ УПРАВЛЕНИЯ ДОСТУПАМИ /*/}

            {isAccessOpen && (
                <div className="dialog-container">
                    <h3>
                        Настроить доступы
                    </h3>

                    {accesses.length > 0 ? (<ul className="all-workspaces-container">
                        {accesses.map(access => (
                            <div>
                                 {access.class === "DepartmentAccess" ? (<li
                                     className="remove-action-button"
                                     onClick={() => handleDeleteDepartmentAccessWorkspace(workspace.id, access.content)}
                                 >Удалить доступ для отдела {access.content}
                                 </li>) : (<p></p>) }
                                 {access.class === "UserAccess" ? (<li
                                     className="remove-action-button"
                                     onClick={() => handleDeleteUserAccessWorkspace(workspace.id, access.content)}
                                 >Удалить доступ для {access.content}</li>) : (<p></p>) }
                            </div>
                        ))}

                    </ul>) : (<p></p>)}

                      {!accesses.some(access => access.class === "UrlAccess") && (
                        <button className="access-action-button" onClick={() => handleAddUrlAccessWorkspace(workspace.id)}>Добавить общий доступ</button>
                      )}
                      {accesses.some(access => access.class === "UrlAccess") && (
                        <button className="remove-action-button" onClick={() => handleDeleteUrlAccessWorkspace(workspace.id)}>Удалить общий доступ</button>
                      )}

                        <button className="access-action-button" onClick={toggleAddUserAccessDialog}>Добавить доступ пользователю</button>
                        <button className="access-action-button" onClick={toggleAddDepartmentAccessDialog}>Добавить доступ отделу</button>

                    <button className="workspace-archive-button-close" onClick={() => toggleAccess()}>
                        Закрыть
                    </button>
                </div>
            )}

            {/*/ ГЛАВНЫЙ ЭКРАН /*/}

            <div className="workspaces-container">

                {/*/ ЗАГОЛОВОК /*/}

                <div className="workspace-title-container">
                    <h2 className="workspace-title"><span
                        onClick={() => goHome()}
                        style={{cursor: "pointer"}}
                    >🏠</span>Рабочие пространства</h2>
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
                            {workspaces.length > 0 ? (<ul className="all-workspaces-container">
                                {workspaces.map(workspace => (
                                    <li onClick={() => handleWorkspaceClick(workspace.id)} className="workspace-item"
                                        key={workspace.id}>{workspace.title}</li>))}
                            </ul>) : (<p className="workspace-item-p">Не найдено рабочих пространств</p>)}

                            {workspaces_access.length > 0 ? (
                                <ul className="all-workspaces-container">
                                    <p className="workspace-item-title">Пространства, к которым предоставлен доступ</p>
                                    {workspaces_access.map(workspace => (
                                        <li onClick={() => handleWorkspaceClick(workspace.id)}
                                            className="workspace-item"
                                            key={workspace.id}>
                                            {2 === workspace.access_type && <span><b>👤</b> </span>}
                                            {3 === workspace.access_type && <span><b>👥</b> </span>}
                                            {workspace.title}
                                        </li>))}
                                </ul>) : (<p></p>)}

                            {workspaces_open.length > 0 ? (
                                <ul className="all-workspaces-container">
                                    <p className="workspace-item-title">Общедоступные пространства</p>
                                    {workspaces_open.map(workspace => (
                                        <li onClick={() => handleWorkspaceClick(workspace.id)}
                                            className="workspace-item"
                                            key={workspace.id}>
                                            {1 === workspace.access_type && <span><b>🔗</b> </span>}
                                            {workspace.title}
                                        </li>))}
                                </ul>) : (<p></p>)}

                            <button className="add-workspace" onClick={toggleDialog}><p>+</p></button>
                        </div>
                    </div>

                    {/*/ ТЕКУЩЕЕ ПРОСТРАНСТВО /*/}

                    <div className="all-files-branches">
                        {workspace !== "" ? (<div>
                            <div className="request-content-title-container">
                                <div>
                                    <h3 className="request-content-title">{workspace.title}</h3>
                                    <p className="request-content">{workspace.description}</p>
                                    <p className="request-content"><b>Автор:</b> {workspace.username}</p>
                                </div>
                                <div className="info-right">
                                    <div className="branches-number">
                                        <p><b>Ветки:</b> {workspace.branches_num}</p>
                                    </div>

                                    <div className="workspace-status"
                                         style={{backgroundColor: getStatusColor(workspace.status)}}>
                                        <p>{STATUS_MAP[workspace.status] || 'Неизвестно'}</p>
                                    </div>
                                </div>
                            </div>

                            <h3>Все ветки</h3>
                            <div className="all-branches">
                                {workspace.branches.length > 0 ? (<ul className="all-branches-container">
                                    {workspace.branches.map(branch => (
                                        <li
                                            className="branch-item"
                                            key={branch.id}
                                            onClick={() => goToBranch(workspace.id, branch.id)}
                                        >
                                            {branch.id === workspace.main_branch && <span><b>🏠</b> </span>}{branch.name}
                                        </li>
                                    ))}
                                </ul>) : (<p>Нет веток</p>)}
                            </div>

                            <h3>Все реквесты</h3>
                            <div className="all-request">
                                {workspace.requests.length > 0 ? (<ul className="all-requests-container">
                                    {workspace.requests.map(request => (
                                        <li className="request-item" key={request.id}>
                                            <div>{request.title}</div>
                                            <div>{request.description}</div>
                                            <div>Статус: {R_STATUS_MAP[workspace.status] || 'Неизвестный статус'}</div>
                                        </li>))}
                                </ul>) : (<p>Нет реквестов.</p>)}
                            </div>

                            {workspace.username === username ? (
                                <div className="workspace-action">
                                    <button className="workspace-access" onClick={() => handleAccessesClick(workspace.id)}><p>Доступы</p></button>
                                    <button className="workspace-archive" onClick={toggleConfirm}><p>Архивировать</p>
                                    </button>
                                </div>
                            ) : (<p></p>)}

                        </div>) : (<p>Нажмите на рабочее пространство для просмотра</p>)}
                    </div>
                </div>
            </div>
        </div>);
}

export async function handleWorkspaceAdding(title, description) {
    try {
        const response = await add_workspace({title, description});

        if (response === 200) {
            localStorage.setItem('authToken', response.token);

            window.location.href = '/workspaces';
            console.error('Registration was successful, token provided in the response.');
        } else {
            console.error('Registration was unsuccessful, no token provided in the response.');
        }
    } catch (error) {
        console.error('An error occurred during login:', error);
    }
}

export async function handleWorkspaceArchiving(id) {
    try {
        const response = await archive_workspace(id);

        if (response === 200) {
            localStorage.setItem('authToken', response.token);

            window.location.href = '/workspaces';
            console.error('Registration was successful, token provided in the response.');
        } else {
            console.error('Registration was unsuccessful, no token provided in the response.');
        }
    } catch (error) {
        console.error('An error occurred during login:', error);
    }
}

export async function handleAddUserAccessWorkspace(space_id, email) {
    try {
        const response = await add_email_access(space_id, email);

        if (response === 200) {
            localStorage.setItem('authToken', response.token);
            goHome()

            console.error('Successfully');
        } else {
            console.error('Unsuccessfully');
        }
    } catch (error) {
        console.error('Error:', error);
    }
}
export async function handleDeleteUserAccessWorkspace(space_id, email) {
    try {
        const response = await delete_email_access(space_id, email);

        if (response === 200) {
            localStorage.setItem('authToken', response.token);
            goHome()

            console.error('Successfully');
        } else {
            console.error('Unsuccessfully');
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

export async function handleAddDepartmentAccessWorkspace(space_id, department) {
    try {
        const response = await add_department_access(space_id, department);

        if (response === 200) {
            localStorage.setItem('authToken', response.token);
            goHome()

            console.error('Successfully');
        } else {
            console.error('Unsuccessfully');
        }
    } catch (error) {
        console.error('Error:', error);
    }
}
export async function handleDeleteDepartmentAccessWorkspace(space_id, department) {
    try {
        const response = await delete_department_access(space_id, department);

        if (response === 200) {
            localStorage.setItem('authToken', response.token);
            goHome()

            console.error('Successfully');
        } else {
            console.error('Unsuccessfully');
        }
    } catch (error) {
        console.error('Error:', error);
    }
}


export async function handleAddUrlAccessWorkspace(space_id, department) {
    try {
        const response = await add_url_access(space_id);

        if (response === 200) {
            localStorage.setItem('authToken', response.token);
            goHome()

            console.error('Successfully');
        } else {
            console.error('Unsuccessfully');
        }
    } catch (error) {
        console.error('Error:', error);
    }
}
export async function handleDeleteUrlAccessWorkspace(space_id, department) {
    try {
        const response = await delete_url_access(space_id);

        if (response === 200) {
            localStorage.setItem('authToken', response.token);
            goHome()

            console.error('Successfully');
        } else {
            console.error('Unsuccessfully');
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

function getStatusColor(status) {
    const statusColors = {
        1: 'green',
        2: 'gray',
        3: 'red'
    };

    return statusColors[status] || 'white'; // Set your default color here.
}

function goHome() {
    window.location.href = '/workspaces';
}

function goToProfile() {
    window.location.href = '/me';
}

function goToBranch(spaceId, branchId) {
    window.location.href = `/branch/${spaceId}/${branchId}`;
}

export default UserWorkspaces;

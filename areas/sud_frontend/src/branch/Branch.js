import React, {useState, useEffect} from 'react';
import './Branch.css';
import {add_request, add_branch, delete_branch} from "../api";
import {useParams} from "react-router-dom";
import {handleWorkspaceAdding} from "../workspaces/UserWorkspaces";

const API_BASE_URL = 'http://localhost:5000';

function Branch() {
    const {space_id, branch_id} = useParams();

    const [branch, setBranch] = useState([]);
    const [username, setUsername] = useState("Anonim");
    const [error, setError] = useState(null);

    const [isDialogOpen, setIsDialogOpen] = useState(false);
    const [isCreateOpen, setIsCreateOpen] = useState(false);
    const [isConfirmOpen, setIsConfirmOpen] = useState(false);

    const [title, setTitle] = useState('');
    const [description, setDescription] = useState('');

    const toggleDialog = () => {
        setIsDialogOpen(!isDialogOpen);
    };

    const toggleCreate = () => {
        setIsCreateOpen(!isCreateOpen);
    };

    const toggleConfirm = () => {
        setIsConfirmOpen(!isConfirmOpen);
    };

    useEffect(() => {
        fetch(`${API_BASE_URL}/workspace/${space_id}/view/${branch_id}`, {
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
                setBranch(data);
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

            {/*/ ДИАЛОГ СОЗДАНИЯ  РЕКВКСТА /*/}

            {isDialogOpen && (
                <div className="dialog-container">
                    <h3>
                        Создать реквест
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
                            onClick={() => handleRequestAdding(space_id, title, description, branch.id, branch.parent)}>Сохранить
                    </button>
                    <button className="add-workspace-button-close" onClick={toggleDialog}>Закрыть</button>
                </div>
            )}

            {/*/ ДИАЛОГ СОЗДАНИЯ  ВЕТКИ /*/}

            {isCreateOpen && (
                <div className="dialog-container">
                    <h3>
                        Создать ветку
                    </h3>
                    <div className="form-group">
                        <label htmlFor="title">Название</label>
                        <input
                            type="text"
                            id="title"
                            value={title}
                            onChange={(e) => setTitle(e.target.value)}
                            required
                        />
                    </div>
                    <button className="add-workspace-button"
                            onClick={() => handleBranchAdding(space_id, title, "-1", branch.id)}>Сохранить
                    </button>
                    <button className="add-workspace-button-close" onClick={toggleCreate}>Закрыть</button>
                </div>
            )}

            {/*/ ДИАЛОГ ПОДТВЕРЖЕНИЯ  АРХИВИРОВАНИЯ /*/}

            {isConfirmOpen && (
                <div className="dialog-container">
                    <h3>
                        Удалить ветку?
                    </h3>
                    <button className="branch-delete-button"
                            onClick={() => handleBranchDeletion(space_id, branch.id, branch.parent)}>Да
                    </button>
                    <button className="branch-delete-button-close" onClick={toggleConfirm}>Нет</button>
                </div>
            )}

            {/*/ ГЛАВНЫЙ ЭКРАН /*/}

            <div className="workspaces-container">

                {/*/ ЗАГОЛОВОК /*/}

                <div className="workspace-title-container">
                    <h2 className="workspace-title">
                        <span
                            onClick={() => goHome()}
                            style={{cursor:"pointer"}}
                        >🏠</span> Просмотр ветки
                    </h2>
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
                            {branch.requests != null && branch.requests.length > 0 ? (<ul className="all-workspaces-container">
                                {branch.requests.map(current_branch => (
                                    <li onClick={() => goToRequest(space_id, branch_id, current_branch.id)} className="workspace-item"
                                        key={current_branch.id}> {current_branch.title}</li>))}
                            </ul>) : (<p className="workspace-item-p">Не найдено реквестов</p>)}

                            {branch.parent !== "-1" && <button className="add-workspace" onClick={toggleDialog}><p>+</p></button>}
                        </div>
                    </div>

                    {/*/ ТЕКУЩЕЕ ПРОСТРАНСТВО /*/}

                    <div className="all-files-branches">
                        {branch !== "" ? (<div>
                            <div className="request-content-title-container">
                                <div>
                                    <h3 className="request-content-title">{branch.parent === "-1" &&
                                        <span><b>🏠</b> </span>} {branch.name}</h3>
                                    <p className="request-content"><b>Автор ветки: </b>{branch.authorName}</p>
                                    {branch.parent !== "-1" &&
                                        <p className="request-content">
                                            <b>Исходная ветка: </b>
                                            <p
                                                className="original-branch-item"
                                                onClick={() => goToBranch(space_id, branch.parent)}
                                            >
                                                {branch.parentName}
                                            </p>
                                        </p>
                                    }
                                    <p className="request-content"><b>Task ID:</b> {branch.task_id}</p>
                                    <p className="request-content"><b>Document name:</b> {branch.document}</p>
                                    <p className="request-content"><b>Document ID:</b> {branch.document_id}</p>
                                </div>
                            </div>
                            
                            <button className="branch-add" onClick={toggleCreate}>Создать ветку</button>
                            {branch.name !== "master" && <button className="branch-delete" onClick={toggleConfirm}>Удалить</button>}

                        </div>) : (<p>Нажмите на рабочее пространство для просмотра</p>)}
                    </div>
                </div>

            </div>
        </div>);
}

export async function handleBranchAdding(space_id, name, document_id, parent_branch_id) {
    try {
        const response = await add_branch({name, document_id, parent_branch_id}, space_id);

        if (response[1] === 200) {
            localStorage.setItem('authToken', response.token);

            goToBranch(space_id, response[0].id);
            console.error('Registration was successful, token provided in the response.');
        } else {
            console.error('Registration was unsuccessful, no token provided in the response.');
        }
    } catch (error) {
        console.error('An error occurred during login:', error);
    }
}

export async function handleRequestAdding(space_id, title, description, source_branch_id, target_branch_id) {
    try {
        const response = await add_request({ title, description, source_branch_id, target_branch_id}, space_id);

        if (response === 200) {
            localStorage.setItem('authToken', response.token);

            goToBranch(space_id, source_branch_id);
            console.error('Registration was successful, token provided in the response.');
        } else {
            console.error('Registration was unsuccessful, no token provided in the response.');
        }
    } catch (error) {
        console.error('An error occurred during login:', error);
    }
}

export async function handleBranchDeletion(space_id, branch_id, branch_parent) {
    try {
        const response = await delete_branch(space_id, branch_id);

        if (response === 200) {
            localStorage.setItem('authToken', response.token);

            goToBranch(space_id, branch_parent);
            console.error('Registration was successful, token provided in the response.');
        } else {
            console.error('Registration was unsuccessful, no token provided in the response.');
        }
    } catch (error) {
        console.error('An error occurred during login:', error);
    }
}

function goToProfile() {
    window.location.href = '/me';
}

function goHome() {
    window.location.href = '/workspaces';
}

function goToBranch(space_id, branch_id) {
    window.location.href = `/branch/${space_id}/${branch_id}`;
}

function goToRequest(space_id, branch_id, request_id) {
    window.location.href = `/request/${space_id}/${branch_id}/${request_id}`;
}

export default Branch;

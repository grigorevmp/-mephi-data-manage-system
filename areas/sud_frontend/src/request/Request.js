import React, {useState, useEffect} from 'react';
import './Request.css';
import {merge_request, close_request} from "../api";
import {useParams} from "react-router-dom";

const API_BASE_URL = 'http://localhost:5000';

function Request() {
    const {space_id, request_id} = useParams();

    const [branch, setBranch] = useState([]);
    const [request, setRequest] = useState([]);
    const [workspace, setWorkspace] = useState([]);
    const [user, setUser] = useState("Anonim");
    const [error, setError] = useState(null);

    const [isCreateOpen, setIsCreateOpen] = useState(false);
    const [isConfirmOpen, setIsConfirmOpen] = useState(false);

    const [title, setTitle] = useState('');
    const [description, setDescription] = useState('');

    const R_STATUS_MAP = {
        1: 'Открыт', 2: 'В ревью', 3: 'Принят', 4: 'Отклонён', 5: 'Закрыт',
    };

    const toggleCreate = () => {
        setIsCreateOpen(!isCreateOpen);
    };

    const toggleConfirm = () => {
        setIsConfirmOpen(!isConfirmOpen);
    };

    useEffect(() => {
        fetch(`${API_BASE_URL}/workspace/${space_id}/request/${request_id}`, {
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
                setRequest(data);
                return fetch(`${API_BASE_URL}/workspace/${space_id}/view/${data.source_branch_id}`, {
                    method: 'GET', headers: {
                        'Content-Type': 'application/json',
                    }, credentials: 'include',
                })
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

    // useEffect(() => {
    //     fetch(`${API_BASE_URL}/workspace/${space_id}/view/${branch_id}`, {
    //         method: 'GET', headers: {
    //             'Content-Type': 'application/json',
    //         }, credentials: 'include',
    //     })
    //         .then(response => {
    //             if (!response.ok) {
    //                 throw new Error(`HTTP error! status: ${response.status}`);
    //             }
    //             return response.json();
    //         })
    //         .then(data => {
    //             setBranch(data);
    //         })
    //         .catch(error => {
    //             setError(error.message);
    //         });
    // }, []);

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
                setUser(data);
            })
            .catch(error => {
                setError(error.message);
            });
    }, []);

    useEffect(() => {
        fetch(`${API_BASE_URL}/get_workspace/${space_id}`, {
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
    }, []);

    if (error) {
        return <div>Error: {error}</div>;
    }

    return (
        <div className="page">
            {/*/ ДИАЛОГ ПОДТВЕРЖЕНИЯ  СОГЛАСОВАНИЯ /*/}

            {isCreateOpen && (
                <div className="dialog-container">
                    <h3>
                        Согласовать изменения?
                    </h3>
                    <button className="branch-delete-button"
                            onClick={() => handleRequestConfirm(space_id, request_id)}>Да
                    </button>
                    <button className="branch-delete-button-close" onClick={toggleCreate}>Нет</button>
                </div>
            )}

            {/*/ ДИАЛОГ ПОДТВЕРЖЕНИЯ  УДАЛЕНИЯ /*/}

            {isConfirmOpen && (
                <div className="dialog-container">
                    <h3>
                        Удалить реквест?
                    </h3>
                    <button className="branch-delete-button"
                            onClick={() => handleRequestDeletion(space_id, request_id)}>Да
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
                        >🏠</span> Просмотр реквеста
                    </h2>
                    <div className="username-info-right">
                        <div className="username" onClick={() => goToProfile()}>
                            <p className="request-content">{user.username}</p>
                        </div>
                    </div>
                </div>

                <div className="workspace-block">

                    {/*/ ТЕКУЩЕЕ ПРОСТРАНСТВО /*/}

                    <div className="all-files-branches">
                        {request !== "" ? (<div>
                            <div className="request-content-title-container">
                                <div>
                                    <h3 className="request-content-title">{request.title}</h3>
                                    <p className="request-content"><b>Описание: </b>{request.description}</p>
                                </div>
                                <div className="info-right">
                                    <div className="workspace-status"
                                            style={{backgroundColor: getStatusColor(request.status)}}>
                                            <p>{R_STATUS_MAP[request.status] || 'Неизвестно'}</p>
                                    </div>
                                </div>
                            </div> 
                            <div className="all-branches">      
                                <p className="request-content">
                                    <b>Исходная ветка: </b>
                                    <p
                                        className="original-branch-item"
                                        onClick={() => goToBranch(space_id, request.source_branch_id)}
                                    >
                                        {branch.name}
                                    </p>
                                </p>
                                <p className="request-content">
                                    <b>Целевая ветка: </b>
                                    <p
                                        className="original-branch-item"
                                        onClick={() => goToBranch(space_id, request.target_branch_id)}
                                    >
                                        {branch.parentName}
                                    </p>
                                </p>
                            </div>
                            
                            {(workspace.user_id === user.id && request.status < 3) && <button className="branch-add" onClick={toggleCreate}>Согласовать</button>}
                            {((branch.author === user.id || workspace.user_id === user.id) && request.status < 3) && <button className="branch-delete" onClick={toggleConfirm}>Удалить</button>}

                        </div>) : (<p>Нажмите на рабочее пространство для просмотра</p>)}
                    </div>
                </div>

            </div>
        </div>);
}

export async function handleRequestConfirm(space_id, request_id) {
    try {
        const response = await merge_request(space_id, request_id);

        if (response === 200) {
            localStorage.setItem('authToken', response.token);

            goHome();
            console.error('Registration was successful, token provided in the response.');
        } else {
            console.error('Registration was unsuccessful, no token provided in the response.');
        }
    } catch (error) {
        console.error('An error occurred during login:', error);
    }
}

export async function handleRequestDeletion(space_id, request_id) {
    try {
        const response = await close_request(space_id, request_id);

        if (response === 200) {
            localStorage.setItem('authToken', response.token);

            goHome();
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

function getStatusColor(status) {
    const statusColors = {
        1: 'blue',
        2: 'yellow',
        3: 'green',
        4: 'red',
        5: 'gray'
    };

    return statusColors[status] || 'white'; 
}

export default Request;
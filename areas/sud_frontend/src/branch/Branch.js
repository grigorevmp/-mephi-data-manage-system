import React, {useState, useEffect} from 'react';
import './Branch.css';
import {
    add_request, add_branch, delete_branch, rename_file, upload_file, copy_to_workspace
} from "../api";
import {useParams} from "react-router-dom";

const API_BASE_URL = 'http://localhost:5000';

function Branch() {
    const {space_id, branch_id} = useParams();

    const [branch, setBranch] = useState([]);
    const [username, setUsername] = useState("Anonim");
    const [error, setError] = useState(null);
    const [file, setFile] = useState();
    const [result, setResult] = useState(null);

    const [isDialogOpen, setIsDialogOpen] = useState(false);
    const [isCopyDialogOpen, setCopyDialogOpen] = useState(false);
    const [isViewDocumentOpen, setViewDocumentOpen] = useState(false);
    const [isUploadDocumentOpen, setUploadDocumentOpen] = useState(false);
    const [isCreateOpen, setIsCreateOpen] = useState(false);
    const [isConfirmOpen, setIsConfirmOpen] = useState(false);
    const [isRenameDocumentOpen, setRenameDocumentOpen] = useState(false);

    const [title, setTitle] = useState('');
    const [titleError, setTitleError] = useState('');
    const [description, setDescription] = useState('');
    const [fileContent, setFileContent] = useState('');
    const [name, setName] = useState('');

    function readFileDataAsBase64(e) {
        const file = e.target.files[0];

        return new Promise((resolve, reject) => {
            const reader = new FileReader();

            reader.onload = (event) => {
                resolve(event.target.result);
            };

            reader.onerror = (err) => {
                reject(err);
            };

            reader.readAsDataURL(file);
        });
    }

    const handleFileChange = (e) => {
        if (e.target.files && e.target.files.length > 0) {
            const uploadedFile = e.target.files[0];
            setFile(uploadedFile);
            console.error(e.target.files[0]);

            readFileDataAsBase64(e).then(value => {
                console.error(value);
                setResult(value);
            })
        }
    };

    const toggleCopy = () => {
        setCopyDialogOpen(!isCopyDialogOpen);
    };

    const toggleDialog = () => {
        setIsDialogOpen(!isDialogOpen);
    };

    const toggleUploadDocumentOpen = () => {
        setUploadDocumentOpen(!isUploadDocumentOpen);
    };

    const toggleCreate = () => {
        setIsCreateOpen(!isCreateOpen);
    };

    const toggleViewDocument = () => {
        setViewDocumentOpen(!isViewDocumentOpen);
    };

    const toggleRenameDocumentOpen = () => {
        setRenameDocumentOpen(!isRenameDocumentOpen);
    };

    const toggleConfirm = () => {
        setIsConfirmOpen(!isConfirmOpen);
    };

    const viewFileById = (document_id) => {
        fetch(`${API_BASE_URL}/file/${document_id}/view`, {
            method: 'GET', headers: {
                'Content-Type': 'application/json',
            }, credentials: 'include',
        })
            .then(async response => {
                if (!response.ok) {
                    setFileContent("Невозможно просмотреть файл данного типа");
                    toggleViewDocument()
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const contentType = response.headers.get('Content-Type');

                if (contentType.includes('text/plain')) {
                    const textData = await response.text();
                    setFileContent(textData);
                    toggleViewDocument()
                } else {
                    setFileContent("Невозможно просмотреть файл данного типа");
                    toggleViewDocument()
                }
            })
            .catch(error => {
                setFileContent("Невозможно просмотреть файл данного типа");
                toggleViewDocument()
                setError(error.message);
            });
    };

    const downloadFileById = (name, document_id) => {
        fetch(`${API_BASE_URL}/file/${document_id}/view`, {
            method: 'GET', headers: {
                'Content-Type': 'application/json',
            }, credentials: 'include',
        })
            .then(async response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const fileBlob = await response.blob();

                const fileURL = URL.createObjectURL(fileBlob);

                if (response.headers.get('Content-Type').includes('image') || response.headers.get('Content-Type').includes('video')) {
                    // Display it directly.
                    window.open(fileURL, '_blank', 'noopener,noreferrer');
                } else {
                    // For non-displayable files, trigger a download.
                    const a = document.createElement('a');
                    a.href = fileURL;
                    a.download = name;
                    a.click();
                    window.URL.revokeObjectURL(a.href); // Clean up the object URL.
                }
            })
            .catch(error => {
                setError(error.message);
            });
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
                setName(branch.document);
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

    return (<div className="page">


        <div id="fullscreenLoader" className="loader-cover">
            <div className="loader"/>
        </div>
        {/*/ ДИАЛОГ ПРОСМОТРА ФАЙЛА /*/}

        {isViewDocumentOpen && (<div className="dialog-container">
            <h3>
                Просмотр файла
            </h3>
            <p>{fileContent}</p>
            <button className="add-workspace-button-close" onClick={toggleViewDocument}>Закрыть</button>
        </div>)}

        {/*/ ДИАЛОГ СОЗДАНИЯ РЕКВЕСТА /*/}

        {isDialogOpen && (<div className="dialog-container">
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
                {titleError === "Введите заголовок" && <div className="error-message">{titleError}</div>} {}
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
                    onClick={() => {
                        if (title !== "") {
                            handleRequestAdding(space_id, title, description, branch.id, branch.parent)
                            document.getElementById('fullscreenLoader').style.display = 'flex';
                        } else {
                            if (title === "") setTitleError("Введите заголовок");
                        }
                    }

                    }>Сохранить
            </button>
            <button className="add-workspace-button-close" onClick={toggleDialog}>Закрыть</button>
        </div>)}

        {/*/ КОПИРОВАНИЕ ВОРКСПЕЙСА /*/}

        {isCopyDialogOpen && (<div className="dialog-container">
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
                    onClick={() => {
                        document.getElementById('fullscreenLoader').style.display = 'flex';
                        handleWorkspaceAddingByCopy(space_id, branch_id, title, description)
                    }}>Сохранить
            </button>
            <button className="add-workspace-button-close" onClick={toggleCopy}>Закрыть</button>
        </div>)}

        {/*/ ДИАЛОГ ПЕРЕИМЕНОВАНИЯ ДОКУМЕНТА /*/}

        {isRenameDocumentOpen && (<div className="dialog-container">
            <h3>
                Переименование документа
            </h3>
            <div className="form-group">
                <label htmlFor="name">Имя документа</label>
                <input
                    type="text"
                    id="name"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    required
                />
            </div>
            <button className="add-workspace-button"
                    onClick={() => handleDocumentRename(branch.document_id, name)}>Сохранить
            </button>
            <button className="add-workspace-button-close" onClick={() => {
                toggleRenameDocumentOpen();
                setName(branch.document);
            }}>Закрыть
            </button>
        </div>)}

        {/*/ ДИАЛОГ ЗАГРУЗКИ ФАЙЛА ДОКУМЕНТА /*/}

        {isUploadDocumentOpen && (<div className="dialog-container">
            <h3>
                Загрузить новый документ
            </h3>

            <div className="form-group">
                <label htmlFor="fileUpload">Загрузить файл</label>
                <input
                    type="file"
                    id="fileUpload"
                    onChange={handleFileChange}
                />
            </div>
            <button className="add-workspace-button"
                    onClick={() => handleUploadFile(branch.document_id, file, result)}>Сохранить
            </button>
            <button className="add-workspace-button-close" onClick={() => {
                toggleUploadDocumentOpen();
                setName(branch.document);
            }}>Закрыть
            </button>
        </div>)}

        {/*/ ДИАЛОГ СОЗДАНИЯ  ВЕТКИ /*/}

        {isCreateOpen && (<div className="dialog-container">
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
                {titleError === "Введите заголовок" && <div className="error-message">{titleError}</div>} {}
            </div>

            <button className="add-workspace-button"
                    onClick={() => {
                        if (title !== "") {
                            handleBranchAdding(space_id, title, branch.document_id, branch.id)

                            document.getElementById('fullscreenLoader').style.display = 'flex';
                        } else {
                            if (title === "") setTitleError("Введите заголовок");
                        }
                    }}>Сохранить
            </button>
            <button className="add-workspace-button-close" onClick={toggleCreate}>Закрыть</button>
        </div>)}

        {/*/ ДИАЛОГ ПОДТВЕРЖЕНИЯ  АРХИВИРОВАНИЯ /*/}

        {isConfirmOpen && (<div className="dialog-container">
            <h3>
                Удалить ветку?
            </h3>
            <button className="branch-delete-button"
                    onClick={() => handleBranchDeletion(space_id, branch.id, branch.parent)}>Да
            </button>
            <button className="branch-delete-button-close" onClick={toggleConfirm}>Нет</button>
        </div>)}

        {/*/ ГЛАВНЫЙ ЭКРАН /*/}

        <div className="workspaces-container">

            {/*/ ЗАГОЛОВОК /*/}

            <div className="workspace-title-container">
                <h2 className="workspace-title">
                        <span
                            onClick={() => goHome()}
                            style={{cursor: "pointer"}}
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
                        {branch.requests != null && branch.requests.length > 0 ? (
                            <ul className="all-workspaces-container">
                                {branch.requests.map(current_branch => (
                                    <li onClick={() => goToRequest(space_id, current_branch.id)}
                                        className="workspace-item"
                                        key={current_branch.id}> {current_branch.title}</li>))}
                            </ul>) : (<p className="workspace-item-p">Не найдено реквестов</p>)}

                        {branch.parent !== "-1" &&
                            <button className="add-workspace" onClick={toggleDialog}><p>+</p></button>}
                    </div>
                </div>

                {/*/ ТЕКУЩАЯ ВЕТКА /*/}

                <div className="all-files-branches">
                    {branch !== "" ? (<div>
                        <div className="request-content-title-container">
                            <div>
                                <h3 className="request-content-title">{branch.parent === "-1" &&
                                    <span><b>🏠</b> </span>} {branch.name}</h3>
                                <p className="request-content"><b>Автор ветки: </b>{branch.authorName}</p>
                                {branch.parent !== "-1" && <p className="request-content">
                                    <b>Исходная ветка: </b>
                                    <p
                                        className="original-branch-item"
                                        onClick={() => goToBranch(space_id, branch.parent)}
                                    >
                                        {branch.parentName}
                                    </p>
                                </p>}

                                <p className="request-content"><b>Привязанная задача:</b> {branch.task_id}</p>

                                <button className="workspace-archive" onClick={toggleCopy}><p>Копировать ветку в
                                    новое рабочее пространство</p></button>

                                <div className="document-action-block">
                                    <p className="request-content document-name-title"><b>Имя:</b> {branch.document}</p>
                                    <p className="request-content"><b>Идентификатор:</b> {branch.document_id}</p>
                                    <br/>
                                    <button
                                        className="document-action-bottom"
                                        onClick={() => downloadFileById(branch.document, branch.document_id)}>Скачать
                                    </button>
                                    <button
                                        className="document-action-bottom" onClick={toggleUploadDocumentOpen}>Загрузить
                                    </button>
                                    <br/>
                                    <button
                                        className="document-action-bottom"
                                        onClick={() => viewFileById(branch.document_id)}>Просмотр
                                    </button>
                                    <button
                                        className="document-action-bottom" onClick={() => {
                                        setName(branch.document)
                                        toggleRenameDocumentOpen()
                                    }}>Переименовать
                                    </button>
                                </div>

                            </div>
                        </div>

                        <button className="branch-add" onClick={toggleCreate}>Создать ветку</button>
                        {branch.name !== "master" &&
                            <button className="branch-delete" onClick={toggleConfirm}>Удалить</button>}

                    </div>) : (<p>Нажмите на рабочее пространство для просмотра</p>)}
                </div>
            </div>

        </div>
    </div>);
}

export async function handleUploadFile(id, file, result) {
    console.error(file);
    console.error(file.name);
    // const document_data = new FormData();
    // document_data.append(file.name, file, file.name);
    const document_name = file.name

    // This result contains the bytestring data of the file
    const document_data = result;

    // Convert it to a UInt8Array if necessary
    // const bytes = new Uint8Array(arrayBuffer);
    //
    // // Or directly create a Blob if you're going to use formData
    // const document_data = new Blob([arrayBuffer], {type: file.type});

    try {
        const response = await upload_file(id, {document_name, document_data});

        if (response === 200) {
            localStorage.setItem('authToken', response.token);

            window.location.reload();
            console.error('Registration was successful, token provided in the response.');
        } else {
            console.error('Registration was unsuccessful, no token provided in the response.');
        }
    } catch (error) {
        console.error('An error occurred during login:', error);
    }
}

export async function handleDocumentRename(document_id, new_name) {
    try {
        const response = await rename_file(document_id, new_name);

        if (response[1] === 200) {
            localStorage.setItem('authToken', response.token);
            window.location.reload();

            console.error('Registration was successful, token provided in the response.');
        } else {
            console.error('Registration was unsuccessful, no token provided in the response.');
        }
    } catch (error) {
        console.error('An error occurred during login:', error);
    }
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
        const response = await add_request({title, description, source_branch_id, target_branch_id}, space_id);

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

export async function handleWorkspaceAddingByCopy(space_id, branch_id, title, description) {
    try {
        const response = await copy_to_workspace(space_id, branch_id, {title, description});

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

function goToProfile() {
    window.location.href = '/me';
}

function goHome() {
    window.location.href = '/workspaces';
}

function goToBranch(space_id, branch_id) {
    window.location.href = `/branch/${space_id}/${branch_id}`;
}

function goToRequest(space_id, request_id) {
    window.location.href = `/request/${space_id}/${request_id}`;
}

export default Branch;

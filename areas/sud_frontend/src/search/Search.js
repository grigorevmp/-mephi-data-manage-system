import React, {useEffect, useState} from 'react';
import './Search.css';
import {useParams} from "react-router-dom";

const API_BASE_URL = 'http://localhost:5000';

function Search() {
    const {name} = useParams();

    const [documents, setDocuments] = useState([]);
    const [username, setUsername] = useState("Anonim");
    const [search, setSearch] = useState("Поиск");
    const [searchError, setSearchError] = useState('');
    const [error, setError] = useState(null);
    const [branch, setBranch] = useState("");
    const [spaceId, setSpaceId] = useState("");

    useEffect(() => {
        fetch(`${API_BASE_URL}/search?name=${name}`, {
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
                setDocuments(data["items"]);
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

    const handleBranchLoad = (space_id, branch_id) => {
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
                setSpaceId(space_id)
                setBranch(data);
            })
            .catch(error => {
                setError(error.message);
            });
    };

    if (error) {
        return <div>Error: {error}</div>;
    }

    return (<div className="page">

        {/*/ ГЛАВНЫЙ ЭКРАН /*/}

        <div className="workspaces-container">

            {/*/ ЗАГОЛОВОК /*/}

            <div className="workspace-title-container">
                <h2 className="workspace-title">
                        <span
                            onClick={() => goHome()}
                            style={{cursor: "pointer"}}
                        >🏠</span> Поиск
                </h2>

                <div className="search-container">
                    <input
                        type="text"
                        id="search"
                        className={searchError === "Введите название документа для поиска" ? 'input-error' : 'input-search'}
                        value={search}
                        onChange={(e) => {
                            setSearch(e.target.value)
                        }}
                        onKeyDown={(event) => {
                            if (event.key === 'Enter') {
                                if (search !== "") goToSearch(search); else setSearchError('Введите название документа для поиска');
                            }
                        }}
                        required
                    />
                    {searchError === "Введите название документа для поиска" && <div className="error-message">{searchError}</div>} {}
                </div>

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
                        {documents != null && documents.length > 0 ? (<ul className="all-workspaces-container">
                            {documents.map(document => (<li onClick={() => {
                                handleBranchLoad(document.space_id, document.branch_id)
                            }}
                                                            className="workspace-item"
                                                            key={document.id}> {document.name}</li>))}
                        </ul>) : (<p className="workspace-item-p">Не найдено документов</p>)}
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
                                        onClick={() => {
                                        }}
                                    >
                                        {branch.parentName}
                                    </p>
                                </p>}

                                <p className="request-content">
                                    <b>Привязанная задача: </b>
                                    <a href={`http://jira.com/${branch.task_id}`} target="_blank"
                                       rel="noopener noreferrer">
                                        {branch.task_id}
                                    </a>
                                </p>

                                <div className="document-action-block">
                                    <p className="request-content document-name-title"><b>Имя:</b> {branch.document}</p>
                                    <p className="request-content"><b>Идентификатор:</b> {branch.document_id}</p>
                                    <br/>
                                </div>

                                <button className="workspace-archive" onClick={() => {
                                    goToBranch(spaceId, branch.id)
                                }}><p>Открыть ветку</p></button>

                            </div>
                        </div>

                    </div>) : (<p>Нажмите на документ для просмотра</p>)}
                </div>
            </div>

        </div>
    </div>);
}

function goToProfile() {
    window.location.href = '/me';
}

function goToSearch(name) {
    window.location.href = `/search/${name}`;
}

function goHome() {
    window.location.href = '/workspaces';
}

function goToBranch(spaceId, branchId) {
    window.location.href = `/branch/${spaceId}/${branchId}`;
}

export default Search;

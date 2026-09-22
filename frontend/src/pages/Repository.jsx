import { useState } from "react";
import axios from "axios";

function Repository() {
    const [repoUrl, setRepoUrl] = useState("");
    const [repository, setRepository] = useState(null);
    const [files, setFiles] = useState([]);
    const [selectedFile, setSelectedFile] = useState(null);
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);
    const [fileLoading, setFileLoading] = useState(false);

    const handleImport = async (e) => {
        e.preventDefault();

        setError("");
        setRepository(null);
        setFiles([]);
        setSelectedFile(null);
        setLoading(true);

        try {
            const repoResponse = await axios.post(
                "http://127.0.0.1:8000/repositories/import",
                {
                    repo_url: repoUrl
                }
            );

            const repo = repoResponse.data.repository;

            setRepository(repo);

            const filesResponse = await axios.get(
                `http://127.0.0.1:8000/repositories/files/${repo.owner}/${repo.name}`
            );

            setFiles(filesResponse.data.files);

        } catch (err) {
            if (err.response) {
                setError(
                    err.response.data.detail ||
                    "Failed to import repository"
                );
            } else {
                setError("Cannot connect to backend");
            }
        } finally {
            setLoading(false);
        }
    };

    const handleFileClick = async (path) => {
        setError("");
        setFileLoading(true);

        try {
            const response = await axios.get(
                "http://127.0.0.1:8000/repositories/file",
                {
                    params: {
                        owner: repository.owner,
                        repo: repository.name,
                        path: path
                    }
                }
            );

            setSelectedFile(response.data);

        } catch (err) {
            if (err.response) {
                setError(
                    err.response.data.detail ||
                    "Failed to load file"
                );
            } else {
                setError("Cannot connect to backend");
            }
        } finally {
            setFileLoading(false);
        }
    };

    return (
        <div>
            <h1>CodeLens Repository Explorer</h1>

            <form onSubmit={handleImport}>
                <input
                    type="url"
                    value={repoUrl}
                    onChange={(e) => setRepoUrl(e.target.value)}
                    placeholder="https://github.com/user/repository"
                    required
                />

                <button type="submit" disabled={loading}>
                    {loading ? "Importing..." : "Import Repository"}
                </button>
            </form>

            {error && <p>{error}</p>}

            {repository && (
                <div>
                    <h2>{repository.name}</h2>

                    <p>
                        <strong>Owner:</strong> {repository.owner}
                    </p>

                    <p>
                        <strong>Language:</strong>{" "}
                        {repository.language || "Not specified"}
                    </p>
                </div>
            )}

            {files.length > 0 && (
                <div>
                    <h2>Repository Files</h2>

                    {files.map((item, index) => (
                        <div key={index}>
                            {item.type === "folder" ? (
                                <p>
                                    📁 {item.path}
                                </p>
                            ) : (
                                <button
                                    onClick={() =>
                                        handleFileClick(item.path)
                                    }
                                >
                                    📄 {item.path}
                                </button>
                            )}
                        </div>
                    ))}
                </div>
            )}

            {fileLoading && (
                <p>Loading file...</p>
            )}

            {selectedFile && (
                <div>
                    <h2>{selectedFile.name}</h2>

                    <pre>
                        <code>
                            {selectedFile.content}
                        </code>
                    </pre>
                </div>
            )}
        </div>
    );
}

export default Repository;
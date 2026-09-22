from pydantic import BaseModel, HttpUrl


class RepositoryImport(BaseModel):
    repo_url: HttpUrl
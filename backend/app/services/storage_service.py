import os
import uuid
import hashlib
from abc import ABC, abstractmethod
from typing import Tuple
from fastapi import UploadFile, HTTPException, status
from app.config import settings


class StorageServiceBase(ABC):
    @abstractmethod
    async def save_file(self, file: UploadFile) -> Tuple[str, str, int, str]:
        """Saves file securely, returning (stored_filename, file_path, file_size_bytes, sha256_hash)"""
        pass

    @abstractmethod
    def get_file_path(self, stored_filename: str) -> str:
        """Returns safe absolute path to stored file or raises 404"""
        pass

    @abstractmethod
    def delete_file(self, stored_filename: str) -> bool:
        """Deletes file from storage"""
        pass


class LocalStorageService(StorageServiceBase):
    def __init__(self, upload_dir: str = settings.UPLOAD_DIR):
        self.upload_dir = os.path.abspath(upload_dir)
        os.makedirs(self.upload_dir, exist_ok=True)
        self.max_size_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        self.allowed_extensions = settings.allowed_extensions_set

    def _validate_file_extension(self, filename: str) -> str:
        if not filename or "." not in filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Filename has no extension or is invalid",
            )
        ext = filename.rsplit(".", 1)[1].lower()
        if ext not in self.allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file extension '.{ext}'. Allowed: {sorted(list(self.allowed_extensions))}",
            )
        return ext

    async def save_file(self, file: UploadFile) -> Tuple[str, str, int, str]:
        ext = self._validate_file_extension(file.filename)
        
        # Unique non-guessable storage identifier
        unique_id = uuid.uuid4().hex
        stored_filename = f"doc_{unique_id}.{ext}"
        target_path = os.path.join(self.upload_dir, stored_filename)

        # Read content while computing SHA256 and enforcing size limit
        hasher = hashlib.sha256()
        total_size = 0
        chunk_size = 1024 * 64

        try:
            with open(target_path, "wb") as f:
                while True:
                    chunk = await file.read(chunk_size)
                    if not chunk:
                        break
                    total_size += len(chunk)
                    if total_size > self.max_size_bytes:
                        # Clean up partial file
                        f.close()
                        if os.path.exists(target_path):
                            os.remove(target_path)
                        raise HTTPException(
                            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                            detail=f"File exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB}MB",
                        )
                    hasher.update(chunk)
                    f.write(chunk)
        except Exception as e:
            if os.path.exists(target_path):
                try:
                    os.remove(target_path)
                except OSError:
                    pass
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save document securely: {str(e)}",
            )

        sha256_hash = hasher.hexdigest()
        return stored_filename, target_path, total_size, sha256_hash

    def get_file_path(self, stored_filename: str) -> str:
        # Prevent directory traversal attacks
        base_name = os.path.basename(stored_filename)
        safe_path = os.path.abspath(os.path.join(self.upload_dir, base_name))
        
        # Verify the resolved path starts with upload_dir
        if not safe_path.startswith(self.upload_dir):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file path or path traversal detected",
            )
        if not os.path.exists(safe_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document file not found on server",
            )
        return safe_path

    def delete_file(self, stored_filename: str) -> bool:
        try:
            safe_path = self.get_file_path(stored_filename)
            if os.path.exists(safe_path):
                os.remove(safe_path)
                return True
        except Exception:
            pass
        return False


# Singleton storage provider
storage_service = LocalStorageService()

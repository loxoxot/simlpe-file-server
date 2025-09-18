# main.py
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import FileResponse
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from pathlib import Path

app = FastAPI(title="Simple File Server")

# Базовая директория, из которой разрешено отдавать файлы
BASE_DIR = (Path(__file__).parent / "files").resolve()
BASE_DIR.mkdir(exist_ok=True)  # на всякий случай создадим папку


def safe_path(filename: str) -> Path:
    """
    Безопасно получаем абсолютный путь к файлу внутри BASE_DIR.
    Защита от path traversal и пустых имен.
    """
    if not filename or filename.strip() == "":
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail="Параметр 'name' обязателен."
        )
    # запрещаем путь с разделителями каталогов
    if any(sep in filename for sep in ("/", "\\", "..")):
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail="Недопустимое имя файла."
        )

    candidate = (BASE_DIR / filename).resolve()
    # убеждаемся, что файл остаётся внутри BASE_DIR
    if BASE_DIR not in candidate.parents and candidate != BASE_DIR:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail="Недопустимое имя файла."
        )
    return candidate


@app.get("/download")
async def download_file(name: str = Query(..., description="Имя файла в папке 'files'")):
    path = safe_path(name)

    if not path.exists() or not path.is_file():
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail="Файл не найден."
        )

    # FileResponse сам подставит корректные заголовки и content-type по расширению
    return FileResponse(
        path,
        filename=path.name,           # имя в диалоге сохранения
        media_type="application/octet-stream"  # можно не указывать, но так надёжнее
    )


if __name__ == "__main__":
    import uvicorn
    # запуск: uvicorn main:app --reload
    uvicorn.run("main:app", host="0.0.0.0", port=8085, workers=4)

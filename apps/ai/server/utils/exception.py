from fastapi import HTTPException, status


def raise_for_status(status_code: int, message: str = None):
    if status_code < status.HTTP_400_BAD_REQUEST:
        return

    raise HTTPException(status_code=status_code, detail=message)

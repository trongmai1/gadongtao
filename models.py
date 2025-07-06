from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

class SinhVien(BaseModel):
    IDSINHVIEN: str
    HOVATEN: str
    LOP: str
    NGANHHOC: str
    NGAYSINH: Optional[date]

    class Config:
        from_attributes = True

class HocKy(BaseModel):
    IDHOCKY: str
    TENHK: str
    NAMHOC: int

    class Config:
        from_attributes = True

class TieuChiDanhGia(BaseModel):
    IDTIEUCHI: str
    TENTIEUCHI: str
    DIEMTOIDA: int

    class Config:
        from_attributes = True

class DanhGia(BaseModel):
    IDPHIEU: str
    IDTIEUCHI: str
    SVDANHGIA: int
    CANBODANHGIA: int
    CVHTXACNHAN: int

    class Config:
        from_attributes = True

class PhieuDiemRenLuyen(BaseModel):
    IDPHIEU: str
    IDSINHVIEN: str
    IDHOCKY: str
    TONGDIEM: int
    XEPLOAI: str
    GHICHU: Optional[str]

    class Config:
        from_attributes = True
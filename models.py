from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

class SinhVien(BaseModel):
    IDSINHVIEN: str
    HOVATEN: str
    LOP: str 
    NGANHHOC: str
    NGAYSINH: Optional[date]

class HocKy(BaseModel):
    IDHOCKY: str
    TENHK: str
    NAMHOC: int

class TieuChiDanhGia(BaseModel):
    IDTIEUCHI: str
    TENTIEUCHI: str
    DIEMTOIDA: int

class DanhGia(BaseModel):
    IDPHIEU: str
    IDTIEUCHI: str
    SVDANHGIA: str
    CANBODANHGIA: str
    CVHTXACNHANL: str

class PhieuDiemRenLuyen(BaseModel):
    IDPHIEU: str
    IDSINHVIEN: str
    IDHOCKY: str
    TONGDIEM: str
    XEPLOAI:str
    GHICHU: Optional[str]


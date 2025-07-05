from fastapi import FastAPI, HTTPException, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from models import SinhVien, HocKy, TieuChiDanhGia, DanhGia, PhieuDiemRenLuyen
from database import execute_query
from typing import List, Optional
import mysql.connector
from datetime import date

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/sinhvien", response_class=HTMLResponse)
async def get_sinhvien_page(request: Request):
    return templates.TemplateResponse("sinhvien.html", {"request": request})

@app.get("/hocky", response_class=HTMLResponse)
async def get_hocky_page(request: Request):
    return templates.TemplateResponse("hocky.html", {"request": request})

@app.get("/tieuchi", response_class=HTMLResponse)
async def get_tieuchi_page(request: Request):
    return templates.TemplateResponse("tieuchi.html", {"request": request})

@app.get("/danhgia", response_class=HTMLResponse)
async def get_danhgia_page(request: Request):
    return templates.TemplateResponse("danhgia.html", {"request": request})

@app.get("/phieudiem", response_class=HTMLResponse)
async def get_phieudiem_page(request: Request):
    return templates.TemplateResponse("phieudiem.html", {"request": request})

async def check_foreign_key(table: str, column: str, value: str) -> bool:
    queries = {
        "SINHVIEN": ["SELECT COUNT(*) as count FROM PHIEUDIEMRENLUYEN WHERE IDSINHVIEN = %s"],
        "HOCKY": ["SELECT COUNT(*) as count FROM PHIEUDIEMRENLUYEN WHERE IDHOCKY = %s"],
        "TIEUCHIDANHGIA": ["SELECT COUNT(*) as count FROM DANHGIA WHERE IDTIEUCHI = %s"],
        "PHIEUDIEMRENLUYEN": ["SELECT COUNT(*) as count FROM DANHGIA WHERE IDPHIEU = %s"]
    }
    for query in queries.get(table, []):
        result = execute_query(query, (value,), fetch=True)
        if result and result[0]["count"] > 0:
            return True
    return False

@app.get("/api/sinhvien", response_model=List[SinhVien])
async def get_sinhvien():
    result = execute_query("SELECT * FROM SINHVIEN", fetch=True)
    if result is None:
        raise HTTPException(status_code=500, detail="Lỗi cơ sở dữ liệu")
    return result

@app.post("/api/sinhvien")
async def add_sinhvien(
    IDSINHVIEN: str = Form(...),
    HOVATEN: str = Form(...),
    LOP: str = Form(...),
    NGANHHOC: str = Form(...),
    NGAYSINH: Optional[str] = Form(None)
):
    try:
        ngaysinh_date = date.fromisoformat(NGAYSINH) if NGAYSINH else None
        query = "INSERT INTO SINHVIEN (IDSINHVIEN, HOVATEN, LOP, NGANHHOC, NGAYSINH) VALUES (%s, %s, %s, %s, %s)"
        try:
            success = execute_query(query, (IDSINHVIEN, HOVATEN, LOP, NGANHHOC, ngaysinh_date))
            if not success:
                raise HTTPException(status_code=400, detail="Lỗi khi thêm sinh viên")
            return {"message": "Thêm sinh viên thành công"}
        except mysql.connector.Error as e:
            if e.errno == 1062:
                raise HTTPException(status_code=400, detail="Mã sinh viên đã tồn tại")
            raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Ngày sinh không hợp lệ")

@app.put("/api/sinhvien/{IDSINHVIEN}")
async def update_sinhvien(
    IDSINHVIEN: str,
    HOVATEN: str = Form(...),
    LOP: str = Form(...),
    NGANHHOC: str = Form(...),
    NGAYSINH: Optional[str] = Form(None)
):
    try:
        ngaysinh_date = date.fromisoformat(NGAYSINH) if NGAYSINH else None
        query = "UPDATE SINHVIEN SET HOVATEN = %s, LOP = %s, NGANHHOC = %s, NGAYSINH = %s WHERE IDSINHVIEN = %s"
        success = execute_query(query, (HOVATEN, LOP, NGANHHOC, ngaysinh_date, IDSINHVIEN))
        if not success:
            raise HTTPException(status_code=400, detail="Lỗi khi cập nhật sinh viên")
        return {"message": "Cập nhật sinh viên thành công"}
    except mysql.connector.Error as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Ngày sinh không hợp lệ")

@app.delete("/api/sinhvien/{IDSINHVIEN}")
async def delete_sinhvien(IDSINHVIEN: str):
    if await check_foreign_key("SINHVIEN", "IDSINHVIEN", IDSINHVIEN):
        raise HTTPException(status_code=400, detail="Không thể xóa sinh viên vì có dữ liệu liên quan")
    query = "DELETE FROM SINHVIEN WHERE IDSINHVIEN = %s"
    try:
        success = execute_query(query, (IDSINHVIEN,))
        if not success:
            raise HTTPException(status_code=400, detail="Lỗi khi xóa sinh viên")
        return {"message": "Xóa sinh viên thành công"}
    except mysql.connector.Error as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/hocky", response_model=List[HocKy])
async def get_hocky():
    result = execute_query("SELECT * FROM HOCKY", fetch=True)
    if result is None:
        raise HTTPException(status_code=500, detail="Lỗi cơ sở dữ liệu")
    return result

@app.post("/api/hocky")
async def add_hocky(
    IDHOCKY: str = Form(...),
    TENHK: str = Form(...),
    NAMHOC: int = Form(...)
):
    if NAMHOC < 2000:
        raise HTTPException(status_code=400, detail="Năm học phải lớn hơn hoặc bằng 2000")
    query = "INSERT INTO HOCKY (IDHOCKY, TENHK, NAMHOC) VALUES (%s, %s, %s)"
    try:
        success = execute_query(query, (IDHOCKY, TENHK, NAMHOC))
        if not success:
            raise HTTPException(status_code=400, detail="Lỗi khi thêm học kỳ")
        return {"message": "Thêm học kỳ thành công"}
    except mysql.connector.Error as e:
        if e.errno == 1062:
            raise HTTPException(status_code=400, detail="Mã học kỳ đã tồn tại")
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/api/hocky/{IDHOCKY}")
async def update_hocky(
    IDHOCKY: str,
    TENHK: str = Form(...),
    NAMHOC: int = Form(...)
):
    if NAMHOC < 2000:
        raise HTTPException(status_code=400, detail="Năm học phải lớn hơn hoặc bằng 2000")
    query = "UPDATE HOCKY SET TENHK = %s, NAMHOC = %s WHERE IDHOCKY = %s"
    try:
        success = execute_query(query, (TENHK, NAMHOC, IDHOCKY))
        if not success:
            raise HTTPException(status_code=400, detail="Lỗi khi cập nhật học kỳ")
        return {"message": "Cập nhật học kỳ thành công"}
    except mysql.connector.Error as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/api/hocky/{IDHOCKY}")
async def delete_hocky(IDHOCKY: str):
    if await check_foreign_key("HOCKY", "IDHOCKY", IDHOCKY):
        raise HTTPException(status_code=400, detail="Không thể xóa học kỳ vì có dữ liệu liên quan")
    query = "DELETE FROM HOCKY WHERE IDHOCKY = %s"
    try:
        success = execute_query(query, (IDHOCKY,))
        if not success:
            raise HTTPException(status_code=400, detail="Lỗi khi xóa học kỳ")
        return {"message": "Xóa học kỳ thành công"}
    except mysql.connector.Error as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/tieuchi", response_model=List[TieuChiDanhGia])
async def get_tieuchi():
    result = execute_query("SELECT * FROM TIEUCHIDANHGIA", fetch=True)
    if result is None:
        raise HTTPException(status_code=500, detail="Lỗi cơ sở dữ liệu")
    return result

@app.post("/api/tieuchi")
async def add_tieuchi(
    IDTIEUCHI: str = Form(...),
    TENTIEUCHI: str = Form(...),
    DIEMTOIDA: int = Form(...)
):
    if DIEMTOIDA <= 0 or DIEMTOIDA > 25:
        raise HTTPException(status_code=400, detail="Điểm tối đa phải từ 1 đến 25")
    query = "INSERT INTO TIEUCHIDANHGIA (IDTIEUCHI, TENTIEUCHI, DIEMTOIDA) VALUES (%s, %s, %s)"
    try:
        success = execute_query(query, (IDTIEUCHI, TENTIEUCHI, DIEMTOIDA))
        if not success:
            raise HTTPException(status_code=400, detail="Lỗi khi thêm tiêu chí")
        return {"message": "Thêm tiêu chí thành công"}
    except mysql.connector.Error as e:
        if e.errno == 1062:
            raise HTTPException(status_code=400, detail="Mã tiêu chí đã tồn tại")
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/api/tieuchi/{IDTIEUCHI}")
async def update_tieuchi(
    IDTIEUCHI: str,
    TENTIEUCHI: str = Form(...),
    DIEMTOIDA: int = Form(...)
):
    if DIEMTOIDA <= 0 or DIEMTOIDA > 25:
        raise HTTPException(status_code=400, detail="Điểm tối đa phải từ 1 đến 25")
    query = "UPDATE TIEUCHIDANHGIA SET TENTIEUCHI = %s, DIEMTOIDA = %s WHERE IDTIEUCHI = %s"
    try:
        success = execute_query(query, (TENTIEUCHI, DIEMTOIDA, IDTIEUCHI))
        if not success:
            raise HTTPException(status_code=400, detail="Lỗi khi cập nhật tiêu chí")
        return {"message": "Cập nhật tiêu chí thành công"}
    except mysql.connector.Error as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/api/tieuchi/{IDTIEUCHI}")
async def delete_tieuchi(IDTIEUCHI: str):
    if await check_foreign_key("TIEUCHIDANHGIA", "IDTIEUCHI", IDTIEUCHI):
        raise HTTPException(status_code=400, detail="Không thể xóa tiêu chí vì có dữ liệu liên quan")
    query = "DELETE FROM TIEUCHIDANHGIA WHERE IDTIEUCHI = %s"
    try:
        success = execute_query(query, (IDTIEUCHI,))
        if not success:
            raise HTTPException(status_code=400, detail="Lỗi khi xóa tiêu chí")
        return {"message": "Xóa tiêu chí thành công"}
    except mysql.connector.Error as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/danhgia", response_model=List[DanhGia])
async def get_danhgia():
    result = execute_query("SELECT * FROM DANHGIA", fetch=True)
    if result is None:
        raise HTTPException(status_code=500, detail="Lỗi cơ sở dữ liệu")
    return result

@app.post("/api/danhgia")
async def add_danhgia(
    IDPHIEU: str = Form(...),
    IDTIEUCHI: str = Form(...),
    SVDANHGIA: int = Form(...),
    CANBODANHGIA: int = Form(...),
    CVHTXACNHAN: int = Form(...)
):
    if not (0 <= SVDANHGIA <= 25 and 0 <= CANBODANHGIA <= 25 and 0 <= CVHTXACNHAN <= 25):
        raise HTTPException(status_code=400, detail="Điểm phải từ 0 đến 25")
    query = "INSERT INTO DANHGIA (IDPHIEU, IDTIEUCHI, SVDANHGIA, CANBODANHGIA, CVHTXACNHAN) VALUES (%s, %s, %s, %s, %s)"
    try:
        success = execute_query(query, (IDPHIEU, IDTIEUCHI, SVDANHGIA, CANBODANHGIA, CVHTXACNHAN))
        if not success:
            raise HTTPException(status_code=400, detail="Lỗi khi thêm đánh giá")
        return {"message": "Thêm đánh giá thành công"}
    except mysql.connector.Error as e:
        if e.errno == 1062:
            raise HTTPException(status_code=400, detail="Đánh giá đã tồn tại cho phiếu và tiêu chí này")
        if e.errno == 1452:
            raise HTTPException(status_code=400, detail="Mã phiếu hoặc tiêu chí không tồn tại")
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/api/danhgia/{IDPHIEU}/{IDTIEUCHI}")
async def update_danhgia(
    IDPHIEU: str,
    IDTIEUCHI: str,
    SVDANHGIA: int = Form(...),
    CANBODANHGIA: int = Form(...),
    CVHTXACNHAN: int = Form(...)
):
    if not (0 <= SVDANHGIA <= 25 and 0 <= CANBODANHGIA <= 25 and 0 <= CVHTXACNHAN <= 25):
        raise HTTPException(status_code=400, detail="Điểm phải từ 0 đến 25")
    query = "UPDATE DANHGIA SET SVDANHGIA = %s, CANBODANHGIA = %s, CVHTXACNHAN = %s WHERE IDPHIEU = %s AND IDTIEUCHI = %s"
    try:
        success = execute_query(query, (SVDANHGIA, CANBODANHGIA, CVHTXACNHAN, IDPHIEU, IDTIEUCHI))
        if not success:
            raise HTTPException(status_code=400, detail="Lỗi khi cập nhật đánh giá")
        return {"message": "Cập nhật đánh giá thành công"}
    except mysql.connector.Error as e:
        if e.errno == 1452:
            raise HTTPException(status_code=400, detail="Mã phiếu hoặc tiêu chí không tồn tại")
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/api/danhgia/{IDPHIEU}/{IDTIEUCHI}")
async def delete_danhgia(IDPHIEU: str, IDTIEUCHI: str):
    query = "DELETE FROM DANHGIA WHERE IDPHIEU = %s AND IDTIEUCHI = %s"
    try:
        success = execute_query(query, (IDPHIEU, IDTIEUCHI))
        if not success:
            raise HTTPException(status_code=400, detail="Lỗi khi xóa đánh giá")
        return {"message": "Xóa đánh giá thành công"}
    except mysql.connector.Error as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/phieudiem", response_model=List[PhieuDiemRenLuyen])
async def get_phieudiem():
    result = execute_query("SELECT * FROM PHIEUDIEMRENLUYEN", fetch=True)
    if result is None:
        raise HTTPException(status_code=500, detail="Lỗi cơ sở dữ liệu")
    return result

@app.post("/api/phieudiem")
async def add_phieudiem(
    IDPHIEU: str = Form(...),
    IDSINHVIEN: str = Form(...),
    IDHOCKY: str = Form(...),
    GHICHU: Optional[str] = Form(None)
):

    query = """
    SELECT SUM((SVDANHGIA + CANBODANHGIA + CVHTXACNHAN) / 3) as total
    FROM DANHGIA
    WHERE IDPHIEU = %s
    """
    result = execute_query(query, (IDPHIEU,), fetch=True)
    TONGDIEM = int(result[0]["total"]) if result and result[0]["total"] else 0

    if not (0 <= TONGDIEM <= 100):
        raise HTTPException(status_code=400, detail="Tổng điểm không hợp lệ")

    XEPLOAI = (
        "Xuất sắc" if TONGDIEM >= 90 else
        "Tốt" if TONGDIEM >= 80 else
        "Khá" if TONGDIEM >= 70 else
        "Trung bình"
    )

    query = "INSERT INTO PHIEUDIEMRENLUYEN (IDPHIEU, IDSINHVIEN, IDHOCKY, TONGDIEM, XEPLOAI, GHICHU) VALUES (%s, %s, %s, %s, %s, %s)"
    try:
        success = execute_query(query, (IDPHIEU, IDSINHVIEN, IDHOCKY, TONGDIEM, XEPLOAI, GHICHU))
        if not success:
            raise HTTPException(status_code=400, detail="Lỗi khi thêm phiếu điểm")
        return {"message": "Thêm phiếu điểm thành công"}
    except mysql.connector.Error as e:
        if e.errno == 1452:
            raise HTTPException(status_code=400, detail="Mã sinh viên hoặc học kỳ không tồn tại")
        if e.errno == 1062:
            raise HTTPException(status_code=400, detail="Mã phiếu đã tồn tại")
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/api/phieudiem/{IDPHIEU}")
async def update_phieudiem(
    IDPHIEU: str,
    IDSINHVIEN: str = Form(...),
    IDHOCKY: str = Form(...),
    GHICHU: Optional[str] = Form(None)
):

    query = """
    SELECT SUM((SVDANHGIA + CANBODANHGIA + CVHTXACNHAN) / 3) as total
    FROM DANHGIA
    WHERE IDPHIEU = %s
    """
    result = execute_query(query, (IDPHIEU,), fetch=True)
    TONGDIEM = int(result[0]["total"]) if result and result[0]["total"] else 0

    if not (0 <= TONGDIEM <= 100):
        raise HTTPException(status_code=400, detail="Tổng điểm không hợp lệ")

    XEPLOAI = (
        "Xuất sắc" if TONGDIEM >= 90 else
        "Tốt" if TONGDIEM >= 80 else
        "Khá" if TONGDIEM >= 70 else
        "Trung bình"
    )

    query = "UPDATE PHIEUDIEMRENLUYEN SET IDSINHVIEN = %s, IDHOCKY = %s, TONGDIEM = %s, XEPLOAI = %s, GHICHU = %s WHERE IDPHIEU = %s"
    try:
        success = execute_query(query, (IDSINHVIEN, IDHOCKY, TONGDIEM, XEPLOAI, GHICHU, IDPHIEU))
        if not success:
            raise HTTPException(status_code=400, detail="Lỗi khi cập nhật phiếu điểm")
        return {"message": "Cập nhật phiếu điểm thành công"}
    except mysql.connector.Error as e:
        if e.errno == 1452:
            raise HTTPException(status_code=400, detail="Mã sinh viên hoặc học kỳ không tồn tại")
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/api/phieudiem/{IDPHIEU}")
async def delete_phieudiem(IDPHIEU: str):
    if await check_foreign_key("PHIEUDIEMRENLUYEN", "IDPHIEU", IDPHIEU):
        raise HTTPException(status_code=400, detail="Không thể xóa phiếu vì có dữ liệu liên quan")
    query = "DELETE FROM PHIEUDIEMRENLUYEN WHERE IDPHIEU = %s"
    try:
        success = execute_query(query, (IDPHIEU,))
        if not success:
            raise HTTPException(status_code=400, detail="Lỗi khi xóa phiếu điểm")
        return {"message": "Xóa phiếu điểm thành công"}
    except mysql.connector.Error as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/report/class/{LOP}/{IDHOCKY}", response_model=List[dict])
async def get_class_report(LOP: str, IDHOCKY: str):
    query = """
    SELECT s.HOVATEN, p.TONGDIEM, p.XEPLOAI, p.GHICHU
    FROM SINHVIEN s
    JOIN PHIEUDIEMRENLUYEN p ON s.IDSINHVIEN = p.IDSINHVIEN
    WHERE s.LOP = %s AND p.IDHOCKY = %s
    """
    result = execute_query(query, (LOP, IDHOCKY), fetch=True)
    if result is None:
        raise HTTPException(status_code=500, detail="Lỗi cơ sở dữ liệu")
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)